# Auditing Existing Docs

Existing documentation is a claim, not a fact. Treat every sentence in an existing doc as
"someone believed this was true when they wrote it" — your job is to check whether it
still is, not to assume it is because it reads confidently or has been there a long time.

---

## The verdict system

For each doc file (or section, for large files), assign one verdict:

- **ACCURATE** — checked the concrete claims against current source, no material drift.
- **OUTDATED** — quote the specific stale claim and what's actually true now, with a
  file:line reference to the evidence. A vague "this seems old" is not a verdict — pin it
  to a specific sentence and a specific piece of code that contradicts it.
- **REDUNDANT** — significant content overlap with another doc. Name which one. Overlap
  alone isn't automatically a problem (see `structure-and-splitting.md` on legitimate
  splits like "backend reference" vs "frontend integration cheat sheet") — REDUNDANT means
  the *same* fact is asserted in two places and they've since drifted apart, or one fully
  supersedes the other.
- **RESOLVED** — the doc describes a bug/issue that has since been fixed. Don't just delete
  it silently; check whether the fix is confirmed merged to the branch/mainline you care
  about (a fix can exist on an unmerged branch while the bug is still live everywhere
  else — that's a meaningfully different situation from "fixed everywhere").

## How to verify a claim

Don't take a doc's word for anything checkable:

- **Class/method names** → grep for them in the actual source. If a referenced test file
  or class doesn't exist, that's not a nitpick — check `git log --all` before concluding
  it never existed; it might live on an unmerged branch, or have been extracted into a
  separate repo entirely. State what you actually found, don't guess at "probably deleted."
- **Config keys / property names** → read the actual config-loading code (constructor,
  `setConfiguration`, environment binding), not just the deploy/env file — a doc can match
  the YAML and still be wrong if the YAML itself doesn't match what the code actually binds.
- **Endpoint paths, permission strings** → read the actual route table and the actual
  authorization/security config side by side. These two commonly drift from each other
  independently of the docs.
- **"X is used by Y"** → grep for the actual call site. Don't infer usage from proximity or
  naming similarity.
- **Numbers that change with every commit** (graph node/edge counts, file counts, line
  counts) → don't hardcode a snapshot as if it were permanent. Either omit the exact number
  or explicitly label it as a point-in-time reading with the tool/command to get the
  current value.

## Scaling the check to a large doc tree

A single doc file, read and check directly. A tree of dozens of files, don't try to hold
it all in one pass — fan out. Group files by module/subsystem and assign each group to a
parallel investigation (a subagent, or a background task) with explicit instructions to:

- verify concrete claims against real source, not skim-and-assume
- return a verdict per file with evidence, not prose summaries without citations
- flag redundancy with sibling files in its own group, and note (without fully
  investigating) any suspected redundancy with files outside its group

Then the primary agent applies fixes based on the returned verdicts — but re-verify before
writing anything non-trivial (see `verification-rigor.md`); a subagent's claim is a strong
lead, not a fact you can paste in unchecked.

## Fixing what's confirmed wrong

- Fix only what's verified — don't "improve" prose that was already accurate just because
  you're in the file.
- When a fix reverses something surprising (e.g. two things map opposite of what their
  names suggest), keep the surprising fact in the doc explicitly, with the evidence
  pointer — future readers will make the same wrong assumption otherwise.
- If a doc's structure genuinely doesn't match its content anymore (e.g. it was clearly a
  bug-tracking note that's since become a stale reference), that's a `redundancy-and-deletion.md`
  question, not just a content fix.

## Don't assume a decision was already made

If the audit surfaces something that looks like an open design question (e.g. two docs
disagree, or a piece of infrastructure looks half-finished), say so plainly and let the
project owner decide — don't quietly pick a side and document it as settled.