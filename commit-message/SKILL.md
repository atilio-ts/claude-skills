---
name: commit-message
version: 1.0.0
description: |
  Generate a conventional commit message for staged or unstaged changes.
  Reads git log and diff to produce a message that matches the project's
  style and the commit guidelines.
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
If no files are staged (`git diff --cached --stat` is empty), check for unstaged changes with `git diff --stat`.
If both are empty, tell the user there are no changes to commit and stop.

## Step 2 — Read the full diff

```bash
git diff --staged
```

If `git diff --staged` is empty, use `git diff` instead.

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
`fix(rpo): ...`, `feature(nexito): ...`

### Breaking changes

Append `!` and add a `BREAKING CHANGE:` footer.

### Body rules

- Use bullet points starting with `-`
- Each bullet is a self-contained line ≤ 80 characters
- No wrapped continuations — split long ideas into separate bullets
- Omit body if the first line is self-explanatory

### NEVER include

- "Co-Authored-By" or any AI attribution
- References to AI tools
- The same idea or phrase more than once — consolidate duplicates into one bullet

## Step 4 — Output the message

Output only the commit message, formatted in a code block.
Do not explain the message unless the user asks.

If the diff spans multiple logical changes, suggest splitting into
separate commits and propose one message per logical group.