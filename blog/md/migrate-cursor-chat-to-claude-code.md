# Migrate Cursor Chat to Claude Code

Migrate **Cursor agent chat history** into **Claude Code native JSONL sessions** so conversations appear in Claude's session picker. Also migrates **plan files**. Based on production migration tooling — local disk only, no cloud API.

**Composer vs agent:** [Composer threads in state.vscdb](./export-cursor-chat-history-vscdb.html) use SQLite. **Agent transcripts** are JSONL under `~/.cursor/projects/.../agent-transcripts/` — this guide migrates those.

## Table of contents

1. [Overview](#overview)
2. [Cursor local data map](#cursor-local-data-map)
3. [What gets migrated](#what-gets-migrated)
4. [Slug mapping](#slug-mapping-cursor--claude)
5. [Format differences](#format-differences)
6. [Migration script](#migration-script)
7. [How to run](#how-to-run)
8. [Verify in Claude Code](#verify-in-claude-code)
9. [Manifest and re-runs](#manifest-and-re-runs)
10. [Plans migration](#plans-migration)
11. [Safety](#safety)
12. [Rollback](#rollback)
13. [Troubleshooting](#troubleshooting)
14. [FAQ](#faq)

## Overview

| | Path |
|---|------|
| **Source (chats)** | `~/.cursor/projects/<slug>/agent-transcripts/<runId>/<runId>.jsonl` |
| **Target (chats)** | `~/.claude/projects/-<slug>/<session-uuid>.jsonl` |
| **Source (plans)** | `~/.cursor/plans/*.plan.md` |
| **Target (plans)** | `~/.claude/plans/*.md` |
| **Manifest** | `~/.claude/.cursor-migration-manifest.json` |

Non-destructive. Stable session IDs (SHA-256 of source path). `entrypoint: cursor-migrated` on every message.

## Cursor local data map

**macOS:** `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`

| Table | Keys |
|-------|------|
| `ItemTable` | `composer.composerHeaders`, auth metadata |
| `cursorDiskKV` | `composerData:`, `bubbleId:`, `checkpointId:`, `agentKv:blob:` |

**Agent transcripts (migrated):**

```
~/.cursor/projects/<slug>/agent-transcripts/<runId>/<runId>.jsonl
```

**Also on disk:**

- `~/.cursor/ai-tracking/ai-code-tracking.db` — `conversation_summaries`, `scored_commits`
- `.../anysphere.cursor-commits/checkpoints/` — AI-edit snapshots
- `User/workspaceStorage/<hash>/workspace.json` — maps slug → repo path (used for `cwd`)

**Security:** never ship `cursorAuth/accessToken` off-machine. This migrator is filesystem-only.

## What gets migrated

- Agent transcript user/assistant messages
- Correct `cwd` from workspace index
- Plans: `~/.cursor/plans/` → `~/.claude/plans/` (front matter stripped)

**Not migrated:** subagent sidechains, Composer state.vscdb bubbles, checkpoints, tool replay.

## Slug mapping (Cursor → Claude)

| Repo | Cursor slug | Claude folder |
|------|-------------|---------------|
| `~/dev/my-app` | `Users-you-dev-my-app` | `-Users-you-dev-my-app` |

Claude adds a **leading dash**. The script resolves real paths from `workspaceStorage/*/workspace.json`.

## Format differences

**Cursor (per line):**

```json
{ "role": "user", "message": { "content": "..." } }
```

**Claude Code (per line):**

```json
{
  "type": "user",
  "message": { "role": "user", "content": "..." },
  "uuid": "...",
  "sessionId": "...",
  "entrypoint": "cursor-migrated",
  "cwd": "/Users/you/dev/my-app",
  "version": "migrated-from-cursor"
}
```

Wrapped with `queue-operation` enqueue/dequeue lines.

## Migration script

Save as `migrate_cursor_to_claude.py` — see the [HTML article](../posts/migrate-cursor-chat-to-claude-code.html) for the full highlighted script. Key behaviors:

- `list_agent_chats()` — scans all `~/.cursor/projects/*/agent-transcripts/`
- `stable_session_id(path)` — deterministic session filename
- `build_slug_cwd_map()` — real repo path for each slug
- `migrate_chat()` / `migrate_plan()` — with skip-if-unchanged via manifest
- `--dry-run`, `--yes`, `--project`, `--chats-only`, `--plans-only`

## How to run

```bash
python3 migrate_cursor_to_claude.py --dry-run
python3 migrate_cursor_to_claude.py --project ~/dev/my-app --dry-run
python3 migrate_cursor_to_claude.py --yes
python3 migrate_cursor_to_claude.py --chats-only --yes
python3 migrate_cursor_to_claude.py --plans-only --yes
```

## Verify in Claude Code

```bash
cd ~/dev/my-app && claude --resume
grep -l '"entrypoint": "cursor-migrated"' ~/.claude/projects/-Users-you-dev-my-app/*.jsonl
```

## Manifest and re-runs

`~/.claude/.cursor-migration-manifest.json` tracks source → dest, `mtime`, `session_id`. Re-runs skip unchanged files. Delete manifest to force full re-migration.

## Plans migration

`api-redesign_387ebee5.plan.md` → `~/.claude/plans/api-redesign.md`

## Safety

- Read-only on Cursor sources
- Dry-run mode
- Per-item error isolation
- No network / no JWT handling

## Rollback

```bash
grep -l '"entrypoint": "cursor-migrated"' ~/.claude/projects/-Users-you-dev-my-app/*.jsonl
# delete those files; remove manifest to reset
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Nothing to migrate | Open repo in Cursor first; check `agent-transcripts/` exists |
| Wrong cwd | Fix `workspace.json` mapping; clear manifest entry and re-run |
| Not in UI | Leading dash on Claude folder; restart Claude Code |
| Need Composer too | [state.vscdb export](./export-cursor-chat-history-vscdb.html) |

## FAQ

**Stable session IDs?** Same Cursor chat → same Claude filename. Message UUIDs inside are new each run.

**Cloud usage API?** Out of scope — local migration only.
