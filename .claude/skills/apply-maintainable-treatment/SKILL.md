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
protecting the wrong things, which teaches confident fabrication (see
`skills/verify-dont-assert.md`, `skills/scoping-the-ask.md`). Do the diagnosis every time.

Real examples of "the sacred thing" from repos already treated — note how different each is:
record ids that must never be regenerated; `CREATE TABLE IF NOT EXISTS` that silently
ignores schema edits in production; a CSV that is the single source of truth; an index
that must stay a bijection with its files; bilingual page-parity and honest placeholders.

## Procedure

1. **Survey.** Read any existing `CLAUDE.md` / `AGENTS.md` / `README`, map the file tree,
   and identify what the repo *is*: application code, generated data, hand-maintained
   documents, static sites, config. Read enough of the actual code/data to understand how
   it is consumed and where a wrong write does damage. Do not skim.
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
   mechanically enforce every invariant from step 3. For a running application, this is a
   **smoke test** that boots the built app and exercises the real contract end-to-end, not
   just a static lint. Add a script alias (`npm run check`) if there is a manifest.
5. **Wire CI** — a `.github/workflows/*.yml` that runs the validator on every push and PR,
   needing no secrets and never touching production.
6. **Verify BOTH directions.** The validator must pass on the current repo, AND you must
   deliberately break each invariant in a throwaway copy and confirm the validator fails
   (exit 1) with a clear message. A validator never seen to fail proves nothing — this
   step is non-negotiable.
7. **Branch, commit, PR.** Work on `claude/maintainable-treatment` (or the repo's branch
   convention). The commit/PR body states what was found sacred and how it is now enforced.
   Do not merge; leave the PR for the owner.

## Mechanical checklist — before calling it done

- [ ] Contract lives in the file the repo's agents already load (`CLAUDE.md`/`AGENTS.md`).
- [ ] Every invariant has a stated *why* and a matching validator check.
- [ ] Validator is zero-dependency and runs with one command.
- [ ] Apps have a smoke test that drives real behavior, not only static checks.
- [ ] CI runs the validator on push + PR.
- [ ] Negative test done: each invariant, broken in a scratch copy, is caught (exit 1).
- [ ] Branch pushed, PR body names the sacred invariant(s); nothing merged.

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
