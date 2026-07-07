---
name: apply-maintainable-treatment
description: Make a repository safely maintainable by AI agents — diagnose what is load-bearing, write a contract, build an executable validator that proves it, wire CI, and verify the validator catches a real break. Use when the user asks to "apply the maintainable treatment", "make this repo Claude-maintainable/agent-maintainable", set up guardrails so future agents don't corrupt a system, or harden a repo before letting agents work in it autonomously. Runs per-repo and is safe to fan out one agent per repo in parallel.
---

# Apply the maintainable treatment

Turn a repository into one that AI agents (or humans) can change *without silently
breaking it*, by giving it three layers that reinforce each other: a written **contract**,
an **executable validator** that proves the contract mechanically, and **CI** that runs the
validator on every change. This skill is the repeatable form of that procedure.

## The one idea that makes this work

**The treatment is bespoke, never a template.** Its entire value is finding what is
*load-bearing* in THIS repo — the invariant that, if violated, corrupts the system
silently — and making that specific thing impossible to break unnoticed. A generic
`CLAUDE.md` dropped into every repo is worse than nothing: it reads authoritative while
protecting the wrong things, which teaches confident fabrication (background rationale:
`skills/verify-dont-assert.md`, `skills/scoping-the-ask.md` — not required reading under
a tight budget). Do the diagnosis every time.

Real examples of "the sacred thing" from repos already treated — note how different each is:
record ids that must never be regenerated; `CREATE TABLE IF NOT EXISTS` that silently
ignores schema edits in production; a CSV that is the single source of truth; an index
that must stay a bijection with its files; bilingual page-parity and honest placeholders.

**Fence, don't fix.** The diagnosis will often surface real latent bugs (a
nondeterministic fallback, missing escaping, a race). The treatment is additive-only:
contract, validator, CI — never product-code changes. Make the validator catch the
hazard's consequences, and list the bug itself as a recommended follow-up in the PR
body. Why: mixing guardrails with behavior changes makes the diff unreviewable, and
fixing on your own initiative is scope creep (`skills/scoping-the-ask.md`) — the owner
decides what to fix and when.

## Procedure

1. **Survey.** Read any existing `CLAUDE.md` / `AGENTS.md` / `README`, map the file tree,
   and identify what the repo *is*: application code, generated data, hand-maintained
   documents, static sites, config. Read enough of the actual code/data to understand how
   it is consumed and where a wrong write does damage. Do not skim. Run whatever
   verification already exists (tests, lint, build) to establish a green baseline before
   you change anything. **If a contract or validator already exists, your job is to
   extend it** — a second parallel contract is drift waiting to happen; never duplicate.
2. **Diagnose what is sacred.** Name the 1–5 invariants that, if broken, corrupt the
   system silently or irreversibly — the failures no test currently catches and a
   well-meaning agent would plausibly cause. This is the judgment step; everything else is
   mechanical. If you cannot name a concrete failure scenario for an invariant, it is a
   preference, not an invariant — drop it.
3. **Write the contract** in `CLAUDE.md` (or extend `AGENTS.md` if the repo already uses
   that convention — build on what exists, do not replace it). For each invariant state the
   rule imperatively *and its why* (the concrete thing that breaks without it). Add short
   playbooks for the common changes an agent will actually make.
