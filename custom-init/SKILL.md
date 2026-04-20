---
name: custom-init
version: 2.0.0
description: |
  Bootstraps a new project with the full productivity setup: verifies filestash,
  code-review-graph, and houtini-lm are configured as global MCPs and online, writes a
  .code-review-graphignore tuned to the project type, builds the knowledge graph for the
  repo, generates a .vscode/CLAUDE.md (with per-module files for monorepos), and
  adds the tool output folders to .gitignore.
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

Bootstrap a new project with filestash + code-review-graph so every session starts fast and cheap.

## Usage

```
/custom-init                        # auto-detect project structure, full setup
/custom-init --modules rpo,nexito   # only build graph for specific modules
/custom-init --skip-graph           # skip graph build (configure MCP only)
/custom-init --skip-docs            # skip CLAUDE.md generation
```

## What this skill does

1. **Verify global MCPs** — checks that filestash, code-review-graph, and houtini-lm are registered
   globally; prints fix commands for any that are missing. Verifies houtini-lm can reach
   LM Studio via `mcp__houtini-lm__discover`.
2. **Build knowledge graph** — runs `code-review-graph build` on the specified paths (or the whole repo),
   writes `.code-review-graph/` SQLite database.
3. **Generate `.vscode/CLAUDE.md`** — produces a filled-in project doc with module index,
   build commands, architecture overview, and the Knowledge Graph workflow section.
   For monorepos, also creates one stub `<module>-CLAUDE.md` per module.
4. **Update `.gitignore`** — appends `.filestash` and `.code-review-graph` if they are missing.

> filestash, code-review-graph, and houtini-lm are all **global** MCPs. No `.mcp.json` is written
> unless the project requires additional project-scoped MCPs beyond these three.

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

### 2a — Check filestash in `~/.claude.json`

Read `~/.claude.json` and check for a `filestash` key under `mcpServers`:

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
try:
    d = json.load(open(p))
    mcp = d.get('mcpServers', {})
    if 'filestash' in mcp:
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

**If filestash is missing**, print this message to the user and continue — do NOT modify
`~/.claude.json` automatically:

```
⚠  filestash MCP not found in ~/.claude.json.

Install globally and add manually:

  npm install -g @claude-code/filestash
  echo "$(npm prefix -g)/bin/filestash"   # copy this path

Then open ~/.claude.json and insert under "mcpServers":

  "filestash": {
    "command": "<path from above>",
    "args": ["serve"]
  }

Do NOT use npx — it is unreliable when the npx cache expires.
Restart Claude Code after editing.
```

**If filestash is present**, print: `✓ filestash MCP is configured globally`.

### 2b — Check code-review-graph global MCP in `~/.claude.json`

code-review-graph is configured globally (not per-project) as a direct binary:

```bash
python3 -c "
import json, os
p = os.path.expanduser('~/.claude.json')
try:
    d = json.load(open(p))
    mcp = d.get('mcpServers', {})
    if 'code-review-graph' in mcp:
        print('OK')
    else:
        print('MISSING')
except Exception as e:
    print(f'ERROR: {e}')
"
```

Also verify the binary exists:

```bash
[ -f "/Users/atilio/.local/bin/code-review-graph" ] && echo "OK" || echo "MISSING"
```

**If code-review-graph is missing**, print this message and continue — do NOT modify files automatically:

```
⚠  code-review-graph global MCP not found.

Install and register globally:

  pipx install code-review-graph

Then add to ~/.claude.json under "mcpServers":

  "code-review-graph": {
    "command": "/Users/<username>/.local/bin/code-review-graph",
    "args": ["serve"]
  }

Restart Claude Code after editing.
```

**If present**, print: `✓ code-review-graph MCP is configured globally`.

### 2c — Check houtini-lm global MCP

houtini-lm is configured globally (not per-project) and connects Claude Code to the
local LLM running in LM Studio on `localhost:1234`. Check that it is registered and
using a direct binary path (not `npx -y`, which is unreliable):

```bash
claude mcp list 2>/dev/null | grep -i houtini
```

**If missing**, print this message and continue — do NOT modify files automatically:

