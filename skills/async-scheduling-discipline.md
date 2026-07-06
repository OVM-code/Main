# Async and Scheduling Discipline

## Why this exists

Long-running or externally-paced work (CI, background agents, deploys)
tempts a lazy pattern: poll on a short fixed interval until it's done. That
pattern is expensive (repeated cache misses, wasted turns) and doesn't scale
past one thing being watched. The discipline is to match the wait mechanism
to what's actually being waited on.

## Rules

1. **Never poll harness-tracked background work with a sleep loop.** If
   something you started will notify you on completion, waiting for that
   notification is free; polling it is pure waste. Only build an explicit
   poll loop for state the system genuinely cannot push to you (an external
   CI run, a remote queue).
2. **Pick wait duration based on a cache-lifetime boundary, not round
   numbers.** Sub-5-minute waits stay cheap because context stays warm;
   anything from five minutes to an hour pays a one-time reload cost — so if
   you're going to wait past the short window, commit to a real wait (tens
   of minutes) rather than parking right at the boundary, which pays the
   expensive cost without buying a correspondingly longer wait.
3. **Default idle check-ins to a long interval (tens of minutes), not a
   short one**, when there's no specific signal to watch — the human can
   always interrupt sooner if they need to.
4. **A recurring watch (a PR subscription, a monitoring loop) isn't finished
   just because you set it up.** It ends when its actual terminal condition
   is reached (merged, closed, resolved) — schedule your own fallback
   check-ins to cover states that don't arrive as push notifications, and
   stop the moment the human says to stop.
5. **Don't manufacture urgency with tight polling when the underlying process
   is known to be slow.** If a step reliably takes several minutes, checking
   every few seconds just burns turns restating "still waiting" — space
   checks to roughly match the process's own pace.

## Decision table — what am I waiting on?

| Waiting on | Correct mechanism |
|---|---|
| Background work the harness tracks (subagent, background command, workflow) | Nothing — you'll be re-invoked when it finishes. Schedule only a *long* fallback (20+ min) in case it hangs. |
| External state that changes in minutes (a CI run, a deploy in progress) | Check-ins spaced to the process's own pace, kept under the ~5-min context-cache window (e.g. every ~4 min for an 8-min CI run — two warm checks, not eight). |
| External state that changes in tens of minutes or hours (review, slow deploy, remote queue) | Commit to long check-ins, 20-30+ min apart. |
| Nothing specific — idle heartbeat on a subscription | 20-30 min. The human can always interrupt sooner. |

Never: a foreground sleep loop, or a check-in right at the cache boundary
(pays the full reload cost while buying almost no extra wait).

## Worked example (this project)

The scheduling tooling available in this environment enforces rule 2
structurally: it clamps wait durations to a fixed range and explicitly warns
against picking a value right at the cache-lifetime boundary — "the
worst-of-both" — steering instead toward either staying comfortably under it
(for something like a live CI run) or committing to a genuinely long wait
(for something with no reason to check back sooner). The same tooling also
states outright: don't schedule a short wake-up just to poll for background
work the harness already tracks and will notify you about automatically.
