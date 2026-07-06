# Workflow Orchestration Patterns

## Why this exists

Multi-agent orchestration (fan-out, verify, synthesize) buys thoroughness at
a real token cost. Used well it catches things a single pass misses; used by
default it's an expensive way to do something a single Read would have
solved. The discipline is knowing when the structure earns its cost, and
picking the cheapest structure that gets it.

## Rules

1. **Never reach for heavy multi-agent orchestration unless the human
   explicitly opted in**, or the task is genuinely too broad for one context
   window (a full-repo migration, an exhaustive audit). "This would benefit
   from parallelism" is not the same as "the human asked for parallelism" —
   when in doubt, describe the option and its rough cost, and ask.
2. **Default to a pipeline, not a barrier, across multiple stages.** A
   barrier (wait for every item to finish stage N before any item starts
   stage N+1) is only correct when stage N+1 genuinely needs *all* of stage
   N's results at once — deduplicating findings before expensive
   verification, or early-exiting when a count is zero. "I need to
   flatten/filter the results first" is not a reason for a barrier; that
   transform belongs inside a pipeline stage.
3. **For open-ended discovery (bugs, edge cases, unknown-sized problems),
   loop until dry (K consecutive empty rounds), not until a fixed count.** A
   fixed `while count < N` stops as soon as it hits N even if there's an
   unexplored tail; loop-until-dry keeps going until the search is actually
   exhausted.
4. **Verify adversarially when a finding matters.** Don't just re-read your
   own reasoning — have an independent pass try to *refute* the finding, and
   only keep it if a majority survive refutation. For findings that can fail
   in more than one way, give each verifier a different lens (correctness,
   security, perf) rather than three identical skeptics.
5. **Never silently truncate coverage.** If you cap to top-N, sample instead
   of covering everything, or skip retries, say so in the output. A workflow
   that quietly covered 20% of the surface and reports as if it covered 100%
   is worse than one that never ran.
6. **Scale the fleet to the ask.** "Find any bugs" → a couple of finders,
   light verification. "Thoroughly audit this" → wider finder pool, multi-vote
   adversarial verify, a synthesis stage. Don't apply audit-scale
   orchestration to a quick-check request.

## Shapes to copy

Default shape — pipeline, no barrier (item A can be verifying while item B
is still being reviewed):

```js
const results = await pipeline(
  items,
  item  => agent(findPrompt(item),   {phase: 'Find',   schema: FINDINGS}),
  found => agent(verifyPrompt(found), {phase: 'Verify', schema: VERDICT}),
)
```

Barrier — ONLY when stage 2 needs all of stage 1 at once (here: dedup
across every finder's output before paying for verification):

```js
const all      = await parallel(items.map(i => () => agent(findPrompt(i), {schema: FINDINGS})))
const deduped  = dedupe(all.filter(Boolean).flat())   // cross-item dependency — barrier earned
const verified = await parallel(deduped.map(f => () => agent(verifyPrompt(f), {schema: VERDICT})))
```

The smell test: if the code between two `parallel()` calls is a plain
`.flat()`, `.map()`, or `.filter()` with no cross-item logic, the barrier
is unearned — fold the transform into a pipeline stage.

## Worked example (this project)

The orchestration tooling available in this environment models exactly this
trade-off in its own documentation: it explicitly bars its use "for any other
task — even one that would clearly benefit from parallelism" without an
explicit human opt-in (a keyword, a standing session setting, or the human's
own words asking for orchestration) — and gives a concrete anti-pattern: code
that does `parallel(...)` then a plain `.filter()`/`.flat()` transform then
another `parallel(...)` should almost always be rewritten as a single
pipeline, because the middle transform never needed to see every result
before the next stage could start on the first one.
