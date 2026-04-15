---
name: custom-init
version: 1.0.0
description: |
  Bootstraps a new project with the full productivity setup: verifies cachebro
  and graphify are configured as MCPs, builds the knowledge graph for the repo,
  writes the project .mcp.json, generates a .vscode/CLAUDE.md (with per-module
  files for monorepos), and adds the tool output folders to .gitignore.
trigger: /custom-init
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /custom-init

Bootstrap a new project with cachebro + graphify so every session starts fast and cheap.

## Usage

```
/custom-init                        # auto-detect project structure, full setup
/custom-init --modules rpo,nexito   # only graphify specific modules
/custom-init --skip-graph           # skip graphify build (configure MCP only)
/custom-init --skip-docs            # skip CLAUDE.md generation
```

## What this skill does

1. **Verify cachebro MCP** — checks `~/.claude.json` for the cachebro server; prints a fix
   command if it is missing.
2. **Build knowledge graph** — runs graphify on the specified paths (or the whole repo),
   writes `graphify-out/graph.json`.
3. **Wire graphify as project MCP** — writes `.mcp.json` pointing to the generated graph
   and updates `.claude/settings.local.json` to enable it.
4. **Generate `.vscode/CLAUDE.md`** — produces a filled-in project doc with module index,
   build commands, architecture overview, and the Knowledge Graph workflow section.
   For monorepos, also creates one stub `<module>-CLAUDE.md` per module.
5. **Update `.gitignore`** — appends `.cachebro` and `graphify-out` if they are missing.

---

## Step 1 — Parse flags and read project context

Parse the user's command for `--modules`, `--skip-graph`, and `--skip-docs` flags.

Read the current working directory structure:

```bash
ls -1
```

Detect whether this is a monorepo by checking for a `modules/` directory or multiple
top-level subproject folders that contain `build.gradle`, `pom.xml`, `package.json`,
or `pyproject.toml`:

```bash
# Gradle monorepo signal
ls modules/ 2>/dev/null && echo "gradle-monorepo"

# Maven monorepo signal  
ls -d */pom.xml 2>/dev/null | head -5

# Node monorepo (workspaces)
cat package.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('workspaces',''))" 2>/dev/null

# Python monorepo
ls -d */pyproject.toml 2>/dev/null | head -5
```

Also read `settings.gradle` or `settings.gradle.kts` if it exists — it contains the
canonical list of included modules:

```bash
cat settings.gradle 2>/dev/null || cat settings.gradle.kts 2>/dev/null
```

Read `build.gradle` or root `pom.xml` to understand the build system, Java version, etc.

If `--modules` was given, use only those. Otherwise, use every detected module (or `.`
for single-module repos).

---

## Step 2 — Verify global MCP setup

### 2a — Check cachebro in `~/.claude.json`

Read `~/.claude.json` and check for a `cachebro` key under `mcpServers`:

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
try:
    d = json.load(open(p))
    mcp = d.get('mcpServers', {})
    if 'cachebro' in mcp:
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

**If cachebro is missing**, print this message to the user and continue — do NOT modify
`~/.claude.json` automatically:

```
⚠  cachebro MCP not found in ~/.claude.json.

Add it manually by opening ~/.claude.json and inserting under "mcpServers":

  "cachebro": {
    "command": "npx",
    "args": ["cachebro", "serve"]
  }

Or run:  npx cachebro --version   to confirm it is installed first.
Then restart Claude Code for the MCP to load.
```

**If cachebro is present**, print: `✓ cachebro MCP is configured globally`.

### 2b — Check `enableAllProjectMcpServers` in `~/.claude/settings.json`

This setting auto-enables any `.mcp.json` found in a project root, without needing a
per-project `.claude/settings.local.json`. Without it, graphify (and any project MCP)
must be manually enabled every time.

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude/settings.json')
try:
    d = json.load(open(p))
    if d.get('enableAllProjectMcpServers'):
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

**If missing**, print this message and continue — do NOT modify the file automatically:

```
⚠  enableAllProjectMcpServers not set in ~/.claude/settings.json.

Add it manually by opening ~/.claude/settings.json and inserting at the top level:

  "enableAllProjectMcpServers": true

Without this, the graphify MCP in .mcp.json won't load automatically.
Then restart Claude Code.
```

**If present**, print: `✓ enableAllProjectMcpServers is set globally`.

---

## Step 3 — Build the knowledge graph (skip if --skip-graph)

### 3a — Ensure graphify is installed

