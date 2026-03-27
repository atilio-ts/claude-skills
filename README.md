# claude-skills

Personal collection of skills for [Claude Code](https://claude.ai/code).

## Available skills

| Skill | Description |
|-------|-------------|
| [`/commit`](./commit/SKILL.md) | Generates commit messages in Conventional Commits format by reading the diff and project history. |
| [`/estimate`](./estimate/SKILL.md) | Produces a technical analysis and effort estimation document for a feature or change, including phases, impact map, and justified hours. |

---

## What is a Claude Code skill

A skill is an instruction file that extends Claude Code with a custom command. When you invoke `/skill-name`, Claude loads the skill's instructions and executes them in the context of the current conversation.

Skills let you:
- Standardize repetitive tasks (commits, estimations, code reviews).
- Share workflows across projects and environments.
- Build a personal library of reusable commands.

---

## Skill structure

Each skill lives in its own folder inside `~/.claude/skills/` and contains a single `SKILL.md` file:

```
~/.claude/skills/
└── skill-name/
    └── SKILL.md
```

`SKILL.md` has two parts:

**1. YAML frontmatter** — skill metadata:

```yaml
---
name: skill-name
version: 1.0.0
description: |
  One or two line description that Claude uses to decide
  when to activate the skill automatically.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Write
  - Edit
---
```

**2. Markdown body** — the instructions Claude follows when running the skill. Can include numbered steps, examples, reference tables, and code blocks.

### Available tools

The `allowed-tools` field controls which tools the skill can use. The most common ones:

| Tool | What it does |
|------|--------------|
| `Bash` | Runs terminal commands |
| `Read` | Reads files from the project |
| `Write` | Creates new files |
| `Edit` | Modifies existing files |
| `Glob` | Finds files by pattern |
| `Grep` | Searches content inside files |

---

## Installation

### Install a single skill

```bash
cp -r commit ~/.claude/skills/
```

### Install all skills from this repo

```bash
for dir in */; do
  cp -r "$dir" ~/.claude/skills/
done
```

> Run from the root of the repository.

Once copied, the skill is available immediately. No need to restart Claude Code.

### Verify the installation

In any Claude Code conversation, type `/find-skills` to list all installed skills, or just start typing `/` to see the autocomplete suggestions.

---

## Usage

Type the skill name prefixed with `/`:

```
/commit
/estimate
```

You can combine it with additional context in the same message:

```
/estimate
The feature adds Google OAuth authentication to the merchant portal.
Requirements are in @docs/auth-requirements.md
```

---

## Creating a new skill

### 1. Create the folder and file

```bash
mkdir -p ~/.claude/skills/my-skill
touch ~/.claude/skills/my-skill/SKILL.md
```

### 2. Write the SKILL.md

```markdown
---
name: my-skill
version: 1.0.0
description: |
  Clear description of what this skill does and when to use it.
allowed-tools:
  - Read
  - Bash
---

# My Skill Name

Instructions for Claude. Describe step by step what it should do
when this skill is invoked.

## Step 1 — ...

## Step 2 — ...

## Expected output

Describe what the skill should produce when it finishes.
```

### 3. Back it up to this repository

```bash
cp -r ~/.claude/skills/my-skill /path/to/this/repo/
```

### Best practices

- **Be specific in each step**: the more concrete the instructions, the more consistent the results.
- **Include examples**: showing the expected output format inside the skill avoids ambiguity.
- **One skill, one responsibility**: skills focused on a single task are more reliable than multipurpose ones.
- **Version your changes**: increment the `version` field in the frontmatter whenever the skill behavior changes.
- **Update this README**: add a row to the skills table every time a new skill is created.

---

## Updating an existing skill

Edit the `SKILL.md` directly in `~/.claude/skills/skill-name/` then sync the change back to the repo:

```bash
cp ~/.claude/skills/skill-name/SKILL.md /path/to/this/repo/skill-name/SKILL.md
```

The change takes effect in the next conversation that uses the skill.

---

## Uninstalling a skill

```bash
rm -rf ~/.claude/skills/skill-name
```

The skill stops being available immediately.