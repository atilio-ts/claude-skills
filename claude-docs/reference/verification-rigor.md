# Verification Rigor

The whole point of this skill is that the documentation it produces can be trusted more
than the code comments or the tribal knowledge it's replacing. That trust is earned one
verified claim at a time. The rule: **code is truth — every factual claim in the output
must be traceable to source you actually read this session**, not to memory of a similar
project, not to what would be reasonable to assume, not to a prior doc's wording.

---

## What this means concretely

- Never write a class name, config key, endpoint path, or default value you haven't seen
  in the actual file. If you're not sure, open the file — don't approximate from a similar
  pattern elsewhere in the codebase.
- When a fact seems surprising or counter-intuitive (two things mapped opposite to what
  their names suggest, a default that seems backwards), that's exactly when to double-check
  rather than to soften the claim into vagueness — surprising-but-true is more useful to a
  reader than smoothed-over-and-wrong.
- Numbers that change with every commit (graph stats, file counts, line counts) are
  snapshots, not facts — label them as such or omit them rather than presenting a
  point-in-time reading as a stable property of the system.

## Subagent findings are leads, not facts

If you delegate investigation to a subagent (for coverage across a large tree, or to
parallelize independent lookups), its report is a strong starting point — not something to
paste into a doc unchecked. Before writing anything the subagent's report concludes as
fact, especially anything you're about to assert confidently or that a downstream fix
depends on:

- Spot-check the load-bearing claims yourself against the actual file, particularly if the
  subagent's own report contains any internal inconsistency (e.g. contradicts itself about
  which commit/branch it was looking at) — that's a signal to re-verify from scratch, not
  to average the two versions.
- If a subagent's finding would change behavior it didn't investigate (e.g. it recommends
  changing a value it inferred from a similar-looking config elsewhere), verify the
  specific wire format/name against the actual consuming code before applying it — a
  plausible-looking parameter name is not the same as the one the code actually reads.
- Catch your own mistakes the same way: if you add a "corrected" value based on inference
  rather than direct observation, verify it before it lands in the file — self-correcting
  a wrong guess before writing beats needing a later audit pass to catch it.

## When you genuinely can't verify something

Say so in the doc rather than presenting a guess as fact. A flagged uncertainty
("⚠ could not confirm X — re-check when this is next touched") is more useful to a future
reader than a confident-sounding sentence that turns out to be wrong, because the reader
can act on a flagged unknown but will be actively misled by false confidence.

## Scope discipline while verifying

Verification sometimes surfaces real bugs, not just doc drift (a genuine security
misconfiguration, a route that isn't protected the way its neighbors are). Documenting that
finding is in scope. Silently fixing production code while you were only asked to fix docs
is not — flag it, and only fix the underlying code if the user separately asks you to.