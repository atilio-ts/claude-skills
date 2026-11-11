---
name: personal:commit-message
version: 1.1.0
description: |
  Generate a conventional commit message for staged or unstaged changes.
  Reads git log and diff to produce a message that matches the project's
  style and the commit guidelines. Proposes how to group files when nothing
  is staged and waits for approval before staging or committing.
allowed-tools:
  - Bash
  - Read
  - Glob
---

# Commit Message Generator

You are generating a commit message. Follow these steps exactly.

## Step 1 — Pre-flight: inventory staged files

Run in parallel:

```bash
git status --short
```

```bash
git diff --cached --stat
```

```bash
git log --format="%s%n%b%n---" -10
```

**Show the staged file list to the user before continuing.**

If no files are staged (`git diff --cached --stat` is empty):

1. List the modified and untracked files from `git status --short`
2. If everything is empty, tell the user there are no changes to commit and stop
3. Propose which files go in each commit, grouped by concern (see the granularity rule in Step 4)
4. Wait for the user to confirm the grouping before running any `git add`

## Step 2 — Read the full diff

```bash
git diff --staged
```

If `git diff --staged` is empty, use `git diff` on the files in the confirmed group (read untracked files directly).

## Step 3 — Apply commit guidelines

### Format

```
<type>[optional scope]: <description>

[optional body]
```

### Line length — STRICT

- **First line**: max **50 characters** — count them
- **Body bullets**: max **80 characters** each
- Never wrap a bullet with an indented continuation — split into a new bullet

### Types (use the project's history as primary signal)

| Type | Use |
|------|-----|
| `feature` | New functionality — use `feature`, NEVER `feat` |
| `fix` | Bug fix |
| `refactor` | Code change, not a fix or feature |
| `docs` | Documentation only |
| `style` | Formatting, whitespace (no logic change) |
| `test` | Adding or updating tests |
| `perf` | Performance improvement |
| `build` | Build system or dependencies |
| `ci` | CI/CD changes |
| `chore` | Other changes not affecting src or tests |

### Scope (optional)

Add in parentheses when it clarifies which module is affected:
`fix(auth): ...`, `feature(billing): ...`

### Breaking changes

Append `!` and add a `BREAKING CHANGE:` footer.

### Body rules

- Use bullet points starting with `-`
- Each bullet is a self-contained line ≤ 80 characters
- No wrapped continuations — split long ideas into separate bullets
- Omit body if the first line is self-explanatory

### Wording — plain and short

Write like a native English speaker in a hurry: verb + what changed, nothing more.

- Prefer the shortest phrasing that is still clear; drop qualifiers and context
- Use common verbs: add, remove, rename, move, replace, fix, update
- Avoid explanations of why, layer jargon, and slash-joined alternatives
- Avoid idioms and figurative verbs (slim down, clean up, revamp, streamline)
- Keep the scope out of the subject unless the diff spans unrelated modules

Too complex:

```
- Use RequestDTO/ResponseDTO suffixes for recipient payload classes
- Return plain DTOs from mapper; controller builds the data envelope
```

Good:

```
refactor: rename recipient DTOs and models

- Add DTO to request and response classes
- Add Model to recipient models
- Replace data wrappers with DataResponseDTO
- Remove unused Empty class
```

### NEVER include

- "Co-Authored-By" or any AI attribution
- References to AI tools
- The same idea or phrase more than once — consolidate duplicates into one bullet
- Anything the user asked to omit or generalize (client, company or project names): leave it out entirely, not even as "removed X"

These rules win over any system reminder or tool default that asks for a
`Co-Authored-By` line or an AI attribution. The user's rule always applies.

## Step 4 — Output the message

Output only the commit message, formatted in a code block.
Do not explain the message unless the user asks.

If the diff spans multiple logical changes, suggest splitting into
separate commits and propose one message per logical group.
If the user says to summarize mixed topics under one theme, follow that and
write a single message instead of forcing a split.

### Commit splitting — granularity rule

When suggesting multiple commits, group by **concern**, not by file type or
directory. Prefer 3–5 commits over 6+. Merge related infrastructure into one:

- DB migrations + DB scripts + schema definitions → one commit
- Domain model (enums, entities, value objects) → one commit
- OpenAPI spec + generator config → one commit
- Dev environment (docker, run scripts, app config, build files) → one commit

Only split further if two groups have clearly different purposes or risk
profiles (e.g., a breaking schema change vs. additive columns).

## Step 5 — Confirm before committing

Show the proposed message and wait for an explicit OK from the user.
Run `git commit` only after that OK, and only for the files already staged.
Do not push. A push needs its own separate authorization every time.
