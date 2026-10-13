---
name: personal:timesheet
version: 2.0.0
description: |
  Generates timesheet entries in the Clockify format for a day, a week, or a custom range.
  Asks the user what to base the report on: the Claude Code and omp conversations of the period,
  the git changes of the current repo, queries/support work, or a combination.
  Breaks the work into tasks of max 3 hours each, grouped per day.
  Supports English and Spanish. Matches the vocabulary and tone of existing Clockify reports
  (action noun + subject + detail).
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - AskUserQuestion
---

# Timesheet Report Generator

You are generating timesheet entries for the hours the user can log in their time tracking system. Follow every step in order.

---

## Step 0 — Parse arguments and ask what is missing

Extract from the invocation whatever the user already said:

- **Period**: `today` (default), `yesterday`, `week` (Monday to today), or an explicit date/range
- **Sources**: where the hours come from (see below)
- **Language**: `english` or `spanish` (default: `spanish`)

Project and client are not part of the report: only the description and the hours matter.

**Sources:**

| Source | What it covers |
|--------|----------------|
| `conversations` | Claude Code and omp sessions of the period in the current repo: what was asked, analyzed, tested, written |
| `changes` | Commits of the period (and uncommitted changes) in the current repo |
| `queries` | Conversations that were questions, support, or analysis with no code edits (answering a colleague, investigating behavior, reading docs) |

If the user did not say which sources to use, ask with AskUserQuestion (multi-select, recommend `conversations` + `changes`). If the period is missing, assume today. Do not ask anything else.

By default only sessions from the current repo count. If the user asks for all repos, pass `--all` to the script.

---

## Step 1 — Gather evidence

Resolve the dates first (`YYYY-MM-DD`, local time). Then run what the chosen sources need.

### Conversations and queries

```bash
python3 ~/.claude/skills/timesheet/scripts/sessions.py --from <start> --to <end>
```

The script reads both Claude Code (`cc`) and omp (`omp`) sessions and prints, per day and session: tool, time window, active minutes (gaps over 10 minutes are not counted), prompt count, number of file edits, branch (Claude Code only), session title, and the first prompts. Use `--all` for every repo, `--cwd <path>` for another one, `--prompts <n>` to see more prompts.

- Sessions with edits are implementation, fixes, or documentation work.
- Sessions with `edits=0` are analysis, review, testing, meetings prep, or queries.
- A session that spans several topics becomes several tasks.
- Prompts that are pasted logs or SQL output show the user was testing, not writing code: classify as testing.
- Ignore sessions whose only purpose was to run this skill.
- The same work can show up in a `cc` and an `omp` session; count it once.

### Changes

```bash
git log --all --since="<start> 00:00" --until="<end> 23:59:59" --author="$(git config user.email)" --pretty=format:"%ad | %h | %s" --date=short
git log --all --since="<start> 00:00" --until="<end> 23:59:59" --author="$(git config user.email)" --stat --pretty=format:"%n%ad %s" --date=short
git status --short
git diff --stat
```

Group by commit date. Uncommitted changes count toward today.

---

## Step 2 — Build the tasks

Identify logical work units per day, merging what the sources say about the same work (a session and its commits are one task, not two).

**Rules:**
- Each task must be **≤ 3 hours**. Split larger efforts into several entries with different subjects (analysis, implementation, testing, corrections).
- Minimum task time: **15 minutes (0.25h)**, in quarter-hour increments.
- Derive hours from evidence: the active time of the session is the floor, then add the work that happened outside the conversation and is visible in the evidence (reading, running tests, meetings mentioned). Never inflate to reach a full workday.
- A day's total must be explainable by its evidence. If a day has little evidence, report few hours.
- Do not report the same work twice across days or sources.

---

## Step 3 — Write task descriptions

### Description style (CRITICAL — match the examples exactly)

The tone is **professional and direct**. Descriptions are **noun phrases** that state the action and the subject. No articles in Spanish. No filler words. Specific enough to be meaningful, not so technical that a non-developer can't understand.

