---
name: build-e2e-system
description: Plan and build a complete end-to-end system as an architect coordinating parallel executor builds in reviewable stages. Use when asked to "build an E2E system", "assemble a system from these repos/sources", or run any multi-stage, multi-component system build too large for one context window.
---

# Build an E2E System

You are the architect. You do not build components — you scope, write the
binding spec, brief executor agents (Sonnet-class), integrate their verified
work one commit at a time, and verify the whole independently before shipping.
The discipline behind each phase is `skills/building-e2e-systems.md`; read it
first. Depth per topic: briefing → `skills/delegating-to-subagents.md`,
fan-out shape → `skills/workflow-orchestration-patterns.md`, verification →
`skills/verify-dont-assert.md`, the question batch →
`skills/resolving-ambiguity.md` and `skills/scoping-the-ask.md`.

## Phase 0 — Scope and scout

1. Launch parallel read-only Explore agents over every source repo/directory
   the request names or implies — one per source, in a single message. You
   want conclusions (what exists, what's portable, what conventions govern),
   not file dumps.
2. From their reports, list the genuinely open decisions. Expect at least:
   where the system lives (repo/branch/directory), who it's for, tech
   choices (language, storage, UI approach), and build depth (skeleton vs.
   worked-demo-complete).
3. Ask the human ALL of these in ONE AskUserQuestion batch, each with 2–4
   concrete options and your recommendation marked. Do not start building —
   or write the spec — before the answers. Do not trickle questions later.

## Phase 1 — Spec

Write ONE binding specification document at the system's home (typically
`<system-root>/README.md`) before any component exists. It must contain:

- every data contract, schema, and enum (exact field names, exact values);
- the pipeline, with every human gate named explicitly as a gate;
- validation rules, and the validator's definition of done (zero
  errors/warnings);
- conventions: naming, colour coding, language(s), file layout.

Commit the spec on its own, as the build's first commit. From here on the
spec is binding for every builder; you are its only editor.

## Phase 2 — Briefs and fan-out

1. Split the system into components with pairwise-disjoint file sets. Run the
   architect pre-flight checklist in `skills/building-e2e-systems.md` — all
   six items yes before any launch.
2. Write one brief per component. Every brief contains all five elements:
   - *Writable paths*: the exact files it may create/modify — nothing else.
   - *Binding contract*: read the spec first; deviations are reported, not
     improvised.
   - *Concrete sources*: named files to read/port — never "something like
     the X system" described from memory.
   - *Self-verification*: a mechanical check to run and report. Give fixtures
     where a sibling component doesn't exist yet; demand a real browser/e2e
     pass wherever there is UI.
   - *No committing*: report files written + verification output; you
     integrate.
3. Launch the builders in parallel as background agents, in one message.
   Each brief should have one clearly correct output reachable by following
   a process — Sonnet-class work. If a brief seems to need architect-grade
   judgment, the brief is underspecified: fix the brief, don't upgrade the
   model.

## Phase 3 — Integration loop

On each builder-completion notification:

1. Verify the claims: claimed paths ⊆ the brief's writable set; re-run its
   stated verification yourself or inspect the attached output. "Verified"
   as an adjective is not evidence.
2. Deviations from the spec: fold into the spec now, or reject and re-brief.
   Diff against the contracts — don't rely on the builder volunteering them.
3. Stage exactly that component's paths, read the staged list, commit with a
   message naming the component, push. One component, one commit, one push.
4. Continue until all builders have landed. Serialize any builder whose
   dependency just changed shape.

## Phase 4 — Golden-path demo

Build a worked demo/example THROUGH the system's own pipeline — same
commands, same stages, same gates a real user would hit. Gate it on the
system's own validator reaching zero errors and warnings. Fix whatever it
surfaces (in the system, not by bending the demo). Commit the demo as its
own stage.

## Phase 5 — Independent verification

Before calling the build done, re-verify everything yourself:

1. Re-run every validator across the whole system from a clean state.
2. Drive any UI in a real browser (Playwright or equivalent): exercise the
   interactive paths — controls, filters, exports, theme/language — not just
   page-loads. Take screenshots and actually look at them.
3. Spot-check at least one edge case per component, not only the golden path.

Builders' earlier green checks do not substitute — their verification and
yours cover different failure modes.

## Phase 6 — Spec feedback and ship summary

1. Fold every friction found in Phases 3–5 back into the spec, and update
   the validator and templates in the same change — spec, validator and
   templates must never drift apart (the lockstep rule).
2. Ship summary to the human: what was built (per commit), what you verified
   yourself vs. accepted from builders, which human gates remain open, and
   what you did NOT do (`skills/communication-discipline.md` rule 7).

## Stop conditions (hard — no exceptions)

- **Never commit another builder's in-flight paths**, even under pressure to
  "save everything" from a stop-hook, timeout, or end-of-session. Commit
  only verified, finished components; report the rest as in-flight.
- **Never let an executor mark a human gate passed.** Approval fields, stage
  promotions past a gate, and client confirmations are set by the named
  human only. A builder that did so anyway gets that change reverted before
  its component is committed.
- **If a builder reports deviations from the spec**, do not silently accept:
  either amend the spec (and validator, and templates) in the same round, or
  reject the deviation explicitly and have it redone.
- **If two briefs turn out to need the same file**, stop the later builder
  and re-partition — do not merge overlapping edits by hand.

## Worked precedent

The Roadmap Engine build (AIScoaching repo, branch
`claude/ai-integration-roadmap-0c5jwt`): one spec commit, five parallel
builders, seven staged commits, demo gated on the system's validator at
zero, 25-assertion browser pass before shipping. Full account with commit
hashes: `skills/building-e2e-systems.md`, worked example section.