```
⚠  houtini-lm global MCP not found.

Install and register globally with a direct binary path:

  npm install -g @houtini/lm
  HOUTINI_BIN="$(npm prefix -g)/bin/houtini-lm"
  claude mcp add --scope user houtini-lm -- "$HOUTINI_BIN"

Then restart Claude Code.
```

**If present but using `npx`**, print this message — the registration should be updated
to use the installed binary for reliability:

```
⚠  houtini-lm is registered via npx — this can fail on slow networks or cold starts.

Re-register with the direct binary path:

  npm install -g @houtini/lm
  claude mcp remove houtini-lm
  HOUTINI_BIN="$(npm prefix -g)/bin/houtini-lm"
  claude mcp add --scope user houtini-lm -- "$HOUTINI_BIN"

Then restart Claude Code.
```

**If present with a direct binary path**, call `mcp__houtini-lm__discover` to verify
the local LLM server is reachable:

- If the tool returns `Status: ONLINE` → print: `✓ houtini-lm connected — <model name>`
- If it returns `Status: OFFLINE` → print:

```
⚠  houtini-lm is registered but LM Studio is not running.

Start LM Studio and load a model, then re-run /custom-init or verify manually
with: claude mcp list
```

Do NOT fail the setup — continue with the remaining steps.

### 2d — Check `enableAllProjectMcpServers` in `~/.claude/settings.json`

This setting auto-enables any `.mcp.json` found in a project root, without needing a
per-project `.claude/settings.local.json`.

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

Then restart Claude Code.
```

**If present**, print: `✓ enableAllProjectMcpServers is set globally`.

---

## Step 3 — Write `.code-review-graphignore`

code-review-graph has native support for `.code-review-graphignore` (gitignore-style patterns). It already
excludes common noise by default (`node_modules`, `__pycache__`, `.git`, `build`, `target`,
`dist`, `out`, `venv`, lock files). The `.code-review-graphignore` file adds project-type-specific
patterns that are NOT excluded by default, reducing extraction cost.

**This file should be committed** — it is project config, not machine-specific output.

### 3a — Check if `.code-review-graphignore` already exists

```bash
[ -f ".code-review-graphignore" ] && echo "EXISTS" || echo "MISSING"
```

If it already exists, skip this step.

### 3b — Detect project type and write patterns

Based on the build system detected in Step 1, write `.code-review-graphignore` with the
appropriate patterns. Always include the universal block, then append the
language-specific block.

```bash
cat > .code-review-graphignore << 'EOF'
# ── Universal noise ──────────────────────────────────────────────────────────
# code-review-graph already skips: node_modules, __pycache__, .git, build,
# target, dist, out, venv, lock files. These extend that baseline.

# Tool output folders (machine-specific, no semantic value)
.code-review-graph/
.filestash/
temporary/

# IDE and OS noise
.idea/
.DS_Store
*.iml
EOF
```

Then append the block that matches the detected build system:

**Java / Gradle or Maven:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Java ─────────────────────────────────────────────────────────────────────
# Compiled bytecode
*.class
*.jar
*.war
*.ear

# Gradle caches and wrapper binaries
.gradle/
gradle/wrapper/gradle-wrapper.jar

# Vendored / local Maven repos (binary JARs, no source value)
local-maven/

# Generated source (OpenAPI codegen output, etc.)
build/gm/

# Test fixtures and generated test data (high volume, low semantic value)
src/test/resources/
**/test-data/
**/fixtures/
**/__snapshots__/
EOF
```

**Node.js / TypeScript:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Node.js / TypeScript ─────────────────────────────────────────────────────
# Framework build output
.next/
.nuxt/
.svelte-kit/

# Test coverage reports and snapshots
coverage/
.nyc_output/
**/__snapshots__/
**/*.snap

# Type declaration caches
*.tsbuildinfo

# Test fixtures (data files, not logic)
**/fixtures/
**/test-data/
**/mocks/data/
EOF
```

**Python:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Python ───────────────────────────────────────────────────────────────────
*.pyc
*.pyo
*.pyd
.Python
*.egg
*.egg-info/
dist/
htmlcov/
.coverage

# Test fixtures
**/fixtures/
**/test_data/
**/__snapshots__/
EOF
```

