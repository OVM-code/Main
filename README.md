# Skill Library — Agentic Coding Handoff

A handoff document set written by a departing principal engineer (an AI
coding agent) for the team that stays behind — specifically for engineers
and less capable models who will do the same kind of work without the same
depth of judgment. It captures the working disciplines the author actually
used, written so they can be followed mechanically rather than re-derived
from experience.

## What's in here

Reference documentation lives in [`skills/`](skills/): 19 skill files plus
an index. One capability also has a *runnable* counterpart in
[`.claude/workflows/`](.claude/workflows/) — everything else in this repo
is a discipline for a human or agent to follow, not something that executes.

- **[`skills/INDEX.md`](skills/INDEX.md)** — start here. Ranks all 19
  skills by quality bought per token spent reading, and tells you which to
  read in full versus which to look up on demand.
- **19 skill files** — one discipline each: scoping requests, planning
  before editing, verifying work instead of asserting it, judging blast
  radius before irreversible actions, root-cause debugging, delegating to
  subagents, multi-agent orchestration, tool selection, communication,
  code minimalism, resolving ambiguity, context/token budgeting,
  **which model tier and reasoning effort a step actually needs (and how
  that choice minimizes token cost)**, GitHub/PR conduct,
  **porting an entire AI system to run on a different model** (researched
  live, not from memorized conventions), security boundaries, async
  scheduling, a consolidated checklist of failure patterns that cost real
  time, and **an explicit opt-in "operator mode" contract** for users who
  want a stricter, terser default than this library ships with.
- **[`.claude/workflows/port-ai-system.js`](.claude/workflows/port-ai-system.js)**
  — the runnable version of `skills/cross-model-porting-discipline.md`.
  Invoke with `Workflow({name: 'port-ai-system', args: {sourceModel,
  targetModel, system, outputPath?}})`: it researches both models' current
  conventions live, builds a compatibility map, transforms the system, and
  adversarially verifies the result before finalizing.

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
- **About to spawn a subagent or run a workflow:** check
  `model-selection-discipline.md` first — it's the rule set for which
  model tier and reasoning effort each step actually needs, so a fan-out
  doesn't default to the most expensive option for every call.
- **Asked to make a system built for one model run on another:** read
  `cross-model-porting-discipline.md`, then invoke
  `.claude/workflows/port-ai-system.js` rather than hand-translating from
  memory — model conventions go stale fast, and the workflow's Research
  phase looks them up live for both models before anything gets rewritten.
- **A human explicitly asks for a stricter, terser operating contract:**
  read `operator-mode.md`. It's opt-in and, on one point, deliberately
  overrides `communication-discipline.md`'s default — don't apply it
  unless it was actually requested.
- **Don't memorize.** The point of the files is that you can reference
  them; holding all 19 in working memory defeats the purpose.

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
- If a skill has a runnable counterpart in `.claude/workflows/`, keep the
  two in sync — the skill file is the methodology a reader follows by hand;
  the workflow is the same methodology automated. A rule change in one that
  isn't reflected in the other is a bug, not a stylistic choice.
