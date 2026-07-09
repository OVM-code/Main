# Skill Library Index

Ranked by quality bought per token spent reading and following the file —
highest leverage first. "Leverage" = (how often the situation comes up) ×
(how expensive it is to get wrong) ÷ (how long the file is). Read top to
bottom if you only have time for a few.

| # | Skill | Why it's ranked here | Read cost (≈tokens) | Saved per trigger (≈tokens) |
|---|---|---|---|---|
| 1 | [`failure-patterns.md`](failure-patterns.md) | A one-page checklist covering 13 distinct expensive mistakes, each pointing at the fuller skill file. Cheapest possible way to catch yourself mid-mistake — skim this one before anything else. | ~830 | ~1,000–2,000 (catches the pattern early, before the full mistake plays out) |
| 2 | [`blast-radius-and-confirmation.md`](blast-radius-and-confirmation.md) | Governs irreversible and visible-to-others actions (force-push, reset --hard, PRs, messages). Getting this wrong is the only category of mistake on this list that can't be undone by trying again. | ~660 | unbounded–20,000+ (some failures here are data loss, not rework — no token count buys it back) |
| 3 | [`scoping-the-ask.md`](scoping-the-ask.md) | Answering the wrong question, correctly, wastes 100% of the effort spent on a task. Cheapest fix is a one-sentence restatement before acting. | ~820 | ~5,000–15,000 (a full redo of whatever was built on the wrong premise) |
| 4 | [`verify-dont-assert.md`](verify-dont-assert.md) | "Tests pass" is not "it works." This is the difference between a report the human can trust and one they have to re-check themselves — which defeats the point of delegating. | ~910 | ~2,000–6,000 (bug surfaces later, gets reported, re-diagnosed, re-fixed) |
| 5 | [`resolving-ambiguity.md`](resolving-ambiguity.md) | A fast, cheap triage step (ask vs. assume vs. recommend) that prevents both over-asking (useless) and under-asking (dangerous). | ~520 | ~3,000–10,000 (rework of whatever was built on a wrong guess) |
| 6 | [`root-cause-debugging.md`](root-cause-debugging.md) | The default failure mode under time pressure is "make the blocker go away." This is the rule that catches that instinct before it ships a workaround instead of a fix. | ~550 | ~2,000–5,000 (a second, proper debugging cycle after the symptom-patch fails) |
| 7 | [`plan-before-touching.md`](plan-before-touching.md) | Read-then-plan-then-edit, externalized as tracked tasks, is what keeps multi-step work coherent across context compression. | ~660 | ~1,000–4,000 (a mis-shapen edit caught in review and redone) |
| 8 | [`delegating-to-subagents.md`](delegating-to-subagents.md) | Only relevant once you're using subagents, but when you are, an under-briefed prompt silently produces confident, wrong work — expensive to catch after the fact. | ~600 | ~2,000–8,000 (one full bad subagent round trip: its context plus the redo) |
| 9 | [`code-minimalism.md`](code-minimalism.md) | Prevents the second-most-common review complaint (scope creep, dead comments, premature abstraction) at the cost of a short read. | ~750 | ~1,000–3,000 (reviewer untangles a mixed diff or requests a split) |
| 10 | [`communication-discipline.md`](communication-discipline.md) | Doesn't change what you do, changes whether the human can follow it without friction — cheap to apply, compounds over every single turn. | ~710 | ~300–1,500 (one avoided clarifying round trip) |
| 11 | [`tool-selection-discipline.md`](tool-selection-discipline.md) | Mechanical and easy to internalize once; mostly prevents friction and permission-prompt noise rather than correctness bugs. | ~590 | ~200–800 per instance (small, but this situation recurs constantly) |
| 12 | [`github-pr-discipline.md`](github-pr-discipline.md) | High stakes (visible to other people) but narrow scope — only load this fully once you're actually touching PRs/issues. | ~710 | ~1,000–3,000 (undoing/reopening/re-describing a PR done wrong) |
| 13 | [`context-and-token-discipline.md`](context-and-token-discipline.md) | Efficiency rather than correctness; matters more on long sessions than short tasks. | ~680 | ~300–1,000 per instance (a redundant read or serialized call that didn't need to be) |
| 14 | [`workflow-orchestration-patterns.md`](workflow-orchestration-patterns.md) | Only relevant once multi-agent orchestration is in play, which itself should be rare (explicit opt-in) — narrow but important when it applies. | ~800 | ~10,000–50,000 (an unearned barrier or reflexive heavy fan-out, avoided) |
| 15 | [`building-e2e-systems.md`](building-e2e-systems.md) | Only triggers when a whole multi-component system is being built — rare, like #14 — but the failure it prevents (a monolithic single-context build that dies on context limits or lands as one unreviewable commit) is the costliest rework item on the list. | ~1,670 | ~20,000–100,000+ (a whole-system build redone in stages after the monolithic attempt collapses) |
| 16 | [`security-boundaries.md`](security-boundaries.md) | Critical when a request is actually dual-use or harmful, but that's a small fraction of requests — high stakes, low frequency. | ~560 | not token-denominated — this prevents harm, not rework |
| 17 | [`async-scheduling-discipline.md`](async-scheduling-discipline.md) | The narrowest scope of the set (only matters for long-running/background work) — lowest read-it-now priority, but cheap and worth having on file. | ~730 | ~3,000–10,000+ (a sleep-poll loop's worth of repeated cache-miss reloads, avoided) |

**How these numbers were made, and how much to trust them.** "Read cost" is
measured (word count × ~1.3, the usual words→tokens ratio). "Saved per
trigger" is *not* measured — there's no telemetry backing it — it's an
order-of-magnitude estimate of the rework a real failure of that kind
typically costs (a redo, an extra round trip, a discarded diff), built the
same way the rank column's reasoning was built. Treat it as a rough dial,
not a budget line: two entries aren't token-denominated at all
(`blast-radius-and-confirmation.md` can guard against unrecoverable loss;
`security-boundaries.md` guards against harm, not wasted tokens), and
`workflow-orchestration-patterns.md` and `building-e2e-systems.md` have the
largest per-trigger savings on the list yet still rank #14–15 — the *rank* is frequency-adjusted
(rare situation × huge cost still nets below a common situation × medium
cost), but this column deliberately isn't, so you can see the two factors
separately instead of pre-multiplied away.

## How to actually use this

- New to the project or the task is high-stakes/ambiguous: read 1-7 in full.
- Mid-task, about to do something specific: jump to the one file that
  matches (delegating a subagent → #8, opening a PR → #12, writing a loop →
  #14, building a whole multi-component system → #15).
- Don't try to hold all seventeen in working memory at once — that defeats
  the purpose of writing them down. Reference, don't memorize.
