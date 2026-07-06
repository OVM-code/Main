# Skill Library Index

Ranked by quality bought per token spent reading and following the file —
highest leverage first. "Leverage" = (how often the situation comes up) ×
(how expensive it is to get wrong) ÷ (how long the file is). Read top to
bottom if you only have time for a few.

| # | Skill | Why it's ranked here |
|---|---|---|
| 1 | [`failure-patterns.md`](failure-patterns.md) | A one-page checklist covering 13 distinct expensive mistakes, each pointing at the fuller skill file. Cheapest possible way to catch yourself mid-mistake — skim this one before anything else. |
| 2 | [`blast-radius-and-confirmation.md`](blast-radius-and-confirmation.md) | Governs irreversible and visible-to-others actions (force-push, reset --hard, PRs, messages). Getting this wrong is the only category of mistake on this list that can't be undone by trying again. |
| 3 | [`scoping-the-ask.md`](scoping-the-ask.md) | Answering the wrong question, correctly, wastes 100% of the effort spent on a task. Cheapest fix is a one-sentence restatement before acting. |
| 4 | [`verify-dont-assert.md`](verify-dont-assert.md) | "Tests pass" is not "it works." This is the difference between a report the human can trust and one they have to re-check themselves — which defeats the point of delegating. |
| 5 | [`resolving-ambiguity.md`](resolving-ambiguity.md) | A fast, cheap triage step (ask vs. assume vs. recommend) that prevents both over-asking (useless) and under-asking (dangerous). |
| 6 | [`root-cause-debugging.md`](root-cause-debugging.md) | The default failure mode under time pressure is "make the blocker go away." This is the rule that catches that instinct before it ships a workaround instead of a fix. |
| 7 | [`plan-before-touching.md`](plan-before-touching.md) | Read-then-plan-then-edit, externalized as tracked tasks, is what keeps multi-step work coherent across context compression. |
| 8 | [`delegating-to-subagents.md`](delegating-to-subagents.md) | Only relevant once you're using subagents, but when you are, an under-briefed prompt silently produces confident, wrong work — expensive to catch after the fact. |
| 9 | [`code-minimalism.md`](code-minimalism.md) | Prevents the second-most-common review complaint (scope creep, dead comments, premature abstraction) at the cost of a short read. |
| 10 | [`communication-discipline.md`](communication-discipline.md) | Doesn't change what you do, changes whether the human can follow it without friction — cheap to apply, compounds over every single turn. |
| 11 | [`tool-selection-discipline.md`](tool-selection-discipline.md) | Mechanical and easy to internalize once; mostly prevents friction and permission-prompt noise rather than correctness bugs. |
| 12 | [`github-pr-discipline.md`](github-pr-discipline.md) | High stakes (visible to other people) but narrow scope — only load this fully once you're actually touching PRs/issues. |
| 13 | [`context-and-token-discipline.md`](context-and-token-discipline.md) | Efficiency rather than correctness; matters more on long sessions than short tasks. |
| 14 | [`workflow-orchestration-patterns.md`](workflow-orchestration-patterns.md) | Only relevant once multi-agent orchestration is in play, which itself should be rare (explicit opt-in) — narrow but important when it applies. |
| 15 | [`security-boundaries.md`](security-boundaries.md) | Critical when a request is actually dual-use or harmful, but that's a small fraction of requests — high stakes, low frequency. |
| 16 | [`async-scheduling-discipline.md`](async-scheduling-discipline.md) | The narrowest scope of the set (only matters for long-running/background work) — lowest read-it-now priority, but cheap and worth having on file. |

## How to actually use this

- New to the project or the task is high-stakes/ambiguous: read 1-7 in full.
- Mid-task, about to do something specific: jump to the one file that
  matches (delegating a subagent → #8, opening a PR → #12, writing a loop →
  #14).
- Don't try to hold all sixteen in working memory at once — that defeats the
  purpose of writing them down. Reference, don't memorize.
