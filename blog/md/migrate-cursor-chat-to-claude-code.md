# Migrate Cursor Chat History to Claude Code

Switching from Cursor Composer to **Claude Code** does not migrate your threads automatically. Cursor stores chats in `state.vscdb`; Claude Code expects **project context** (`CLAUDE.md`), **session memory**, and fresh terminal sessions. This guide bridges that gap: export from Cursor, reshape for Claude, and bootstrap continuity without losing decisions buried in old threads.

**Prerequisite:** [Export Cursor chat history from state.vscdb](./export-cursor-chat-history-vscdb.html)

## Table of contents

1. What you can and cannot migrate
2. Migration workflow overview
3. Step 1 — Export and pick threads
4. Step 2 — Build a Claude context pack
5. Step 3 — Seed Claude Code
6. Step 4 — Ongoing hygiene
7. Plans and agent transcripts
8. FAQ

## What you can and cannot migrate

| Migrates well | Does not migrate |
|---------------|------------------|
| Message text (user + assistant) | Live Composer UI state |
| Plan markdown files | Cursor checkpoints / inline diffs |
| Thread titles and dates | `@file` attachment binaries |
| Architecture decisions in prose | Tool-call replay in Claude |
| Exported code blocks | Exact bubble ordering of draft/tool noise |

Treat migration as **knowledge transfer**, not a 1:1 session restore.

## Migration workflow overview

```
Cursor state.vscdb  →  cursor_export.py  →  Markdown/JSON
                                              ↓
                         Curate + summarize  →  context-pack/
                                              ↓
                         CLAUDE.md + paste   →  Claude Code session
```

## Step 1 — Export and pick threads

Run the export script from the companion article. Sort by `lastUpdatedAt` and tag threads:

- **P0** — active feature / bug you are still working
- **P1** — architecture or conventions worth preserving
- **P2** — archive only

Do not dump 200 threads into Claude — you will blow the context window and dilute signal.

## Step 2 — Build a Claude context pack

Create a folder in your repo (not committed if sensitive):

```
context-pack/
  CLAUDE-bootstrap.md      # distilled rules + decisions
  threads/
    auth-refactor.md         # one file per P0/P1 thread
  plans/
    api-redesign.plan.md     # copied from ~/.cursor/plans/
```

### Thread markdown template

Each exported thread should become:

```markdown
# Thread: Auth refactor (Cursor composerId: abc-123)
Exported: 2026-06-19 | Workspace: my-app

## Summary
- Chose JWT + refresh rotation over sessions
- Postgres table `sessions` deprecated

## Transcript
### User
We need to migrate off cookie sessions...

### Assistant
Recommend refresh tokens with...
```

Strip tool spam, linter noise, and duplicate drafts — keep **decisions** and **code snippets** that still apply.

### Distill into CLAUDE-bootstrap.md

Merge P0/P1 summaries into a single file Claude Code reads every session:

- Stack and versions
- Non-obvious conventions
- Open TODOs with file paths
- Links to `threads/*.md` for deep history

## Step 3 — Seed Claude Code

1. **Project instructions** — Copy the bootstrap into your repo’s `CLAUDE.md` (or merge with existing). Claude Code loads this automatically.

2. **First session** — Start Claude Code in the project root:
   ```bash
   cd my-app && claude
   ```
   Paste a short preamble:
   > I migrated from Cursor. `CLAUDE.md` has current conventions. For the auth refactor background see `context-pack/threads/auth-refactor.md`. Continue from the open TODOs there.

3. **Memory** — Use Claude’s project memory for stable facts (package manager, test command, deploy target). Do not store secrets.

4. **Large histories** — For threads over ~50k tokens, import **summary + last 10 messages** instead of the full transcript.

## Step 4 — Ongoing hygiene

- Export Cursor monthly if you still dual-run tools
- One canonical `CLAUDE.md` — avoid duplicating rules across thread files
- When a Cursor thread resolves, merge the decision into `CLAUDE.md` and delete the thread file
- Keep `context-pack/` in `.gitignore` if it contains client names or private URLs

## Plans and agent transcripts

| Source | Claude Code use |
|--------|-----------------|
| `~/.cursor/plans/*.plan.md` | Copy into repo `docs/plans/` or link from `CLAUDE.md` |
| Agent JSONL transcripts | Convert to markdown; useful for debugging agent behavior, not day-to-day coding |
| `conversation_summaries` in ai-tracking.db | Fast TL;DR when picking which threads to migrate |

## FAQ

**Will Claude Code read my old Cursor composerId?** No — IDs are for your export filenames only.

**Should I paste the entire export?** No — curate P0/P1 threads and summarize the rest.

**Can I automate this?** Yes — extend `cursor_export.py` to emit `context-pack/` directly (filter bubbles, merge plans).

**What about Cursor Plan mode vs Claude Plan?** Both output markdown plans — copy the markdown; re-run planning in Claude Code on the new stack.
