---
name: elaborate
description: Turn a minimal prompt into a fully-specified, ready-to-execute prompt for Opus or Sonnet by questioning the user until a completeness checklist is satisfied. Use when the user invokes /elaborate or explicitly asks to have a terse prompt elaborated/expanded through questioning. Do NOT trigger on ordinary terse messages the user hasn't asked to elaborate.
---

# Elaborate a minimal prompt

You are running the interactive counterpart of
`skills/prompt-elaboration-discipline.md`. The user's terse prompt is in the
invocation arguments (or their message). Your job: fill the completeness
checklist through structured questioning, then produce a standalone prompt
and let the user decide what happens with it. This runs in the main
conversation — do not delegate the questioning to a subagent (subagents
cannot ask the user anything).

## Procedure

**Step 1 — Harvest before asking.** Read the terse prompt. Check the
conversation, repo files, and anything it references for answers to the
checklist slots below. Fill every slot you can without the user. Never ask
a question whose answer is already on disk or earlier in this conversation.

**Step 2 — Question rounds.** For the remaining empty slots, use
AskUserQuestion: up to 4 questions per round, each closed-ended with 2-4
concrete options, your recommended option first and marked "(Recommended)".
Group related slots into one question where natural. Typical runs take 1-3
rounds; ask another round only for slots still empty. If the user answers
"you decide" (or picks Other with that intent), record the slot as
agent's-choice and write your chosen default into the final prompt — do not
re-ask.

**Checklist — questioning stops only when every slot is filled or marked
agent's-choice:**

- **Goal** — what does done look like, in one sentence
- **Context / inputs** — files, data, prior work, environment it builds on
- **Constraints** — what must not change; scope boundaries
- **Output shape** — code / PR / report / plan / prompt text; format, length
- **Success criteria** — how the result gets verified
- **Model tier + effort** — per `skills/model-selection-discipline.md`:
  fully-specified familiar-shape work → Sonnet; wide-open judgment,
  architecture, or hard debugging → Opus; state the reason in one line.
  (Recommend one — this slot is usually agent's-choice unless the user
  cares.)

**Step 3 — Assemble the prompt.** Write it as a briefing for a competent
stranger with zero memory of this conversation, following
`skills/delegating-to-subagents.md`. Use this shape:

```
## Task
<goal, one paragraph: what and why>

## Context
<inputs, files, environment — everything the executor needs, inlined or
pointed at precisely; nothing that requires this conversation>

## Instructions
<concrete numbered steps or requirements; research vs implementation
stated outright>

## Constraints
<what must not change; ruled-out approaches; scope boundaries>

## Output
<exact shape, format, length of the deliverable>

## Verification
<how the executor should check its own work before reporting; what
"done" evidence looks like>

## Assumptions made on your behalf
<every agent's-choice slot and the default chosen for it>
```

Recommended executor: **<model>** at **<effort>** — <one-line reason>.

**Step 4 — Disposition (always, as a final AskUserQuestion).** Options:
run it now / hand over the prompt text / both. Elaboration is not
authorization to execute.

- **Run it now / both:** dispatch via the Agent tool with the chosen model
  (`model: "sonnet"` or `"opus"`) and the assembled prompt verbatim. When
  results return, verify them against the Success criteria slot before
  reporting (per `skills/verify-dont-assert.md`) — the subagent's summary
  is intent, not evidence.
- **Hand over / both:** deliver the prompt in a single copy-ready block,
  with nothing in it that depends on this conversation.

## Guardrails

- If the terse prompt's premise doesn't hold (target doesn't exist, task
  already done), surface that instead of elaborating a prompt built on it.
- If the elaborated task would be irreversible or outward-facing (pushes,
  PRs, messages, deletions), the Constraints section must say what the
  executor may NOT do without confirmation.
- Keep the whole exchange cheap: questioning is Steps 1-2 only — don't
  start executing mid-elaboration, and don't pad rounds with questions
  whose answer wouldn't change the prompt.
