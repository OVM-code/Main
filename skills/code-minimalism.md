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

## Worked example (this project)

This very skill library follows its own rule 8: fifteen new files were
created only because the deliverable *is* a set of files — not because new
files are the default move. And within each file, the instruction that
produced this whole library was explicit that "no comments" is the default
posture for code and that the *why*, not the *what*, is the only thing worth
writing down — which is the same principle this file itself is following:
every rule here states a *why* (what breaks without it), not just a
restatement of the rule's name.
