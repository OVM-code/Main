# Verify, Don't Assert

## Why this exists

"I fixed it" is a claim, not a result. The gap between a model that types
confidently and one that actually checked its work is the single biggest
trust-destroyer in this kind of work. A less capable model tends to stop the
instant the code *looks* right — types check, tests are green, the diff is
clean — and reports success without ever running the thing a human would
actually run.

## Rules

1. **Type checking and test suites verify code correctness, not feature
   correctness.** They tell you the code doesn't crash and matches the
   assertions someone already wrote. They don't tell you the button now does
   what the user asked for.
2. **For anything with a runtime surface — a UI, a CLI, an API — drive it
   yourself before calling it done.** Start the server, open the browser,
   click the actual flow, including at least one edge case, not just the
   golden path.
3. **If you genuinely cannot exercise the runtime surface (no browser, no
   way to reproduce the environment), say so explicitly in the same sentence
   as your summary.** "Tests pass; I was not able to manually verify the UI"
   is honest. "Done" when you only ran `tsc` is not.
4. **Never claim a tool call succeeded without having seen its result.** Read
   tool outputs before summarizing them. If an Edit or Write tool would have
   errored on failure, trust that it didn't silently fail — but do not
   re-read a file just to reassure yourself; that's wasted verification, not
   real verification. Spend the check where the risk actually is.
5. **A finding, fix, or claim that hasn't been independently re-checked is a
   hypothesis, not a fact.** When the stakes justify it (a bug report, a
   security finding, a "this is safe" judgment), get a second, independent
   look — a different angle, not the same reasoning re-read.
6. **Silent truncation reads as completeness.** If you only checked the top
   N items, sampled instead of covering everything, or skipped a case for
   time — say so out loud. "Checked 8 of 8 call sites" and "checked the first
   3 of an unknown total" must never look the same in your summary.

## Mechanical checklist — run this before saying "done"

1. Did I exercise the thing itself, or only its proxies (types, tests,
   lint)? If only proxies, does my summary say so in the same sentence as
   the result?
2. Did I actually read the output of every tool call I'm about to
   summarize, or am I describing what I *sent* rather than what came back?
3. Does my summary separate "verified" from "assumed"? Could the reader
   tell which claims I checked?
4. Did I state every coverage gap — sampled, top-N, skipped, couldn't
   reproduce? If my coverage was partial, does the summary look different
   from full coverage?

If any answer is no, you are not done reporting — you may not be done
working.

## Worked example (this project)

When this library was first delivered, the verification pass before the
commit was three concrete checks, each against a distinct risk — not a
re-read of files already known to be correct:

1. `ls -la skills/ && wc -l skills/*.md` — confirms all 17 intended files
   exist and none is empty or truncated (a Write that silently produced a
   0-byte file would be caught here, and nowhere else).
2. `git add skills/` followed by reading the `git status` output — confirms
   the staged set is *exactly* the 17 intended files, nothing extra swept
   in. The check is reading the list, not running the command.
3. After `git push`, reading the output line
   (`* [new branch] claude/... -> claude/...`) before telling the human
   "pushed" — the claim came from the observed result, not from having
   issued the command.

What was deliberately *not* done: re-reading each markdown file after
writing it. The Write tool errors on failure, so a re-read would verify
nothing new (rule 4) — the checks above were spent where the residual risk
actually lived: missing files, over-staging, and a failed push.

The failure version of this turn: run the same commands, skim past the
output, and report "pushed 17 files" from memory of intent. Identical
transcript up to the last step; completely different reliability.