4. **Build the executable validator** — zero dependencies, in the repo's own language
   (`node check.mjs` for JS/docs/data; the repo's test runner otherwise). It must
   mechanically enforce every invariant from step 3. Match its shape to the repo's shape:
   - **Running application** → a smoke test that boots the *built* app against throwaway
     local resources (never production credentials) and exercises the real contract
     end-to-end, not just a static lint.
   - **Generator / build-artifact repo** (static sites, feeds, compiled docs) → run the
     real build in a scratch copy and byte-compare against the committed artifact. If
     rebuilding unchanged inputs is not byte-identical (timestamps, randomness), that
     nondeterminism is itself a finding — fence it and flag it.
   - **Invariants about immutability over time** ("published X never changes") cannot be
     checked from the working tree alone — materialize a committed reference (an
     append-only ledger, a lockfile) for the validator to compare against. A git-diff
     check is not enough: in CI the break is already committed, so there is no diff.
   Add a script alias (`npm run check`) if there is a manifest.
5. **Wire CI** — a `.github/workflows/*.yml` that runs the validator on every push and PR,
   needing no secrets and never touching production. If you cannot exercise CI itself
   (no remote, Actions disabled), confirm the workflow's steps are exactly the commands
   you already ran locally — no untested extras.
6. **Verify BOTH directions, plus a happy-path control.** The validator must pass on the
   current repo; each invariant, deliberately broken in a throwaway copy, must fail
   (exit 1) with a message naming the consequence; and a *legitimate* change made by the
   contract's own playbook must still pass — a validator that also rejects correct work
   will get deleted, not obeyed. A validator never seen to fail proves nothing — this
   step is non-negotiable.
7. **Branch, commit, PR.** Work on `claude/maintainable-treatment` (or the repo's branch
   convention). The commit/PR body states what was found sacred and how it is now
   enforced, lists any latent bugs found-but-fenced (see "Fence, don't fix"), and —
   since a fan-out agent cannot ask questions — records any diagnosis you are *unsure*
   about as an open question rather than enshrining a guess. Do not merge; leave the PR
   for the owner.

## Mechanical checklist — before calling it done

- [ ] Existing verification ran green as a baseline before any change.
- [ ] Contract lives in the file the repo's agents already load (`CLAUDE.md`/`AGENTS.md`);
      an existing contract/validator was extended, not duplicated.
- [ ] Every invariant has a stated *why* and a matching validator check.
- [ ] Validator is zero-dependency and runs with one command.
- [ ] Apps: smoke test drives real behavior on throwaway resources. Generators: real
      build byte-compared in a scratch copy. Immutability invariants: committed reference.
- [ ] CI runs the validator on push + PR; its steps are exactly the commands run locally.
- [ ] Negative test done: each invariant, broken in a scratch copy, is caught (exit 1).
- [ ] Happy-path control done: a playbook-correct change still passes.
- [ ] No product code changed; latent bugs are listed in the PR body, not fixed.
- [ ] Branch pushed, PR body names the sacred invariant(s) and any open uncertainty;
      nothing merged.

## Running it across many repos in parallel

Each repo is independent, so fan out one agent per repo (see
`skills/delegating-to-subagents.md` and `skills/workflow-orchestration-patterns.md`). Give
each agent this skill and one repo; each produces its own branch + PR. Parallelism is safe
*because step 6 is self-verifying* — an agent cannot open a green PR unless its validator
actually runs and passes. Review every PR's **diagnosis** (the judgment); trust the passing
validator for correctness. A wrong contract is worse than none, so a shallow diagnosis is
the one failure mode fan-out will not catch for you.

## Worked example (this project)

This skill is the generalization of a real, repeated event: the treatment was applied by
hand to five repositories in one session — a personal-knowledge store (sacred: stable
record ids), a Next.js waitlist app (sacred: no-op `CREATE TABLE IF NOT EXISTS` schema
trap + sticky A/B assignment, caught by a booting smoke test), a holding-company doc repo
(sacred: `pipeline.csv` source-of-truth + legal callouts), this skill library (sacred:
INDEX↔files bijection), and a multi-site web repo (sacred: language-folder parity +
honest placeholder stubs). Each got a different contract and a different `check.mjs`, and
in each the validator was proven to fail on a deliberately broken scratch copy before the
PR was opened. The diagnosis differed every time; the procedure did not — which is why it
is written down here rather than re-derived per repo.

The skill was then itself tested end-to-end: a fresh agent, given only this file and a
synthetic podcast-feed repo with a planted trap (a `Date.now()` guid fallback in the
build script, documented consequence buried in the README), independently diagnosed the
guid-immutability invariant plus two the author hadn't planted, invented a committed
guid ledger to make "never changes" checkable in CI, and verified with eleven negative
scenarios plus a happy-path control. Its feedback produced the "Fence, don't fix" rule,
the generator/ledger/CI-fallback clauses in steps 4–5, and the happy-path control in
step 6.
