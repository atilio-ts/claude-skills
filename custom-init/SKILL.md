---
name: personal:custom-init
version: 3.0.0
description: |
  Bootstraps a new project with the full productivity setup: verifies filestash
  and code-review-graph are configured as global MCPs and online, registers markdown
  as a parsed language so .vscode/ docs get indexed, builds the knowledge graph for the repo,
  recommends stack-specific plugins, MCPs and skills (prints commands, installs nothing),
  hands off to /claude-docs to generate .vscode/CLAUDE.md and .vscode/docs/, hides every
  tooling path from git through .git/info/exclude (never .gitignore), and links .claude/
  and .omp/ to .vscode/ so Claude Code and omp share one config. Re-running it on a repo
  set up by an older version repairs the legacy setup.
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

1. **Verify global MCPs** — checks that filestash and code-review-graph are
   registered globally; prints fix commands for any that are missing.
2. **Write `.vscode/code-review-graph/languages.toml`** — registers markdown so
   the `.vscode/` docs become graph nodes.
3. **Build knowledge graph** — runs `code-review-graph build --data-dir
   .vscode/code-review-graph`.
4. **Recommend stack tooling** — plugins, project MCPs and skills that fit the detected
   stack, as commands for the user to run.
5. **Hand off to `/claude-docs`** — generates `.vscode/CLAUDE.md` and `.vscode/docs/`
   from the project metadata gathered in Step 1.
6. **Hide tooling from git** — adds every tooling path to `.git/info/exclude`. Never
   adds to `.gitignore`, which is committed and visible to the team.
7. **Repair a legacy setup** — removes what older versions left behind (`.gitignore`
   lines, root ignore files, `.mcp.json`, stale tool data), with confirmation.
8. **Link `.claude/` and `.omp/`** — `.claude/CLAUDE.md`, `.claude/agents` and
   `.claude/skills` point into `.vscode/`; `.omp/agents` too, since omp reads everything
   else from `.claude/`.
9. **Check nothing leaks** — `git status` must show no tooling path.

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

Read `reference/mcp-verification.md` and apply it in full (checks 2a–2b: filestash and
code-review-graph).

---

## Step 3b — Write `.vscode/code-review-graph/languages.toml`

Read `reference/languages-config.md` and apply it. This registers markdown as a parsed
language so `.vscode/CLAUDE.md` and `.vscode/docs/` become graph nodes, not just visible
files.

---

## Step 4 — Build the knowledge graph (skip if `--skip-graph`)

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

If `--modules` was given (e.g. `api,worker`), build the graph over those paths.
Otherwise, if a `modules/` directory was detected, ask the user which modules to include
before running. For single-module repos, use the repo root.

```bash
code-review-graph build --data-dir .vscode/code-review-graph
```

`--data-dir` persists in a machine-wide registry (`~/.code-review-graph/registry.json`)
keyed by resolved repo path — set it once and every later `build`/`status`/MCP call
resolves there automatically, no need to repeat the flag.

For targeted builds over specific directories:

```bash
code-review-graph build --repo <path> --data-dir <path>/.vscode/code-review-graph
```

This produces `.vscode/code-review-graph/` (SQLite database, alongside the
`languages.toml` from Step 3b) instead of a top-level `.code-review-graph/` — so nothing
code-review-graph-related is ever created outside `.vscode/`, which Step 7 hides from
git.

After build completes, run `code-review-graph status` and print the node/edge counts.

---

## Step 5 — Recommend stack tooling

Read `reference/tooling-catalog.md` and apply it to the stack detected in Step 1. Print
the recommendations with their commands; don't install, enable, or write any config.
filestash and code-review-graph are global (see `reference/mcp-verification.md`) and
never go in a project `.mcp.json`.

---

## Step 6 — Hand off to `/claude-docs` (skip if `--skip-docs`)

Documentation generation is not implemented in this file — it lives in the `claude-docs`
skill so there's exactly one place that owns doc-generation logic, used both for initial
bootstrap and for every later update.

