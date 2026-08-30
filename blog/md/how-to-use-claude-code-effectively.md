# How to Use Claude Code Effectively: CLAUDE.md, AGENTS.md, and Rules

August 2026 · Published by Amar Kumar

Developers searching for **how to use Claude Code effectively**, **what to put in CLAUDE.md**, or **Claude Code best practices** usually hit the same wall: Claude works great for one session, then forgets everything next time — or ignores instructions buried in a 400-line rules file.

Claude Code is an agent, not a chatbot. It reads files, runs shell commands, and edits your repo autonomously. The difference between a frustrating session and one you can walk away from is **project memory**: what you put in `CLAUDE.md`, how you wire `AGENTS.md`, when to use `.claude/rules/`, and how you prompt with verification loops.

This guide is a practical setup reference — file templates, what belongs where, and workflow habits that actually stick.

## Table of contents

1. [The memory stack](#memory-stack)
2. [What CLAUDE.md should contain](#claude-md)
3. [What AGENTS.md should contain](#agents-md)
4. [Path-scoped rules in `.claude/rules/`](#rules)
5. [Personal and user-level config](#personal)
6. [Essential `settings.json`](#settings)
7. [Session workflow that works](#workflow)
8. [Example repo layout](#layout)
9. [Common mistakes](#mistakes)
10. [FAQ](#faq)

## The memory stack

Claude Code loads instructions at session start. Think of it as layers — broadest first, most specific last:

| Layer | File / path | Who reads it | Loaded when |
|-------|-------------|--------------|-------------|
| Org policy | `/etc/claude-code/CLAUDE.md` (Linux) | Everyone in org | Every session |
| User prefs | `~/.claude/CLAUDE.md` | You, all projects | Every session |
| User rules | `~/.claude/rules/*.md` | You, all projects | Every session |
| Project root | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team via git | Every session |
| Personal project | `./CLAUDE.local.md` (gitignored) | Just you | Every session |
| Modular rules | `.claude/rules/*.md` | Team via git | Every session, or on demand if path-scoped |
| Subdirectory | `src/api/CLAUDE.md` | Team | When Claude reads files in that folder |
| Auto memory | `.claude/memory/` | Claude writes it | First 200 lines / 25KB per session |
| Skills | `.claude/skills/` or `~/.claude/skills/` | On invoke | Only when relevant |

**Key distinction:** `CLAUDE.md` and rules are **instructions you write**. Auto memory is **notes Claude writes** from corrections. Skills are **procedures** that load on demand — use them for multi-step workflows, not facts that should apply every session.

Run `/context` after starting a session to confirm what loaded. Run `/memory` to inspect auto memory.

## What CLAUDE.md should contain

Target **under 200 lines**. Everything in root `CLAUDE.md` loads into every session and burns context. If removing a line wouldn't cause Claude to make mistakes, cut it.

### Include

- **Build and test commands** — exact strings, not "run the tests"
- **Project layout** — where API handlers, migrations, and configs live
- **Non-obvious conventions** — things Claude can't infer from code alone
- **Git workflow** — branch naming, commit style, "never push to main"
- **Verification command** — the one check Claude should run before stopping
- **Security boundaries** — no prod credentials, no force-push, ask before destructive ops

### Exclude

- Generic advice ("write clean code")
- Full API docs (link to docs instead)
- File-by-file codebase tour (Claude can grep)
- Long tutorials (use a skill)
- Info that changes weekly (put in a skill or path-scoped rule)

### Starter template

```markdown
# Project: acme-api

## Commands
- Install: `pnpm install`
- Dev server: `pnpm dev` (port 3000)
- Test: `pnpm test`
- Lint: `pnpm lint`
- Typecheck: `pnpm typecheck`

## Layout
- `src/api/handlers/` — HTTP route handlers
- `src/db/` — Drizzle schema and migrations
- `src/lib/` — shared utilities (no business logic)

## Code style
- TypeScript strict mode; no `any` without a comment
- 2-space indent
- Prefer `async/await` over raw Promises

## Workflow
- Create a feature branch before edits
- Run `pnpm test && pnpm lint` before committing
- IMPORTANT: never commit `.env` or secrets

## Verification
After any change under `src/api/`, run:
`pnpm test src/api/`
```

### Generate a first draft

```bash
cd your-repo
claude
# then inside Claude Code:
/init
```

`/init` scans your repo and proposes a starter `CLAUDE.md`. Refine from there — add only what Claude got wrong twice.

Use `@path/to/file` imports to pull in shared docs without duplicating:

```markdown
@AGENTS.md

## Claude-specific
- Use plan mode for changes under `src/billing/`
- Run `pnpm test src/billing/` after billing edits
```

Wrap paths in backticks (`` `@README` ``) when you want literal text, not an import.

## What AGENTS.md should contain

`AGENTS.md` is an **open standard** used by Cursor, Codex, Devin, and other agents. **Claude Code does not read `AGENTS.md` automatically** — it reads `CLAUDE.md`.

If your team already maintains `AGENTS.md`, don't duplicate. Bridge them:

**Option A — import (recommended on all platforms):**

```markdown
@AGENTS.md

## Claude Code
- Prefer plan mode for database migrations
- Use `claude -p` in CI for automated fix loops
```

**Option B — symlink (macOS/Linux):**

```bash
ln -s AGENTS.md CLAUDE.md
```

**Option C — one-time import:**

```
/import
```

Claude Code v2.1.213+ copies supported agent configs (including `AGENTS.md`, `.cursor/rules/`, MCP servers, skills) into your Claude setup.

### What belongs in AGENTS.md

Write **agent-agnostic** instructions any coding agent should follow:

| Section | Example content |
|---------|-----------------|
| Project overview | One paragraph: what the repo does |
| Setup | Install, env vars, first-run commands |
| Architecture | High-level module map, data flow |
| Conventions | Naming, error handling, logging |
| Testing | How to run tests, coverage expectations |
| PR checklist | What must pass before merge |
| Boundaries | Files never to edit, secrets handling |

Keep Claude-only or Cursor-only quirks in `CLAUDE.md` or `.cursor/rules/` — not in `AGENTS.md`.

### Mirror with Cursor

If you use both Cursor and Claude Code:

```
AGENTS.md              ← shared team rules (committed)
CLAUDE.md              ← @AGENTS.md + Claude-specific notes
.cursor/rules/*.mdc    ← Cursor-specific (Tab, Composer hints)
```

Duplicate only what each tool can't import. Shared build commands and architecture belong in `AGENTS.md` once.

## Path-scoped rules in `.claude/rules/`

When `CLAUDE.md` grows past ~150 lines, split topic-specific instructions into `.claude/rules/`. One file per topic:

```
.claude/
├── CLAUDE.md
└── rules/
    ├── testing.md
    ├── api-design.md
    ├── frontend/
    │   └── react.md
    └── backend/
        └── database.md
```

Rules **without** frontmatter load every session (same cost as `CLAUDE.md`). Rules **with** `paths` load only when Claude reads matching files — saving context.

### Path-scoped example

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/api/**/*.tsx"
---

# API rules

- All endpoints return `{ data, error }` envelope
- Validate input with Zod schemas in `src/api/schemas/`
- Add OpenAPI comments on every exported handler
```

### When to use rules vs skills

| Use `.claude/rules/` | Use skills (`.claude/skills/`) |
|----------------------|--------------------------------|
| Conventions that apply while editing certain files | Multi-step procedures (deploy, release, migration) |
| "Always do X when touching Y" | "Run this checklist when I say /release" |
| Loaded when matching files are read | Loaded on invoke or when Claude decides they're relevant |

Path-scoped rules may reload after context compaction when Claude touches matching files again. Put must-survive-compaction rules in root `CLAUDE.md` without `paths`.

## Personal and user-level config

### `CLAUDE.local.md` (project, gitignored)

Personal sandbox URLs, test accounts, local DB names. Add to `.gitignore`:

```
CLAUDE.local.md
```

### `~/.claude/CLAUDE.md` (user, all projects)

Your cross-project preferences:

```markdown
# Personal preferences
- Prefer concise commit messages
- Always show git diff summary before committing
- Use British spelling in comments
```

### `~/.claude/rules/` (user, all projects)

Same format as project rules. Loaded before project rules — project wins on conflict.

## Essential `settings.json`

Project settings live in `.claude/settings.json`. Local overrides in `.claude/settings.local.json` (usually gitignored).

```json
{
  "permissions": {
    "allow": [
      "Bash(pnpm test *)",
      "Bash(pnpm lint)"
    ],
    "deny": [
      "Bash(git push --force *)",
      "Read(.env)"
    ]
  },
  "env": {
    "NODE_ENV": "development"
  }
}
```

Useful keys:

| Key | Purpose |
|-----|---------|
| `permissions.allow` / `deny` | Hard gates — unlike CLAUDE.md, these are enforced |
| `claudeMdExcludes` | Skip irrelevant ancestor CLAUDE.md files in monorepos |
| `cleanupPeriodDays` | How long session transcripts are kept (default 30) |
| `sandbox.enabled` | Isolate bash from your real filesystem |

**CLAUDE.md = soft guidance. Settings permissions = hard enforcement.** Use PreToolUse hooks when you need to block actions regardless of what Claude decides.

## Session workflow that works

Configuration files alone don't make Claude efficient. These habits compound:

### 1. Explore → plan → implement

Press `Shift+Tab` for plan mode (or `claude --permission-mode plan`). Claude reads and plans without editing. Approve the plan, then implement.

Skip planning for one-line fixes. Use it for multi-file changes.

### 2. Give Claude a verification loop

Tell Claude what "done" means and how to check:

```
Add rate limiting to POST /api/login.
Write a test that sends 11 requests and expects 429 on the 11th.
Run pnpm test src/api/login.test.ts and fix until green.
```

Without a check, you become the verification loop.

### 3. Scope prompts with `@` files

```
@src/auth/session.ts fix the token refresh bug described in #842.
Match error handling in @src/auth/login.ts.
```

### 4. Use `/doctor` on bloated CLAUDE.md

Claude proposes cuts for content it can derive from the codebase. Treat `CLAUDE.md` like code — review when behavior drifts.

### 5. Headless CI with `claude -p`

```bash
claude -p "Fix the failing test in src/api/health.test.ts. Run pnpm test after."
```

Passes a single prompt, runs autonomously, exits. Pair with `CLAUDE.md` in the repo so CI gets the same context as local sessions.

## Example repo layout

```
my-app/
├── AGENTS.md                 # Shared agent instructions (team)
├── CLAUDE.md                 # @AGENTS.md + Claude-specific
├── CLAUDE.local.md           # Personal (gitignored)
├── .gitignore                # includes CLAUDE.local.md
├── .claude/
│   ├── settings.json         # Team permissions
│   ├── settings.local.json   # Personal overrides (gitignored)
│   ├── rules/
│   │   ├── testing.md
│   │   ├── api-design.md
│   │   └── frontend/
│   │       └── react.md
│   ├── skills/
│   │   └── release/
│   │       └── SKILL.md
│   └── commands/             # Custom slash commands
│       └── review.md
├── src/
│   └── billing/
│       └── CLAUDE.md         # Loads when Claude edits billing/
└── .cursor/
    └── rules/                # Cursor-only (optional)
        └── composer.mdc
```

## Common mistakes

1. **500-line CLAUDE.md** — Claude ignores buried rules. Split into path-scoped `.claude/rules/`.
2. **Duplicating AGENTS.md in CLAUDE.md** — use `@AGENTS.md` import instead.
3. **No test command** — Claude stops when code "looks done" instead of when tests pass.
4. **Contradicting rules** — "always use mocks" in one file, "avoid mocks" in another. Claude picks arbitrarily.
5. **Skills for static facts** — "our API base URL is …" belongs in CLAUDE.md or a rule, not a skill.
6. **Editing with two agents at once** — Cursor and Claude Code on the same branch causes merge conflicts. One agent per folder at a time.
7. **Never pruning** — outdated CLAUDE.md instructions cause more harm than no instructions.

## FAQ

### How long should CLAUDE.md be?

Under 200 lines. Move domain-specific content to path-scoped rules or skills.

### Does Claude Code read AGENTS.md?

Not directly. Create `CLAUDE.md` with `@AGENTS.md` at the top, symlink, or run `/import`.

### What's the difference between CLAUDE.md and .claude/rules/?

Root `CLAUDE.md` loads every session. Rules split instructions by topic; path-scoped rules load only when relevant files are read.

### Should I commit CLAUDE.local.md?

No. It's for personal preferences. Add it to `.gitignore`.

### How do I check if instructions loaded?

Run `/context` in a Claude Code session. Memory files appear under the Memory section.

### CLAUDE.md vs auto memory?

You write CLAUDE.md. Claude writes auto memory from your corrections. Use CLAUDE.md for standards; let auto memory capture preferences Claude learns over time.

## Related guides

- [Claude Code vs Cursor vs Copilot: Which Should You Use?](/blog/posts/claude-code-vs-cursor-vs-copilot/)
- [Skills vs MCP vs Subagents: When to Use Each](/blog/posts/skills-vs-mcp-vs-subagents/)
- [How to Migrate Cursor Chat to Claude Code](/blog/posts/migrate-cursor-chat-to-claude-code/)
- [How to Build a Cursor-Like AI Coding Agent](/blog/posts/how-to-build-cursor-like-ai-coding-agent/)
