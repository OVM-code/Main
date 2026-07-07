# Skill Library — maintainer instructions

This repo is a **skill library for AI coding agents**: 16 one-page discipline files in
`skills/` plus `skills/INDEX.md`, written as a handoff so less capable models (and
humans) can follow the disciplines mechanically. `README.md` explains the anatomy and
provenance. You — the session reading this — are both the audience and the maintainer:
the skills apply to your own work here, and this file governs how to change them.

## The contract

**1. `skills/INDEX.md` is the index-of-record.** Every skill file appears in it exactly
once, ranked sequentially by leverage (frequency × cost-of-getting-it-wrong ÷ length).
Any add, remove, or major edit requires updating the row AND re-considering the ranking
of the whole table — a stale index defeats the library's skimmability, which is its
entire value.

**2. Every skill follows the same anatomy.** `## Why this exists` (the failure mode it
prevents), then `## Rules` (numbered, imperative, followable without inferring intent —
or `## The patterns` for checklist-style files), optionally a mechanical checklist or
decision table, then `## Worked example (this project)`.

**3. Worked examples must be real and checkable — never invented.** A plausible
fabricated anecdote is worse than no example, because it teaches confident fabrication.
If no real event exists, omit the section and say so in the file
(`failure-patterns.md` is the accepted precedent; the validator warns rather than
errors for this reason).

**4. One page per skill (≤ ~800 words).** If a skill outgrows that, it's two skills.

**5. Every rule states its *why*** — what breaks without it. A rule that's just a
preference doesn't earn a slot.

**6. Keep the numbers honest.** INDEX read-cost estimates are measured (words × 1.3);
update them when a file's length changes materially. The "Saved per trigger" column is
explicitly an unmeasured estimate — preserve the honesty note under the table that says
so. The skill counts stated in README prose must track reality.

**7. Zero dependencies.** `check.mjs` uses only Node built-ins; no npm, no build step.

## Verification — run before every commit

```
node check.mjs
```

Exit 0 required. It enforces the INDEX↔files bijection, sequential ranks, anatomy,
page-length, read-cost drift (>30% warns), and README counts. CI
(`.github/workflows/check.yml`) runs it on every push and pull request — do not push
with it failing. If you change `check.mjs` itself, break the library deliberately in a
scratch copy and confirm the validator still catches it.

## Playbooks

**Add a skill:** write the file following the anatomy → insert an INDEX row and re-rank
the whole table (don't just append at the bottom — place it by leverage) → renumber →
update the count mentions in `README.md` → `node check.mjs`.

**Edit a skill:** if the length changed materially, refresh the read-cost estimate; if
its leverage changed (applies more/less often, or the cost of failure changed), move
its row and renumber.

**Remove or rename a skill:** delete/rename file and INDEX row together, renumber,
update README counts. For renames, grep the whole repo — skills cross-reference each
other by filename.

**When this repo grows a real codebase** (see README provenance): add project-specific
skills alongside these general ones, re-rank INDEX, and extend this CLAUDE.md with the
codebase's own contract — don't dilute the skill files with project trivia.

## Style

Write for the least capable reader who will follow the instructions: imperative rules,
no judgment assumed, mechanical checklists where judgment would otherwise be needed.
Match the voice of the existing files — direct, concrete, no filler.
