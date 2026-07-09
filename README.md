# Skill Library — Agentic Coding Handoff

A handoff document set written by a departing principal engineer (an AI
coding agent) for the team that stays behind — specifically for engineers
and less capable models who will do the same kind of work without the same
depth of judgment. It captures the working disciplines the author actually
used, written so they can be followed mechanically rather than re-derived
from experience.

## What's in here

Everything lives in [`skills/`](skills/): 17 skill files plus an index.

- **[`skills/INDEX.md`](skills/INDEX.md)** — start here. Ranks all 17
  skills by quality bought per token spent reading, and tells you which to
  read in full versus which to look up on demand.
- **17 skill files** — one discipline each: scoping requests, planning
  before editing, verifying work instead of asserting it, judging blast
  radius before irreversible actions, root-cause debugging, delegating to
  subagents, multi-agent orchestration, building end-to-end systems
  (spec-first, parallel executor builds, staged integration), tool
  selection, communication, code minimalism, resolving ambiguity,
  context/token budgeting, GitHub/PR conduct, security boundaries, async
  scheduling, and a consolidated checklist of failure patterns that cost
  real time.

## Anatomy of a skill file

Every skill follows the same shape, on purpose:

1. **Why this exists** — the failure mode the skill prevents, so you know
   when it applies without being told.
2. **Rules** — numbered, imperative, followable without inferring intent.
   Wherever the original author used judgment, the rule they were following
   is written down explicitly.
3. **Mechanical checklists / decision tables / code shapes** (where the
   rules alone assume judgment) — something to execute literally.
4. **Worked example** — a real, checkable event from the session that
   produced this library, not an invented anecdote. Where an example
   couldn't be tied to a real event, the file says so.

## How to use this library

- **New to this kind of work, or the task is high-stakes/ambiguous:** read
  skills 1–7 in INDEX order before starting.
- **Mid-task, about to do something specific:** jump straight to the
  matching file — delegating work → `delegating-to-subagents.md`, opening
  a PR → `github-pr-discipline.md`, about to run something destructive →
  `blast-radius-and-confirmation.md`.
- **Before any high-stakes turn:** skim `failure-patterns.md` like a
  pre-flight checklist. Recognizing "this is pattern #6" mid-mistake is
  faster than reconstructing the right instinct from scratch.
- **Don't memorize.** The point of the files is that you can reference
  them; holding all 17 in working memory defeats the purpose.

## Provenance — why these skills and not codebase conventions

This repository was empty when the handoff task arrived, so there was no
code history to mine for project-specific conventions. With the owner's
explicit direction, the library instead documents the operating disciplines
of the agentic coding session that produced it — how the agent planned,
verified, scoped, debugged, and decided when to ask versus assume. The
worked examples cite real moments from that session (the empty-repo
discovery itself is the worked example in `scoping-the-ask.md`).

That origin makes the library general rather than project-specific: the
skills apply to agentic software work in any repository, and they are
designed to be extended. When this repo grows a real codebase, add
project-specific skills alongside these and re-rank INDEX.md.

## Maintaining the library

- Keep each skill under roughly a page. If a skill outgrows that, it's two
  skills.
- Every rule must state its *why* — what breaks without it. A rule that's
  just a preference doesn't earn a slot.
- Worked examples must be real and checkable. A plausible invented anecdote
  is worse than no example, because it teaches confident fabrication.
- When you add or remove a skill, update INDEX.md and re-rank — the index
  is the contract that keeps the library skimmable.
