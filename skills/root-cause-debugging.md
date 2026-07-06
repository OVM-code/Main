# Root-Cause Debugging

## Why this exists

When something blocks progress, there are always two paths: make the
blocker go away, or understand why it's there and fix the actual cause. The
first path is always faster in the moment and almost always more expensive
later, because the blocker was usually protecting against something real.

## Rules

1. **When you hit a failure, ask "why does this exist" before "how do I get
   past it."** A failing pre-commit hook, a permission denial, a lockfile, a
   type error, a flaky test — each is a symptom pointing at a cause. Silencing
   the symptom (skip the hook, delete the lock, add `any`, retry until green)
   leaves the cause in place for the next person to hit.
2. **If the user denies a tool call, do not retry the identical call.** Stop
   and think about *why* it might have been denied — wrong scope, wrong
   target, insufficiently explained — and adjust the approach or ask, rather
   than re-submitting and hoping for a different answer.
3. **Don't retry a failing command in a sleep loop hoping it self-resolves.**
   If a command fails, diagnose why before re-running it. Repetition without
   a changed hypothesis is not debugging, it's stalling.
4. **Reproduce before you theorize.** Read the actual error text, the actual
   log line, the actual stack trace. A plausible-sounding cause that you
   didn't confirm against the real output is a guess wearing a diagnosis's
   clothes.
5. **When a blocker turns out to be legitimate and out of scope, say so
   instead of quietly working around it.** "This CI failure is a pre-existing
   flake unrelated to my change, and here's why I believe that" is a valid,
   honest outcome — silently disabling the check is not.
6. **Escalate to the human the moment a fix requires judgment you don't
   have**, e.g. a reviewer comment admits multiple valid interpretations, or
   the fix touches something architecturally significant. Guessing and
   shipping is worse than a 30-second clarifying question.

## Worked example (this project)

The GitHub PR-babysitting instructions in this environment draw exactly this
line: on a CI failure, the correct loop is re-diagnose → identify the actual
cause → fix or re-run → push, repeated until green — not "silence the check"
and not "give up after one try." And the instructions are explicit that
`--no-verify` and disabling TLS verification are off the table even when
they would make an annoying blocker disappear immediately — the task
description for this very environment says outbound HTTPS failures should be
diagnosed via the proxy status endpoint, never worked around by disabling
verification.