**Go:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Go ───────────────────────────────────────────────────────────────────────
vendor/
*.test
*.out

# Test fixtures
**/testdata/
**/fixtures/
EOF
```

**Rust:**
```bash
cat >> .code-review-graphignore << 'EOF'

# ── Rust ─────────────────────────────────────────────────────────────────────
**/*.rs.bk

# Test fixtures
**/fixtures/
**/test_data/
EOF
```

> **Note on test source files** (`.java`, `.ts`, `.py`, etc.): test logic files are
> intentionally NOT ignored. They contain domain knowledge, reveal how the system is
> expected to behave, and produce high-value nodes in the graph. Only data/fixture files
> are excluded since they are high-volume with no architectural signal.

For **monorepos** mixing languages, append all relevant blocks.

After writing, print the number of patterns added and confirm the file was created.

---

## Step 4 — Build the knowledge graph (skip if --skip-graph)

> code-review-graph will automatically respect the `.code-review-graphignore` written in Step 3.

### 4a — Ensure code-review-graph is installed

```bash
which code-review-graph 2>/dev/null && echo "OK" || echo "MISSING"
```

If missing, print:

```
⚠  code-review-graph not found in PATH.

Install with:

  pipx install code-review-graph

Then restart Claude Code and re-run /custom-init.
```

### 4b — Run the build

If `--modules` was given (e.g. `rpo,nexito`), build the graph over those paths.
Otherwise, if a `modules/` directory was detected, ask the user which modules to include
before running. For single-module repos, use the repo root.

```bash
code-review-graph build
```

For targeted builds over specific directories:

```bash
code-review-graph build --repo <path>
```

This produces `.code-review-graph/` (SQLite database) in the repo root.

After build completes, run:

```bash
code-review-graph status
```

Print the node/edge counts from the status output.

---

## Step 5 — code-review-graph MCP is global — no `.mcp.json` needed for it

code-review-graph is configured globally via `~/.claude.json` as a direct binary invocation.
**Do not write code-review-graph into `.mcp.json`.**

The MCP server (`code-review-graph serve`) resolves the `.code-review-graph/` database
dynamically from `$PWD` at startup. If the database doesn't exist yet (before first build),
the server will still start but graph tools will return empty results — this is expected.

### 5a — houtini-lm is global — no `.mcp.json` needed for it

houtini-lm is registered globally and connects to LM Studio on `localhost:1234`.
**Do not write houtini-lm into `.mcp.json`.** Its availability was already verified
in Step 2c.

Only create `.mcp.json` if this specific project requires MCPs beyond the three global
ones (filestash, code-review-graph, houtini-lm). If no project-specific MCPs are needed, skip
this file entirely.

### 5b — No per-project `.claude/` needed

Since `enableAllProjectMcpServers: true` lives in the global `~/.claude/settings.json`,
any `.mcp.json` written in step 5a is picked up automatically. Do NOT create
`.claude/settings.local.json` or any `.claude/` folder in the project.

---

## Step 6 — Generate `.vscode/CLAUDE.md` (skip if --skip-docs)

### 6a — Gather project metadata

Before writing, read as many of these as exist to fill in real values:

- `README.md` — project name, description, overview
- `settings.gradle` / `settings.gradle.kts` — module names
- `build.gradle` / `build.gradle.kts` — Java version, dependencies
- `docker-compose.yml` — service names, ports
- `Makefile` or `run.sh` — common commands

### 6b — Detect language and build tool

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

### 6c — Write central `.vscode/CLAUDE.md`

Create the `.vscode/` directory if it does not exist. Write the file using the template
below. Fill in every placeholder with real values gathered in 6a–6b. Do not leave
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

## Response Approach

- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Do not re-read files you have already read unless the file may have changed.
- Skip files over 100KB unless explicitly required.
- Suggest running `/cost` when a session runs long to monitor cache ratio.
- Recommend starting a new session when switching to an unrelated task.
- Test your code before declaring done.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct.
- User instructions always override everything in this file.

## Knowledge Graph

A pre-built knowledge graph lives in `.code-review-graph/`.

**Use the graph BEFORE reading files for any architecture, cross-module, or change-impact question.**

Workflow:
1. Use `mcp__code-review-graph__semantic_search_nodes_tool` or `mcp__code-review-graph__query_graph_tool`
   to find relevant nodes and their source file paths
2. Use `mcp__filestash__read_file` to read only those specific files (cached after first read)
3. Before touching any file, use `mcp__code-review-graph__get_impact_radius_tool` to assess blast radius

Available graph tools:
- `mcp__code-review-graph__get_minimal_context_tool` — ultra-compact context (~100 tokens), call first
- `mcp__code-review-graph__semantic_search_nodes_tool` — find symbols by name or meaning
- `mcp__code-review-graph__query_graph_tool` — callers, callees, imports, inheritance
- `mcp__code-review-graph__traverse_graph_tool` — BFS/DFS traversal from any node
- `mcp__code-review-graph__get_hub_nodes_tool` — most-connected nodes (core abstractions)
- `mcp__code-review-graph__get_impact_radius_tool` — blast radius of changed files
- `mcp__code-review-graph__detect_changes_tool` — risk-scored change impact for review
- `mcp__code-review-graph__get_architecture_overview_tool` — architecture from community structure
- `mcp__code-review-graph__list_graph_stats_tool` — graph size and health

Update after significant code changes: `code-review-graph update`
```

