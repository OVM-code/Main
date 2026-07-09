---
name: generate-user-manual
description: Generate a clear, complete USER_MANUAL.md for any repository — explains what the repo is, how to use everything in it, and how to maintain it, calibrated to a chosen audience. Use when someone asks for a user manual, usage guide, or "how do I use this repo" documentation.
---

# Generate a User Manual for a Repository

You are producing a `USER_MANUAL.md` for the repository you are currently
in (or a repository the user names). The manual must let its intended
reader use **everything** in the repo without asking anyone for help.

This skill is reusable: copy this folder into any repo's
`.claude/skills/`, or into `~/.claude/skills/` to make it available in
every project. It also works as a plain prompt — paste the "Process" and
"Manual template" sections below into any capable AI assistant along with
access to the repo.

## Step 0 — Ask before writing (unless already answered)

Ask the user, with concrete options:

1. **Audience** — technical users, mixed/non-technical readers, or AI
   agents? This changes vocabulary, how much is explained from scratch,
   and whether a glossary is needed.
2. **Scope** — the whole repo, or a specific part?
3. **Where it lives** — committed to the repo (default: `USER_MANUAL.md`
   at the root), or delivered separately?

If the user already answered these, do not re-ask.

## Process

1. **Inventory everything.** List every file and directory. Read the
   README, any docs, config files (`package.json`, `pyproject.toml`,
   `Makefile`, CI workflows, `.claude/`), and enough source to understand
   what each part is for. Small repo: read it all. Large repo: read all
   entry points and docs fully, sample the rest, and say in the manual
   what you sampled.
2. **Classify the repo.** Library, application, CLI, documentation set,
   infrastructure, mixed? The classification decides which manual
   sections apply (a docs-only repo has no "installation" section; an app
   has no "how to read these documents" section).
3. **Find every "thing a user can do."** Installing, running, testing,
   configuring, reading, extending, contributing, releasing. The manual
   must cover each one it finds — "everything in the repo" is the
   contract.
4. **Write to the template below**, calibrated to the audience:
   - *Non-technical/mixed*: define every term of art on first use or in a
     glossary; assume no tools installed; give click-paths (GitHub web UI)
     as well as command lines.
   - *Technical*: skip basics, keep commands copy-pasteable, lead with
     the fastest path.
   - *AI agents*: front-load a machine-usable map (paths, entry points,
     invariants), state rules imperatively, and keep it loadable as
     context in one read.
5. **Verify against the inventory.** Walk the file list from step 1 and
   confirm every file/directory is either covered by the manual or
   deliberately excluded with a stated reason. Check every relative link
   resolves. Check every command against the repo's actual scripts/docs —
   never invent a command you haven't seen defined.

## Manual template

Include the sections that apply; omit the ones that don't. Keep the
order.

```markdown
# <Repo name> — User Manual

One-paragraph plain-language answer to "what is this and why would I
use it?"

## Who this manual is for
## What you need before starting        <- prerequisites, or "nothing but a browser"
## Map of the repository                 <- tree + one line per file/dir
## Getting started                       <- the shortest path to first value
## How to use <each major capability>    <- one section per thing a user can do
## Glossary                              <- only for non-technical audiences
## Maintaining and extending             <- how to add/change things without breaking conventions
## FAQ / Troubleshooting                 <- real questions the repo's shape invites
```

## Quality bar

- A reader in the stated audience can go from zero to using every part
  of the repo with no other source.
- Every claim is checkable against the repo as it exists — no invented
  commands, files, or URLs.
- Plain sentences over fragments; define jargon before using it.
- The map covers 100% of the repo's top-level contents, explicitly.
- State what the manual does NOT cover, if anything.
