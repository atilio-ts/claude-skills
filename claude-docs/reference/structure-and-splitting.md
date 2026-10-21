# Structure and Splitting

Documentation that lives in one giant file is hard to navigate and hard to keep current —
every edit risks touching unrelated content, and nobody reads the whole thing to find one
fact. The goal is: a reader with a specific question should load only what's relevant, not
the whole tree.

---

## The default shape

```
.vscode/
├── CLAUDE.md                  # root index — loaded every session, keep it under ~150 lines
└── docs/
    ├── architecture.md        # modules, data flow, external dependencies
    ├── modules/
    │   ├── <module>.md        # one per module/service; omit for single-module projects
    │   └── <module>/          # only when a module has independent subsystems
    │       └── <subsystem>.md
    ├── decisions/
    │   └── NNNN-<topic>.md    # one per non-obvious decision (ADR style)
    └── ...                    # conditional files, see below
```

Conditional files — create one only when the project has real content for it:

| File | Create when |
|---|---|
| `docs/glossary.md` | Business terms map to classes/tables in a way the names don't make obvious |
| `docs/data.md` | There is a schema, migrations, or entities worth mapping |
| `docs/api.md` | The project exposes endpoints or a public API (link an OpenAPI spec if one exists, don't copy it) |
| `docs/integrations.md` | External services with their own config and failure modes |
| `docs/setup.md` | Local setup needs more than the commands in `CLAUDE.md` (env vars, docker, seed data) |
| `docs/testing.md` | Test types, fixtures, or manual procedures need explanation |
| `docs/deploy.md` | CI/CD pipelines or environments differ in non-obvious ways |
| `docs/runbooks/<incident>.md` | A recurring failure has a known diagnosis procedure |
| `docs/conventions.md` | The Conventions section of `CLAUDE.md` outgrows ~40 lines |

Never create a file, folder, or section as an empty stub "for later". A missing file
means "nothing to say yet"; an empty one means someone has to open it to find that out.

Never write anything outside `.vscode/` — no root `CLAUDE.md`, `AGENTS.md`, or `docs/`
folder. The `.claude/CLAUDE.md` symlink that loads the root file is created by
`/custom-init`, not by this skill.

## The root `CLAUDE.md`

Its job is navigation, not content — a "where do I go for X" index. It is loaded into
every session, so every line costs context. Sections, in this order, skipping any with
nothing real to say:

1. **What it is** — two or three lines: purpose, stack, shape (monorepo or single module).
2. **Commands** — build, test, run, lint, exactly as they run in this repo.
3. **Component map** — the table described below, pointing into `docs/`.
4. **Conventions** — see the next section.
5. **Gotchas** — facts a reader would get wrong from reading the code alone.
6. **Docs index** — one line per file under `docs/`, saying what question it answers.

If the root file is growing past ~150 lines, something in it belongs in `docs/`.

## The Conventions section

Project rules that code must follow: layers and their allowed dependencies, architecture
tests (ArchUnit, dependency-cruiser, import-linter), naming patterns, error-handling and
testing conventions. Two sources, and only these two:

- **Inferred** — rules the code enforces or follows consistently: architecture-test
  rules, linter/formatter config, a pattern repeated across most modules. Cite where each
  one comes from (`ArchitectureTest.java`, `.eslintrc`, "every handler in `api/`").
- **Confirmed** — rules the user states. In create mode, after drafting the inferred
  list, ask the user (`AskUserQuestion`) whether there are project-specific rules the
  code doesn't show, and whether any inferred rule is actually an accident rather than
  a convention.

Don't copy the user's general coding style into this section — that lives in their global
config and applies to every project. Only project-specific rules belong here. Never
invent a principle that neither the code nor the user supports.

## When a module needs its own deep-dive folder

Not every module needs one. Split `docs/modules/<module>.md` into a
`docs/modules/<module>/` folder when a module has:

- More than one genuinely independent subsystem (e.g. a payments engine with separate
  card-update, tokenization, and clearing integrations — each with its own config, own
  failure modes, own external dependency).
- A subsystem complex enough that explaining it inline would make the module's main doc
  unreadable (a full protocol/encryption scheme, a state machine with many transitions,
  a generic framework other parts of the module build on).

Don't split by default "just in case" — a module with one straightforward responsibility
and no distinct sub-concerns is fine as a single file. Splitting prematurely just adds
navigation overhead for no benefit. Runbook-style how-tos go in `docs/runbooks/`, not in
the module folder.

## When to write a decision record

Write `docs/decisions/NNNN-<topic>.md` when the code reflects a choice a reader would
question or undo without knowing why (an unusual library, a deliberate duplication, a
workaround for an external limitation). Keep each one short: context, decision,
consequences. Only record decisions with evidence in the code, a commit, or the user's
own words — never reconstruct a rationale by guessing.

## The Component Map pattern

The root `CLAUDE.md` maps **component → where it's configured/entered → deep doc**. This
is the single highest-value addition for navigability: a developer facing an incident or
a question can go straight to the right file instead of grepping cold. Base the "where
it's configured/entered" column on whatever the project's real entry-point layer is (see
`gap-analysis.md`) — deploy config, route group, command name, etc. A module doc with
more than a couple of subsystem files gets its own smaller map of the same shape.

```markdown
| Component | Where it's wired | Deep doc |
|---|---|---|
| <name> | <config file / route / entry point> | .vscode/docs/modules/<name>.md |
```

## Cross-reference, never duplicate

If two files both need to explain the same fact, one of them explains it and the other
links to it. Concretely:

- Before writing an explanation, grep the existing doc tree for whether it's already
  explained somewhere. If it is, link to it (`See .vscode/docs/path/to/file.md for X`) instead of
  re-deriving it.
- When a new doc's subject matter overlaps an existing one's, say explicitly in prose which
  file owns which part ("read X for the crypto mechanics, this file only covers how the
  provider gets selected").
- Two docs are allowed to cover the same *area* from different angles for a legitimately
  different audience (e.g. a full backend reference vs. a condensed frontend-integration
  cheat sheet) — that's not duplication, it's a deliberate split. But when they do, note
  in each which is the source of truth for facts they share, so they don't quietly drift
  apart on the same fact stated twice.

## Naming and cross-linking conventions

- Use plain paths relative to the repo root for every cross-reference
  (`.vscode/docs/architecture.md`), in the root file and inside `docs/` alike. The root
  file loads through the `.claude/CLAUDE.md` symlink and tools resolve paths from the repo
  root, so a bare `docs/...` points at a folder that doesn't exist.
- Don't use `@path` imports. They pull the whole file into every session, which defeats
  loading docs on demand.
- Give every new file a name that describes its subject, not its creation date or a ticket
  number — these files are meant to outlive the task that created them.
- File names are lowercase kebab-case.

## Migrating the old layout

Older projects keep deep-dives directly under `.vscode/`: `.vscode/<module>-CLAUDE.md`
files and `.vscode/<module>/` folders. Detect them with:

```bash
ls .vscode/*-CLAUDE.md 2>/dev/null
find .vscode -mindepth 2 -name '*.md' -not -path '.vscode/docs/*' -not -path '.vscode/.claude/*' \
  -not -path '.vscode/code-review-graph/*' -not -path '.vscode/file-stash/*' -not -path '.vscode/temporary/*'
```

When found, propose a move table (old path → new path under `docs/`) and apply it only
after the user confirms — `.vscode/` has no git history to recover a wrong move, so the
hard rule in `redundancy-and-deletion.md` covers moves too. Move with `mv`, never
copy-then-delete. After moving, fix every link in the tree that pointed to an old path,
and audit the moved content like any other existing doc.
