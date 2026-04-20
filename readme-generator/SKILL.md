---
name: readme-generator
description: Generate or update a professional README for the current project by analyzing its code, structure, and dependencies. Supports multiple languages and adapts to the project type.
trigger: /readme
args:
  - name: lang
    description: Output language for the README (e.g. "en", "es", "pt"). Defaults to English.
    required: false
  - name: update
    description: Pass --update to update an existing README instead of generating from scratch.
    required: false
---

# /readme — README Generator

Analyze the current project and generate (or update) a professional README that is accurate, developer-friendly, and easy to follow.

## Usage

```
/readme                        # Generate README in English
/readme --lang es              # Generate README in Spanish
/readme --lang pt              # Generate README in Portuguese
/readme --update               # Update an existing README
/readme --update --lang es     # Update existing README in Spanish
```

The user may also provide context about the project inline:

```
/readme This is a REST API for managing inventory, built with NestJS and PostgreSQL
/readme --lang es CLI tool for encrypting files using AES-256
```

---

## What This Skill Does

1. Discovers the project type, tech stack, and structure
2. Reads key files to extract real facts (no invented content)
3. Produces a README that answers: *What is it? How do I install it? How do I use it? Who made it?*
4. Mirrors the tone and depth appropriate for the project size and audience

---

## Execution Steps

### Step 1 — Orient yourself

Run these checks before reading any file:

```
1. Check for .code-review-graph/ → use code-review-graph tools if present
2. Check for an existing README.md → read it if --update flag was given
3. Detect the output language:
   - Use --lang argument if provided
   - Otherwise default to English
```

### Step 2 — Discover the project

Use the tools available to you to answer these questions from the actual code. **Never invent facts.**

| Question | Where to look |
|---|---|
| What does this project do? | README (if exists), package.json/build.gradle/pyproject.toml description field, main entry point |
| What language/framework? | File extensions, package manifest, imports in entry files |
| How do you install it? | package.json scripts, Makefile, Dockerfile, README |
| How do you run it? | `scripts.start/dev`, `main` field, shell scripts, docker-compose |
| How do you test it? | `scripts.test`, test directories, CI config |
| What are the key features? | Public API/routes, exported classes, core modules |
| What is the project structure? | Top-level directories and their purpose |
| Is there a license? | LICENSE file, package.json `license` field |
| Are there environment variables? | `.env.example`, `docker-compose.yml`, config files |

**If `.code-review-graph/` exists**, use these tools instead of Glob/Grep for navigation:
- `mcp__code-review-graph__get_hub_nodes_tool` → identify the most connected/important modules
- `mcp__code-review-graph__query_graph_tool` → find entry points, controllers, routes
- `mcp__code-review-graph__get_community_tool` → understand module clusters

### Step 3 — Determine which sections to include

Include a section **only if** you found real content for it in the code. Do not add placeholder sections.

| Section | Include when |
|---|---|
| Badges | CI config, package.json with version, license detected |
| Highlights | Project has 3+ distinct features worth calling out |
| Overview / About | Always include — the elevator pitch |
| Table of Contents | README is expected to be long (>5 sections) |
| Architecture | Project has layers, modules, or a non-trivial structure |
| Prerequisites | Project requires specific runtimes, tools, or services |
| Quick Start | There's a one-liner or simple setup path |
| Installation | Always include |
| Configuration | .env.example exists or config files found |
| Usage | Always include — show the most common code/command |
| API Reference | REST API or public library with clear public surface |
| Project Structure | Monorepo or non-obvious folder layout |
| Testing | Test scripts exist |
| Docker | Dockerfile or docker-compose.yml found |
| Contributing | Open-source project or CONTRIBUTING.md exists |
| License | LICENSE file found |

### Step 4 — Write the README

**Tone and style principles** (learned from the example READMEs):

- **Lead with the value**, not the implementation. First sentence answers "what does this do for me?"
- **Friendly and approachable** — write for a capable developer who has never seen this project
- **Concise** — no manifestos. One paragraph per section is usually enough
- **Show, don't tell** — include real code snippets, not just descriptions
- **Use code blocks with syntax highlighting** for all commands and code examples
- **Section headers are navigational** — make them clear and scannable
- **Badges go at the top** — CI status, version, license
- **Quick Start should be truly quick** — ideally 2–4 commands to a running app
- **Don't document the entire API in the README** — link to docs instead

**Language-specific notes:**
- English (`en`): Use active voice, imperative mood for instructions ("Run the server", "Install dependencies")
- Spanish (`es`): Use formal "usted" form for instructions. Section headers in Spanish. ("Ejecute el servidor", "Instale las dependencias")
- Portuguese (`pt`): Use formal form for instructions. ("Execute o servidor", "Instale as dependências")

### Step 5 — Output

Write the README to `README.md` in the project root.

If `--update` was passed:
- Read the existing README first
- Preserve sections that contain information you cannot derive from code (e.g. author bio, credits, custom notices)
- Update or add sections based on what you found in Step 2
- Remove sections that are no longer accurate

---

## README Template

Use this as a structural guide, not a rigid template. Adapt it to what the project actually needs.

```markdown
# Project Name

> One-sentence description of what this does and who it's for.

[badges here if applicable]

## Highlights

- Key selling point one
- Key selling point two  
- Key selling point three

## Overview

Two or three sentences explaining what the project does, how it works, and who would use it. Optionally compare to similar tools or explain where it fits in a broader ecosystem.

## Prerequisites

- Runtime / language version (e.g. Node.js 20+, Python 3.11+, Java 21)
- Required external services (e.g. PostgreSQL, Redis)
- Required tools (e.g. Docker, Make)

## Quick Start

```bash
# Clone and run in < 5 commands
git clone <repo-url>
cd <project>
cp .env.example .env
npm install && npm run dev
```

## Installation

Step-by-step instructions. Include platform differences if relevant (macOS/Linux/Windows).

## Configuration

List environment variables with descriptions. Reference `.env.example` if it exists.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | PostgreSQL connection string |

## Usage

Show the most common use case with real code. Screenshots or GIFs are highly effective here.

```language
// minimal working example
```

## API Reference (if applicable)

Brief overview of the public API. Link to full docs if they exist.

## Project Structure (if non-obvious)

```
src/
├── feature-a/    # What this does
├── feature-b/    # What this does
└── shared/       # Shared utilities
```

## Testing

```bash
npm test
npm run test:coverage
```

## Docker (if applicable)

```bash
docker compose up
```

## Contributing

How to contribute. Link to CONTRIBUTING.md if it exists.

## License

[License name](./LICENSE)
```

---

## Quality Checklist

Before writing the file, verify:

- [ ] Every command in the README was found in the actual project (scripts, Makefiles, Dockerfiles)
- [ ] Version numbers and port numbers come from config files, not guesses
- [ ] Environment variable names come from `.env.example` or source code
- [ ] The Quick Start actually gets someone to a running app
- [ ] No section contains placeholder text like "coming soon" or "TODO"
- [ ] Code blocks have syntax highlighting (` ```bash `, ` ```typescript `, etc.)
- [ ] The tone is consistent throughout (don't mix formal and informal)

---

## Examples of Good READMEs

When in doubt, model the output after these patterns:

- **Brief + impactful**: python-magic style — two paragraphs, straight to usage
- **Feature-rich library**: pooch style — About block with bullet features, code examples for different audiences
- **Enterprise/internal tool**: base-project-readme style — Table of Contents, architecture section, full command reference
- **Open-source tool**: flower style — badges, features list, quick installation one-liner
