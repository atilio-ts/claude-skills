---
name: personal:custom-init
version: 2.1.0
description: |
  Bootstraps a new project with the full productivity setup: verifies filestash,
  code-review-graph, and houtini-lm are configured as global MCPs and online, writes a
  .code-review-graphignore tuned to the project type, builds the knowledge graph for the
  repo, hands off to /claude-docs to generate the initial .vscode/CLAUDE.md documentation
  set, and adds the tool output folders to .gitignore.
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

Bootstrap a new project with filestash + code-review-graph so every session starts fast
and cheap, then hand off to `/claude-docs` for the actual documentation content.

This file is a thin orchestrator for tooling setup. Detailed procedures live in
`reference/` — read the relevant file before acting on that step. Documentation
generation itself is not this skill's job — see Step 6.

## Usage

```
/custom-init                        # auto-detect project structure, full setup
/custom-init --modules name         # only build graph for specific modules
/custom-init --skip-graph           # skip graph build (configure MCP only)
/custom-init --skip-docs            # skip the /claude-docs hand-off
```

## What this skill does

1. **Verify global MCPs** — checks that filestash, code-review-graph, and houtini-lm are
   registered globally; prints fix commands for any that are missing.
2. **Write `.code-review-graphignore`** — patterns tuned to the detected project type.
3. **Build knowledge graph** — runs `code-review-graph build`, writes `.code-review-graph/`.
4. **Hand off to `/claude-docs`** — generates `.vscode/CLAUDE.md` and its deep-dive docs
   from the project metadata gathered in Step 1.
5. **Update `.gitignore`** — appends `.filestash` and `.code-review-graph` if missing.

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
Also read `README.md`, `docker-compose.yml`, and any `Makefile`/`run.sh` if present — this
metadata is what you'll hand off to `/claude-docs` in Step 6, so gather it thoroughly once
here rather than re-detecting it later.

If `--modules` was given, use only those. Otherwise, use every detected module (or `.`
for single-module repos).

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

---

## Step 2 — Verify global MCP setup

Read `reference/mcp-verification.md` and apply it in full (checks 2a–2d: filestash,
code-review-graph, houtini-lm, and `enableAllProjectMcpServers`).

---

## Step 3 — Write `.code-review-graphignore`

Read `reference/ignore-patterns.md` and apply it, using the project type(s) detected in
Step 1.

---

## Step 4 — Build the knowledge graph (skip if `--skip-graph`)

> code-review-graph automatically respects the `.code-review-graphignore` written in Step 3.

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

After build completes, run `code-review-graph status` and print the node/edge counts.

---

## Step 5 — No project `.mcp.json` needed for the global three

filestash, code-review-graph, and houtini-lm are all global — already covered in
`reference/mcp-verification.md`. Only create `.mcp.json` if this specific project needs
MCPs beyond those three; if so, add it to `.gitignore` in Step 7. If no project-specific
MCPs are needed, skip `.mcp.json` and any `.claude/` folder entirely.

---

## Step 6 — Hand off to `/claude-docs` (skip if `--skip-docs`)

Documentation generation is not implemented in this file — it lives in the `claude-docs`
skill so there's exactly one place that owns doc-generation logic, used both for initial
bootstrap and for every later update.

Read and apply `../claude-docs/SKILL.md` in **create mode**, passing it the project
metadata you already gathered in Step 1 (module list, build commands, README summary,
detected language/framework) so it doesn't re-detect what you already know.

If `--skip-docs` was passed, skip this step entirely and note in the final summary that
documentation was not generated.

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
> in Step 5. If no project-specific MCPs were needed, skip this entry.

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
✓ .vscode/CLAUDE.md and deep-dive docs — [generated via /claude-docs / skipped (--skip-docs)]
✓ .gitignore updated (.filestash, .code-review-graph)

Next steps:
  1. Restart Claude Code so the code-review-graph MCP loads the new database.
  2. If houtini-lm was offline, start LM Studio and load a model before the session.
  3. Run `code-review-graph update` after significant code changes.
  4. Run /claude-docs periodically as the codebase evolves — generated docs go stale
     fast, and /claude-docs's audit mode catches drift against the current code.
```

---

## Important notes

- **Never modify `~/.claude.json` or `~/.claude/settings.json` automatically** — only
  print instructions for the user.
- **Never create `.claude/settings.local.json` in the project** — the global
  `enableAllProjectMcpServers: true` in `~/.claude/settings.json` makes it unnecessary.
- **Never overwrite an existing `.vscode/CLAUDE.md`** without asking the user first — and
  in practice this shouldn't come up, since Step 6 delegates to `/claude-docs`, which
  already detects existing docs and switches to audit-and-update mode instead of
  overwriting.
- **`.vscode/` is typically gitignored** — treat anything written there as uncommitted
  work with no `git checkout` safety net. Never delete a file in there without explicit
  user confirmation (this matters most in `/claude-docs`'s audit mode, not this skill,
  but it's worth remembering while writing anything under `.vscode/`).
- **code-review-graph is global** — never write code-review-graph into `.mcp.json`. The
  global binary at `/Users/atilio/.local/bin/code-review-graph` handles all projects via
  `$PWD` resolution.
- **`.mcp.json` only for project-scoped MCPs** — only create it if the project needs
  MCPs beyond the global ones (filestash, code-review-graph, houtini-lm). Add it to
  `.gitignore`.
- **houtini-lm is global** — never write houtini-lm into `.mcp.json`. It is registered
  globally and connects to LM Studio on `localhost:1234`. Verify it is online via
  `mcp__houtini-lm__discover` during setup.