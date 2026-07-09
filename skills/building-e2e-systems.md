# Building End-to-End Systems

## Why this exists

Asked to "build a complete system", the default failure mode is a monolithic
single-context build: one agent reads everything, designs while building, and
writes every component in one uninterrupted pass. That build dies in one of
three ways — the context window runs out before the system does; components
drift apart because their contracts were never pinned anywhere; or it lands
as one enormous commit the human can only accept or reject wholesale. The fix
is a division of labour: one architect-grade model scopes, writes a binding
spec, and briefs executor models that build components in parallel against
that spec; the architect integrates one component per commit and verifies
independently before shipping. This file is the discipline for the architect
seat. It leans on the rest of the library rather than restating it —
references below are load-bearing.

## Rules

1. **Scout first, then ask everything once.** Explore all source material
   with parallel read-only agents before forming a plan
   (`plan-before-touching.md` rule 2's "verify the state first" applies to
   whole repositories here). Then put every genuinely open decision to the
   human in one batch — where the system lives, who it's for, tech choices,
   how deep to build — with your recommendation marked per question
   (`resolving-ambiguity.md` rule 2). One batch, before any building:
   questions trickled out later stall parallel builders, and questions never
   asked become assumptions buried in the deliverable
   (`scoping-the-ask.md` rule 5).
2. **Write one binding specification before any component.** Every data
   contract, schema, and enum; the pipeline with its human gates named
   explicitly; the validation rules; the naming/colour/language conventions.
   The spec is the coordination mechanism — builders who share a spec never
   need to talk to each other. A contract that lives only in the architect's
   head is not a contract.
3. **Fan out with briefs, not gestures.** Every executor brief contains the
   five elements in the template below. The writable-path sets across briefs
   must be pairwise disjoint — zero overlap, checked mechanically before
   launch, because two builders touching one file turns integration into
   archaeology. Briefing standards are `delegating-to-subagents.md`; the
   pipeline-versus-barrier choice is `workflow-orchestration-patterns.md`.
4. **Integrate in stages: one component, one commit, one push.** The moment a
   builder reports finished-and-verified, verify it (checklist below), then
   commit exactly that component's paths. Never commit another builder's
   in-flight paths — not even under pressure to "save everything now" from a
   stop-hook or timeout. Staged commits are the human's review surface; a
   mixed commit destroys it.
5. **Prove the golden path through the system's own pipeline.** Build a
   worked demo using the system exactly as its user would — same tools, same
   stages, same gates — and gate the demo on the system's own validator
   reaching zero errors and warnings. Until that demo exists, you have a pile
   of components, not a system.
6. **Verify independently before shipping.** A builder's report is a claim
   (`delegating-to-subagents.md` rule 6). Re-run the validators yourself,
   drive any UI in a real browser yourself, and look at the screenshots
   (`verify-dont-assert.md` rules 2 and 5). Never ship on builders' word
   alone — their verification and yours cover different failure modes.
7. **Feed frictions back into the spec in the same round.** Every ambiguity a
   builder or the demo trips over is a spec bug. Amend the spec, the
   validator, and the templates together — they must never drift apart (the
   lockstep rule). A deviation a builder made is either folded into the spec
   or rejected explicitly; it is never left as unwritten local knowledge.
8. **Route models by judgment, not prestige.** Architect work — spec, briefs,
   integration verdicts, independent verification — goes to the strongest
   tier available (Opus-class). Each executor brief is deliberately written
   so there is one clearly correct output reachable by following a process,
   which is precisely the Sonnet-class criterion. If a brief seems to need
   Opus-class judgment, the brief is underspecified: fix the brief. Humans
   review at the staged commits and at the domain gates the spec names.

## Mechanical checklists

**Architect pre-flight — all yes before launching any builder:**

1. Scouts have reported on every source repo/directory the system draws from?
2. The human has answered the open-decision batch (home, audience, tech,
   depth)?
3. The spec exists as one document and covers: every schema and enum, the
   pipeline with human gates, validation rules, and conventions?
4. The system's validator is specified — what it checks, and that zero
   errors/warnings is the definition of done — even if a builder will write it?
5. Every planned component has a brief, and the union of writable-path sets
   has zero pairwise overlap?
6. No brief depends on a sibling builder's live output — dependencies are
   served by fixtures, or that builder is serialized after its dependency?

**Builder brief template — every brief contains all five:**

1. *Writable paths* — "you may create/modify exactly these files", disjoint
   from every sibling brief.
2. *Binding contract* — "read the spec at `<path>` first; it is binding;
   deviations are reported, never improvised".
3. *Concrete sources* — named files to read or port ("port the viewer from
   `<path>`"), never a description of them from memory.
4. *Self-verification* — a mechanical check the builder must run and report:
   fixtures where sibling components don't exist yet; a real browser/e2e pass
   wherever there is UI.
5. *No committing* — "do not commit or push; report files written plus
   verification output; the architect integrates".

**Integration loop — per builder-completion notification:**

1. Read the report; confirm claimed paths are a subset of the brief's
   writable set.
2. Re-run the builder's stated verification yourself, or inspect the output
   it attached — don't accept the adjective "verified".
3. Check for deviations from the spec — diff against the contracts, don't
   rely on the builder volunteering them. Fold each into the spec now, or
   reject and re-brief.
4. Stage exactly that component's paths, read the staged list before
   committing (`verify-dont-assert.md`, worked example), commit, push.
5. Note any friction for the spec-feedback pass (rule 7).

## Worked example (the Roadmap Engine build)

Verifiable against the AIScoaching repository, branch
`claude/ai-integration-roadmap-0c5jwt` — `git log --oneline --stat` there
checks every number below.

- **Spec first:** commit `5f321d3` added `07-roadmap-engine/README.md` — 356
  lines of pipeline, data contracts, enums, gates, colour and language
  conventions — before any component existed.
- **Fan-out:** five executor briefs ran in parallel with disjoint path sets,
  landing as five component commits: agent cores and wrappers (`2775307`),
  the AS-IS viewer ported from a named sibling ERP system (`2326eb4`), the
  department catalog and standard flows (`c61098d`), the workspace template,
  effort baselines and an 804-line validator (`59e00b4`), and the proposal
  generator (`aa5bf8b`).
- **Staged integration:** seven commits in total — one spec, five components,
  one demo — each committed by the architect the moment its builder's work
  was verified, never batched.
- **Golden path:** the demo client (`f526f35`, ~4,000 lines) was built
  through the pipeline itself and gated on `check_engagement.py` reaching
  zero; re-run at the time of writing it still prints
  `0 error(s), 0 warning(s)`.
- **Spec feedback, same round:** the demo surfaced two spec ambiguities
  (PAIN ids are numbered once per engagement, not per department; `Aannames`
  must list bare assumption ids matching the formula's tokens) — the demo
  commit amends the spec README in the same commit, keeping spec, validator
  and templates in lockstep.
- **Independent verification:** before shipping, the architect drove the
  built proposal HTML in a scripted browser itself — a 25-assertion pass over
  sliders, filters, quadrant clicks, the confirm-export flow, and
  theme/language chrome. That script lives in the build session, not the
  repo; what the repo pins (and so what you can check) is the five-interaction
  verification contract in `07-roadmap-engine/cores/proposal-builder-core.md`.

The failure version of this build: one agent, one context, everything from
catalog to browser verification in a single pass — which at ~11,700 inserted
lines across the seven commits would have exhausted its context long before
the demo, and left the human one take-it-or-leave-it diff to review.
