#!/usr/bin/env python3
"""Export Cursor Composer chat history from local state.vscdb (read-only).

Usage:
  python3 cursor_export.py --out ./cursor-export
  python3 cursor_export.py --composer-id <uuid> --out ./cursor-export
  python3 cursor_export.py --list
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}\b")
SECRET_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
]


def cursor_paths() -> dict[str, Path]:
    home = Path.home()
    if sys.platform == "darwin":
        base = home / "Library/Application Support/Cursor"
    elif sys.platform == "win32":
        base = home / "AppData/Roaming/Cursor"
    else:
        base = home / ".config/Cursor"
    return {
        "global_db": base / "User/globalStorage/state.vscdb",
        "workspace_root": base / "User/workspaceStorage",
        "plans": home / ".cursor/plans",
        "projects": home / ".cursor/projects",
    }


def redact(text: str) -> str:
    if not text:
        return text
    text = JWT_RE.sub("<REDACTED_JWT>", text)
    for pat in SECRET_RES:
        text = pat.sub("<REDACTED_SECRET>", text)
    return text


@contextmanager
def ro_sqlite(path: Path) -> Iterator[sqlite3.Connection]:
    if not path.exists():
        raise FileNotFoundError(path)
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5.0)
    try:
        yield con
    finally:
        con.close()


def _parse_json(val: Any) -> Any:
    if isinstance(val, (bytes, bytearray)):
        val = val.decode("utf-8", errors="replace")
    return json.loads(val)


def workspace_folders(root: Path) -> dict[str, Optional[str]]:
    out: dict[str, Optional[str]] = {}
    if not root.exists():
        return out
    for ws in root.iterdir():
        if not ws.is_dir():
            continue
        folder = None
        wj = ws / "workspace.json"
        if wj.exists():
            try:
                folder = json.loads(wj.read_text()).get("folder")
            except Exception:
                pass
        out[ws.name] = folder
    return out


def list_composers(global_db: Path, workspace_root: Path, limit: int = 500) -> list[dict]:
    folders = workspace_folders(workspace_root)
    by_id: dict[str, dict] = {}

    if global_db.exists():
        with ro_sqlite(global_db) as con:
            row = con.execute(
                "SELECT value FROM ItemTable WHERE key = 'composer.composerHeaders'"
            ).fetchone()
            if row:
                data = _parse_json(row[0])
                for c in (data.get("allComposers") or []):
                    if not isinstance(c, dict):
                        continue
                    cid = c.get("composerId")
                    if not cid:
                        continue
                    wi = c.get("workspaceIdentifier") or {}
                    ws_id = wi.get("id") if isinstance(wi, dict) else None
                    by_id[cid] = {
                        "composerId": cid,
                        "name": redact(str(c.get("name") or ""))[:200],
                        "createdAt": c.get("createdAt"),
                        "lastUpdatedAt": c.get("lastUpdatedAt"),
                        "workspace": ws_id,
                        "workspaceFolder": folders.get(str(ws_id)) if ws_id else None,
                    }

    # Fallback: older Cursor builds store composer lists per workspace
    if workspace_root.exists():
        for ws in workspace_root.iterdir():
            ws_db = ws / "state.vscdb"
            if not ws_db.exists():
                continue
            try:
                with ro_sqlite(ws_db) as con:
                    row = con.execute(
                        "SELECT value FROM ItemTable WHERE key = 'composer.composerData'"
                    ).fetchone()
            except Exception:
                continue
            if not row:
                continue
            try:
                data = _parse_json(row[0])
            except Exception:
                continue
            for c in (data.get("allComposers") or []):
                if not isinstance(c, dict):
                    continue
                cid = c.get("composerId")
                if not cid or cid in by_id:
                    continue
                by_id[cid] = {
                    "composerId": cid,
                    "name": redact(str(c.get("name") or ""))[:200],
                    "createdAt": c.get("createdAt"),
                    "lastUpdatedAt": c.get("lastUpdatedAt"),
                    "workspace": ws.name,
                    "workspaceFolder": folders.get(ws.name),
                }

    return sorted(
        by_id.values(),
        key=lambda x: x.get("lastUpdatedAt") or 0,
        reverse=True,
    )[:limit]


def _bubble_order(meta: dict) -> dict[str, int]:
    headers = meta.get("fullConversationHeadersOnly") or []
    return {
        h["bubbleId"]: i
        for i, h in enumerate(headers)
        if isinstance(h, dict) and h.get("bubbleId")
    }


def load_conversation(global_db: Path, composer_id: str, max_chars: int = 8000) -> dict:
    out: dict[str, Any] = {"composerId": composer_id, "bubbles": []}
    with ro_sqlite(global_db) as con:
        meta_row = con.execute(
            "SELECT value FROM cursorDiskKV WHERE key = ?",
            (f"composerData:{composer_id}",),
        ).fetchone()
        meta = _parse_json(meta_row[0]) if meta_row else {}
        order = _bubble_order(meta) if isinstance(meta, dict) else {}
        restrict = bool(order)

        rows = con.execute(
            "SELECT key, value FROM cursorDiskKV WHERE key LIKE ?",
            (f"bubbleId:{composer_id}:%",),
        ).fetchall()

    bubbles: list[tuple, dict] = []
    for idx, (key, val) in enumerate(rows):
        try:
            d = _parse_json(val)
        except Exception:
            continue
        bubble_id = key.rsplit(":", 1)[-1]
        if restrict and bubble_id not in order:
            continue
        sort_key = (0, order.get(bubble_id, idx)) if restrict else (1, idx)
        kind = "user" if d.get("type") == 1 else "assistant" if d.get("type") == 2 else "other"
        text = d.get("text") or d.get("richText") or ""
        if isinstance(text, list):
            text = " ".join(
                str(x.get("text", "")) for x in text if isinstance(x, dict)
            )
        bubbles.append((sort_key, {
            "bubbleId": bubble_id,
            "role": kind,
            "text": redact(str(text))[:max_chars],
        }))

    bubbles.sort(key=lambda t: t[0])
    out["bubbles"] = [b for _, b in bubbles]
    out["name"] = redact(str(meta.get("name") or "")) if isinstance(meta, dict) else ""
    return out


def to_markdown(conv: dict) -> str:
    title = conv.get("name") or conv.get("composerId", "untitled")
    lines = [f"# {title}", "", f"composerId: `{conv.get('composerId')}`", ""]
    for b in conv.get("bubbles") or []:
        role = "User" if b["role"] == "user" else "Assistant"
        lines += [f"## {role}", "", b.get("text", ""), ""]
    return "\n".join(lines)


def copy_plans(plans_root: Path, out_dir: Path) -> int:
    if not plans_root.exists():
        return 0
    dest = out_dir / "plans"
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in plans_root.glob("*.plan.md"):
        dest.joinpath(p.name).write_text(p.read_text(encoding="utf-8", errors="replace"))
        n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description="Export Cursor chat history from state.vscdb")
    ap.add_argument("--out", type=Path, default=Path("cursor-export"))
    ap.add_argument("--composer-id", help="Export a single composer UUID")
    ap.add_argument("--list", action="store_true", help="List composers and exit")
    ap.add_argument("--max-chars", type=int, default=8000, help="Max chars per bubble")
    args = ap.parse_args()

    paths = cursor_paths()
    gdb = paths["global_db"]
    if not gdb.exists():
        sys.exit(f"Cursor global DB not found: {gdb}")

    composers = list_composers(gdb, paths["workspace_root"])
    if args.list:
        for c in composers:
            print(f"{c['composerId']}\t{c.get('lastUpdatedAt')}\t{c.get('name')}")
        return

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "chats").mkdir(exist_ok=True)
    (args.out / "composers.json").write_text(
        json.dumps(composers, indent=2), encoding="utf-8"
    )

    targets = composers
    if args.composer_id:
        targets = [c for c in composers if c["composerId"] == args.composer_id]
        if not targets:
            targets = [{"composerId": args.composer_id, "name": args.composer_id}]

    for c in targets:
        cid = c["composerId"]
        conv = load_conversation(gdb, cid, max_chars=args.max_chars)
        (args.out / "chats" / f"{cid}.json").write_text(
            json.dumps(conv, indent=2), encoding="utf-8"
        )
        (args.out / "chats" / f"{cid}.md").write_text(to_markdown(conv), encoding="utf-8")

    n_plans = copy_plans(paths["plans"], args.out)
    print(f"Exported {len(targets)} chat(s), {n_plans} plan file(s) → {args.out.resolve()}")


if __name__ == "__main__":
    main()
