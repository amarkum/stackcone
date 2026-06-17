# How to Export Cursor Chat History from state.vscdb

Cursor does not ship a “export all chats” button. Composer threads, Agent runs, and Plan files live in local SQLite databases and markdown on disk. This guide shows a **generic, read-only** way to list every conversation and dump them to JSON or Markdown — without calling Cursor’s cloud API or touching auth tokens in your exports.

## Table of contents

1. Where Cursor stores chats
2. SQLite schema (ItemTable + cursorDiskKV)
3. Prerequisites and safety
4. Export script (Python)
5. Export plans and agent transcripts
6. Output formats
7. Troubleshooting
8. FAQ

## Where Cursor stores chats

On **macOS** (Linux and Windows paths differ slightly — see script):

| Path | Contents |
|------|----------|
| `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb` | Global chats, composer index, bubbles |
| `~/Library/Application Support/Cursor/User/workspaceStorage/<hash>/state.vscdb` | Per-workspace prompt history |
| `~/.cursor/plans/*.plan.md` | Plan mode outputs |
| `~/.cursor/projects/<slug>/agent-transcripts/<runId>/*.jsonl` | Agent run logs |
| `~/.cursor/ai-tracking/ai-code-tracking.db` | Conversation summaries, AI authorship stats |

The main chat payload is in **`state.vscdb`**, a SQLite file with two tables:

- **`ItemTable`** — `key TEXT, value BLOB` — settings, auth metadata, composer headers
- **`cursorDiskKV`** — `key TEXT, value BLOB` — chat bubbles, blobs, checkpoints

### Notable keys

**ItemTable (global):**

- `composer.composerHeaders` — index of all composers (`allComposers` + `workspaceIdentifier`)

**cursorDiskKV prefixes:**

- `composerData:<composerId>` — thread metadata
- `bubbleId:<composerId>:<bubbleId>` — each user/assistant message
- `messageRequestContext:<composerId>:<bubbleId>` — request context per bubble
- `checkpointId:<composerId>:<uuid>` — checkpoint pointers
- `agentKv:blob:<sha256>` — content-addressed JSON blobs

**Per-workspace ItemTable:**

- `aiService.prompts` — verbatim prompt history for that workspace

## Prerequisites and safety

1. **Quit Cursor** (or accept occasional `database is locked` errors — the script uses read-only mode).
2. **Never commit exports** that may contain API keys, JWTs, or private repo paths.
3. The script **redacts** JWT-shaped strings and common secret patterns before writing output.
4. Do **not** paste `cursorAuth/accessToken` from ItemTable into scripts that send data anywhere — local export only.

## Export script

Save as `cursor_export.py` and run: `python3 cursor_export.py --out ./cursor-export`

See the published HTML article for the full script block.

## Export plans and agent transcripts

**Plans** are plain markdown — copy `~/.cursor/plans/*.plan.md` directly.

**Agent transcripts** are JSONL under `~/.cursor/projects/`. Each line is a JSON event; concatenate `text` fields for a readable log.

**Conversation summaries** (optional) live in `ai-code-tracking.db` → table `conversation_summaries` with `title`, `tldr`, `overview`, `summaryBullets`.

## Output formats

- **`composers.json`** — index of all threads (id, name, dates, workspace)
- **`chats/<composerId>.json`** — full bubble timeline per thread
- **`chats/<composerId>.md`** — Markdown transcript for humans / Claude import
- **`plans/`** — copy of plan files

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `database is locked` | Close Cursor; retry |
| Messages out of order | Sort by `fullConversationHeadersOnly` in composer metadata, not `createdAt` |
| Empty composer list | Older Cursor builds store summaries in workspace DBs — script falls back automatically |
| Huge bubble text | Truncate with `--max-chars` per message |

## FAQ

**Is this supported by Cursor?** No — it reads local files Cursor already writes. Schema may change between versions.

**Does this sync cloud-only chats?** Only what is cached locally in `state.vscdb`.

**Can I export on Windows/Linux?** Yes — adjust base paths in `cursor_paths()`.