Read and apply `../claude-docs/SKILL.md`, letting it auto-detect the mode: create mode on
a fresh repo, audit mode when `.vscode/CLAUDE.md` already exists — which is also what
migrates an old `.vscode/<module>-CLAUDE.md` layout into `.vscode/docs/`. Pass it the project
metadata you already gathered in Step 1 (module list, build commands, README summary,
detected language/framework) so it doesn't re-detect what you already know. It writes
`.vscode/CLAUDE.md` and `.vscode/docs/`, nothing else.

If `--skip-docs` was passed, skip this step entirely and note in the final summary that
documentation was not generated.

---

## Step 7 — Hide tooling from git

Nothing AI- or agent-related may show up in the committed repo — not as files, and not as
`.gitignore` entries either, since `.gitignore` is itself committed. Every path goes into
`.git/info/exclude`, which is local to this clone and never committed. Never write to
`.gitignore`.

If the repo already tracks files under `.vscode/` (a shared `settings.json`, launch
configs), excluding the whole folder would hide the team's future files too — exclude
only the paths this setup owns instead:

```bash
if git rev-parse --git-dir >/dev/null 2>&1; then
    EXCLUDE=$(git rev-parse --git-path info/exclude)
    mkdir -p "$(dirname "$EXCLUDE")"
    if [ -n "$(git ls-files .vscode)" ]; then
        VSCODE=".vscode/CLAUDE.md .vscode/docs/ .vscode/.claude/ .vscode/.mcp.json .vscode/code-review-graph/ .vscode/file-stash/ .vscode/temporary/"
    else
        VSCODE=".vscode/"
    fi
    for p in $VSCODE .claude/ .omp/ .mcp.json .file-stash/ .filestash/ .code-review-graph/ .code-review-graphignore .cachebro/ graphify-out/ .graphifyignore; do
        rg -qxF "$p" "$EXCLUDE" 2>/dev/null || echo "$p" >> "$EXCLUDE"
    done
fi
```

If a tooling path is already tracked, exclusion has no effect on it — Step 7a handles
that.

> If `~/.claude.json` doesn't have `FILESTASH_DIR` set yet, file-stash writes to
> `.file-stash` at the repo root — the exclude above still hides it, but the global MCP
> fix is outside this skill's scope, see DEV_SETUP.md's file-stash section.

---

## Step 7a — Repair a legacy setup

Read `reference/legacy-repair.md` and apply it. On a fresh repo it finds nothing; on a
repo bootstrapped by an older version it cleans up the `.gitignore` lines, tracked or
leftover root files, and stale tool data those versions left, each with confirmation.

---

## Step 7b — Link `.claude/` and `.omp/` to `.vscode/`

Everything real lives in `.vscode/`; the root `.claude/` and `.omp/` folders hold only
symlinks, already hidden by Step 7.

- `.claude/CLAUDE.md` makes Claude Code load the project instructions on its own, and
  omp loads the same file through its `.claude/` discovery.
- `.claude/agents` and `.claude/skills` — omp reads skills from `.claude/skills` too.
- `.omp/agents` — omp doesn't read `.claude/agents`, so agents need their own link.
  No `.vscode/.omp/` copy: omp already takes the rest of its project config from
  `.claude/`.

```bash
mkdir -p .vscode/.claude/agents .vscode/.claude/skills .vscode/docs .claude .omp
link() {
    if [ -L "$2" ]; then
        echo "$2 already linked"
    elif [ -e "$2" ]; then
        echo "WARNING: $2 exists and is not a symlink — left untouched"
    else
        ln -s "$1" "$2"
    fi
}
link ../.vscode/.claude/agents .claude/agents
link ../.vscode/.claude/skills .claude/skills
link ../.vscode/.claude/agents .omp/agents
[ -f .vscode/CLAUDE.md ] && link ../.vscode/CLAUDE.md .claude/CLAUDE.md
```

