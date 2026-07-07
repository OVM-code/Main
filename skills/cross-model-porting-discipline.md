# Cross-Model Porting Discipline

## Why this exists

Porting an AI system — prompts, tool schemas, orchestration logic — from one
model to another fails in a specific, non-obvious way: the ported version
looks structurally equivalent (same sections, same instructions) but behaves
differently, because each model family has its own conventions for what a
system prompt should look like, how tools are described, how much explicit
structure it needs, and which capabilities it does or doesn't have. Memorized
knowledge of "how model family X wants prompts written" goes stale between
provider releases faster than almost any other fact in this field — a port
built from memory is a stale port wearing a plausible outfit. The runnable
counterpart to this file is `.claude/workflows/port-ai-system.js`.

## Rules

1. **Never port from memory of a model's conventions — look them up live,
   every time.** Prompting conventions, tool-calling formats, and context
   limits change between provider releases faster than a training cutoff
   tracks. Treat "I remember how family X wants prompts written" as a
   hypothesis to check against the provider's current documentation, not a
   fact to port from directly.
2. **Read the actual source system before touching it, not a summary of
   what it's supposed to do.** Same principle as `plan-before-touching.md`:
   know which sections do real work, which are boilerplate, and which
   encode a workaround for a source-model-specific quirk, before rewriting
   any of it for a different target.
3. **Separate structural translation from genuine capability gap.** Most of
   a port is mechanical — renaming a role, reformatting a tool schema,
   adjusting section markers. A minority is a real gap: the source system
   depends on something the target doesn't have (extended reasoning, a
   specific tool-use protocol, a context window it assumes). Only that
   minority needs real design judgment; don't spend judgment-tier effort on
   the mechanical majority.
4. **Every capability gap needs an explicit decision, not a silent drop.**
   If the source relies on something the target doesn't support, state
   whether you're substituting an equivalent, degrading gracefully, or
   dropping it — a silent omission produces a port that looks complete and
   isn't.
5. **A translated prompt that "reads right" for the target model is not
   verified until checked against what the target model actually does with
   it.** Structural resemblance to the target's documented conventions is
   necessary, not sufficient — `verify-dont-assert.md`'s standard for code
   applies to ported prompts too.
6. **Match tier and effort to the step, per `model-selection-discipline.md`.**
   Fetching and summarizing documentation is mechanical — the cheapest
   reliable tier, run in parallel across source and target. Deciding how to
   handle a genuine capability gap, and the final adversarial check that
   nothing broke quietly, are the two places worth paying for a stronger
   model or higher effort.
7. **Direction is symmetric.** "Port this system to run on model family Y"
   and "port this system built for Y back onto the original family" are the
   same procedure with source and target swapped — don't hardcode an
   assumption about which side is "home."

## Dimensions to compare, source vs. target

- Message roles and structure (system/developer/user/assistant, and the
  intended use of each)
- Tool/function-calling protocol (schema format, structured-output support,
  parallel tool calls)
- Context window size, and any documented behavior as it fills
- Extended-reasoning support, and how it's invoked if at all
- Multimodal input support (images, audio, documents)
- Prompt-caching or other cost/latency mechanisms that shape how a system
  should be structured
- Provider-documented style conventions (tag vs. markdown preference,
  instruction placement, typical system-prompt length)
- Known quirks per family (steerability differences, refusal patterns,
  verbosity tendencies)

## Worked example (this project)

This library's own `model-selection-discipline.md` already drew the
boundary this file generalizes: it declined to hardcode specific model IDs
or a snapshot comparison table in the same session that produced it,
because "the exact names will change" and any such table would go stale
before the file was next read. The same session's `operator-mode.md`
update handled an unverifiable third-party claim (a plugin's marketed
capabilities) by pointing at checking the live catalog instead of
asserting the marketing copy as fact. Porting an entire system to another
model multiplies that exact risk across every convention involved — a
baked-in "model X does Y" table would be stale before the next release, so
the discipline has to be "look it up now," not "here's what was true."
