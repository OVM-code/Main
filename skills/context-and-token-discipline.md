# Context and Token Discipline

## Why this exists

Context is a shared, shrinking resource across a whole session, and tokens
spent on unnecessary exploration or verbose output are tokens unavailable
later for the part of the task that actually needs depth. This isn't about
being terse for its own sake — it's about spending the budget where it
changes the outcome.

## Rules

1. **Don't re-derive facts already established in the conversation.** If a
   decision was already made, or a piece of state was already checked, use
   it — don't re-run the check "just to be sure" unless something plausibly
   changed it.
2. **Don't re-read a file you just edited to confirm the edit worked.** The
   edit tool already validates against the file's current content and
   fails loudly if something's wrong; a redundant read burns context to
   confirm something you already have evidence for.
3. **Push heavy exploration into a subagent when it would otherwise flood
   your own context with search noise.** The point of delegating research
   isn't just parallelism — it's keeping raw grep/read output out of the
   main conversation, so only the synthesized answer lands there.
4. **When retrieving from an external source (docs, MCP tools, paginated
   APIs), pull only what the task needs**, in small batches, rather than
   dumping everything and filtering after the fact.
5. **Use scratch space for intermediate files, not the conversation.**
   Working files, temporary scripts, and intermediate outputs belong in a
   dedicated scratch directory — keeping them out of tracked project files
   and out of the context you re-read on every turn.
6. **When a task has an explicit token or effort budget, treat it as a hard
   ceiling for planning purposes, not a soft target** — decide fleet size or
   loop depth against the budget up front, rather than spending freely and
   hoping it fits.
7. **Trust that prior context will be summarized, not lost, as the
   conversation grows — but don't rely on the summary to preserve details
   you haven't externalized.** Anything load-bearing (a decision, a plan, a
   set of file paths) should be written down (tasks, files, commit messages)
   rather than left implicit in reasoning that summarization might compress
   away.

## Worked example (this project)

Three checkable instances from the turn that produced this library:

- **Batched independent calls (rule: parallelize, don't serialize):** the
  session's first investigation ran `git log --all`, `git branch -a`, and
  `git ls-remote origin` combined into single shell invocations rather
  than one command per turn — same information, a third of the round trips.
- **No redundant re-reads (rule 2):** after each of the 17 Writes, the
  harness confirmed the file state was current; not one file was re-read
  afterward. The single `wc -l skills/*.md` before committing was *new*
  information (a cross-file completeness check no individual Write result
  could provide), not a re-check of content already in context — that's
  the line between verification and reassurance.
- **Files written once, to their final destination (rule 5):** the skill
  files went directly into `skills/`, not drafted in scratch and copied
  over, because they *are* the deliverable. Scratch space is for
  intermediates; routing the deliverable through it would have doubled the
  write cost for nothing.
