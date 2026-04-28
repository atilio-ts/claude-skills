---
name: timesheet
version: 1.0.0
description: |
  Generates a timesheet report from the git changes in the current branch.
  Analyzes commits and file diffs, breaks the work into tasks of max 3 hours each,
  and outputs entries in the Clockify/timesheet format. Supports English and Spanish.
  Matches the vocabulary and tone of existing timesheet reports (action noun + subject + detail).
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Timesheet Report Generator

You are generating a timesheet report based on git changes. Follow every step in order.

---

## Step 0 — Parse arguments

The user invokes this skill with arguments. Extract:

- **Language**: `english` or `spanish` (default: `spanish` if not specified)
- **Branch**: the branch to analyze (default: current branch)
- **Project name**: the project/ticket name to use in the report (default: infer from branch name or ask)
- **Client**: the client name (default: infer from context or ask)

If the user provided a branch name other than the current one, use that branch.
If project or client cannot be inferred, use `"[Project]"` and `"[Client]"` as placeholders and note it at the end.

---

## Step 1 — Gather git data

Run the following commands to understand what changed:

```bash
# Current branch name
git branch --show-current
```

```bash
# Commits in this branch vs main/develop/master (whichever exists)
git log --oneline $(git merge-base HEAD $(git rev-parse --verify main 2>/dev/null || git rev-parse --verify develop 2>/dev/null || git rev-parse --verify master 2>/dev/null) 2>/dev/null || echo "HEAD~20")..HEAD
```

```bash
# Full diff stat to understand files changed
git diff --stat $(git merge-base HEAD $(git rev-parse --verify main 2>/dev/null || git rev-parse --verify develop 2>/dev/null || git rev-parse --verify master 2>/dev/null) 2>/dev/null || echo "HEAD~20")..HEAD
```

```bash
# Commit messages with dates
git log --pretty=format:"%ad | %s%n%b" --date=short $(git merge-base HEAD $(git rev-parse --verify main 2>/dev/null || git rev-parse --verify develop 2>/dev/null || git rev-parse --verify master 2>/dev/null) 2>/dev/null || echo "HEAD~20")..HEAD
```

If the user specified a target branch for comparison, replace `main`/`develop`/`master` with that branch.

---

## Step 2 — Analyze the changes

Based on the git data, identify the logical work units. Group related commits and file changes into cohesive tasks. Consider:

- What was created, modified, or fixed
- Which modules, services, or components were touched
- What the purpose of the changes was (feature, fix, refactor, config, test, etc.)

Think about the actual development effort involved — analysis, implementation, testing, corrections, documentation.

---

## Step 3 — Break work into timesheet tasks

**Rules:**
- Each task must be **≤ 3 hours**. Split larger efforts into multiple entries.
- Minimum task time: **15 minutes (0.25h)**
- Be realistic: a small config change = 0.5–1h, a new service/feature = 2–3h (possibly split), fixes = 0.5–2h
- Aim for tasks that reflect actual development phases: analysis, implementation, corrections, testing, deployment prep, documentation
- Total hours should be reasonable for the scope of changes observed

---

## Step 4 — Write task descriptions

### Description style (CRITICAL — match the examples exactly)

The tone is **professional and direct**. Descriptions are **noun phrases** that state the action and the subject. No articles in Spanish. No filler words. Specific enough to be meaningful, not so technical that a non-developer can't understand.

**Spanish patterns (follow these exactly):**

| Action type | Spanish pattern | Example |
|-------------|----------------|---------|
| Creating new code | `Implementacion de [what] en [where]` | `Implementacion de job de alertas en modulo RPO` |
| Updating/modifying | `Actualizacion de [what] en [where]` | `Actualizacion de configuracion de variables de entorno` |
| Analysis/research | `Analisis de [what] para [purpose]` | `Analisis de implementacion de sistema de alertas` |
| Review/verification | `Revision de [what]` | `Revision de endpoints y configuracion del workflow` |
| Fix/correction | `Correcciones en [what] para [purpose]` | `Correcciones en el builder de mensajes de alerta` |
| Testing | `Pruebas de [what]` | `Pruebas de pipeline de despliegue` |
| Documentation | `Documentacion de [what]` | `Documentacion de detalles de implementacion` |
| Configuration | `Configuracion de [what] en [where]` | `Configuracion de variables de entorno en AWS` |

**English patterns (parallel structure):**

| Action type | English pattern | Example |
|-------------|----------------|---------|
| Creating new code | `Implementation of [what] in [where]` | `Implementation of alerts job in RPO module` |
| Updating/modifying | `Update of [what] in [where]` | `Update of environment variable configuration` |
| Analysis/research | `Analysis of [what] for [purpose]` | `Analysis of alerts system implementation` |
| Review/verification | `Review of [what]` | `Review of endpoints and workflow configuration` |
| Fix/correction | `Corrections to [what] for [purpose]` | `Corrections to alert message builder` |
| Testing | `Testing of [what]` | `Testing of deployment pipeline` |
| Documentation | `Documentation of [what]` | `Documentation of implementation details` |
| Configuration | `Configuration of [what] in [where]` | `Configuration of environment variables in AWS` |

**Do NOT:**
- Use vague descriptions like "Working on feature X" or "Code changes"
- Start with "I" or use first person
- Add punctuation at the end of the description
- Use deep technical jargon (class names, method signatures, stack traces)
- Use markdown, asterisks, or formatting inside the description

**DO:**
- Name the module, service, or component (e.g., "modulo RPO", "backoffice", "workflow de pagos")
- Be specific about what changed (config, endpoint, service, job, builder, validator, etc.)
- Match the level of specificity in the examples above

---

## Step 5 — Output the report

Output a table followed by the CSV data.

### Table (human-readable)

```
| # | Descripción / Description | Tiempo (h) | Decimal |
|---|--------------------------|:----------:|:-------:|
| 1 | ...                      | 02:00:00   | 2.00    |
...
|   | **TOTAL**                | HH:MM:SS   | X.XX    |
```

### CSV (Clockify format)

```
"Proyecto","Cliente","Descripción","Tiempo (h)","Tiempo (decimal)"
"[Project]","[Client]","Description here","02:00:00","2.00"
...
```

Format rules:
- Time: `HH:MM:SS` (e.g., `01:30:00`, `02:45:00`, `00:30:00`)
- Decimal: two decimal places (e.g., `1.50`, `2.75`, `0.50`)
- Quarter-hour increments: 0.25, 0.50, 0.75, 1.00, 1.25, ... 3.00
- All values quoted in CSV

---

## Step 6 — Summary note

After the CSV, add a brief note (2–3 lines) stating:
- Total hours
- Number of tasks
- Which branch/commits were analyzed
- Any placeholders the user needs to fill in (project name, client, etc.)

Do not mention AI or tools in this note.
