---
name: personal:timesheet
version: 3.0.0
description: |
  Generates timesheet entries in the Clockify format for a day, a week, or a custom range.
  Asks the user what to base the report on: the Claude Code and omp conversations of the period,
  the git changes of the current repo, queries/support work, the entries already loaded in Clockify,
  or a combination. Breaks the work into tasks of max 3 hours each, grouped per day, with project
  and tag, completing 8 hours per workday and skipping what is already loaded.
  Supports English and Spanish. Matches the vocabulary and tone of existing Clockify reports
  (action noun + subject + detail).
trigger: /timesheet
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

**Sources:**

| Source | What it covers |
|--------|----------------|
| `conversations` | Claude Code and omp sessions of the period in the current repo: what was asked, analyzed, tested, written |
| `changes` | Commits of the period (and uncommitted changes) in the current repo |
| `queries` | Conversations that were questions, support, or analysis with no code edits (answering a colleague, investigating behavior, reading docs) |
| `clockify` | Entries already loaded in Clockify for the period: projects, tags and descriptions in use, and hours already covered |

If the user did not say which sources to use, ask with AskUserQuestion (multi-select, recommend `conversations` + `changes` + `clockify`). If the period is missing, assume today. Do not ask anything else at this step.

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

### Clockify

```bash
python3 ~/.claude/skills/timesheet/scripts/clockify.py --from <start> --to <end>
python3 ~/.claude/skills/timesheet/scripts/clockify.py --catalog
```

The script is read-only. It takes `token`, `workspace` and `user.id` from `~/.clockify-cli.yaml` (and `time-zone`, where `Local` means the system zone) and never prints them. Never copy the key into a command, a file or the output.

- Entries: `GET https://api.clockify.me/api/v1/workspaces/{workspace}/user/{userId}/time-entries` with header `X-Api-Key`, `hydrated=true` (project and tags by name), and `start`/`end` in ISO 8601 UTC covering the local days of the period. Pages of `page-size=200`, incrementing `page` until a page comes back with fewer items.
- `--catalog`: active projects (`/projects?archived=false`) and tags (`/tags?archived=false`), to pick names when the period has no entries yet.
- Output per day: time window, hours, project, tags in brackets, billable, description, and the day total. A running timer shows as `running`.

Only query the period the user asked for. Use the entries to:
- Reuse the project and tag names they already carry.
- Skip work already loaded: same day and same description after normalizing case, accents and spacing (`Revision de logs en QA` matches `Revisión de logs en QA`). A fixed meeting counts as loaded when any entry that day contains its key words (`daily` + `integraciones`, `daily` + `comercios`).
- Count their hours toward the day's total.

---

## Step 2 — Build the tasks

Identify logical work units per day, merging what the sources say about the same work (a session and its commits are one task, not two).

**Rules:**
- Each task must be **≤ 3 hours**. Split larger efforts into several entries with different subjects (analysis, implementation, testing, corrections).
- Minimum task time: **15 minutes (0.25h)**, in quarter-hour increments.
- Derive hours from evidence: the active time of the session is the floor, then add the work that happened outside the conversation and is visible in the evidence (reading, running tests, meetings mentioned).
- Do not report the same work twice across days or sources, and do not repeat what Clockify already has.

**Fixed meetings** (add them unless Clockify already has them that day or the user says they did not happen):

| Meeting | Days | Hours |
|---------|------|-------|
| `Reunión: Daily de Integraciones` (10:30–10:45) | Monday to Friday | 0.25 |
| `Reunión: Daily de Comercios` | Monday, Wednesday, Friday | 0.25 |

When the daily of Integraciones also covered code review, write `Reunión: Daily de Integraciones y code review` with 0.50h. Other meetings (planning, retrospective, internal sync) only go in when the evidence or the user mentions them.

**Daily total — 8 hours per workday (Monday to Friday):**
1. Add the hours already in Clockify, the fixed meetings and the evidence-based tasks.
2. Spread what is missing up to 8h across that day's evidence-based tasks, in quarter hours, keeping each one ≤ 3h. When the cap is reached, add another entry for the same work with a different subject (testing, corrections, review).
3. A day already at 8h or more in Clockify gets no new entries, fixed meetings included.
4. A workday with no evidence besides the fixed meetings: do not invent tasks; ask the user what was done.
5. Weekends only get entries with evidence, and are not completed to 8h.

