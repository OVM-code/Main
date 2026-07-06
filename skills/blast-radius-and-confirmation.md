# Blast Radius and Confirmation

## Why this exists

Most actions in a coding session are free to retry. A small number are not:
they destroy work, become visible to other people, or touch systems outside
your local sandbox. The entire discipline here is a single classification
step performed *before* every action that isn't obviously a local file edit.

## Rules

1. **Classify every action before running it:**
   - *Local and reversible* (edit a file, read, run tests, `git diff`) → just
     do it.
   - *Hard to reverse* (`git push --force`, `git reset --hard`, amending
     published commits, `rm -rf`, dropping a table, downgrading a dependency)
     → confirm first, every time, regardless of prior approvals.
   - *Visible to others / shared state* (pushing code, opening/closing a PR,
     commenting on an issue, sending a message, modifying CI config,
     modifying shared infra) → confirm first.
2. **One approval does not imply standing approval.** If a user approves a
   `git push` once, that is not blanket permission to push again later in the
   same session without asking — approvals are scoped to the specific action
   in the specific moment, unless durable instructions (a CLAUDE.md, explicit
   "you can always do X") say otherwise.
3. **Never bypass a safety mechanism to make an obstacle disappear.**
   `--no-verify`, `--no-gpg-sign`, disabling TLS verification, deleting a
   lockfile that's blocking you — these remove the symptom and leave the
   actual problem (a failing hook, an untrusted cert, a legitimate lock)
   unsolved. Find out why the guard exists before you consider going around
   it, and only go around it if the user explicitly asks.
4. **Before any command that could discard uncommitted work
   (`checkout`/`restore`/`reset`/`clean`, `rm -rf` inside a repo, restoring a
   snapshot), run `git status` first.** If it shows anything, stash it
   (`-u` for untracked too) or commit it before proceeding — don't discard
   silently on the assumption it was scratch work.
5. **Prefer new commits over amending.** Amending rewrites history that might
   already be shared; a new commit is always safe to add. Only amend when the
   user explicitly asks for it.
6. **When staging broadly (`git add -A`/`.`), re-check what actually got
   staged** (`git status` / `git diff --staged`) before committing — broad
   adds pick up files you didn't mean to include, and some of those might be
   credentials.
7. **Match the scope of the action to what was actually authorized.** "Push
   this branch" is not "push and open a PR" is not "push, open a PR, and
   merge it." Each of those is a separate authorization boundary.

## Worked example (this project)

The governing instructions for this session spell this out concretely: never
force-push to main without explicit request, never skip hooks or bypass
signing unless asked, always create a new commit rather than amend, always
run `git status` before a destructive git command, and — specifically for
this task — "do NOT create a pull request unless the user explicitly asks for
one," even though pushing a branch and opening a PR feel like one continuous
"ship it" motion to a less careful reader. The two are different
authorization boundaries and must be treated as such.