```bash
GRAPHIFY_BIN=$(which graphify 2>/dev/null)
if [ -n "$GRAPHIFY_BIN" ]; then
    PYTHON=$(head -1 "$GRAPHIFY_BIN" | tr -d '#!')
    case "$PYTHON" in
        *[!a-zA-Z0-9/_.-]*) PYTHON="python3" ;;
    esac
else
    PYTHON="python3"
fi
"$PYTHON" -c "import graphify" 2>/dev/null || \
    "$PYTHON" -m pip install graphifyy -q 2>/dev/null || \
    "$PYTHON" -m pip install graphifyy -q --break-system-packages 2>&1 | tail -3
mkdir -p graphify-out
"$PYTHON" -c "import sys; open('graphify-out/.graphify_python', 'w').write(sys.executable)"
```

### 3b — Run graphify

If `--modules` was given (e.g. `rpo,nexito`), build the graph over those paths.
Otherwise, if a `modules/` directory was detected, ask the user which modules to include
before running. For single-module repos, use `.` as the source path.

Use the graphify skill's full extraction pipeline — invoke `/graphify <path>` with the
resolved path. This produces `graphify-out/graph.json`.

If multiple module paths are given, run graphify on each and merge, or run on the root
with the modules listed as source paths (whichever graphify supports).

---

## Step 4 — Configure graphify as project MCP

### 4a — Write `.mcp.json`

Detect the graphify Python interpreter from `graphify-out/.graphify_python`:

```bash
cat graphify-out/.graphify_python 2>/dev/null || echo "python3"
```

Write `.mcp.json` in the project root with the absolute path to `graphify-out/graph.json`:

```bash
PYTHON_BIN=$(cat graphify-out/.graphify_python 2>/dev/null || echo "python3")
PROJECT_ROOT=$(pwd)
GRAPH_PATH="$PROJECT_ROOT/graphify-out/graph.json"

cat > .mcp.json <<EOF
{
  "mcpServers": {
    "graphify": {
      "type": "stdio",
      "command": "$PYTHON_BIN",
      "args": [
        "-m",
        "graphify.serve",
        "$GRAPH_PATH"
      ],
      "env": {}
    }
  }
}
EOF
echo "Wrote .mcp.json"
```

### 4b — No per-project `.claude/` needed

Since `enableAllProjectMcpServers: true` lives in the global `~/.claude/settings.json`,
the `.mcp.json` written in step 4a is enough — Claude Code will auto-enable graphify on
next restart. Do NOT create `.claude/settings.local.json` or any `.claude/` folder in
the project.

If for any reason `enableAllProjectMcpServers` is missing from the global settings (as
reported in step 2b), remind the user to add it globally rather than creating a local
workaround.

---

## Step 5 — Generate `.vscode/CLAUDE.md` (skip if --skip-docs)

### 5a — Gather project metadata

Before writing, read as many of these as exist to fill in real values:

- `README.md` — project name, description, overview
- `settings.gradle` / `settings.gradle.kts` — module names
- `build.gradle` / `build.gradle.kts` — Java version, dependencies
- `docker-compose.yml` — service names, ports
- `Makefile` or `run.sh` — common commands

### 5b — Detect language and build tool

Determine build commands based on what is present:

| Signal file | Build tool | Test command |
|-------------|------------|-------------|
| `gradlew` | Gradle wrapper | `./gradlew test` |
| `mvnw` | Maven wrapper | `./mvnw test` |
| `pom.xml` | Maven | `mvn test` |
| `package.json` | npm/yarn/pnpm | `npm test` |
| `pyproject.toml` | uv/poetry | `uv run pytest` |
| `Cargo.toml` | Cargo | `cargo test` |
| `go.mod` | Go | `go test ./...` |

### 5c — Write central `.vscode/CLAUDE.md`

Create the `.vscode/` directory if it does not exist. Write the file using the template
below. Fill in every placeholder with real values gathered in 5a–5b. Do not leave
`[PLACEHOLDER]` text in the output — if you cannot determine the real value, use a
reasonable default or omit the section.

```markdown
# CLAUDE.md

[One paragraph describing what this project does, who uses it, and what its main
responsibilities are. Pull from README.md if available.]

## Module Index

[Only include this section for monorepos. One row per module.]

| Module | Type | Description | Deep Docs |
|--------|------|-------------|-----------|
| `module-name` | Spring Boot / jPOS / CLI / Library | What it does | @.vscode/module-CLAUDE.md |

[For single-module repos, omit this section entirely.]

## Build Commands

[Real commands based on the build tool detected. Include: build, test, run/start,
any code generation commands, and database migration commands if present.]

```bash
# Build
./gradlew build

# Test
./gradlew test

