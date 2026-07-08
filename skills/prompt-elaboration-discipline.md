# Prompt Elaboration Discipline

## Why this exists

A minimal prompt handed straight to an executing model produces confident
work built on guessed requirements — the same failure
`delegating-to-subagents.md` documents, except the under-briefed party is
the human's own one-line request. The fix is a deliberate elaboration step:
interrogate the human with structured questions until a completeness
checklist is satisfied, *then* write the full prompt the executing model
actually needs. This is the inverse of `resolving-ambiguity.md`'s default
triage (assume when cheap, ask when expensive): here the human has
explicitly opted into being questioned, so thoroughness of asking is the
point, not a cost to minimize. The invocable counterpart is
`.claude/skills/elaborate/SKILL.md`.

## Rules

1. **Only on explicit invocation.** An ordinary terse message gets the
   normal triage from `resolving-ambiguity.md`, not an interrogation.
   Elaboration mode is opt-in per request — auto-detecting "this prompt
   seems terse" and questioning uninvited makes you useless on quick asks.
2. **Look before you ask.** Before any question reaches the human, check
   whether the conversation, the repo, or the files already answer it. A
   question the codebase can answer is your work being pushed onto the
   human — the same line rule 1 of `resolving-ambiguity.md` draws.
3. **Ask closed-ended, batched, recommended-first.** Up to four questions
   per round, each with 2-4 concrete options and your recommended default
   listed first. The human should be able to answer a round in seconds.
   Open "what do you want?" questions push the framing work back onto them.
4. **Stop against the checklist, not against a feeling.** Questioning ends
   when every slot below is filled or explicitly marked "agent's choice" —
   typically one to three rounds. "I think I get it now" is not a stop
   condition; an unfilled slot is a question you haven't asked, and a
   filled checklist you keep questioning past is the human's time wasted.
5. **"You decide" is an answer.** When the human delegates a slot, record
   it as agent's-choice with your chosen default written into the final
   prompt — don't re-ask it later, and don't leave it silently unresolved.
6. **The output is a briefing for a competent stranger.** The final prompt
   must stand alone per `delegating-to-subagents.md`: goal and why, concrete
   instructions, constraints, what's ruled out, research vs. implementation
   stated outright, expected output shape, and how the result will be
   verified. If the elaborated prompt still needs this conversation as
   context, elaboration isn't done.
7. **The prompt names its executor deliberately.** Pick the model tier and
   effort per `model-selection-discipline.md`'s decision table and say why
   in one line — a fully-specified task with a familiar shape runs on the
   mid tier; wide-open judgment or architecture calls earn the top tier.
8. **Disposition is the human's call, every run.** End by asking whether to
   execute the prompt now, hand the text over, or both. Elaborating a
   prompt is not authorization to run it — the same boundary
   `blast-radius-and-confirmation.md` rule 7 draws between adjacent
   authorizations.

## The completeness checklist

| Slot | The question it answers |
|---|---|
| Goal | What does done look like, in one sentence? |
| Context / inputs | Which files, data, prior work, or environment does this build on? |
| Constraints | What must not change, and where are the scope boundaries? |
| Output shape | Code, PR, report, plan, prompt text? In what format, at what length? |
| Success criteria | How will the result be checked — tests, manual verification, review? |
| Model tier + effort | Which executor, at what effort, and why (one line)? |
| Disposition | Run now, hand back the prompt, or both? (always the final question) |

## Worked example (this project)

The request that produced this skill was itself a minimal prompt: "a system
that allows me to write minimalistic prompts and lets you question me until
you have all details needed." Three structural decisions were genuinely the
human's to make, so three closed-ended questions went back — output
disposition (execute / hand over / ask each time), trigger (explicit
invocation vs. auto-detect), and stop rule (checklist vs. judgment vs.
round-cap) — each with a recommended default listed first. The human
answered all three in seconds, and two of the answers (explicit-only
trigger, checklist-driven stop) are now rules 1 and 4 of this file. Had
those been guessed instead, an auto-detecting version would have violated
this library's own ambiguity-triage discipline on every terse message — a
design flaw baked in by skipping the very questioning step the system
exists to provide.
