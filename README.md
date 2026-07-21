# claude-skills

Personal collection of skills for [Claude Code](https://claude.ai/code).

## Available skills

| Skill | Description |
|-------|-------------|
| [`/claude-docs`](./claude-docs/SKILL.md) | Creates or updates a project's `.vscode/CLAUDE.md` documentation set: maps undocumented components, audits existing docs against current code, splits deep-dives into their own files, and flags redundant/stale docs for confirmed deletion. |
| [`/commit-message`](./commit-message/SKILL.md) | Generates a conventional commit message by reading the staged diff and project history. |
| [`/custom-init`](./custom-init/SKILL.md) | Bootstraps a new project with the full productivity setup: verifies global MCPs, builds the knowledge graph, hands off to `/claude-docs` for the initial documentation set, and updates `.gitignore`. |
| [`/estimate`](./estimate/SKILL.md) | Produces a technical analysis and effort estimation document for a feature or change, including phases, impact map, and justified hours. |
| [`/readme`](./readme-generator/SKILL.md) | Generates or updates a professional README by analyzing the project's code, structure, and dependencies. Supports multiple output languages. |
| [`/user-story`](./user-story/SKILL.md) | Drafts stories, bugs, analysis tasks, or meeting notes for Jira and Asana from loose requirements, adapting format (markdown vs. plain text) and tone to the platform and task type. |

---

## What is a Claude Code skill

A skill is an instruction file that extends Claude Code with a custom command. When you invoke `/skill-name`, Claude loads the skill's instructions and executes them in the context of the current conversation.

Skills let you:
- Standardize repetitive tasks (commits, estimations, code reviews).
- Share workflows across projects and environments.
- Build a personal library of reusable commands.

---

## Skill structure

Each skill lives in its own folder inside `~/.claude/skills/` and contains a `SKILL.md` file:

```
~/.claude/skills/
└── skill-name/
    └── SKILL.md
```

For skills that cover several variants of the same task (e.g. different task types or output formats), `SKILL.md` can act as a thin orchestrator and delegate details to files in a `reference/` subfolder, read on demand instead of loaded every time:

```
~/.claude/skills/
└── skill-name/
    ├── SKILL.md
    └── reference/
        ├── variant-a.md
        └── variant-b.md
```

See [`user-story`](./user-story/SKILL.md) for a real example: it routes to a `reference/` file per task type (story, bug, meeting, analysis) and per platform (Asana, Jira).

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