# Migrate Cursor Chat History to Claude Code

Switching from Cursor Composer to **Claude Code** does not migrate your threads automatically. Cursor stores chats in SQLite `state.vscdb`; Claude Code stores **new** sessions as JSONL under `~/.claude/projects/`. This guide covers both sides: where Claude Code keeps its own history, and how to import Cursor decisions via `CLAUDE.md` and curated markdown.

**Prerequisite:** [Export Cursor chat history from state.vscdb](./export-cursor-chat-history-vscdb.html)

## Table of contents

1. Where Claude Code stores chats
2. What you can and cannot migrate
3. Migration workflow overview
4. Step 1 — Export and pick threads
5. Step 2 — Build a Claude context pack
6. Step 3 — Seed Claude Code
7. Step 4 — Ongoing hygiene
8. Plans and agent transcripts
9. FAQ

## Where Claude Code stores chats

Claude Code **auto-saves every CLI session** to local JSONL files as you work ([official docs](https://code.claude.com/docs/en/sessions)). There is no cloud sync for session files. Default root: `~/.claude/` (override with `CLAUDE_CONFIG_DIR`).

| Path | What it holds |
|------|----------------|
| `~/.claude/projects/<path-hash>/*.jsonl` | Full session transcripts — prompts, replies, tool calls, metadata (one JSON object per line) |
| `~/.claude/history.jsonl` | Global chronological index of prompts across all projects |
| `~/.claude/plans/` | Plan mode markdown outputs |
| `~/.claude/file-history/` | Per-file snapshots for `/rewind` and undo |
| `~/.claude/settings.json` | Global settings — includes `cleanupPeriodDays` (default **30**: old JSONL deleted) |
| `~/.claude/CLAUDE.md` | **User-level** instructions loaded in every session |
| `CLAUDE.md` (repo root) | **Project-level** instructions for that codebase |
| `.claude/settings.json` (in repo) | Project permissions, hooks — safe to commit |
| `~/.claude.json` (home root, not inside `~/.claude/`) | OAuth, MCP, runtime caches — do not edit manually |

The `<path-hash>` folder name is derived from your project's **absolute path**. Each repo/worktree gets its own directory.

### Resume, name, and export native sessions

| Command | Purpose |
|---------|---------|
| `claude --continue` | Resume the most recent session in the current directory |
| `claude --resume` | Open the interactive session picker |
| `claude --resume <name>` | Resume a named session |
| `claude -n auth-refactor` | Start with a session name (findable later) |
| `/export [file]` | Copy current conversation to clipboard or a text file |
| `/rename <name>` | Rename the active session |

List session files:

```bash
ls ~/.claude/projects/*/
find ~/.claude/projects -name "*.jsonl" | head
```

### Retention — back up before you lose history

Transcripts are deleted after **30 days** by default. Extend retention in `~/.claude/settings.json`:

```json
{ "cleanupPeriodDays": 365 }
```

### Where migrated Cursor content goes

Imported Cursor threads **do not** land in `~/.claude/projects/*.jsonl` by themselves. You put them in:

- Repo **`CLAUDE.md`** — distilled conventions and open TODOs
- **`context-pack/threads/*.md`** — curated Cursor transcripts (optional, gitignored if sensitive)
- A **new `claude` session** — paste a preamble; Claude then saves *that* conversation as a fresh JSONL file

Treat Cursor exports as **source material**; Claude Code's native store is for **new** work after you switch.

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

1. **Project `CLAUDE.md`** — Merge bootstrap content into your **repo root** `CLAUDE.md`. Claude Code loads this when you run `claude` in that directory. Optional: add rules to `~/.claude/CLAUDE.md` only for personal prefs that apply to all projects.

2. **Start a named session** — Names make `/resume` usable later:
   ```bash
   cd my-app && claude -n cursor-migration-auth
   ```

3. **First message** (example):
   > I migrated from Cursor. `CLAUDE.md` has current conventions. For auth background see `context-pack/threads/auth-refactor.md`. Continue from the open TODOs there.

4. **Native storage** — This session is now written to `~/.claude/projects/<path-hash>/<session>.jsonl` automatically. Use `/export` anytime for a plain-text backup.

5. **Large Cursor threads** — Import **summary + last ~10 messages**, not 200k tokens of tool noise.

## Step 4 — Ongoing hygiene

- Back up `~/.claude/projects/` if you rely on long history (or raise `cleanupPeriodDays`)
- When a Cursor thread resolves, merge the decision into repo `CLAUDE.md` and delete the thread file
- Re-export from Cursor monthly if you still dual-run tools
- Keep `context-pack/` in `.gitignore` if it has client names or private URLs

## Plans and agent transcripts

| Source | Claude Code use |
|--------|-----------------|
| `~/.cursor/plans/*.plan.md` | Copy to repo `docs/plans/` or into `~/.claude/plans/` / link from `CLAUDE.md` |
| Agent JSONL transcripts | Convert to markdown; useful for debugging agent behavior, not day-to-day coding |
| `conversation_summaries` in ai-tracking.db | Fast TL;DR when picking which threads to migrate |

## FAQ

**Where does Claude Code store chat history?** In `~/.claude/projects/<path-hash>/*.jsonl` — one JSONL file per session, saved continuously. Global prompt index: `~/.claude/history.jsonl`. Override root with `CLAUDE_CONFIG_DIR`.

**Will Claude Code read my old Cursor composerId?** No — IDs are for your export filenames only.

**Should I paste the entire Cursor export?** No — curate P0/P1 threads and summarize the rest.

**Can I automate this?** Yes — extend `cursor_export.py` to emit `context-pack/` directly (filter bubbles, merge plans).

**What about Cursor Plan mode vs Claude Plan?** Both output markdown. Copy into repo `docs/plans/` or `~/.claude/plans/`; re-run planning in Claude Code on the current tree.
