---
name: personal:estimate
version: 1.2.0
description: |
  Generates a technical analysis and effort estimation document for a new
  feature or system change. From the requirements and specifications provided
  by the user, analyzes real code impact, identifies risks, and produces a
  structured hour estimate with clear implementation phases. The document is
  aimed at non-technical clients and management teams.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
---

# Estimation Document Generator

Your task is to produce a technical analysis and effort estimation document.
The document is intended for a **client or management team** that needs to
understand what the development involves, how many hours it will cost, and
what risks are involved.

---

## Step 1 — Read the input materials

Read all documents, specifications, PDFs, and code snippets the user has
attached or mentioned in their message.

If the user mentioned project file paths, read them. If they mentioned a
technical specification PDF (FSD, PRD, etc.), read it as well.

---

## Step 2 — Analyze the code impact

Use Grep and Glob to identify the project files the change actually touches.
Confirm:

- Schema, configuration, or resource files that change.
- Source code files that need to be modified.
- Existing tests that must be updated.
- Files that do **not** need changes (to explicitly bound the scope).

Do not assume impact — verify it by reading the actual code when possible.
If the user did not provide access to the source code, note it in the document.

---

## Step 3 — Choose the right estimation method

The method depends on the size and complexity of the change. Evaluate the
feature against the criteria below and apply the matching method.

---

### METHOD A — Flat decomposition (small, well-defined changes)

**When to use:** the change touches few files, the logic does not change, the
team knows the affected code well, and there are no new integrations.

**Examples:** changing a field in an XML schema and its tests, adjusting a
configuration constant, renaming or moving an existing component.

**How to apply:**

1. List all concrete tasks with their hour estimates.
   Each task must be ≤ 8 hours. If a task exceeds 8 hours, break it down.
2. Sum the base hours.
3. Apply a **20–30 %** contingency on the base total.
   Use 20 % if everything is known and well defined; 30 % if there is an
   external environment or another team dependency involved.
4. Report: base hours + hours with contingency + reason for the contingency.

**Example table:**

| Task | Estimate |
|------|:--------:|
| Update input XML schema | 1h |
| Update output XML schema | 1h |
| Update file generation test | 2h |
| Update file parsing test | 2h |
| Build and test verification | 1h |
| Update manual test files | 1h |
| Validation in staging environment | 4h |
| Cutover coordination and deploy | 2h |
| **Total** | **14h** |

> With 30 % contingency: **~18h**. The contingency covers the staging
> environment not reflecting the change before the agreed date.

---

### METHOD B — Component-by-component base and justified revision (medium features)

**When to use:** the feature introduces new components (module, table,
integration), affects files across multiple layers of the system, or requires
cross-team coordination to validate in a real environment.

**Examples:** new alerts module, new integration with an external service,
new endpoint with persistence, database migration + associated logic.

**How to apply:**

1. Break the work down into logical components or areas.
2. For each component, estimate base hours decomposed into tasks of ≤ 8h.
3. Sum the base hours for the component.
4. Revise component by component, justifying a buffer for specific risks:
   - Dependency on an external system: +10–15 % on that component.
   - Integration with complex infrastructure (e.g. poorly documented framework): +15 %.
   - Environment coordination for testing: +10 % on the validation phase.
5. Present a table with **base** and **revised** hours per phase.
6. Calculate the revised total. Do not apply additional contingency on top of
   the buffers already justified per component.
7. If the feature has optional phases, estimate them separately using the same
   technique and present them as an additional line item.

**Buffer reference by risk type:**

| Situation | Recommended buffer |
|-----------|:-----------------:|
| Integration with an unknown external system | +15 % on that component |
| Project-specific framework | +15 % |
| Infrastructure configuration dependency (email, storage) | +10 % |
| Environment coordination for E2E testing or validation | +10 % on that phase |
| Entirely new phase with no prior team experience | +20 % |

**Example revision table:**

| Phase | Base | Revised | Difference |
|-------|:----:|:-------:|:----------:|
| Phase 1 – Module implementation | 105h | 120h | +15h |
| Phase 2 – Integration component | 55h | 60h | +5h |
| Phase 3 – Validation and production deploy | 45h | 50h | +5h |
| **Total (mandatory phases)** | **205h** | **230h** | **+25h** |
| Phase 4 – Frontend visualization _(optional)_ | 70h | 80h | +10h |
| **Total with Phase 4** | **275h** | **310h** | **+35h** |

