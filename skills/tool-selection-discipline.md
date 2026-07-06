# Tool Selection Discipline

## Why this exists

Every general-purpose shell command has a dedicated tool that does the same
job with better permission handling, better output shaping, and fewer
surprises. Reaching for the shell out of habit is the single most common
"looks fine, works worse" mistake — it usually still works, so nobody
notices the friction it created until later.

## Rules

1. **Use the dedicated tool over its shell equivalent whenever one exists:**
   file search → the glob tool, not `find`; content search → the grep tool,
   not raw `grep`/`rg`; reading a file → the read tool, not `cat`/`head`/
   `tail`; editing → the edit tool, not `sed`/`awk`; creating a file → the
   write tool, not heredocs; talking to the user → plain text output, not
   `echo`/`printf`. Reserve the shell for things that are genuinely
   shell-only: running builds, tests, git commands, package managers.
2. **Before creating a file or directory via a shell command, verify the
   parent exists first** (a quick listing) rather than assuming and finding
   out from an error.
3. **Always quote paths that might contain spaces.** This is cheap insurance
   against a whole class of shell-splitting bugs.
4. **Don't `cd` and stay there.** Use absolute paths and let the working
   directory persist naturally; only `cd` when the user explicitly wants a
   different persistent working directory, and never prefix a git command
   with a redundant `cd <same-directory>` — it does nothing except trigger an
   extra permission prompt.
5. **For a small number of independent lookups, call the tools directly; for
   open-ended exploration likely to take more than a few queries, hand it to
   a read-only search agent instead of grinding through it turn by turn.**
   This keeps your own context from filling up with search noise.
6. **Fire independent tool calls in parallel, not sequentially.** If two
   calls don't depend on each other's output, issue them in the same
   response. Only serialize when a later call needs a value produced by an
   earlier one.
7. **When a deferred/unloaded tool might fit, look it up before assuming it
   doesn't exist or guessing its parameters.** Guessing a schema wastes a
   round trip on a validation error; looking it up costs one search call.

## Worked example (this project)

This session's own tool set enforces rule 1 structurally: there are
purpose-built Read/Edit/Write/Glob/Grep tools, and the operating instructions
say outright to avoid `find`, `grep`, `cat`, `head`, `tail`, `sed`, `awk`, and
`echo` in the shell "unless explicitly instructed or after you have verified
that a dedicated tool cannot accomplish your task" — with the dedicated tool
named for each. When investigating whether this very repository had any
history, the check used the shell (`git log --all`, `git branch -a`,
`git ls-remote`) because those are genuinely git-only operations with no
dedicated-tool equivalent — not because shell-first is the default.
