# Plan Before Touching

## Why this exists

Editing code before you understand its shape produces edits that compile but
don't fit — wrong abstraction level, duplicated logic that already existed
elsewhere, a fix in the wrong layer. The fix is always to read first, plan
second, edit third, and to externalize the plan so it survives context
compression instead of living only in short-term reasoning.

## Rules

1. **Read before you edit — not "search," read.** A tool that edits a file
   will refuse to run if you haven't read that file first in this
   conversation. Treat that as a floor, not a target: read enough surrounding
   code to know callers, siblings, and naming conventions, not just the one
   line you're changing.
2. **For anything with more than ~3 steps or more than one file, write the
   steps down as tracked tasks before starting**, and flip each to
   in-progress/completed as you go — don't batch status updates at the end.
   This is what lets a task survive context summarization: the plan is state,
   not memory.
3. **For genuinely ambiguous or exploratory asks, enter an explicit planning
   mode before writing any code.** Produce the plan, get it approved, then
   execute. Don't blend "figuring out what to build" with "building it" in
   the same uninterrupted pass — the human has no checkpoint to redirect you.
4. **Check blast radius before you check syntax.** Before running any command
   or edit, ask: is this local and reversible, or does it touch shared state,
   other people's work, or something hard to undo? That answer determines
   whether you proceed solo or confirm first (see
   `blast-radius-and-confirmation.md`).
5. **Investigate unfamiliar state before acting on it.** An unfamiliar file,
   branch, stash, or lockfile is presumptively someone's in-progress work, not
   debris. Look at it before deciding whether to keep, move, or ignore it.
6. **Don't design for hypothetical future requirements.** A plan should cover
   the task in front of you. Speculative extensibility is scope creep wearing
   a planning hat.

## How to tell "just do it" from "plan first"

| Signal | Action |
|---|---|
| Single file, single clear change, no ambiguity | Just do it |
| Multi-file, multi-step, but the *what* is clear | Track with tasks, then execute |
| The *what* itself is unclear or has real tradeoffs | Explicit plan-and-approve step first |
| Task rests on state you haven't verified yet (repo contents, existing tests, current behavior) | Verify the state first — a plan built on a wrong assumption about the codebase is worse than no plan |

## Worked example (this project)

Before writing any of these skill files, the plan was: (1) check whether the
repo actually had history worth studying, via `git log --all`, `git branch
-a`, `git ls-remote origin`, and a filesystem walk — all cheap, reversible,
read-only — *before* deciding what the deliverable should even be. Only after
that came back genuinely empty did the next decision point (ask the human)
get triggered. Writing 15 files first and discovering the premise was wrong
afterward would have wasted the entire turn.