**Spanish patterns (follow these exactly):**

| Action type | Spanish pattern | Example |
|-------------|----------------|---------|
| Creating new code | `Implementacion de [what] en [where]` | `Implementacion de job de alertas en modulo de pagos` |
| Updating/modifying | `Actualizacion de [what] en [where]` | `Actualizacion de configuracion de variables de entorno` |
| Analysis/research | `Analisis de [what] para [purpose]` | `Analisis de implementacion de sistema de alertas` |
| Review/verification | `Revision de [what]` | `Revision de endpoints y configuracion del workflow` |
| Fix/correction | `Correcciones en [what] para [purpose]` | `Correcciones en el builder de mensajes de alerta` |
| Testing | `Pruebas de [what]` | `Pruebas en ambiente QA de endpoints de la API` |
| Documentation | `Documentacion de [what]` | `Documentacion de detalles de implementacion` |
| Configuration | `Configuracion de [what] en [where]` | `Configuracion de variables de entorno en AWS` |
| Meetings | `Reunion: [topic]` | `Reunion: Planning Integracion` |
| Queries/support | `Analisis de [what] para responder consulta de [who/what]` | `Analisis de control de duplicados en archivos de liquidacion para responder consulta del equipo` |

**English patterns (parallel structure):**

| Action type | English pattern | Example |
|-------------|----------------|---------|
| Creating new code | `Implementation of [what] in [where]` | `Implementation of alerts job in payments module` |
| Updating/modifying | `Update of [what] in [where]` | `Update of environment variable configuration` |
| Analysis/research | `Analysis of [what] for [purpose]` | `Analysis of alerts system implementation` |
| Review/verification | `Review of [what]` | `Review of endpoints and workflow configuration` |
| Fix/correction | `Corrections to [what] for [purpose]` | `Corrections to alert message builder` |
| Testing | `Testing of [what]` | `QA environment testing of API endpoints` |
| Documentation | `Documentation of [what]` | `Documentation of implementation details` |
| Configuration | `Configuration of [what] in [where]` | `Configuration of environment variables in AWS` |
| Meetings | `Meeting: [topic]` | `Meeting: Integration planning` |
| Queries/support | `Analysis of [what] to answer [who/what] query` | `Analysis of duplicate control in settlement files to answer team query` |

**Do NOT:**
- Use vague descriptions like "Working on feature X" or "Code changes"
- Start with "I" or use first person
- Add punctuation at the end of the description
- Use deep technical jargon (class names, method signatures, stack traces)
- Use markdown, asterisks, or formatting inside the description
- Copy prompts literally or mention conversations, sessions, or tools

**DO:**
- Name the module, service, or component (e.g., "modulo de pagos", "backoffice", "pagos recurrentes")
- Name the environment when testing (QA, homologacion, local)
- Be specific about what changed or was verified

---

## Step 4 — Output the report

One block per day, in chronological order. Each block has a table and the CSV rows. For a multi-day period, finish with a weekly total.

### Table

```
### YYYY-MM-DD (weekday)

| # | Descripción / Description | Hora (h) | Decimal |
|---|---------------------------|:--------:|:-------:|
| 1 | ...                       | 02:00:00 | 2.00    |
|   | **TOTAL**                 | HH:MM:SS | X.XX    |
```

### CSV

```
"Descripción","Hora (h)","Hora (decimal)"
"Description here","02:00:00","2.00"
```

Format rules:
- Time: `HH:MM:SS` (e.g., `01:30:00`)
- Decimal: two decimal places (e.g., `1.50`)
- All values quoted in CSV
- Keep accents in the descriptions (UTF-8) when writing in Spanish

---

## Step 5 — Summary note

After the last block, add 2–3 lines stating:
- Total hours and number of tasks, per day for multi-day periods
- Sources and period used
- Days with little evidence or sessions that were skipped, so the user can adjust the hours

Hours are an estimate from activity; the user adjusts before logging them. Do not mention AI or tools in the note.