**Project and tag:**
- Client work goes to the client project (billable), always with the workstream tag that fits: the ticket's tag when the branch or commit names a ticket, the meetings tag for meetings, the production-support tag for support work.
- Internal company work (internal sync, internal presentations, company tooling, vacations) goes to the internal non-billable project, without tag.
- Entries never use a Clockify task.
- Take the names from the period's Clockify entries. If the period has none, use `--catalog` and ask the user which project and tags apply. If no tag clearly fits a task, write `?` and flag it in the summary note.

---

## Step 3 — Write task descriptions

### Description style (CRITICAL — match the examples exactly)

The tone is **professional and direct**. Descriptions are **noun phrases** that state the action and the subject. No articles in Spanish. No filler words. Specific enough to be meaningful, not so technical that a non-developer can't understand.

**Spanish patterns (follow these exactly):**

| Action type | Spanish pattern | Example |
|-------------|----------------|---------|
| Creating new code | `Implementación de [what] en [where]` | `Implementación de job de alertas en módulo de pagos` |
| Updating/modifying | `Actualización de [what] en [where]` | `Actualización de configuración de variables de entorno` |
| Analysis/research | `Análisis de [what] para [purpose]` | `Análisis de implementación de sistema de alertas` |
| Review/verification | `Revisión de [what]` | `Revisión de endpoints y configuración del workflow` |
| Fix/correction | `Correcciones en [what] para [purpose]` | `Correcciones en el builder de mensajes de alerta` |
| Testing | `Pruebas de [what]` | `Pruebas en ambiente QA de endpoints de la API` |
| Documentation | `Documentación de [what]` | `Documentación de detalles de implementación` |
| Configuration | `Configuración de [what] en [where]` | `Configuración de variables de entorno en AWS` |
| Combined actions | `[Acción] y [acción] de [what]` | `Revisión y pruebas de funciones implementadas en API de pagos` |
| Meetings | `Reunión: [topic]` | `Reunión: Planning Integraciones` |
| Queries/support | `Revisión de [what] para [purpose]` | `Revisión de archivos de liquidación duplicados en producción para responder consulta del equipo` |

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
| Combined actions | `[Action] and [action] of [what]` | `Review and testing of functions implemented in payments API` |
| Meetings | `Meeting: [topic]` | `Meeting: Integration planning` |
| Queries/support | `Review of [what] for [purpose]` | `Review of duplicated settlement files in production to answer team query` |

**Do NOT:**
- Use vague descriptions like "Working on feature X" or "Code changes"
- Start with "I" or use first person
- Add punctuation at the end of the description
- Use deep technical jargon (class names, method signatures, stack traces)
- Use markdown, asterisks, or formatting inside the description
- Copy prompts literally or mention conversations, sessions, or tools
- Put ticket ids in the description (the ticket goes in the tag)

**DO:**
- Start with a capital letter and keep it to one line (about 15 words or fewer)
- Name the module, service, or component (e.g., "módulo de pagos", "panel de administración", "servicio de notificaciones")
- Name the environment when testing (QA, HML, DEV, local, producción)
- Be specific about what changed or was verified
- Use the fixed descriptions for recurring work: `Actualización y seguimiento de tareas`, `Redacción y envío de reporte semanal`

---

## Step 4 — Output the report

One block per day, in chronological order. Each block has a table and the CSV rows. Entries already in Clockify are not repeated. For a multi-day period, finish with a weekly total.

### Table

```
### YYYY-MM-DD (weekday)

| # | Proyecto / Project | Tag | Descripción / Description | Hora (h) | Decimal |
|---|--------------------|-----|---------------------------|:--------:|:-------:|
| 1 | ...                | ... | ...                       | 02:00:00 | 2.00    |
|   |                    |     | **TOTAL**                 | HH:MM:SS | X.XX    |
```

### CSV

```
"Proyecto","Tag","Descripción","Hora (h)","Hora (decimal)"
"Project name","Tag name","Description here","02:00:00","2.00"
```

Format rules:
- Time: `HH:MM:SS` (e.g., `01:30:00`)
- Decimal: two decimal places (e.g., `1.50`)
- All values quoted in CSV; empty tag as `""`
- Keep accents in the descriptions (UTF-8) when writing in Spanish
- The day's `TOTAL` covers only the new entries; the summary note gives the total with what was already loaded

---

## Step 5 — Summary note

After the last block, add 2–4 lines stating:
- Total hours and number of tasks, per day for multi-day periods, plus the hours already loaded in Clockify
- Sources and period used
- Hours added to reach 8h per day and the tasks that received them, so the user can adjust
- Days with little evidence, sessions that were skipped, and tasks with tag `?`

Hours are an estimate from activity; the user adjusts before logging them. Do not mention AI or tools in the note.
