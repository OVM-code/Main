# Delegating to Subagents

## Why this exists

A subagent starts with zero memory of your conversation. Every piece of
context it needs must be in the prompt you hand it, or it will guess — and a
subagent's guess is invisible to you until its result comes back wrong. The
entire skill is: write the prompt as if briefing a competent stranger who
just walked in, because that's literally what's happening.

## Rules

1. **Never delegate understanding.** Don't write "based on the research, fix
   the bug" or "implement what makes sense" — that pushes the synthesis step
   onto the subagent. Do the synthesis yourself, then hand the subagent a
   concrete instruction: which file, which line, what specifically to
   change and why.
2. **State what you're trying to accomplish and why, not just the immediate
   step.** A subagent that understands the goal can make good judgment calls
   on the parts you didn't spell out; one that only gets the literal
   instruction cannot.
3. **Include what you've already ruled out.** If you already know approach A
   doesn't work, say so — otherwise the subagent may burn its whole budget
   rediscovering that.
4. **Match the tool to the job:**
   - Known target (a specific file, a specific symbol) → use `Read`/`Grep`
     directly, don't spin up an agent.
   - Open-ended search across the codebase → a read-only explore-type agent.
   - Multi-step task that needs judgment but not deep back-and-forth →
     a general-purpose agent, briefed fully, run in the background if you
     don't need the answer immediately.
   - Deterministic fan-out/fan-in across many independent items, with
     verification stages → a workflow, not a hand-rolled loop of agent calls
     (see `workflow-orchestration-patterns.md`) — and only when the human
     actually asked for that scale of orchestration.
5. **Don't duplicate a subagent's work.** If you handed research to an agent,
   don't also run the same searches yourself while waiting — that's wasted
   effort in both directions.
6. **Trust but verify.** A subagent's summary describes what it *intended* to
   do, not necessarily what it *did*. Before reporting its work as finished,
   check the actual diff or output it produced.
7. **State explicitly whether you want research or an implementation.** A
   fresh agent has no way to infer intent from a conversation it never saw —
   say "just investigate and report" or "write the code" outright.

## Worked example (this project)

The instructions governing this session describe an anti-pattern directly:
"Terse command-style prompts produce shallow, generic work," contrasted with
a good example where a request for "what's left to ship this branch?" gets
expanded into an explicit checklist (uncommitted changes, commits ahead of
main, whether tests exist, whether a specific named gate is wired up) plus an
explicit length cap ("under 200 words") — because the terse version invites
the subagent to guess at what "ready to ship" even means for this particular
project.
