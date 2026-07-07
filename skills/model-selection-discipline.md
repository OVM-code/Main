# Model Selection Discipline

## Why this exists

Every step of agentic work has a model tier and a reasoning-effort level
attached to it, separate from whether the output is correct. The expensive
failure isn't picking a bad model — it's picking a *uniform* one: running an
entire fan-out at the top tier because one step in it needed that, or
running the one hard judgment call at the cheap tier because the easy steps
around it were fine there. The discipline is matching tier and effort to
what each step actually requires, not to how important the task feels
overall.

Where this is checkable: this session's own subagent-spawning tools expose a
model-tier override and a reasoning-effort override (`low`/`medium`/`high`/
`xhigh`/`max`) as *per-call* parameters, both defaulting to "omit and inherit
the session's own choice" — read that tool's own parameter docs directly
rather than trust this file's paraphrase of them.

## Rules

1. **Decide per step, not per task.** A task can legitimately mix tiers:
   cheap/low-effort for mechanical fan-out (grep-and-report, apply a known
   transform), expensive/high-effort for the one step that synthesizes or
   verifies across all of it. One tier for the whole task over-pays for the
   easy steps or under-pays for the hard one.
2. **Only escalate when you can name what the cheaper option would get
   wrong.** "This seems important" isn't a reason; "this step weighs a
   tradeoff with no clearly-correct answer" is. If you can't name the
   specific failure, don't pay for the upgrade.
3. **Reach for effort before reaching for tier.** Raising reasoning effort on
   the current model (`ultrathink`) is usually cheaper than moving to a
   bigger one, and solves the same class of problem — real tradeoffs, a
   weird bug, a migration plan. Try that first; move tiers only if effort
   alone doesn't close the gap.
4. **In a fan-out, the expensive tier belongs on the minority stage.**
   Finders and extractors run at the cheapest tier that reliably does the
   narrow job; the judge/synthesis/adversarial-verify stage — a handful of
   calls, not hundreds — is where tier and effort earn their cost.
5. **A stated token/effort budget is a hard ceiling, not a target.** Size
   fleet and tier mix against the remaining budget up front, rather than
   spending freely at the default and hoping it fits.
6. **Orchestration is its own cost escalation, separate from tier.** This
   environment gates multi-agent fan-out behind explicit opt-in (a keyword,
   a session setting, or the human's own words) precisely because it
   multiplies whatever per-call tier you chose by the fleet size — getting
   the tier right and then fanning out anyway still overspends.
7. **Don't infer the tier from how the request sounds.** A short, casual bug
   report can hide a real judgment call; a long detailed one can still be
   uniformly mechanical. Judge the reasoning demand, not the tone.

## Decision table

| Signal | Choice |
|---|---|
| Mechanical, deterministic, single-shot | Cheapest tier, default effort |
| Ordinary task, no unusual ambiguity | Inherit session model/effort — omit overrides |
| Real tradeoffs, unclear cause, architecture/migration | Same tier, raised effort before a bigger model |
| Cross-item synthesis, high-stakes verify, judge stage | Top tier, high/max effort — for that stage only |
| High-volume fan-out of narrow, independent items | Cheapest reliable tier; scale count, not per-item cost |
| Explicit human budget ("+500k tokens") | Hard ceiling; size fleet/tier against what's left |

## This environment's own escalation vocabulary

Two keywords observed in this session are, functionally, model-selection
controls, each opt-in for the cost reason a tier upgrade is: **`ultrathink`**
raises the current model's effort to maximum (the cheap lever, rule 3);
**`ultracode`** opts into multi-agent orchestration (the fleet-size lever,
rule 6). Verify these against this session's own behavior when they fire,
not as an assumed constant of every environment this file might be read in
— and hold third-party claims about a specific plugin's performance numbers
or install counts to the same bar: don't repeat one as fact just because it
arrived in a request (`verify-dont-assert.md`).

## Worked example (this project)

This session's own subagent-spawning tool documents rules 1, 2, and 6 almost
verbatim, in text available to read directly rather than take on faith:
"Default to omitting [model] — the agent inherits the main-loop model …
which is almost always correct. Only set it when you're highly confident a
different tier fits the task; when unsure, omit," and separately, "omit to
inherit the session effort; use `low` for cheap mechanical stages and higher
tiers only for the hardest verify/judge stages." The same tool gates
multi-agent orchestration itself behind an explicit opt-in and names the
anti-pattern directly: reaching for fan-out because a task "would clearly
benefit from parallelism" is not the same as the human having asked for it.