---

### METHOD C — PERT with risk multipliers (large projects or high uncertainty)

**When to use:** the project involves multiple independent components, there
are technologies new to the team, there are strict architecture requirements,
or parts of the scope are not yet fully defined.

**Examples:** full system modernization, architecture redesign, integration
with multiple external APIs in parallel.

**How to apply:**

**Step A — Risk multipliers (per component, not on the total)**

Identify which risk factors apply to each component and multiply them
together (do not add them):

| Risk factor | Multiplier |
|-------------|:----------:|
| Legacy code with insufficient documentation | ×1.3 |
| First time the team uses this technology | ×1.4 |
| Strict architecture pattern (Clean Architecture, etc.) | ×1.2 |
| Each new external system crossed | ×1.2 per dependency |
| Security or regulatory compliance requirements | ×1.2 |
| Complex or underspecified business logic | ×1.3 |
| Legacy component without tests | ×1.5 |
| First mini-project for the team (validating pattern + tooling) | ×1.15 |

Formula: `Adjusted hours = Base hours × multiplier_1 × multiplier_2 × …`

Example: 382h base × 1.2 (multiple integrations) × 1.15 (not always documented logic) = ~527h

**Step B — Three-point PERT estimate**

For each component with adjusted hours, define three scenarios:

| Scenario | Description |
|----------|-------------|
| **O** — Optimistic | Everything goes smoothly, no surprises |
| **M** — Most likely | A minor issue comes up, the team resolves it quickly |
| **P** — Pessimistic | One or two real problems requiring redesign or coordination |

Formula: `Expected = (O + 4 × M + P) / 6`

The most likely scenario is weighted 4× more than the extremes, giving a
statistically more robust estimate than a simple average.

Example:
```
O = 420h, M = 530h, P = 700h
Expected = (420 + 4×530 + 700) / 6 = 2240 / 6 ≈ 373h → report as range 530–545h
```

Report as a range (most likely scenario ± margin), not as a single number.

**Step C — Integration factor for validation phases**

Validation and real-environment testing phases consistently run at 1.3× their
initial estimate. Apply this factor to the validation/staging phase:

`Adjusted validation hours = Base validation hours × 1.3`

---

## Step 4 — Calculate calendar time (if the user asks for it)

If the user needs to know how long it takes in calendar time, use:

```
Calendar days = Estimated hours / 5.5
```

A full-time developer delivers on average **5 to 5.5 productive hours per day**
(accounting for meetings, code reviews, interruptions, and context switching).

If multiple profiles work in parallel, divide hours by profile before
converting to days.

```
Example: 230h / 5.5 ≈ 42 days ≈ 8–9 weeks
```

---

## Step 5 — Determine the document language

If the user specified a language (Spanish or English), use it.
If they did not specify, ask before writing the document:

> What language should the document be in? (Spanish / English)

Wait for the answer before continuing.

---

## Step 6 — Write the document

Generate the complete document using the format described below.

**Style rules (CRITICAL):**

- **Language:** whichever the user specified. Apply to all section titles,
  body text, tables, and footnotes. File names, class names, and field
  identifiers (e.g. `input-base.xml`, `brandTransactionId`) always stay in
  their original format — they are identifiers, not prose.
- **Vocabulary:**
  - In Spanish: plain language, avoid English technical jargon the client
    may not know. Avoid: scaffolding, pipeline, payload, hook, middleware,
    hardening, fire-and-forget, backoff, workaround, etc.
  - In English: standard professional technical English. Avoid jargon
    that a non-technical stakeholder would not understand.
- **Tone:** professional, direct.
  - In Spanish: avoid filler phrases like "cabe destacar que",
    "en el marco de", "a los efectos de".
  - In English: avoid filler phrases like "it is worth noting that",
    "in the context of", "for the purposes of".
- **Tables:** use tables for before/after comparisons and for lists of more
  than three items.
- **Length:** as long as needed for the client to understand the scope,
  without repeating information or adding filler.

---

### DOCUMENT FORMAT

#### Header

```
# [Project / System Name]
## [Feature or Change Name]
### Technical Proposal

---

**[Date — format: Month DD, YYYY or DD de mes de AAAA depending on language]**

---
```

If the user did not provide a document code, omit that line.

