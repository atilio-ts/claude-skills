---
name: personal:new-skill
version: 1.0.0
description: |
  Creates a new Claude Code skill in this repo, or updates an existing one, following
  the conventions actually used across the current skill set (frontmatter shape, body
  structure, when to split into reference/ files vs. stay single-file, README upkeep,
  local install). Never assumes what the skill should do — asks the user when the
  requirements, scope, or a structural decision isn't clear from what they provided.
trigger: /new-skill
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /new-skill

Author a new skill for this repo, or update an existing one, matching how the skills
that are actually here are built — not a generic template. Every rule below was verified
against the current skill set at the time this was written; if the skill set changes in
ways that contradict this file, trust the actual skills over this document and flag the
mismatch to the user.

## Usage

```
/new-skill                          # create a new skill — will ask what it should do
/new-skill --update <skill-name>    # update an existing skill's behavior/version
```

---

## Step 1 — Gather requirements (never assume)

Restate, in your own words, what the skill should do and when it should be invoked. Then
check you actually have enough to proceed:

- What triggers it — a slash command with no arguments, one with flags, or is it meant to
  activate automatically when Claude judges it relevant (via the `description` field)?
- What does it produce — text in the conversation, a written file, edits to existing
  files, or a mix?
- Does it need to branch on something (a task type, a platform, a project type, a mode
  like create-vs-update)? If so, what are the branches, concretely?
- Are there existing examples of the desired output the user can point to (past
  commits, sample documents, a reference skill to model after)?

**If any of this is unclear or the user's request is a one-liner with real ambiguity in
it, ask before writing anything.** A skill built on a guessed requirement will be wrong
in a way that's expensive to notice later, since it only surfaces when someone actually
invokes it. Ask up to three concrete questions at a time, don't stall on one at a time
unnecessarily either.

If updating an existing skill (`--update`), read its current `SKILL.md` (and `reference/`
files if it has any) in full first — restate what it currently does before proposing what
changes, so you're editing with the actual current behavior in mind, not a guess from the
name.

---

## Step 2 — Name, trigger, and folder

- Folder name and `name:` frontmatter value: short, action-oriented, kebab-case (e.g.
  `custom-init`, `readme-generator`, `commit-message`). The `name:` field is always
  prefixed `personal:` (e.g. `personal:new-skill`).
- **Always declare `trigger: /command-name` explicitly**, even when it's identical to the
  folder name. Only make it differ from the folder name when there's a real reason to
  (e.g. `readme-generator` folder, `/readme` trigger — shorter and more natural to type).
- Before finalizing the name, check it doesn't collide with an existing skill in this
  repo or a commonly-used plugin/built-in command — a near-miss name (e.g. this skill
  deliberately avoided `create-skill`/`skill-create` because a different, pre-existing
  `/skill-create` command already does something unrelated) causes real confusion about
  which command does what.

---

## Step 3 — Frontmatter

```yaml
---
name: personal:skill-name
version: 1.0.0
description: |
  What this skill does, and when Claude should consider using it. This is the text
  Claude uses to decide whether to activate the skill automatically — be specific about
  the trigger conditions, not just the output.
trigger: /skill-name
allowed-tools:
  - Read
  - ...
---
```

- **`version:` is mandatory**, every skill has one. Start at `1.0.0`. Bump it whenever the
  skill's behavior changes (see Step 7) — this is how a skill's evolution is tracked,
  there's no changelog file per skill.
- **`description:`** should describe both what the skill produces and when it applies —
  not just a title restated. This field is read by Claude to decide on automatic
  invocation, so vague descriptions cause both false triggers and missed ones.
- **`allowed-tools:`** list only what the skill actually uses. Common sets seen across
  the existing skills: read-only analysis (`Read, Glob, Grep, Bash`), analysis that also
  writes output (`Read, Glob, Grep, Bash, Write`), or full edit capability (`Read, Write,
  Edit, Glob, Grep, Bash`). Don't default to the full set out of caution — a skill that
  should only ever list findings (like `review`) explicitly restricts itself to read-only
  tools so it structurally cannot make unrequested edits.
- **Flags/arguments — prefer free-text parsing in the body over a formal `args:` schema.**
  Describe accepted flags in a "Usage" section and parse them from the user's invocation
  text as the first step of the body (see `custom-init`'s or `timesheet`'s Step 1 for the
  pattern). A formal `args:` array exists elsewhere in this repo but is not the default —
  only use it if there's a specific reason free-text parsing won't do (e.g. the harness
  you're targeting requires a declared schema).

---

## Step 4 — Decide: single file, or `SKILL.md` + `reference/`?

Both are valid and both are used in this repo — this is a judgment call, not a rule with
one right answer. Evidence from the actual skill set:

- **Single-file** (`commit-message`, `review`, `timesheet`, `readme-generator`, and
  notably `estimate` — which has three full estimation methods (A/B/C) as inline
  sections, not separate files): the right choice when the skill is fundamentally one
  flow, even if that flow has an internal decision point. Method/branch content lives as
  a `## Method A` / `## Method B` section right where the decision is made, in the same
  file.
- **`SKILL.md` + `reference/`** (`user-story`, `custom-init`, `claude-docs`): the right
  choice when the skill has more than one genuinely independent axis of variation where
  only a subset of the content applies per invocation (task type × platform in
  `user-story`; distinct unrelated concerns like MCP checks vs. ignore-file patterns in
  `custom-init`), and where each branch's content is substantial enough that always
  loading all of it would be wasteful. `SKILL.md` becomes a thin orchestrator: it
  determines which branch applies and explicitly says "read `reference/x.md` now" —
  the reference files are only read when that branch is actually taken.

Ask yourself: **would I ever write the instruction "read reference/X.md" mid-flow, or
does the branch content read naturally as the next section in the same file?** If the
former, split. If the content is short, tightly coupled to the same overall output
format, or there's really just one flow with a decision table (like `estimate`'s method
selection), keep it in one file. Don't split preemptively "for consistency" — extra
files add navigation overhead that only pays for itself when the content they hold is
substantial and genuinely conditional.

