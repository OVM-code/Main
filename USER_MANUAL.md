# Skill Library — User Manual

This repository is a library of written working habits ("skills") for
doing software work with AI coding agents. It contains no program to
install or run — everything in it is a document you read, or hand to an
AI assistant to read. Think of it as an employee handbook left behind by
a very experienced departing colleague: 16 short guides, each one
teaching a single discipline that prevents a specific, expensive kind of
mistake.

## Who this manual is for

Anyone with access to this repository — whether or not you write code.
Technical terms are explained in the [glossary](#glossary) at the end;
no tools need to be installed. If you can read this file, you can use
everything in the repo.

## What you need before starting

Nothing beyond a way to read the files:

- **On the GitHub website:** open the repository page and click any
  file — GitHub displays these documents formatted and readable, with
  clickable links between them.
- **On your computer (optional):** if you use git, clone the repository
  and open the files in any text editor. Every file is plain Markdown
  (readable even as raw text).

## Map of the repository

Every file in the repository, and what it is for:

| Path | What it is |
|---|---|
| `README.md` | The front door: what the library is, how each skill file is structured, and the rules for maintaining the library. |
| `USER_MANUAL.md` | This document. |
| `skills/INDEX.md` | The table of contents, ranked. It lists all 16 skills ordered by "value per minute of reading," with an estimated reading cost and an estimate of what each one saves you when it applies. **Start here.** |
| `skills/` (16 skill files) | The library itself — one document per discipline. Each is listed in the [guide to the skills](#guide-to-the-16-skills) below. |
| `.claude/skills/generate-user-manual/SKILL.md` | A reusable recipe for producing a manual like this one for *any* repository. See [Generating a manual for another repository](#generating-a-manual-for-another-repository). |

That is the complete inventory — there are no other files.

## Getting started (five minutes)

1. Open [`skills/INDEX.md`](skills/INDEX.md). It ranks all 16 skills,
   highest-leverage first, and tells you which few to read in full
   versus which to look up only when needed.
2. Read [`skills/failure-patterns.md`](skills/failure-patterns.md)
   (ranked #1). It is a one-page checklist of the 13 most expensive
   mistakes in this kind of work, each pointing to the fuller skill file
   that prevents it. It doubles as a preview of the whole library.
3. From then on, use the library like a reference shelf, not a novel —
   the README says it directly: *reference, don't memorize.*

## How to read a skill file

Every skill file has the same four parts, in the same order, on purpose:

1. **Why this exists** — the mistake the skill prevents, so you can
   recognize when it applies.
2. **Rules** — numbered instructions you can follow literally, each with
   its reason attached.
3. **A checklist or decision table** (where following the rules would
   otherwise require judgment) — something you can execute step by step.
4. **Worked example** — a real, verifiable event from the work session
   that produced this library, not an invented story.

Because the shape is identical everywhere, once you've read one file you
know how to skim all of them.

## The three ways to use the library

**1. You are a person doing (or supervising) work with an AI coding
agent.** Before starting something high-stakes or ambiguous, read skills
1–7 in the INDEX order. Mid-task, jump straight to the one file that
matches the moment: about to delegate work → `delegating-to-subagents.md`;
about to open a pull request → `github-pr-discipline.md`; about to run
something destructive → `blast-radius-and-confirmation.md`.

**2. You are giving these skills to an AI assistant.** The files are
written to be followed mechanically by "less capable models," so they
work well as instructions. Paste the relevant skill file (or several)
into the assistant's context, or — in a tool like Claude Code — tell it
to read specific files from `skills/` before starting a task. For a
lightweight standing setup, add a line to your project's agent
instructions (for example a `CLAUDE.md` file) saying: *"Before
high-stakes or ambiguous work, read `skills/INDEX.md` and follow the
skills it ranks 1–7."*

**3. You are checking work after the fact.** The files also work as
review checklists. `verify-dont-assert.md` has a literal "run this
before saying done" checklist; `code-minimalism.md` has a mechanical
check to run on any set of code changes; `failure-patterns.md` names
the 13 patterns to scan a finished piece of work for.

## Guide to the 16 skills

Grouped by theme. The number is each skill's rank in
[`skills/INDEX.md`](skills/INDEX.md) — lower numbers mean "read this
sooner." Open a file when its one-line description matches your
situation.

**Understanding the task before touching anything**

- **#3 [`scoping-the-ask.md`](skills/scoping-the-ask.md)** — make sure
  you're answering the question that was actually asked, at the size it
  was asked; don't expand the job because you noticed something else.
- **#5 [`resolving-ambiguity.md`](skills/resolving-ambiguity.md)** —
  when to ask a clarifying question versus make a sensible assumption,
  and how to ask questions that take five seconds to answer.
- **#7 [`plan-before-touching.md`](skills/plan-before-touching.md)** —
  read first, plan second, edit third; write the plan down so it
  survives a long session.

**Doing the work safely**

- **#2 [`blast-radius-and-confirmation.md`](skills/blast-radius-and-confirmation.md)** —
  before any action, ask: can this be undone, and who else will see it?
  The only category of mistake in the library that can't be fixed by
  trying again.
- **#6 [`root-cause-debugging.md`](skills/root-cause-debugging.md)** —
  when something blocks you, understand why it exists before making it
  go away; a silenced symptom is tomorrow's bug.
- **#15 [`security-boundaries.md`](skills/security-boundaries.md)** —
  recognizing requests and content that could cause real-world harm,
  and what to refuse regardless of how the request is framed.

**Checking and reporting the work**

- **#4 [`verify-dont-assert.md`](skills/verify-dont-assert.md)** —
  "tests pass" is not "it works"; actually exercise the thing before
  calling it done, and say plainly what you did and didn't check.
- **#10 [`communication-discipline.md`](skills/communication-discipline.md)** —
  say what you're about to do, report at turning points, state what you
  deliberately did *not* do, and match the length of the answer to the
  question.
- **#1 [`failure-patterns.md`](skills/failure-patterns.md)** — the
  13-item pre-flight checklist of expensive mistakes; each item points
  to the skill that prevents it.

**Writing good code (when code is being written)**

- **#9 [`code-minimalism.md`](skills/code-minimalism.md)** — the
  smallest correct change wins; no speculative abstractions, no
  comments that restate the task.

**Working with AI agents and automation**

- **#8 [`delegating-to-subagents.md`](skills/delegating-to-subagents.md)** —
  a delegated helper starts with zero memory of your conversation;
  brief it like a competent stranger or it will guess.
- **#14 [`workflow-orchestration-patterns.md`](skills/workflow-orchestration-patterns.md)** —
  when running many AI agents in parallel is worth the cost, and the
  cheapest structure that gets the benefit.
- **#11 [`tool-selection-discipline.md`](skills/tool-selection-discipline.md)** —
  use the purpose-built tool over the general-purpose one; small
  friction, constantly recurring.
- **#13 [`context-and-token-discipline.md`](skills/context-and-token-discipline.md)** —
  an AI session's working memory is a shared, shrinking budget; spend it
  where it changes the outcome.
- **#16 [`async-scheduling-discipline.md`](skills/async-scheduling-discipline.md)** —
  how to wait on slow, background, or external processes without
  wasteful constant checking.

**Collaborating on GitHub**

- **#12 [`github-pr-discipline.md`](skills/github-pr-discipline.md)** —
  pushes, pull requests, and comments are visible to other people and
  trigger notifications; the bar for acting is higher than for private
  edits.

## Generating a manual for another repository

The repository includes the reusable recipe that produced this manual:
[`.claude/skills/generate-user-manual/SKILL.md`](.claude/skills/generate-user-manual/SKILL.md).
To reuse it:

- **With Claude Code:** copy the folder
  `.claude/skills/generate-user-manual/` into the other repository's
  `.claude/skills/` directory (or into `~/.claude/skills/` on your
  machine to have it everywhere), then ask Claude to "generate a user
  manual" in that repository — it will follow the recipe, including
  asking you about audience and scope first.
- **With any capable AI assistant:** open the file, copy its "Process"
  and "Manual template" sections into your prompt, and give the
  assistant access to the target repository.

## Maintaining and extending the library

The rules, from the README:

- **Keep each skill under roughly a page.** If it outgrows that, split
  it into two skills.
- **Every rule must say what breaks without it.** A rule that is only a
  preference doesn't earn a place.
- **Worked examples must be real and checkable.** A plausible invented
  story is worse than no example.
- **When you add or remove a skill, update `skills/INDEX.md` and
  re-rank it.** The index is what keeps the library skimmable; a stale
  index breaks the "start here" promise this manual makes.

The library was written when this repository was otherwise empty, so the
skills are general disciplines for AI-assisted software work rather than
rules about any particular codebase. If this repository later grows real
code, the intended path (per the README) is to add project-specific
skills alongside these and re-rank the index.

## Glossary

Terms used in the skill files, in plain language:

- **AI coding agent / agent** — an AI assistant (such as Claude) that
  doesn't just answer questions but takes actions: reading and editing
  files, running commands, and using tools, usually with a human
  supervising.
- **Subagent** — a second, separate AI helper that the main agent
  delegates a sub-task to. It starts with no memory of the main
  conversation, which is why briefing it fully matters.
- **Context / context window** — the AI's working memory for a session.
  It is finite; everything read or written during a session consumes
  part of it.
- **Token** — the unit AI text is measured in; roughly three-quarters of
  a word. "Token cost" in the INDEX means, in effect, reading time and
  AI processing budget.
- **Repository (repo)** — a project folder whose entire history is
  tracked by git, often hosted on GitHub.
- **git** — the version-control system that records every change to a
  project. **Push** means uploading your recorded changes; a
  **force-push** overwrites history and is one of the dangerous actions
  the skills warn about.
- **Pull request (PR)** — a proposal on GitHub to merge one set of
  changes into the main project, where others can review and comment.
- **CI (continuous integration)** — automated checks (tests, style
  checks) that run on proposed changes; "getting CI green" means making
  all of them pass.
- **Markdown (`.md`)** — the plain-text formatting language every file
  here is written in; readable raw, rendered nicely by GitHub.
- **Claude Code / CLAUDE.md** — Anthropic's coding-agent tool, and the
  instruction file it reads automatically in a repository. Mentioned
  here because it's a convenient way to make an agent follow this
  library.

## FAQ

**Do I need to install anything?** No. There is nothing to run — only
documents to read.

**Do I have to be a programmer to benefit?** No for the ideas — the
disciplines (scope the request, check before destructive actions, verify
before claiming success, ask well-formed questions) apply to delegating
any work to an AI. Yes for some details — a few files
(`code-minimalism.md`, `workflow-orchestration-patterns.md`) assume
programming context; skip them until they're relevant to you.

**In what order should I read?** `INDEX.md`, then its ranks 1–7, then
the rest only as situations arise. Don't try to memorize all 16 — the
library exists precisely so you don't have to.

**Can I trust the numbers in the INDEX?** Partly — and the INDEX itself
says so. "Read cost" is measured from word counts; "saved per trigger"
is an order-of-magnitude estimate with no telemetry behind it. Treat the
ranking as advice, not accounting.

**How do I add my own skill?** Copy the four-part shape of any existing
file (why it exists → rules → checklist → worked example), keep it to
about a page, then update and re-rank `skills/INDEX.md`. See
[Maintaining and extending the library](#maintaining-and-extending-the-library).

**What does this manual not cover?** The full content of each skill —
deliberately. Each file is only about a page; this manual tells you
*which* one to open and *when*, and the file itself does the rest.