Run the `.claude/CLAUDE.md` link after Step 6, once `/claude-docs` has written the file.
Never move or delete an existing `.claude/agents`, `.claude/skills`, `.claude/CLAUDE.md`
or `.omp/agents` — if one is a real file or directory, report it in the summary and let
the user decide. Never create a root `CLAUDE.md` or `AGENTS.md`.

---

## Step 8 — Check nothing leaks, then print summary

```bash
git status --porcelain --ignored=no | rg '(^|/)(\.claude|\.omp|\.mcp\.json|\.file-?stash|\.code-review-graph|\.cachebro|graphify-out|\.graphifyignore|\.vscode/(CLAUDE\.md|docs|\.claude))' \
    && echo "LEAK" || echo "clean"
```

Any `LEAK` line is a failure: name the path in the summary and fix the exclude before
finishing.

Print a concise summary:

```
✓ filestash MCP — [configured globally / MISSING — see instructions above]
✓ code-review-graph global MCP — [configured globally / MISSING — see instructions above]
✓ .vscode/code-review-graph/languages.toml written — [markdown registered / already existed]
✓ code-review-graph built — .vscode/code-review-graph/ ([N nodes, M edges] from status output)
✓ Stack tooling — [N recommendations printed above / nothing to recommend]
✓ .vscode/CLAUDE.md and .vscode/docs/ — [generated via /claude-docs / skipped (--skip-docs)]
✓ Legacy repair — [nothing found / repaired: <items> / kept by choice: <items>]
✓ .git/info/exclude — [N paths added / already up to date] ([.vscode/ whole / owned subpaths only, .vscode is tracked])
✓ .claude/{CLAUDE.md,agents,skills} — [linked / already linked / left untouched (real file or directory)]
✓ .omp/agents — [linked / already linked / left untouched (real directory)]
✓ git status — [clean / LEAK: <paths>]

Next steps:
  1. Restart Claude Code so the code-review-graph MCP loads the new database.
  2. Run `code-review-graph update` after significant code changes.
  3. Run /claude-docs periodically as the codebase evolves — generated docs go stale
     fast, and /claude-docs's audit mode catches drift against the current code.
```

---

## Important notes

- **Never modify `~/.claude.json` or `~/.claude/settings.json` automatically** — only
  print instructions for the user.
- **Never create `.claude/settings.local.json` in the project** — project settings live in
  `.vscode/.claude/`.
- **Never write to `.gitignore`** — every tooling path goes to `.git/info/exclude` (Step 7).
- **Never overwrite an existing `.vscode/CLAUDE.md`** without asking the user first — and
  in practice this shouldn't come up, since Step 6 delegates to `/claude-docs`, which
  already detects existing docs and switches to audit-and-update mode instead of
  overwriting.
- **`.vscode/` is excluded from git** — treat anything written there as uncommitted
  work with no `git checkout` safety net. Never delete a file in there without explicit
  user confirmation (this matters most in `/claude-docs`'s audit mode, not this skill,
  but it's worth remembering while writing anything under `.vscode/`).
- **`.vscode/code-review-graph/languages.toml` should still be written even though this
  machine has a global fallback** (`~/.claude/code-review-graph/languages.toml`, applied
  by a patch to the pipx install — see `dev-setup/code-review-graph/patch_global_languages.py`).
  The repo-local file is what makes the config explicit and portable to a machine without
  that patch — but note it is NOT committed (it lives under the excluded `.vscode/`). Don't
  claim otherwise when printing the final summary.
- **code-review-graph is global** — never write code-review-graph into `.mcp.json`. The
  global binary at `$HOME/.local/bin/code-review-graph` handles all projects via
  `$PWD` resolution.
- **`.mcp.json` only for project-scoped MCPs** — recommended in Step 5, never written by
  this skill. When the user adds one, it lives at `.vscode/.mcp.json` with a root
  `.mcp.json` symlink, both hidden by Step 7.
