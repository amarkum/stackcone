# Skills vs MCP vs Subagents: When to Use Each

If you’ve spent the last month hearing “just add an MCP” and “write a skill” and “spin up a subagent” as if they mean the same thing — they don’t.

In 2026, coding agents (Claude Code, Cursor, Codex, Gemini CLI) share a common vocabulary. Mixing these up is the #1 reason setups get over-engineered or break. Here’s the clear split.

**Related:** [AI agents + MCP for data engineering](./ai-agent-mcp-data-engineering-automation.html) · [Migrate Cursor chat to Claude Code](./migrate-cursor-chat-to-claude-code.html) · [GPT-5.6 Sol vs Claude Fable 5 vs Kimi K3](./gpt-5-6-sol-vs-claude-fable-5-vs-kimi-k3.html)

## Table of contents

1. [One-line definitions](#one-line-definitions)
2. [What each one actually does](#what-each-one-actually-does)
3. [MCP architecture](#mcp-architecture)
4. [Skill example](#skill-example)
5. [Subagent types](#subagent-types)
6. [Side-by-side comparison](#side-by-side-comparison)
7. [When to use each](#when-to-use-each)
8. [How they compose](#how-they-compose)
9. [Common mistakes](#common-mistakes)
10. [Decision flowchart](#decision-flowchart)
11. [FAQ](#faq)

## One-line definitions

| Building block | What it is | Analogy |
| --- | --- | --- |
| **MCP** | A connection to an external system | USB-C port |
| **Skill** | Packaged how-to knowledge (`SKILL.md`) | Team playbook |
| **Subagent** | A delegated specialist with its own context | Teammate on a side quest |

**MCP adds capability. Skills change behavior. Subagents protect context.**

![MCP logo](../images/skills-vs-mcp-vs-subagents/mcp-logo.png)

## What each one actually does

### MCP (Model Context Protocol)

An MCP server is **plumbing**. It does not reason. It exposes:

- **Tools** — create a PR, query Postgres, post to Slack, call Figma
- **Resources** — files, tickets, live state the model can read
- **Prompts** — optional reusable prompt templates

Supported across Claude, ChatGPT, Cursor, Copilot, and more. Write once, use everywhere.

**Use MCP when** you need live access to a system the model cannot reach with shell alone.

**Do not use MCP when** you only need to teach the agent *how* your team works. That is a skill.

## MCP architecture

MCP uses a **host → client → server** pattern. The host (Cursor, Claude Desktop, ChatGPT) runs one MCP client per connected server.

| Layer | Role | Example |
| --- | --- | --- |
| **Host** | AI app the user talks to | Cursor, Claude Code |
| **MCP client** | One connection per server | Cursor’s GitHub MCP client |
| **MCP server** | Exposes tools / resources / prompts | `@modelcontextprotocol/server-github` |
| **Transport** | stdio (local) or HTTP+SSE (remote) | Local Node process or hosted MCP |

Official reference: [MCP architecture overview](https://modelcontextprotocol.io/docs/learn/architecture)

### Skills (`SKILL.md`)

A skill is a **markdown playbook** the agent loads when the task matches its description. In Cursor, skills live under `.cursor/skills/` (project) or `~/.cursor/skills/` (personal).

**Use a skill when** you want repeatable behavior: “how we write PRs,” “how we run migrations,” “how we ship blog posts.”

## Skill example

```markdown
---
description: Ship a stackcone blog post — md source, HTML publish, posts.json, sitemap, highlights.
---

# Ship a blog post

1. Write `blog/md/{slug}.md` and `blog/posts/{slug}.html`.
2. Download any hero images to `blog/images/{slug}/` (no hotlinks).
3. Update `blog/posts.json` and `sitemap.xml`.
4. Run `python3 _dev/apply_highlights.py blog/posts/{slug}.html`.
```

### Subagents

A subagent is a **separate agent run** with its own context window, tools, and (often) model. Examples in Cursor: `explore`, `shell`, `ci-investigator`, `best-of-n-runner`.

## Subagent types in Cursor

| Subagent | Best for | Why isolate? |
| --- | --- | --- |
| `explore` | Broad codebase search | Search hits would flood the main transcript |
| `shell` | Git, build, deploy commands | Long command output stays out of your chat |
| `ci-investigator` | One failing PR check | Focused log analysis + root-cause summary |
| `best-of-n-runner` | Parallel experiments | Try N approaches in isolated worktrees |
| Custom Task agent | Scoped reviews (security, SEO) | Does not inherit irrelevant chat context |

## Side-by-side comparison

| Dimension | MCP | Skill | Subagent |
| --- | --- | --- | --- |
| Primary job | Connect to systems | Encode how-to | Isolate work |
| Ships as | Server process + schema | `SKILL.md` (+ files) | Agent type / Task prompt |
| Has its own context? | No | No (loads into main) | **Yes** |
| Reasons by itself? | No | Guides the model | **Yes** |
| Best for | Tools & live data | Conventions & workflows | Exploration, parallelism |
| Failure mode | Auth / schema drift | Ignored if poorly described | Over-delegation, cost |

## When to use each

### Reach for MCP

- GitHub / Linear / Slack / Datadog / Figma integrations
- Database or internal API access with auth

### Reach for a skill

- “Always run highlights before commit”
- “PR title format and test plan checklist”
- Domain playbooks (RAG eval, Flutter release)

### Reach for a subagent

- Broad codebase search that would flood the transcript
- Parallel “try 3 approaches” experiments
- Long-running CI diagnosis while you keep chatting

## How they compose

```text
Skill: "Ship a blog post"
  → tells agent the checklist
  → calls MCP: GitHub (open PR) + Figma (optional)
  → may spawn Subagent: explore (find related posts)
  → main agent writes files and summarizes
```

**Rule of thumb:** MCP = *can*, Skill = *should*, Subagent = *elsewhere*.

## Common mistakes

1. **Putting procedures in MCP prompts** — keep playbooks in skills; keep MCP thin.
2. **One giant skill for everything** — split by trigger; agents skip walls of text.
3. **Subagent for every file edit** — main agent is faster for small diffs.
4. **MCP without auth story** — broken tokens look like “the model is dumb.”
5. **No `AGENTS.md` / skill description** — if the trigger is vague, the skill never loads.

## Decision flowchart

```text
Need live external system access?
  YES → MCP (plus a thin skill for how to use it)
  NO  → Need reusable team procedure?
          YES → Skill
          NO  → Will this flood context or need isolation/parallelism?
                  YES → Subagent
                  NO  → Just prompt the main agent
```

## Bottom line

- **MCP** — ports to the outside world
- **Skills** — your team’s operating manual
- **Subagents** — specialists that keep the main thread clean

Stop asking “MCP or skill?” Ask: *capability, behavior, or context isolation?* Then pick the matching layer — or stack all three.

## FAQ

### Is MCP a replacement for skills?

No. MCP exposes tools. Skills teach *when and how* to use tools.

### Can a skill call an MCP tool?

Yes. The skill instructs the agent; the agent invokes MCP tools available in the session.

### Do subagents see my full chat?

Usually not — that is the point. Pass a detailed prompt with the context they need.

### Where should beginners start?

1. One **skill** for your most repeated workflow
2. One **MCP** for the system you touch daily (GitHub is common)
3. Use a **subagent** only when the main chat gets noisy