### 6d — Write per-module stub files (monorepos only)

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

## Step 7 — Update `.gitignore`

Read the current `.gitignore` (or create it if missing). Check whether `.filestash`
and `.code-review-graph` are already present. Append only the missing ones:

```bash
GITIGNORE=".gitignore"
MISSING=""

grep -qxF ".filestash" "$GITIGNORE" 2>/dev/null          || MISSING="$MISSING\n.filestash"
grep -qxF ".code-review-graph" "$GITIGNORE" 2>/dev/null  || MISSING="$MISSING\n.code-review-graph"

if [ -n "$MISSING" ]; then
    printf "$MISSING\n" >> "$GITIGNORE"
    echo "Updated .gitignore"
else
    echo ".gitignore already up to date"
fi
```

> Only add `.mcp.json` to `.gitignore` if a project-specific `.mcp.json` was created
> in Step 5a. If no project-specific MCPs were needed, skip this entry.

---

## Step 8 — Print summary

After all steps complete, print a concise summary:

```
✓ filestash MCP — [configured globally / MISSING — see instructions above]
✓ code-review-graph global MCP — [configured globally / MISSING — see instructions above]
✓ houtini-lm global MCP — [connected (<model>) / registered but LM Studio offline / MISSING — see instructions above]
✓ enableAllProjectMcpServers — [set globally / MISSING — see instructions above]
✓ .code-review-graphignore written — [N patterns, Java/Node/Python/Go/Rust block]
✓ code-review-graph built — .code-review-graph/ ([N nodes, M edges] from status output)
✓ .mcp.json — [written (project-scoped MCPs only) / skipped (none needed)]
✓ .vscode/CLAUDE.md written
✓ .vscode/<module>-CLAUDE.md stubs written: [list]
✓ .gitignore updated (.filestash, .code-review-graph)

Next steps:
  1. Restart Claude Code so the code-review-graph MCP loads the new database.
  2. If houtini-lm was offline, start LM Studio and load a model before the session.
  3. Fill in any [TODO] placeholders in .vscode/CLAUDE.md.
  4. Run `code-review-graph update` after significant code changes.
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
- **code-review-graph is global** — never write code-review-graph into `.mcp.json`. The global
  binary at `/Users/atilio/.local/bin/code-review-graph` handles all projects via `$PWD` resolution.
- **`.mcp.json` only for project-scoped MCPs** — only create it if the project needs
  MCPs beyond the global ones (filestash, code-review-graph, houtini-lm). Add to `.gitignore`.
- **houtini-lm is global** — never write houtini-lm into `.mcp.json`. It is registered
  globally and connects to LM Studio on `localhost:1234`. Verify it is online via
  `mcp__houtini-lm__discover` during setup.
