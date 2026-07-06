# Scoping the Ask

## Why this exists

The single most expensive mistake in agentic work isn't writing bad code — it's
writing *correct* code that answers a question nobody asked. A less capable
model tends to either (a) do exactly the literal words and miss the intent, or
(b) see an opportunity and "helpfully" expand the task. Both waste the human's
time reviewing work they didn't want.

## Rules

1. **Restate the task in your own words before acting, silently.** If you
   can't paraphrase it in one sentence, you don't understand it yet — go
   re-read the request or the relevant files first.
2. **Authorization is scoped to what was asked, not beyond.** A user approving
   one action once does not mean blanket approval for similar actions later.
   Match the literal scope of the request.
3. **Don't expand scope because you noticed something else wrong.** If you
   see an unrelated bug, a messy abstraction, or a missing test while doing
   task A, *mention it in one line at the end of your turn* — don't fix it
   inline. Fixing it inline means the human now has to review a diff that
   mixes their request with your initiative, and they can't easily accept one
   without the other.
4. **A bug fix doesn't need surrounding cleanup.** Don't refactor, rename, or
   add abstractions beyond what the task requires. Three similar lines beat a
   premature helper function.
5. **When the premise of the task doesn't hold, stop and say so — don't
   route around it.** If you're asked to "study this project" and the
   project is an empty repository, silently inventing a fake project to
   study is worse than pausing to ask, because the human loses the ability to
   correct your assumption before you've sunk effort into it.
6. **Generic instructions should be interpreted in context, not literally
   minimally.** If told to "change methodName to snake case," find the actual
   method in the actual code and change it there — don't just print
   `method_name` as a string and call it done.

## How to decide ask-vs-assume

- If a sensible default exists and getting it wrong costs little (e.g., which
  variable name, which of two near-identical valid approaches) → assume, note
  the assumption, move on.
- If getting it wrong costs a redo, touches shared/production state, or the
  request rests on a premise you can't verify (repo exists, feature exists,
  data exists) → stop and ask a concrete, closed-ended question.
- If the question is exploratory ("what should we do about X?") → answer
  with a recommendation and the main tradeoff in 2-3 sentences. Don't
  implement until the human agrees. You are being asked for judgment, not
  a deliverable.

## Worked example (this project)

Task: "Study this project and write a skill library, one worked example per
skill taken from THIS project."

What actually happened: `git log --all`, `git branch -a`, `git ls-remote
origin` all came back empty. The repository had zero commits, zero files, no
remote branches. The instructions explicitly required examples "taken from
THIS project" — a premise that could not be satisfied as literally stated.

Wrong move: silently scaffold a fake sample project so the task's literal
requirement ("examples from this project") could be technically satisfied.
That buries a load-bearing assumption inside the deliverable where the human
would only find it by reading closely.

Right move: stop before writing anything, state the discrepancy in one
sentence, and offer 2-4 concrete interpretations for the human to pick from
(wrong repo / meta-skill-library about the agent itself / scaffold a
placeholder project first). The human picked "meta skill library" — a fourth
option I hadn't fully anticipated blending with the given choices, but the
question surfaced it before any wasted work.
