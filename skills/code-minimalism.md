# Code Minimalism

## Why this exists

Code that does more than the task requires is a liability, not a bonus: it's
more surface to review, more surface to break, and more surface for the next
change to have to work around. The discipline is to write the smallest
correct diff, not the most complete-feeling one.

## Rules

1. **Don't add abstractions for hypothetical future cases.** If there's one
   caller today, write for one caller. A helper function for something used
   once is indirection, not reuse.
2. **Three similar lines beat a premature shared abstraction.** Wait for a
   third real occurrence before generalizing, and even then, only generalize
   if the three occurrences are actually the same thing, not just
   similar-looking.
3. **Don't validate or error-handle for states that can't happen.** Trust
   internal code and framework guarantees. Only validate at real system
   boundaries — user input, external API responses, file/network I/O that
   can genuinely fail.
4. **No feature flags or compatibility shims for your own in-progress
   change** — if you can just change the call sites, change them, rather than
   keeping the old path alive "just in case."
5. **Default to zero comments.** Well-named identifiers already say *what*
   the code does. Only write a comment when it captures a *why* that isn't
   visible in the code itself — a non-obvious constraint, a workaround for a
   specific external bug, something that would genuinely surprise the next
   reader. If deleting the comment wouldn't confuse anyone, delete it.
6. **Never write comments that reference the current task, a fix, or a
   caller** ("fixes issue #123," "used by the export flow," "// removed old
   logic"). That information belongs in the commit message or PR
   description, where it doesn't rot as the code around it changes.
7. **No half-finished implementations.** If you start an abstraction, finish
   it in the same change or don't start it — a partially-migrated pattern is
   worse than the thing it was replacing.
8. **Prefer editing an existing file to creating a new one**, and don't
   create documentation files nobody asked for.

## Mechanical check — run on your diff before committing

For each hunk, ask: *if I deleted this hunk, would the task still be done?*
If yes, delete it. Apply specifically to: comments, helper functions with
one caller, validation of internal data, `try/catch` around code that can't
throw, renamed variables the task didn't ask about, and any file whose
existence the task didn't require.

## Worked example (this project)

Rule 6 (task context belongs in the commit, not the artifact) has a
checkable instance in this repo's first commit. The load-bearing context for
this whole library — *the repository was empty, so the skills document
session disciplines rather than codebase conventions* — appears in exactly
one place: the commit message body ("Repository had no existing history or
code to derive project-specific skills from, so this documents…"). None of
the 16 skill files opens with a header repeating that context, even though
it would have felt natural to stamp it on each one.

Why that's the right split: the commit message is versioned *with* the
moment the decision was made and never rots; the same paragraph pasted into
16 files becomes 16 copies to keep consistent, and each one addresses a
reader who — a year from now — cares about what the skill says, not about
the circumstances of the session that wrote it. The minimal diff is the one
where each fact lives in exactly one place, chosen by who needs it.
