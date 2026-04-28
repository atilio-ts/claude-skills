---
name: review
version: 1.0.0
description: |
  Produce a numbered code review findings list WITHOUT applying any fixes.
  Lists issues by category, then waits for the user to confirm which items
  to fix in a follow-up prompt.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Code Review — List Only

You are performing a code review. Your job is to **list findings only**.
You MUST NOT edit, write, or modify any source file during this skill.

---

## Step 1 — Determine the review scope

If the user provided specific files or a diff, review those.
Otherwise, run:

```bash
git diff main...HEAD --name-only
```

If on a feature branch with no base specified, review all changed files
against `main`. If the repo has no `main`, use `develop`.

---

## Step 2 — Gather context

For each file in scope:
- Read its content
- Check its callers/dependencies if relevant (use Grep to trace usages)
- Note the language, framework, and conventions already in the file

---

## Step 3 — Analyze for issues

Examine each file against these categories:

| # | Category | What to look for |
|---|----------|-----------------|
| B | **Bugs** | Logic errors, null dereferences, off-by-one, race conditions |
| S | **Security** | Injection, hardcoded secrets, missing auth, unsafe deserialization |
| P | **Performance** | N+1 queries, unbounded loops, unnecessary allocations |
| D | **Design** | SOLID violations, excessive coupling, poor separation of concerns |
| E | **Error handling** | Swallowed exceptions, missing validations, unclear error messages |
| T | **Tests** | Missing coverage for changed logic, brittle assertions |
| C | **Code style** | Naming, dead code, commented-out code, inconsistency with file conventions |

Only report findings that are real issues — do not invent problems or flag
stylistic preferences the existing codebase already accepts.

---

## Step 4 — Write the findings list

Output a numbered markdown list. Each finding must follow this format:

```
**[N] [Category] — [File:line]**
[One-sentence description of the issue]
> [Why it matters or what could go wrong]
```

Group findings by severity: **Critical → High → Medium → Low**.

If there are no findings in a severity tier, omit that tier.

Example:

---

### Critical

**[1] Bug — CheckStageDelayAlertJob.java:42**
`alertThresholdMinutes` is read before null-check, throwing NPE when config is absent.
> Will crash the scheduler job silently with no retry.

### High

**[2] Security — AlertMessageBuilder.java:88**
Topic ARN is constructed via string concatenation with an unvalidated input field.
> An attacker controlling that field could redirect SNS messages to an arbitrary topic.

### Medium

**[3] Error handling — CheckStageDelayAlertJob.java:105**
`catch (Exception e)` swallows all failures without logging the stack trace.
> Makes debugging alert delivery failures impossible in production.

---

## Step 5 — End with the confirmation prompt

After the findings list, always close with:

---

> Review complete. Which findings do you want me to fix? Reference by number
> (e.g. "fix 1, 3, 5") or say "fix all". I will not touch any file until
> you confirm.