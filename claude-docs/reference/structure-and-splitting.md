# Structure and Splitting

Documentation that lives in one giant file is hard to navigate and hard to keep current —
every edit risks touching unrelated content, and nobody reads the whole thing to find one
fact. The goal is: a reader with a specific question should load only what's relevant, not
the whole tree.

---

## The default shape

```
.vscode/
├── CLAUDE.md                  # root: platform overview, module index, build commands,
│                               # cross-cutting conventions — thin, mostly links
├── <module>-CLAUDE.md          # one per module/service in a monorepo, or omit for
│                               # single-module projects
└── <module>/                  # deep-dive folder, only for modules complex enough to
    ├── <subsystem-a>.md        # need it (see "when to split" below)
    ├── <subsystem-b>/
    │   └── ...
    └── ...
```

The root file's job is navigation, not content — a "where do I go for X" index. Every
substantive explanation belongs in a deep-dive file the root links to, not inline in the
root itself. If the root file is growing past a couple hundred lines, that's a signal
something in it should move to its own file.

## When a module needs its own deep-dive folder

Not every module needs one. Split into a dedicated folder/file when a module has:

- More than one genuinely independent subsystem (e.g. a payments engine with separate
  card-update, tokenization, and clearing integrations — each with its own config, own
  failure modes, own external dependency).
- A subsystem complex enough that explaining it inline would make the module's main doc
  unreadable (a full protocol/encryption scheme, a state machine with many transitions,
  a generic framework other parts of the module build on).
- A recurring need for a specific how-to that doesn't belong in an architecture doc (manual
  test procedures, runbook-style incident diagnosis).

Don't split by default "just in case" — a module with one straightforward responsibility
and no distinct sub-concerns is fine as a single file. Splitting prematurely just adds
navigation overhead for no benefit.

## The Component Map pattern

For any module with more than a couple of deep-dive files, add a table near the top of the
module's main doc mapping **component → where it's configured/entered → deep doc**. This
is the single highest-value addition for navigability: a developer facing an incident or a
question can go straight to the right file instead of grepping cold. Base the "where it's
configured/entered" column on whatever the project's real entry-point layer is (see
`gap-analysis.md`) — deploy config, route group, command name, etc.

```markdown
| Component | Where it's wired | Deep doc |
|---|---|---|
| <name> | <config file / route / entry point> | @path/to/deep-dive.md |
```

## Cross-reference, never duplicate

If two files both need to explain the same fact, one of them explains it and the other
links to it. Concretely:

- Before writing an explanation, grep the existing doc tree for whether it's already
  explained somewhere. If it is, link to it (`See path/to/file.md for X`) instead of
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

- Use plain relative paths for cross-references (`path/to/file.md`), not a wiki-link
  syntax that only works inside a different tool.
- Give every new file a name that describes its subject, not its creation date or a ticket
  number — these files are meant to outlive the task that created them.
- If a doc set already has an established reference style (e.g. `@path` imports at the
  root level vs. plain paths in deep-dives), match it — don't introduce a second
  convention in the same tree.