If you do split, put the routing logic and the parts that always apply (final output
format, style rules that apply regardless of branch) in `SKILL.md`; put only the
branch-specific content in `reference/`.

---

## Step 5 — Write the body

Structure seen consistently across every skill in this repo, regardless of single-file
or split:

- **Title** (`# /skill-name` or a descriptive title) and one or two sentences stating
  the skill's job, right after the frontmatter.
- **Usage section**, if the skill takes any flags or arguments — show 2-4 concrete
  invocation examples covering the common cases.
- **Numbered `## Step N — <verb phrase>` sections**, imperative voice, in execution
  order. Each step should be independently understandable — a step should say what to
  check and what to do with the result, not just "analyze the input."
- **Concrete examples wherever a rule could be ambiguous in prose alone** — every skill
  in this repo includes at least one worked example (a sample commit message, a sample
  finding, a sample document section, a sample timesheet row). An abstract rule plus a
  concrete example prevents more misinterpretation than either alone.
- **An explicit "never invent" instruction whenever the skill produces factual claims**
  about a codebase, a diff, or provided documents (seen in `readme-generator`: "Never
  invent facts"; `estimate`: "Do not invent assumptions without declaring them";
  `claude-docs`: verification-rigor). If the skill can plausibly need a fact it can't
  verify, tell it explicitly what to do instead (ask, flag as `[PENDING]`, state the
  assumption out loud) rather than leaving that case unhandled.
- **A precise final-output section** — describe exactly what the deliverable looks like
  (a fenced code block to copy, a file written to a specific path, a table plus a
  confirmation prompt). Don't leave "then show the result" implicit; every existing
  skill spells out the literal output shape.
- **Style/tone rules belong near the output section, not scattered** — if the skill's
  output has house style (line-length limits, banned filler phrases, formatting rules,
  a "never mention AI/tools" instruction), state them together as a checklist right
  before or after the output format, the way `commit-message`, `estimate`, and
  `timesheet` each do.

---

## Step 6 — Update the repo README

`README.md`'s own "Best practices" section requires this: **add a row to the skills
table every time a new skill is created**, and update the existing row's description if
an existing skill's behavior changed enough that the one-line summary is now wrong (as
happened when `custom-init` started delegating documentation generation instead of doing
it inline). Match the existing row style — link to `./skill-name/SKILL.md`, one sentence
covering what it does, not a feature list.

---

## Step 7 — Version bump (updates only)

If this is an update to an existing skill (not a brand-new one), bump `version:` in its
frontmatter following semantic intent: patch for wording/clarity fixes that don't change
behavior, minor for new capability or restructuring (e.g. splitting into `reference/`),
major only for a breaking change to how the skill is invoked or what it produces. Look at
the target skill's own version history in `git log` for that file if you're unsure how
big a jump is proportionate — match the granularity already established for that skill
rather than guessing fresh.

---

## Step 8 — Install locally

Every skill in this repo is made available locally via a **symlink** in
`~/.claude/skills/`, not a copy — confirm this is still the case
(`ls -la ~/.claude/skills/`) before assuming it. For a new skill:

```bash
ln -s /absolute/path/to/this/repo/skill-name ~/.claude/skills/skill-name
```

This makes the skill available immediately in the current session — no restart needed,
since the symlink resolves live and the skill list is re-read on invocation. If a skill
is being updated in place, no re-linking is needed at all, since the symlink already
points at the same files.

---

## Step 9 — Final check before declaring done

- Did you ask the user about anything you were tempted to guess in Steps 1–4? If you
  guessed instead, go back and ask now, before the skill ships with a wrong assumption
  baked in.
- Does the frontmatter have `name`, `version`, `description`, `trigger`, and
  `allowed-tools` — all five, none skipped out of laziness?
- Did you avoid copying an example verbatim from a different skill's domain? (Every
  worked example in the new skill should be specific to what this skill actually does.)
- Is the README updated?
- Is it symlinked into `~/.claude/skills/`?

Report what you created/changed concisely — the file paths, the trigger, and the one
thing a future user most needs to know to invoke it correctly. Don't narrate the
process you followed to get there unless asked.