---
name: personal:claude-docs
version: 1.1.0
description: |
  Creates or updates a project's Claude Code documentation (.vscode/CLAUDE.md and its
  deep-dive docs) so it stays a reliable map of the codebase over time. Detects whether
  docs already exist and switches between two modes: generate from scratch (new project,
  or right after /custom-init), or audit-and-update (verify every existing claim against
  current code, fix what's wrong, fill gaps, flag redundant/stale files for deletion).
  Never invents facts — every claim is grounded in the actual source at write time.
trigger: /claude-docs
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - AskUserQuestion
---

# /claude-docs

Keep a project's Claude Code documentation (`.vscode/CLAUDE.md` + its deep-dive docs)
accurate and easy to navigate — as a one-time generation job right after bootstrap, and as
a recurring maintenance job as the codebase evolves.

This file is a thin orchestrator. Detailed methodology for each concern lives in
`reference/` — read the relevant file before acting on that concern, don't wing it from
this summary alone.

## Usage

```
/claude-docs                  # auto-detect mode: create if no docs exist, else audit+update
/claude-docs --create         # force create-from-scratch mode
/claude-docs --audit          # force audit-and-update mode over existing docs
/claude-docs --module <name>  # scope to one module/subsystem instead of the whole project
```

---

## Step 1 — Detect mode

```bash
[ -f .vscode/CLAUDE.md ] && echo "EXISTS" || echo "MISSING"
```

- No `.vscode/CLAUDE.md` (or `--create` passed) → **create mode**. This is also what
  `/custom-init` hands off to after its own bootstrap steps (MCP setup, graph build,
  ignore files) — if you were invoked from there, you already have: detected project
  type, module list, build commands, and language. Reuse them, don't re-detect.
- `.vscode/CLAUDE.md` exists (or `--audit` passed) → **audit-and-update mode**.
- `--module <name>` scopes either mode to one module/subsystem's docs instead of the
  whole tree.

---

## Step 2 — Map what should be documented

Read `reference/gap-analysis.md` now, regardless of mode. It explains how to find the
project's real "component map" — the entry-point/config layer that enumerates what
actually exists (routes, deploy configs, job schedulers, CLI commands, public API surface,
depending on project type) — and how to cross-check that map against what's already
documented. This is the step that finds "PayStudio has zero docs" or "this cron job was
never mentioned anywhere" — don't skip it even in create mode, since a shallow
directory-listing pass misses subsystems that only show up in configuration.

---

## Step 3a — Create mode

Using the component map from Step 2:

1. Read `reference/structure-and-splitting.md` for how to decide file layout — when a
   single `.vscode/CLAUDE.md` suffices vs. when a module needs its own deep-dive folder,
   and the "Component Map" table pattern that indexes them.
2. Write `.vscode/CLAUDE.md` (root) plus per-module/per-component files per that decision.
   Every factual claim (build commands, ports, config keys, class names) must come from
   files you actually read this session — apply `reference/verification-rigor.md` from the
   first line you write, not just in audit mode.
3. Skip Step 3b, go to Step 4.

## Step 3b — Audit-and-update mode

Read `reference/audit-existing-docs.md`. It covers: how to verify existing claims against
current code (including when to fan out parallel agents for a large doc tree), the
ACCURATE / OUTDATED / REDUNDANT / RESOLVED verdict system, and how to fix what's
confirmed wrong without also touching what's still accurate.

If the audit surfaces redundant, superseded, or dead docs (two files covering the same
thing, a doc describing a mechanism that was later reverted, a doc for a resolved bug),
read `reference/redundancy-and-deletion.md` before proposing anything be removed — there
is a hard confirmation rule in there, don't skip it.

If a doc describes a bug and you need to determine whether the current branch introduced
it (vs. it being pre-existing), or a `RESOLVED` verdict hinges on a fix that lives on some
other branch, read `reference/cross-branch-verification.md` for the concrete git recipe —
don't answer either question from a loose read of a diff.

For genuine gaps found via Step 2 that don't have a file yet, write them following
`reference/structure-and-splitting.md`, same as create mode.

---

## Step 4 — Verification pass (both modes)

Read `reference/verification-rigor.md` if you haven't yet this session. Before finalizing
any file: re-derive every load-bearing claim from the actual current source, especially
anything that came from a subagent's report — subagents are useful for coverage, not a
substitute for the primary agent's own final check on anything you're about to assert as
fact.

---

## Step 5 — Reconcile with project memory

If this project uses the auto-memory system (check for a memory index file for this
project), read `reference/memory-reconciliation.md`. Doc updates frequently resolve or
invalidate something tracked there (a deferred gap that got implemented, an architecture
memory that's now stale) — reconcile it in the same pass, don't leave it for later.

---

## Step 6 — Summarize and confirm

Report, concisely:
- What's new (files created) and what changed (files corrected, with the specific wrong
  claim → corrected claim for anything non-trivial)
- Any files proposed for deletion or merging — present via `AskUserQuestion`, do not
  delete without an explicit answer (see `reference/redundancy-and-deletion.md`)
- Any structural gaps you found but didn't fill (out of scope for this run, or needing a
  decision on where they belong)

Don't pad this with process narration — state results, not the steps you took to get them.