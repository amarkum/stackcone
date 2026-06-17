# Migrate Cursor Chat to Claude Code

Migrate **Cursor agent chat history** into **Claude Code's native session format** so conversations appear in Claude's chat history. Source: `~/.cursor/projects/.../agent-transcripts/`. Target: JSONL files in `~/.claude/projects/`.

**Different data?** [Composer chats in state.vscdb](./export-cursor-chat-history-vscdb.html) use a separate SQLite export. This guide covers **agent transcripts** (JSONL on disk).

## Table of contents

1. [Overview](#overview)
2. [What gets migrated](#what-gets-migrated)
3. [Where files live](#where-files-live)
4. [Format differences](#format-differences)
5. [Migration script](#migration-script)
6. [How to run](#how-to-run)
7. [Verify in Claude Code](#verify-in-claude-code)
8. [Safety features](#safety-features)
9. [Selective migration](#selective-migration)
10. [Rollback](#rollback)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

## Overview

| | Path |
|---|------|
| **Source** | `~/.cursor/projects/<slug>/agent-transcripts/` |
| **Target** | `~/.claude/projects/<path-hash>/` |
| **Format** | JSONL → JSONL (schema conversion) |
| **Result** | Migrated chats show up in Claude Code session history |

## What gets migrated

- All user and assistant messages
- One Claude session per Cursor chat
- Metadata tag `entrypoint: cursor-migrated`

**Not included:** subagent sidechain transcripts (only main `<chat-id>/<chat-id>.jsonl` per folder).

## Where files live

Folder names derive from the project's **absolute path** (slashes, dots, underscores → dashes).

| Tool | Example for `~/dev/my-app` |
|------|---------------------------|
| Cursor | `~/.cursor/projects/Users-you-dev-my-app/agent-transcripts/` |
| Claude | `~/.claude/projects/-Users-you-dev-my-app/` |

Claude's folder has a **leading dash**; Cursor's slug does not.

```bash
ls ~/.cursor/projects/*/agent-transcripts
ls ~/.claude/projects/
```

## Format differences

**Cursor (source)**

```json
{
  "role": "user",
  "message": { "content": "..." }
}
```

**Claude Code (target)**

```json
{
  "type": "user",
  "message": { "role": "user", "content": "..." },
  "uuid": "...",
  "timestamp": "2026-06-17T12:00:00Z",
  "sessionId": "...",
  "entrypoint": "cursor-migrated",
  "cwd": "/path/to/repo",
  "version": "migrated-from-cursor"
}
```

## Migration script

Save as `migrate_cursor_to_claude.py`:

```python
#!/usr/bin/env python3
"""Migrate Cursor agent transcripts to Claude Code chat JSONL.

  python3 migrate_cursor_to_claude.py --project ~/dev/my-app --dry-run
  python3 migrate_cursor_to_claude.py --project ~/dev/my-app --yes
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def path_slug(project: Path, *, leading_dash: bool = False) -> str:
    resolved = str(project.expanduser().resolve())
    slug = resolved.replace(os.sep, "-").lstrip(os.sep)
    slug = slug.replace(".", "-").replace("_", "-")
    return f"-{slug}" if leading_dash else slug


def cursor_transcripts_dir(project: Path) -> Path:
    return Path.home() / ".cursor/projects" / path_slug(project) / "agent-transcripts"


def claude_workspace_dir(project: Path) -> Path:
    return Path.home() / ".claude/projects" / path_slug(project, leading_dash=True)


def new_uuid() -> str:
    return str(uuid.uuid4())


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def queue_operation(session_id: str, operation: str = "enqueue") -> dict[str, Any]:
    return {
        "type": "queue-operation",
        "operation": operation,
        "timestamp": iso_now(),
        "sessionId": session_id,
    }


def cursor_to_claude_message(
    cursor_msg: dict[str, Any], session_id: str, msg_index: int, cwd: str
) -> dict[str, Any]:
    role = cursor_msg.get("role", "user")
    content = cursor_msg.get("message", {}).get("content", "")
    claude_msg: dict[str, Any] = {
        "parentUuid": None,
        "isSidechain": False,
        "promptId": new_uuid(),
        "type": role,
        "message": {"role": role, "content": content},
        "uuid": new_uuid(),
        "timestamp": iso_now(),
        "userType": "external",
        "entrypoint": "cursor-migrated",
        "cwd": cwd,
        "sessionId": session_id,
        "version": "migrated-from-cursor",
        "gitBranch": "unknown",
        "slug": f"migrated-chat-{msg_index}",
    }
    if role == "user":
        claude_msg["isMeta"] = False
    return claude_msg


def find_cursor_chats(transcripts_root: Path) -> list[Path]:
    chats: list[Path] = []
    if not transcripts_root.exists():
        return chats
    for chat_dir in transcripts_root.iterdir():
        if not chat_dir.is_dir():
            continue
        main = chat_dir / f"{chat_dir.name}.jsonl"
        if main.is_file():
            chats.append(main)
    return sorted(chats, key=lambda p: p.stat().st_mtime, reverse=True)


def migrate_chat(
    cursor_chat_path: Path, claude_workspace: Path, project: Path, *, dry_run: bool = False
) -> bool:
    try:
        lines = [
            json.loads(line)
            for line in cursor_chat_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not lines:
            return False
        session_id = new_uuid()
        cwd = str(project.resolve())
        claude_messages = [queue_operation(session_id, "enqueue")]
        for idx, msg in enumerate(lines):
            claude_messages.append(cursor_to_claude_message(msg, session_id, idx, cwd))
        claude_messages.append(queue_operation(session_id, "dequeue"))
        if not dry_run:
            claude_workspace.mkdir(parents=True, exist_ok=True)
            out = claude_workspace / f"{session_id}.jsonl"
            with out.open("w", encoding="utf-8") as fh:
                for m in claude_messages:
                    fh.write(json.dumps(m) + "\n")
        print(f"  ok {cursor_chat_path.parent.name} | {len(lines)} msgs")
        return True
    except Exception as exc:
        print(f"  fail {cursor_chat_path.name}: {exc}")
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--days", type=int, default=0)
    ap.add_argument("--yes", action="store_true")
    args = ap.parse_args()
    project = args.project.expanduser().resolve()
    transcripts = cursor_transcripts_dir(project)
    claude_ws = claude_workspace_dir(project)
    if not transcripts.exists():
        sys.exit(f"No transcripts at {transcripts}")
    chats = find_cursor_chats(transcripts)
    if args.days > 0:
        cutoff = datetime.now() - timedelta(days=args.days)
        chats = [c for c in chats if datetime.fromtimestamp(c.stat().st_mtime) >= cutoff]
    if not args.dry_run and not args.yes:
        if input("Continue? (yes/no/dry-run): ").strip().lower() not in ("yes", "y"):
            return
    ok = sum(migrate_chat(c, claude_ws, project, dry_run=args.dry_run) for c in chats)
    print(f"Done: {ok}/{len(chats)}")


if __name__ == "__main__":
    main()
```

## How to run

```bash
# Preview
python3 migrate_cursor_to_claude.py --project ~/dev/my-app --dry-run

# Migrate
python3 migrate_cursor_to_claude.py --project ~/dev/my-app --yes

# Last 30 days only
python3 migrate_cursor_to_claude.py --project ~/dev/my-app --days 30 --dry-run
```

## Verify in Claude Code

1. `cd ~/dev/my-app && claude`
2. `claude --resume` — migrated sessions should appear
3. `grep -l '"entrypoint": "cursor-migrated"' ~/.claude/projects/-Users-you-dev-my-app/*.jsonl`

## Safety features

- Non-destructive (Cursor files unchanged)
- Dry-run mode
- Per-chat error handling
- Fresh UUIDs per session

## Selective migration

Use `--days 30` to filter by file modification time.

## Rollback

```bash
grep -l '"entrypoint": "cursor-migrated"' ~/.claude/projects/-Users-you-dev-my-app/*.jsonl
# Remove those files only — deleting the whole folder removes native Claude sessions too
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No transcripts found | Match `--project` to Cursor's absolute path; list `~/.cursor/projects/*/agent-transcripts` |
| Chat fails | Validate JSONL: `python3 -m json.tool < file.jsonl` |
| Not in Claude UI | Restart Claude Code; check path hash (leading dash) |
| Permission denied | `chmod -R u+w ~/.claude/projects/` |

## FAQ

**Will migrated chats appear in history?** Yes, when JSONL lands in the correct `~/.claude/projects/<path-hash>/` folder.

**Are Cursor files modified?** No.

**What about Composer / state.vscdb?** Use the [state.vscdb export guide](./export-cursor-chat-history-vscdb.html).
