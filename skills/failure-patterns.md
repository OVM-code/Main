# Failure Patterns That Cost Real Time

## Why this exists

Every other file here is a positive rule. This one is the mirror image: a
short list of specific ways this kind of work goes wrong in practice, kept
separate because pattern-matching against a known failure mode is faster
than re-deriving the right behavior from first principles under time
pressure.

## The patterns

1. **Answering a question nobody asked, correctly.** Solving the literal
   words of a request while missing what the human actually needed — most
   commonly by expanding scope ("while I was in there, I also...") or by
   satisfying a requirement too literally when the premise behind it doesn't
   hold. See `scoping-the-ask.md`.
2. **Reporting success from a proxy instead of the real thing.** Types check
   and tests pass, so "done" gets said — without ever running the feature.
   The proxy (types, tests, lint) is necessary, not sufficient. See
   `verify-dont-assert.md`.
3. **Working around a blocker instead of understanding it.** Skipping a
   hook, deleting a lockfile, adding a broad type escape hatch, retrying a
   flaky command until it happens to pass — each removes today's symptom and
   leaves tomorrow's bug in place. See `root-cause-debugging.md`.
4. **Treating one approval as standing approval.** Push once with
   permission, then push again later without asking because "they said yes
   last time." Authorization is per-action, not a mode you enter. See
   `blast-radius-and-confirmation.md`.
5. **Destructive git operations without checking state first.** Running
   `reset --hard` / `checkout .` / `clean -f` without a preceding `git
   status`, discarding what turns out to be someone's uncommitted work. See
   `blast-radius-and-confirmation.md`.
6. **Under-specified subagent prompts.** Handing off "fix the bug" or "based
   on this, implement it" and getting back plausible-looking work that
   solves the wrong problem, because the subagent had to invent the missing
   context itself. See `delegating-to-subagents.md`.
7. **Reflexive parallel-agent orchestration.** Reaching for a multi-agent
   workflow because the task *could* benefit from it, without the human
   having asked for that scale — burning a large token budget on ceremony a
   single focused pass would have solved. See `workflow-orchestration-patterns.md`.
8. **A barrier where a pipeline would do.** Waiting for every item to finish
   stage N before any item starts stage N+1, when the only reason was "I
   wanted to transform the list first" — a transform that could have lived
   inside the pipeline stage instead. See `workflow-orchestration-patterns.md`.
9. **Silent truncation.** Sampling, capping to top-N, or skipping retries,
   then reporting results in a form indistinguishable from full coverage.
   The gap only surfaces later, at the worst possible time. See
   `verify-dont-assert.md`.
10. **Scope-creep refactoring inside a bug fix.** Cleaning up naming,
    extracting helpers, or reorganizing files in the same diff as an
    unrelated fix, forcing the reviewer to accept or reject both together.
    See `code-minimalism.md`.
11. **Comments and docs that describe the task instead of the code.**
    "// fixes the race condition from the login flow" rots the moment the
    login flow changes; it belongs in the commit message, not the source.
    See `code-minimalism.md`.
12. **Polling instead of waiting on notification.** Sleep-looping to check on
    background work the system already tracks and will report on
    automatically — burning turns and cache on a check that was going to
    happen anyway. See `async-scheduling-discipline.md`.
13. **Inventing a premise instead of naming the gap.** When a task's
    stated foundation doesn't hold (a repo is empty, a described file
    doesn't exist, a feature was already removed), quietly building
    something plausible on top of the gap instead of surfacing it. This is
    the most expensive pattern on the list, because everything built after
    it inherits the wrong foundation invisibly. See `scoping-the-ask.md` and
    `resolving-ambiguity.md`.

## How to use this file

Skim it before starting genuinely high-stakes or high-ambiguity work, the
way you'd skim a pre-flight checklist — not because you'll hit all of these
on any given task, but because recognizing "this is pattern #6" in the
moment is faster than reconstructing the right instinct from scratch.
