# Redundancy and Deletion

Documentation directories are very often **not tracked by git** (a common convention is
keeping them under a gitignored folder so they don't clutter the repo for other
contributors). That changes the risk calculus for deleting anything in there: there is no
`git checkout` to recover a mistake. Treat deletion in a docs tree as seriously as deleting
uncommitted work, because that's exactly what it is.

---

## The hard rule

**Never delete a documentation file without an explicit answer from the user, every
time — even if you're confident it's redundant, even if you already flagged it as a
candidate in a previous turn.** Confidence that a file is stale is not the same as
authorization to remove it. Use a direct confirmation question (not a buried mention in a
larger summary) before running the delete.

This applies even when the doc tree *is* tracked by git and a deletion would technically be
recoverable — the same rule from general engineering practice applies: destructive actions
get a confirmation step regardless of technical recoverability, because the cost of asking
is low and the cost of an unwanted deletion is high.

## What counts as a deletion candidate

- **True duplicate**: two files explain the same subsystem with no meaningful difference
  in audience or angle (see `structure-and-splitting.md` on legitimate splits — don't
  flag those).
- **Superseded**: a doc describes a mechanism, design, or bug fix that was later reverted
  or replaced, and its unique content (not shared with the canonical doc) is now actively
  wrong rather than just incomplete.
- **Resolved and no longer load-bearing**: a bug-tracking doc for an issue that's fully
  fixed everywhere that matters, with no remaining open sub-issue worth keeping visible.

## What does NOT count as a deletion candidate

- A doc describing a bug that's still open on the branch/mainline you're working from,
  even if a fix exists somewhere unmerged — keep it as active documentation and note the
  unmerged fix's location, don't archive it as resolved. See `cross-branch-verification.md`
  for how to actually verify that unmerged fix works before citing it, rather than just
  reading its diff.
- Two docs covering the same area for different audiences (backend reference vs. frontend
  cheat sheet, deep architecture doc vs. quick runbook) — these are a deliberate split, not
  redundancy, even if the audit found they'd drifted apart on a shared fact. Fix the drift,
  don't delete either.
- A doc you personally find less useful or differently organized than you'd have written
  it — style preference isn't a deletion reason.

## How to propose it

When you find a real candidate, present it with the specific evidence (what it overlaps
with, why the unique content is wrong or gone) and let the user pick, e.g.:

- Delete it
- Fix it instead of deleting (correct the stale parts, keep the file)
- Merge its still-valid unique content into the canonical file, then delete
- Leave it as-is for now

Don't pre-decide and just ask "ok to delete?" as a yes/no if there's a reasonable
fix-instead-of-delete alternative — surface the real options.

## After confirmed deletion

Grep the rest of the doc tree for references to the deleted file's path and fix any
dangling links before considering the deletion complete.