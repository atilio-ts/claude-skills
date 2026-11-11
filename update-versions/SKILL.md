---
name: personal:update-versions
version: 1.0.0
description: |
  Updates the open project to the latest stable version of everything it pins: runtimes
  (latest patch of the newest LTS when the runtime has an LTS line), frameworks,
  libraries, build plugins, container images, CI actions and runners, and tools. Builds
  a read-only inventory with official sources and waits for approval, proves
  compatibility in a throwaway copy, writes a phased plan, runs each phase through a
  subagent while the main session reviews the diff and re-runs the checks, and records
  the version policy in the project's docs. Use when the user asks to update, upgrade or
  bump dependencies, images or CI to the latest stable versions.
trigger: /update-versions
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
---

# /update-versions

Bring every pinned version in the open project to the latest stable release, with exact
versions, verified against official sources and proven compatible before anything is
edited. The main session plans and supervises; subagents execute one phase at a time.

## Usage

```
/update-versions                    # full flow: inventory, compatibility, plan, phases
/update-versions --inventory-only   # stop after the inventory table
/update-versions --skip <area>      # leave an area out (images, build, ci, docs)
/update-versions --progress <file>  # also append the final report to that file
```

## The version rule

Apply it everywhere and write it into the project's docs in Step 8:

- Latest stable release of everything the project uses: runtimes, frameworks,
  libraries, build plugins, container images, CI actions and runners, tools.
- Runtimes with an LTS line (Java, Node.js, Ubuntu runners): latest patch of the newest
  LTS, never a newer non-LTS feature release. Say so in the inventory when the newest
  release is not LTS.
- Exact version with patch. Never `latest`, never a tag without patch (`:12`,
  `16-alpine`, `@v4`), never RC, beta, milestone, preview, EA or snapshot.
- Every version comes from its official source at run time (registry API, Maven
  Central, Gradle Plugin Portal, npm, PyPI, GitHub releases, vendor docs via Context7).
  Never from memory.
- If the latest is incompatible with another dependency, use the newest compatible one
  and record the reason next to it and in the report.

## Step 1 — Parse flags and read the project

1. Parse the flags above from the invocation text.
2. Read the project's `CLAUDE.md` (or `.vscode/CLAUDE.md`) and the deploy/testing docs
   it indexes. Extract the project's own verification commands (build, tests, format,
   contract tests, compose stack, smoke tests). Phases reuse those exact commands.
3. Note what is already modified in `git status --short`. Those changes are not yours;
   never revert or reformat them.
4. Ask the user which services, files or plans are off limits (work in progress). Do
   not touch them, only report their versions.

## Step 2 — Inventory (no edits)

Find every pinned version. Search at least: build files and version catalogs, wrapper
properties, lockfile manifests (`package.json`, `pyproject.toml`, `go.mod`...),
Dockerfiles, every compose file and override, testcontainer image strings in tests,
CI workflows (actions, runner labels, runtime versions), dependency bots, READMEs and
project docs that state versions.

Detect the ecosystems present, then read `reference/version-sources.md` and use only
the sections for those ecosystems to query the latest stable versions.

Present one table per area. Mark rule violations with ❌ and classify each change:

| File:line | Component | Current | Latest stable | Source | Type |
|---|---|---|---|---|---|
| `docker-compose.yml:5` | postgres | `16-alpine` ❌ no patch | `18.6-alpine` | Docker Hub API | major |
| `gradle/libs.versions.toml:5` | springdoc | `3.1.1` | `3.2.0` | Maven Central | minor |
| `.github/workflows/ci.yml:20` | runner | `ubuntu-latest` ❌ | `ubuntu-26.04` | actions/runner-images | major |

Also list versions managed by a framework BOM or parent (Spring Boot, a Node framework
preset...) that the repo does not pin, with managed vs. latest. List what is already at
the latest so the user sees the whole picture. List every doc line that states a
version that will change.

If `--inventory-only`, stop here. Otherwise wait for the user's explicit approval of
the inventory. Ask every decision the inventory raises in the same message (non-LTS
runtime, overriding a BOM, a proprietary option in an action, an off-limits service).

## Step 3 — Compatibility (research + throwaway copy)

Never in the repo. Two parts, run in parallel:

1. **Research.** For each major, and for each minor of a tool that hooks into compiler
   or runtime internals (formatters, static analyzers, coverage agents), read the
   official migration notes and release notes of every version in between. Delegate
   independent areas (CI actions, build toolchain, framework-managed libraries) to
   parallel subagents with narrow, read-only briefs; each one cites its sources and
   says "unconfirmed" instead of guessing.
2. **Spike.** Copy the affected module to the session scratchpad (`rsync`, excluding
   build output), apply every candidate version there, and run the project's full
   build with tests. Run spikes with the build cache disabled (`--no-build-cache` for
   Gradle). A cached failure from an incompatible spike can otherwise be replayed in
   the real repo. When a spike fails, find the root cause and try the next older
   version of the culprit until one passes. That is the "newest compatible" version.

