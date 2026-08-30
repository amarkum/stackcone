# Skills vs Rules in Claude Code and Cursor: When to Use Each

August 2026 · Published by Amar Kumar

Developers setting up Claude Code or Cursor often ask: **should this go in a rule or a skill?** They paste a 40-step release checklist into `CLAUDE.md`, then wonder why Claude ignores half of it. Or they create a skill for "use 2-space indent" and it never loads.

**Rules** are persistent instructions — loaded every session or when matching files are read. They shape *how Claude behaves while editing*.

**Skills** are on-demand playbooks — loaded when you invoke them or when the task clearly matches. They shape *how Claude completes a specific workflow*.

This guide explains the split with side-by-side examples for Claude Code (`.claude/rules/`, `SKILL.md`) and Cursor (`.cursor/rules/`, `.cursor/skills/`).

**Related:** [How to Use Claude Code Effectively](./how-to-use-claude-code-effectively.html) · [Skills vs MCP vs Subagents](./skills-vs-mcp-vs-subagents.html)

## Table of contents

1. [One-line definitions](#one-line-definitions)
2. [Where rules and skills live](#locations)
3. [Side-by-side comparison](#comparison)
4. [When to use rules](#when-rules)
5. [When to use skills](#when-skills)
6. [Example: a rule file](#example-rule)
7. [Example: a skill file](#example-skill)
8. [Same task — wrong vs right](#wrong-vs-right)
9. [How they compose with CLAUDE.md](#compose)
10. [Decision flowchart](#flowchart)
11. [Common mistakes](#mistakes)
12. [FAQ](#faq)

## One-line definitions

| | Rules | Skills |
|---|-------|--------|
| **What it is** | Persistent instruction file | On-demand workflow playbook |
| **Analogy** | House rules on the wall | Recipe card you pull out when cooking |
| **Loaded** | Every session, or when matching files are read | When invoked (`/skill-name`) or when task matches description |
| **Best for** | Conventions, constraints, "always do X" | Multi-step procedures, checklists, domain workflows |
| **Context cost** | Paid upfront (or on file read) | Paid only when used |

**Rules = always-on behavior. Skills = sometimes-on procedure.**

## Where rules and skills live

### Claude Code

| Type | Path | Scope |
|------|------|-------|
| Root rules | `CLAUDE.md` or `.claude/CLAUDE.md` | Every session |
| Modular rules | `.claude/rules/*.md` | Every session, or on demand if path-scoped |
| Path-scoped rules | `.claude/rules/api.md` with `paths:` frontmatter | When Claude reads matching files |
| User rules | `~/.claude/rules/*.md` | All your projects |
| Skills | `.claude/skills/{name}/SKILL.md` | On invoke or auto when relevant |
| User skills | `~/.claude/skills/{name}/SKILL.md` | All your projects |

### Cursor

| Type | Path | Scope |
|------|------|-------|
| Project rules | `.cursor/rules/*.mdc` | When rule's glob/trigger matches |
| User rules | Cursor Settings → Rules | All your projects |
| Skills | `.cursor/skills/{name}/SKILL.md` | On invoke or auto when relevant |
| User skills | `~/.cursor/skills/{name}/SKILL.md` | All your projects |

Cursor rules use `.mdc` with optional frontmatter (`globs`, `alwaysApply`). Claude Code rules use plain `.md` with optional `paths:` frontmatter. The *concept* is the same — scoped instructions — even if file formats differ slightly.

## Side-by-side comparison

| Dimension | Rules | Skills |
|-----------|-------|--------|
| **Primary job** | Tell agent how to behave | Tell agent how to complete a task |
| **Typical content** | Style, conventions, boundaries | Step-by-step checklist, scripts |
| **Length** | Short — bullets and constraints | Can be longer — procedures OK |
| **Trigger** | Session start or file path match | User says `/release` or description match |
| **Context window** | Loaded into every relevant session | Loaded on demand |
| **Good example** | "API handlers return `{ data, error }`" | "Ship a release: bump version, changelog, tag, deploy" |
| **Bad example** | 30-step deploy checklist | "Use TypeScript strict mode" |
| **Enforcement** | Soft — Claude may drift if overloaded | Soft — but explicit invoke is reliable |
| **Hard enforcement** | Use `settings.json` permissions or hooks | Use hooks at workflow steps |

## When to use rules

Put content in **rules** (including root `CLAUDE.md`) when:

- It applies **every time** Claude touches certain files
- It's a **constraint** or convention, not a procedure
- Removing it would cause Claude to make **repeated mistakes**
- It's **short** — a few bullets, not a runbook

### Good rule topics

- Build and test commands (`pnpm test`, `make lint`)
- Code style (indent, naming, error envelope format)
- Project layout ("handlers live in `src/api/handlers/`")
- Security boundaries ("never read `.env`", "ask before force-push")
- File-type conventions (React component structure, SQL migration naming)

### Use path-scoped rules when

The instruction only matters for part of the codebase:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API rules
- Validate all inputs with Zod
- Return `{ data, error }` envelope
- Add OpenAPI comments on exported handlers
```

API rules don't need to load while Claude edits CSS.

## When to use skills

Put content in a **skill** when:

- It's a **multi-step workflow** (5+ steps with order)
- It only applies **sometimes** — releases, migrations, incident response
- It includes **scripts, templates, or reference files** alongside instructions
- You want to **invoke it explicitly** (`/ship-blog-post`, `/fix-issue 842`)
- It would **bloat CLAUDE.md** if pasted there

### Good skill topics

- Ship a blog post (md → html → sitemap → highlights)
- Run a production database migration safely
- Triage a failing CI check
- Create a pull request with team template
- Onboard a new service (scaffold + tests + deploy)

### Skill frontmatter matters

The `description` field is how Claude decides to auto-load a skill. Write it like a search query:

```yaml
---
name: ship-blog-post
description: >-
  Ship a stackcone blog post — write md source, publish HTML,
  update posts.json and sitemap, run apply_highlights.py.
---
```

Vague descriptions ("helps with blog stuff") mean the skill never auto-loads. Use `disable-model-invocation: true` when you only want manual `/ship-blog-post` triggers (workflows with side effects).

## Example: a rule file

**File:** `.claude/rules/testing.md`

```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
  - "tests/**/*"
---

# Testing conventions

- Use Vitest, not Jest
- One `describe` block per exported function
- Mock external HTTP at the boundary, not internal helpers
- Run `pnpm test path/to/file.test.ts` after editing a test file
- Never skip tests without a comment explaining why
```

**Why this is a rule, not a skill:** These are constraints that apply whenever Claude edits test files. No multi-step workflow — just "how we write tests here."

**Cursor equivalent:** `.cursor/rules/testing.mdc`

```markdown
---
globs: "**/*.{test,spec}.ts,tests/**"
---

# Testing conventions
(same bullets)
```

## Example: a skill file

**File:** `.claude/skills/ship-blog-post/SKILL.md`

```markdown
---
name: ship-blog-post
description: >-
  Publish a stackcone blog post — md source, HTML page, posts.json,
  sitemap.xml, syntax highlighting. Use when user asks to ship or
  publish a blog post.
---

# Ship a blog post

Follow `.cursor/rules/blog-posts.mdc` conventions.

## Steps

1. Write `blog/md/{slug}.md` (markdown source, not public URL).
2. Write `blog/posts/{slug}/index.html` (canonical published page).
3. Download hero images to `blog/images/{slug}/` — no hotlinks.
4. Add entry to `blog/posts.json` with author "Amar Kumar".
5. Add URL to `sitemap.xml`.
6. Update static listing in `blog/index.html`.
7. Run `python3 _dev/apply_highlights.py blog/posts/{slug}/index.html`.
8. Verify no links point to `.md` files.

## Do not

- Create redirect stub files
- Commit without user asking (unless they said "commit and push")
- Generate AI hero images when real logos exist
```

**Optional supporting files:**

```
.claude/skills/ship-blog-post/
├── SKILL.md
├── template-claude-md-snippet.md   # reference
└── scripts/
    └── check-sitemap.sh            # validation script
```

**Why this is a skill, not a rule:** Eight ordered steps, only runs when publishing. Loading this every session would waste context.

**Invoke manually:**

```
/ship-blog-post claude-code-skills-vs-rules
```

## Same task — wrong vs right

### Task: "Always run tests before committing"

| Wrong | Right |
|-------|-------|
| Skill `run-tests-before-commit/SKILL.md` with one bullet | Rule in `CLAUDE.md`: `- Run pnpm test before every commit` |
| Never auto-loads; you forget to invoke | Loads every session |

### Task: "How we deploy to production"

| Wrong | Right |
|-------|-------|
| 25-step deploy pasted into `CLAUDE.md` | Skill `deploy-production/SKILL.md` with full checklist |
| Bloats context; Claude ignores buried steps | Loads only when you say `/deploy-production` |

### Task: "React components use named exports"

| Wrong | Right |
|-------|-------|
| Skill with description "React help" | Path-scoped rule `.claude/rules/frontend/react.md` with `paths: ["src/components/**/*.tsx"]` |
| Over-broad description; loads at wrong times | Loads only when editing components |

### Task: "Fix GitHub issue #842"

| Wrong | Right |
|-------|-------|
| Rule in CLAUDE.md: "when user mentions issues, follow these 8 steps…" | Skill `fix-issue/SKILL.md` with `disable-model-invocation: true` |
| Fires on every session mentioning "issue" | Invoke with `/fix-issue 842` |

## How they compose with CLAUDE.md

Think of three layers:

```text
CLAUDE.md          → facts true everywhere (build cmd, layout, git rules)
.claude/rules/     → conventions scoped by topic or file path
.claude/skills/    → procedures you run on demand
```

**Example stack for a FastAPI monorepo:**

```
CLAUDE.md                    # pnpm test, never push main, project map
.claude/rules/
  ├── python-style.md        # no paths → loads every session
  ├── api-design.md          # paths: src/api/**
  └── database.md            # paths: src/db/**
.claude/skills/
  ├── add-endpoint/SKILL.md  # scaffold route + test + OpenAPI
  ├── run-migration/SKILL.md # backup, migrate, verify, rollback plan
  └── incident/SKILL.md      # on-call runbook
```

**Rule of thumb:**

- If Claude should **know it always** → `CLAUDE.md` (keep under 200 lines)
- If Claude should **know it when editing X** → path-scoped rule
- If Claude should **do a procedure sometimes** → skill

Run `/context` (Claude Code) to see what's loaded. If the list is huge, move procedures to skills and narrow rules with `paths`.

## Decision flowchart

```text
Is this a multi-step procedure (5+ ordered steps)?
  YES → Skill
  NO  → Does it apply every session regardless of task?
          YES → CLAUDE.md or unconditional .claude/rules/*.md
          NO  → Does it apply only when editing certain files?
                  YES → Path-scoped rule (paths: or globs:)
                  NO  → Probably CLAUDE.md if short; skill if it's a rare workflow
```

## Common mistakes

1. **Release checklist in CLAUDE.md** — move to a skill; root file should stay under 200 lines.
2. **Style rules in a skill** — "use camelCase" belongs in a rule, not a skill that never loads.
3. **Vague skill description** — Claude skips skills it can't match. Write descriptions like search queries.
4. **Duplicate content** — same instruction in CLAUDE.md and a rule and a skill. Pick one place.
5. **Giant skill** — split by trigger: `ship-blog-post` vs `ship-solution-post`, not one mega-skill.
6. **Rules without paths in monorepos** — frontend rules loading during backend work wastes context.
7. **Expecting rules to enforce** — rules are soft guidance. Use `settings.json` deny lists or hooks for hard blocks.

## FAQ

### Can a skill reference a rule?

Yes. A skill can say "follow `.claude/rules/api-design.md`" or "match conventions in `.cursor/rules/`." Rules set defaults; skills orchestrate workflows that respect them.

### Should I duplicate rules in Cursor and Claude Code?

Share agent-agnostic content in `AGENTS.md`, then:

- `CLAUDE.md` with `@AGENTS.md` for Claude Code
- `.cursor/rules/` for Cursor-specific (Tab, Composer hints)
- Skills can live in both `.claude/skills/` and `.cursor/skills/` if workflows differ slightly

### Rules vs CLAUDE.md — what's the difference?

`CLAUDE.md` is the root rules file. `.claude/rules/` splits it into modules. Unconditional rules in `.claude/rules/` cost the same as putting them in `CLAUDE.md` — use `paths:` to defer loading.

### How do I invoke a skill?

Claude Code: `/skill-name` or `/skill-name arguments`. Cursor: same pattern. With `disable-model-invocation: true`, only manual invoke works — use for deploy/release workflows.

### Skills vs MCP?

Rules and skills are instructions. MCP is plumbing to external systems. See [Skills vs MCP vs Subagents](./skills-vs-mcp-vs-subagents.html) for that split.

## Bottom line

- **Rules** — how Claude should behave (constraints, conventions, always-on facts)
- **Skills** — how Claude should complete a task (checklists, workflows, on demand)

When in doubt: if you'd put it on a sticky note on your monitor, it's a rule. If you'd put it in a runbook drawer, it's a skill.

## Related guides

- [How to Use Claude Code Effectively: CLAUDE.md, AGENTS.md, and Rules](/blog/posts/how-to-use-claude-code-effectively/)
- [Skills vs MCP vs Subagents: When to Use Each](/blog/posts/skills-vs-mcp-vs-subagents/)
- [Claude Code vs Cursor vs Copilot: Which Should You Use?](/blog/posts/claude-code-vs-cursor-vs-copilot/)