---

#### Section 1 — Introduction

Concise paragraph (3–5 sentences) explaining:
- What change this feature introduces and why it is being made.
- Which system or component it affects.
- What does NOT change (to bound the scope from the start).

---

#### Section 2 — Change Analysis

**2.1 Description of the change**
What changes and why, in plain language. If there is a new version of a
technical specification, cite it.

**2.2 Current state vs. new behavior**
Before/after comparison table when useful. For file format changes, show
the affected positions and lengths.

**2.3 Discrepancy or open question** *(include only if applicable)*
If the analysis revealed an ambiguity in the requirements that must be
confirmed before implementation, document it here with the required action.
If there are no ambiguities, omit this subsection entirely.

**2.4 Data or process flow through the system**
How the relevant information flows through the system, from input to
persistence or output. Use ASCII text diagrams or numbered lists when
clearer than prose.

---

#### Section 3 — Code Impact

**3.1 Files that change**
For each file that changes, show what changes and why. If there are
concrete code snippets (XML, SQL, Java), show the before and after.

**3.2 Files that do not require changes**
Table of components that remain untouched and the reason.
This section is important to give the client confidence that the scope is
controlled and there are no unexpected side effects.

---

#### Section 4 — Implementation Phases

Break the work into logical phases. For each phase:
- Objective of the phase.
- Numbered subtasks describing what is done in each one.
- Concrete deliverables of the phase.

**Guide for defining phases:**
- Phase 1: production code changes (schemas, logic, database).
- Phase 2: validation in the test environment and production deploy.
- If there is optional work (frontend, reporting, additional integrations),
  include it as a separate phase marked _(optional)_.

---

#### Section 5 — Change Map *(include only if more than 3 files change)*

Directory tree showing which files change and which do not:

```
module/
└── src/
    ├── file-that-changes.ext      ← CHANGE: brief description
    └── other-file-that-changes.ext ← CHANGE: brief description

No changes:
  ComponentA — reason
  ComponentB — reason
```

---

#### Section 6 — Effort Estimate

Apply the method chosen in Step 3 (A, B, or C).

**For Method A** — single task table + total + contingency explained.

**For Method B** — task table per phase (base) + revision table
(base vs revised per phase) + justification of the buffer for each phase.

**For Method C** — base task table per component + applied multipliers
+ PERT per component + consolidated final total.

In all cases, close with a note explaining:
- The total contingency or buffer applied and its percentage.
- The main risk that justifies that contingency.

If the user asked for calendar time, add the conversion at the end.

---

#### Section 7 — Collaboration Model *(include if the feature requires more than 40 hours)*

Table of profiles involved with hours distributed by month.

Common profiles: Backend developer, Software architect, DevOps,
Frontend developer. Adapt to whichever apply to the feature.

Format:

| Profile | Month 1 | Month 2 | Total |
|---------|--------:|--------:|------:|
| Backend developer | Xh | Xh | Xh |
| Software architect | Xh | Xh | Xh |
| **Total** | **Xh** | **Xh** | **Xh** |

Standard footnote:
> Effort is evaluated under a time-and-materials model: a hours-based budget
> is offered with a justified estimate. At the end of each month, a report is
> delivered detailing the tasks completed and hours dedicated to each one.

---

#### Section 8 — Risks and Prerequisites

**Prerequisites (block the start)**

Table of external confirmations or decisions that must be closed before
starting implementation:

| Prerequisite | Owner |
|--------------|-------|
| Description of the prerequisite | Team / Person |

If there are no prerequisites, omit this subsection.

**Identified risks**

For each relevant risk:
- Title and level (high / medium / low).
- Description of the risk and its mitigation or contingency plan.

If the estimate already absorbed the risk with a buffer, state it explicitly.

---

## What to do if information is missing

If the requirements are incomplete and a precise estimate is not possible:

1. List what information is missing.
2. Produce the estimate with the widest reasonable ranges.
3. Mark incomplete sections with `[PENDING: description of what is needed]`.

Do not invent assumptions without declaring them.

---

## Final output

Show the complete document directly in the conversation, ready to copy.
Do not add process explanations unless the user asks for them.

If the user wants to save the document, use Write to save it at the path
they specify or, if they do not specify one, at:

```
[working-directory]/temporary/[feature-name]/[feature-name]-estimation.md
```