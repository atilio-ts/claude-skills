# Memory Reconciliation

If the project has an auto-memory system (a per-project memory index plus individual
memory files, typically typed as `user`/`feedback`/`project`/`reference`), documentation
work frequently intersects with what's tracked there. Reconcile the two in the same pass
you touch the docs — don't leave a memory file quietly contradicting what you just wrote.

---

## When to check memory

- **Before writing**, if a memory file's description looks relevant to the area you're
  about to document — it may contain context (a deferred decision, an open bug, an
  architectural rationale) that belongs in the doc, or that changes what you'd write.
- **After writing**, whenever the doc update:
  - **Resolves** something memory tracked as open/deferred (a gap that just got
    implemented, a bug that just got fixed) — retire or update that memory entry so it
    doesn't keep surfacing stale guidance in future sessions.
  - **Contradicts** a project-architecture-style memory (stats, file paths, a described
    mechanism) that's now out of date because of what you just verified — correct the
    memory's specific claim rather than leaving two disagreeing sources of truth.
  - **Confirms** something memory already said correctly — no action needed, but don't
    duplicate that content into a new memory entry.

## What NOT to do

- Don't write new memory entries for facts that now live in the documentation you just
  produced — memory is for things that can't be derived by reading the current project
  state (decisions, history, in-flight context), not a second copy of architecture facts
  that belong in the docs themselves.
- Don't delete a memory file just because it looks stale without checking whether it's
  still tracking something real (e.g. an "open bug" memory should only be retired once
  you've actually confirmed the bug is fixed, not because it's old).

## How to reconcile

1. Read the memory index for the project (if one exists) and skim entries whose
   description overlaps the area you documented.
2. For each overlapping entry, decide: still accurate (leave it), needs a factual
   correction (edit it), or fully resolved/superseded (remove it and its index line).
3. Make the memory edit in the same turn as the doc edit it relates to — not as a
   separate deferred step — so the two never ship out of sync with each other.