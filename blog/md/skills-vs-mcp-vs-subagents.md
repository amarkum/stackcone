# Skills vs MCP vs Subagents: When to Use Each

If you’ve spent the last month hearing “just add an MCP” and “write a skill” and “spin up a subagent” as if they mean the same thing — they don’t.

In 2026, coding agents (Claude Code, Cursor, Codex, Gemini CLI) share a common vocabulary. Mixing these up is the #1 reason setups get over-engineered or break. Here’s the clear split.

**Related:** [AI agents + MCP for data engineering](./ai-agent-mcp-data-engineering-automation.html) · [Migrate Cursor chat to Claude Code](./migrate-cursor-chat-to-claude-code.html)

## Table of contents

1. [One-line definitions](#one-line-definitions)
2. [What each one actually does](#what-each-one-actually-does)
3. [Side-by-side comparison](#side-by-side-comparison)
4. [When to use each](#when-to-use-each)
5. [How they compose](#how-they-compose)
6. [Common mistakes](#common-mistakes)
7. [Decision flowchart](#decision-flowchart)
8. [FAQ](#faq)

## One-line definitions

| Building block | What it is | Analogy |
| --- | --- | --- |
| **MCP** | A connection to an external system | USB-C port |
| **Skill** | Packaged how-to knowledge (`SKILL.md`) | Team playbook |
| **Subagent** | A delegated specialist with its own context | Teammate on a side quest |

**MCP adds capability. Skills change behavior. Subagents protect context.**

## What each one actually does

### MCP (Model Context Protocol)

An MCP server is **plumbing**. It does not reason. It exposes:

- **Tools** — create a PR, query Postgres, post to Slack, call Figma
- **Resources** — files, tickets, live state the model can read
- **Prompts** — optional reusable prompt templates

Supported across Claude, ChatGPT, Cursor, Copilot, and more. Write once, use everywhere.

**Use MCP when** you need live access to a system the model cannot reach with shell alone — or when you want a stable, typed tool surface instead of ad-hoc curl scripts.

**Do not use MCP when** you only need to teach the agent *how* your team works. That is a skill.

### Skills (`SKILL.md`)

A skill is a **markdown playbook** the agent loads when the task matches its description. It typically includes:

- When to trigger (YAML `description`)
- Step-by-step procedure
- Repo conventions, templates, checklists
- Optional scripts the agent should run

In Cursor, skills live under `.cursor/skills/` (project) or `~/.cursor/skills/` (personal). They are instructions — not network ports.

**Use a skill when** you want repeatable behavior: “how we write PRs,” “how we run migrations,” “how we ship blog posts.”

**Do not use a skill when** you need a live API. Wire MCP (or a CLI) for that; the skill can *tell* the agent which MCP tools to call.

### Subagents

A subagent is a **separate agent run** with its own context window, tools, and (often) model. The parent delegates a scoped job — explore a codebase, run shell, review a PR — then receives a summary.

Examples in Cursor: `explore`, `shell`, `ci-investigator`, `best-of-n-runner`, custom Task agents.

**Use a subagent when** the work would pollute the main chat (huge search dumps, long test logs) or needs isolation (parallel experiments, dangerous shell).

**Do not use a subagent when** a short instruction or skill is enough. Extra agents add latency and cost.

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
- Anything you would otherwise wrap in a one-off script every session

### Reach for a skill

- “Always run highlights before commit”
- “PR title format and test plan checklist”
- Domain playbooks (RAG eval, Flutter release, Upwork invoice flow)

### Reach for a subagent

- Broad codebase search that would flood the transcript
- Parallel “try 3 approaches” experiments
- Long-running CI diagnosis while you keep chatting
- Scoped reviews (security, Bugbot-style) that should not inherit your whole chat

## How they compose

The winning pattern in 2026 is **composition**, not picking one:

```text
Skill: "Ship a blog post"
  → tells agent the checklist
  → calls MCP: GitHub (open PR) + Figma (optional)
  → may spawn Subagent: explore (find related posts)
  → main agent writes files and summarizes
```

Another pattern:

```text
User: "Fix failing CI on this PR"
  → Subagent: ci-investigator (isolated logs)
  → Skill: "how we fix flaky tests"
  → MCP: GitHub (re-run checks, comment)
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

No. MCP exposes tools. Skills teach *when and how* to use tools (and local workflows that need no MCP at all).

### Can a skill call an MCP tool?

Yes. The skill instructs the agent; the agent invokes MCP tools available in the session.

### Do subagents see my full chat?

Usually not — that is the point. Pass a detailed prompt with the context they need.

### Where should beginners start?

1. One **skill** for your most repeated workflow  
2. One **MCP** for the system you touch daily (GitHub is common)  
3. Use a **subagent** only when the main chat gets noisy  

### How does this relate to Claude Code / Cursor / Codex?

Names differ slightly, but the split is the same: connectors (MCP), playbooks (skills / custom instructions), and delegated agents (subagents / Task / swarm).