Edit catalogs in the spike with care: the same alias can appear in several sections
(`[versions]`, `[libraries]`, `[plugins]`). Restrict `sed` to the right section.

Report the outcome. Include the root cause for every version that cannot reach the
latest, for example `jackson 3.3.0 → NoClassDefFoundError: JsonApplyView, the BOM pins
an older annotations module`. Then present the phased plan from Step 4 and wait for
approval.

## Step 4 — Write the phased plan

Write it to `.vscode/temporary/versions-upgrade-plan.md`, or to the session scratchpad
if the project has no `.vscode/`. Write it in the language of the project's existing
plans. Contents:

- **Rules:** the version rule, scope, off-limits items, no commits, no AI mentions, no
  volume deletion, UTF-8 preserved, stop when a failure has no obvious cause.
- **Target table:** component, current, new, source, type, plus an "Exceptions" table
  with the reason for each version that is not the latest.
- **Phases, in this order, each ending in a verification block with exact commands and
  the decisive output expected:**
  0. Baseline: git state, existing containers, build result, test count, warning count.
  1. Images and compose (patch-pinned tags, database majors, testcontainer images).
  2. Build tool, plugins, libraries, BOM overrides.
  3. Runtime major, only if one was approved, as its own phase.
  4. CI (actions, runner, runtime version, action inputs).
  5. Docs (Step 8).
  6. Close: full build, full stack, report.
- Majors that need migration go one at a time, each with its notes read first.

## Step 5 — Execute each phase through a subagent

For each phase, launch one subagent with a self-contained brief:

- The plan path, the single phase to run, and an explicit "stop after it and report".
- The hard rules again: no commit or push, no `down -v` or volume removal, only the
  files the phase lists, no comments beyond those in the plan.
- The local environment quirks found so far, such as blocked commands, wrappers that
  must run from a script, required `JAVA_HOME` or Node version, and the scoped stack
  command if a service is out of scope.
- The report shape: each file with old → new, `git diff --stat`, and every
  verification with its decisive output line.

Run two phases in parallel only when they touch disjoint files (for example CI and
docs). Never parallelize phases that share build or stack verification.

## Step 6 — Supervise between phases

After each subagent returns, before enabling the next phase:

1. Read the diff yourself (`git diff -- <files>`). For scripted edits, check that no
   other section or line was touched.
2. Re-run the decisive checks yourself when the report shows anything odd. Compare
   counts with the baseline. A higher warning count needs an uncached baseline build
   from `git archive HEAD` in the scratchpad before you call it new or pre-existing.
3. Fix tool deprecations the upgrade itself introduces, using the idiom the file
   already uses. Anything else unexpected goes to the user.
4. When a failure comes from something outside this plan, prove it with evidence: the
   off-limits service was already broken, or a pre-existing plan never verified it.
   Then verify this phase with a scoped command that excludes that piece, and report
   the breakage without fixing it.

## Step 7 — Stop conditions

Stop and report to the user, without improvising another design, when:

- a contract, snapshot or golden-file test drifts (never regenerate it to make it pass);
- a static analyzer adds a new error that needs code changes. Show the scope first;
- a database major meets an existing container or volume with data. Explain that the
  new binary cannot open the old data directory and that it needs dump and restore;
  never delete or recreate volumes without explicit confirmation;
- a verification fails and the cause is not obvious.

## Step 8 — Document the rule

- Search the repo and its docs for any existing version policy (`latest`, "exact tag",
  "reference versions", "última versión"...).
- Put one canonical wording of the version rule in the project's `CLAUDE.md`
  Conventions. If the project overrides a framework BOM, add that overrides live in
  the version catalog and are dropped once the framework manages an equal or newer
  version.
- Replace other policy texts with a one-line pointer.
- Committed READMEs never link to a file that is not versioned (for example
  `.vscode/`). In READMEs only fix the stale numbers.
- Fix every doc line that states an old version. Verify with an `rg` of the old
  values that returns nothing.
- Never edit the user's global config (`~/.claude`). If the rule is missing there,
  only mention it.

## Step 9 — Final report

Show it in the chat. If `--progress <file>` was given, or the project already keeps a
progress file the user points to, also append it to the end of that file after a `---`
separator. Never overwrite previous reports.

```
Version update — OK | BLOCKED

Done: 2-5 lines.

| Component | Previous | New | Source | Type |
|---|---|---|---|---|

Files: one line per modified file.
Checks: each exact command with its decisive output line.
Deviations and exceptions: each version below the latest and why.
Pending / manual: dump and restore, majors postponed, CI only proven by a push,
  BOM overrides to drop later, anything broken outside scope.
Git state: `git status --short` and `git diff --stat`.
```

Style checklist:

- Reply in the user's language; files follow the language each one already uses.
- Keep every accent and non-ASCII byte; re-read edited files that contain them.
- No mention of AI or tooling in project files, comments or docs.
- Only one-line comments, and only when the why is not obvious (an exception's reason,
  a BOM override's drop rule).
- Never commit or push.
- State plainly what was verified and what was not, for example CI that only runs on
  a push. Never claim a check you did not run.
