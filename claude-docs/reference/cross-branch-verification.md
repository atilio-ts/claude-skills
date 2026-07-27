# Cross-Branch Verification

Two questions come up constantly while auditing docs on a feature branch, and both have a
concrete git recipe — don't answer either from memory or from reading a diff loosely.

1. **Is this bug/gap something the current branch introduced, or was it already there?**
   Matters for where a finding belongs (a doc note vs. something to fix now) and for not
   misattributing blame in what you write.
2. **A doc (or a teammate) claims a bug is already fixed on some other branch — is that
   actually true?** Matters for the `RESOLVED` verdict in `audit-existing-docs.md` — a fix
   that exists but doesn't work, or doesn't fully cover the case, is not resolved.

---

## Question 1 — did *this* branch touch the file at all?

```bash
git log --oneline <base-branch>..HEAD -- <file>
```

Empty output is a complete, one-command answer: the current branch never touched this file,
so anything wrong in it predates this branch entirely — no further diff analysis needed, and
no need to hedge the claim in the doc as "possibly related to recent changes."

Non-empty output means the file *was* touched, but that alone doesn't tell you whether the
specific bug is related to the change. Follow up with:

```bash
git diff <base-branch>..HEAD -- <file>       # what actually changed
git show <commit> -- <file>                  # one specific commit's exact edit
```

Read the diff looking for one specific distinction: did this branch change *which condition
governs the bug's behavior* (a real candidate for having introduced or altered it), or did it
only change *what value gets written inside a pre-existing condition* (the surrounding logic —
and the bug, if any — predates this branch; it only touched an unrelated field nearby)? State
which one you found, with the diff hunk as evidence — "this branch only changed the field
written inside the existing `if`, not the condition itself" is a materially different, more
useful claim than "this branch touched the file, so it might be related."

This is the same technique whether you're writing a doc note about a live bug or filling in
an `audit-existing-docs.md` `OUTDATED` verdict that needs to say who's responsible for the
drift.

## Question 2 — does the claimed fix on another branch actually work?

Reading the diff on the other branch is a starting point, not a verification. A diff can look
plausible and still not compile, not actually fix the reported symptom, or fix only part of
it. Confirm by running it:

```bash
git worktree add <scratch-path> <other-branch>
cd <scratch-path>
# run the specific test/command that exercises the claimed fix
git worktree remove <scratch-path>   # clean up when done
```

An isolated worktree is worth the setup cost specifically because it lets you run the other
branch's actual test suite/build without disturbing your own working tree or requiring a
stash/checkout dance on the branch you're actively auditing from. If the run confirms the fix
(tests pass, symptom gone), the `RESOLVED` verdict can cite the specific commit and "verified
by running the test suite on `<branch>`, not just reading the diff" — a meaningfully stronger
claim than "a diff exists that looks like a fix." If it doesn't confirm — the tests still fail,
or fail differently — that's itself a finding worth documenting precisely (what changed, what
still fails), not a reason to quietly drop the verification and fall back to trusting the diff.

## How this shapes what you write

- Never write "this might be related to recent changes" when `git log` already gave a
  definitive empty/non-empty answer — that phrasing signals you didn't check something that
  takes one command to check.
- When citing a fix on another branch, always give the exact commit hash and branch name, and
  say explicitly whether you verified it by running it or only by reading the diff — these are
  different confidence levels and a future reader needs to know which one they're getting.
- A confirmed-but-unmerged fix is not the same situation as "fixed" — per
  `redundancy-and-deletion.md`, keep the doc describing the bug as still active on the branch
  you're documenting from, with a pointer to the fix's location, rather than treating it as
  closed.
