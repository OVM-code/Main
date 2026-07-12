# Fable in Claude Chat & Projects

The `.claude/agents/` definitions only work inside Claude Code sessions on
this repository. This folder is the portable version of the same system,
packaged for **claude.ai** — regular chat and Projects — so the Fable
advisor, researcher, planner, and critic are available anywhere.

## Files

- **`fable-suite.md`** — all four roles in one instruction set, with a
  router that picks the right mode from your message. Use this if you want
  a single "Fable" project for everything.
- **`fable-advisor.md`**, **`fable-researcher.md`**, **`fable-planner.md`**,
  **`fable-critic.md`** — standalone instructions for one role each. Use
  these if you prefer a dedicated project per role.

## Setup (recommended: one Fable project)

1. On [claude.ai](https://claude.ai), create a new **Project**, name it
   "Fable".
2. Open the project's **Instructions** (custom instructions) and paste the
   full contents of `fable-suite.md`.
3. Upload the `skills/` files from this repository as **project
   knowledge** — at minimum `verify-dont-assert.md`,
   `scoping-the-ask.md`, `resolving-ambiguity.md`,
   `plan-before-touching.md`, and `failure-patterns.md`. The instructions
   reference them by name.
4. Enable **web search** for the project if your plan supports it — the
   researcher and critic roles depend on it; without it they will say so
   and mark all findings as unverified.

Every chat in that project now starts as Fable. Say what you need in plain
language ("help me decide X", "research Y", "plan Z", "poke holes in
this") — the suite instructions route to the right role — or name the role
explicitly.

## Alternative: one project per role

Same steps, but create up to four projects and paste one role file into
each. Sharper behavior per project, at the cost of switching projects when
an engagement moves from research to decision to plan.

## Using it in plain chat (no Project)

Paste the contents of a role file (or the suite) as the first message of
any conversation, prefixed with: "Adopt these instructions for this whole
conversation:". Works on any plan; you lose the persistent knowledge
files, so the skill-library grounding is weaker.

## Keeping the two systems in sync

The files here are adaptations, not copies, of `.claude/agents/*.md` —
chat has no filesystem, so "write the deliverable to a file" becomes
"produce the deliverable as a formatted document/artifact", and
"return clarifying questions as your output" becomes "ask and wait". When
you change a role's rules, change it in both places; the rules are the
shared core, only the delivery mechanics differ.