# Run
./gradlew bootRun
```

## Architecture Overview

### Data Flow

[ASCII diagram showing how data moves through the system. If unknown, write
a brief prose description instead.]

## Programming Conventions

[Language and framework-specific conventions. Pull from README.md or
infer from the codebase. Always include:]

- **Immutability**: Prefer immutable objects.
- **File size**: Target 200–400 lines per class; 800 max.
- **Error handling**: Handle all exceptions explicitly.
- **No magic strings**: Use constants or enums.

## Local Development

[Commands to start the local dev environment. Port numbers if detectable.]

## Knowledge Graph

A pre-built knowledge graph lives in `graphify-out/`.

**Use the graph BEFORE reading files for any architecture or cross-module question.**

Workflow:
1. Use `mcp__graphify__query_graph` or `mcp__graphify__get_neighbors` to find
   relevant nodes and their source file paths
2. Use `mcp__cachebro__read_file` to read only those specific files (cached after
   first read)

Available graph tools (auto-approved, no prompt):
- `mcp__graphify__query_graph` — BFS/DFS traversal from a concept
- `mcp__graphify__get_node` — details on a specific node
- `mcp__graphify__get_neighbors` — direct connections of a node
- `mcp__graphify__shortest_path` — path between two concepts
- `mcp__graphify__god_nodes` — most-connected nodes (core abstractions)
- `mcp__graphify__graph_stats` — overall graph statistics

Update after significant code changes: `/graphify <module-path> --update`
```

### 5d — Write per-module stub files (monorepos only)

For each module in the module index, create `.vscode/<module>-CLAUDE.md` with a stub:

```markdown
# <Module Name> — Deep Docs

[One paragraph describing this module's responsibilities, its role in the overall
platform, and what other modules it interacts with.]

## Key Concepts

[List 3–5 core concepts or abstractions unique to this module.]

## Entry Points

[Main class, main XML config, or primary controller — wherever execution starts.]

## Configuration

[Where this module reads its config from (env vars, YAML, XML, etc.).]

## Testing

[How to run this module's tests in isolation.]
```

---

## Step 6 — Update `.gitignore`

Read the current `.gitignore` (or create it if missing). Check whether `.cachebro`,
`graphify-out`, and `.mcp.json` are already present. Append only the missing ones:

```bash
GITIGNORE=".gitignore"
MISSING=""

grep -qxF ".cachebro" "$GITIGNORE" 2>/dev/null    || MISSING="$MISSING\n.cachebro"
grep -qxF "graphify-out" "$GITIGNORE" 2>/dev/null || MISSING="$MISSING\ngraphify-out"
grep -qxF ".mcp.json" "$GITIGNORE" 2>/dev/null    || MISSING="$MISSING\n.mcp.json"

if [ -n "$MISSING" ]; then
    printf "\n# Claude productivity tools\n$MISSING\n" >> "$GITIGNORE"
    echo "Updated .gitignore"
else
    echo ".gitignore already up to date"
fi
```

---

## Step 7 — Print summary

After all steps complete, print a concise summary:

```
✓ cachebro MCP — [configured globally / MISSING — see instructions above]
✓ enableAllProjectMcpServers — [set globally / MISSING — see instructions above]
✓ graphify built — graphify-out/graph.json ([N nodes, M edges] from graph_stats)
✓ .mcp.json written
✓ .vscode/CLAUDE.md written
✓ .vscode/<module>-CLAUDE.md stubs written: [list]
✓ .gitignore updated (.cachebro, graphify-out, .mcp.json)

Next steps:
  1. Restart Claude Code so the graphify MCP loads.
  2. Fill in any [TODO] placeholders in .vscode/CLAUDE.md.
  3. Run /graphify <path> --update after significant code changes.
```

---

## Important notes

- **Never modify `~/.claude.json` or `~/.claude/settings.json` automatically** — only
  print instructions for the user.
- **Never create `.claude/settings.local.json` in the project** — the global
  `enableAllProjectMcpServers: true` in `~/.claude/settings.json` makes it unnecessary.
- **Never overwrite an existing `.vscode/CLAUDE.md`** without asking the user first.
  If it already exists, diff the proposed changes and ask for confirmation.
- **Never add `.vscode/` to git** — it is always in `.gitignore`.
- **Absolute paths in `.mcp.json`** — always use the absolute path for `graphify.serve`,
  never a relative one, because Claude Code can be invoked from different working directories.
- **`.mcp.json` stays in the project root** — it is project-specific (contains the path
  to this repo's graph) and must be in `.gitignore` so local machine paths aren't committed.
- For the graphify build step, delegate to the `/graphify` skill — do not re-implement
  the extraction pipeline here.
