#!/usr/bin/env python3
"""Apply span-based syntax highlighting to blog/solution HTML files."""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from highlight_code import already_highlighted, detect_lang, highlight

BLOCK_RE = re.compile(
    r"<pre><code(?:\s+class=\"language-([\w-]+)\")?>([\s\S]*?)</code></pre>",
    re.MULTILINE,
)

SPAN_RE = re.compile(r'<span class="[^"]+">([^<]*)</span>')


def strip_spans(raw: str) -> str:
    return SPAN_RE.sub(r"\1", raw)

HLJS_HEAD_RE = re.compile(
    r"\n?\s*<link rel=\"stylesheet\" href=\"https://cdn\.jsdelivr\.net/gh/highlightjs[^>]+>\n?"
    r"(?:\s*<script src=\"https://cdn\.jsdelivr\.net/gh/highlightjs[^>]+></script>\n?)*",
    re.MULTILINE,
)

CODE_HIGHLIGHT_SCRIPT_RE = re.compile(
    r"\n?\s*<script src=\"(?:\.\./\.\./)?blog/code-highlight\.js\"></script>",
    re.MULTILINE,
)

DOUBLE_ENTITY_RE = re.compile(r"&amp;(gt|lt|amp);")


def fix_double_entities(text: str) -> str:
    """Fix over-escaped entities in prose/tables (not inside code blocks)."""
    parts: list[str] = []
    last = 0
    for m in BLOCK_RE.finditer(text):
        chunk = text[last : m.start()]
        chunk = DOUBLE_ENTITY_RE.sub(r"&\1;", chunk)
        parts.append(chunk)
        parts.append(m.group(0))
        last = m.end()
    chunk = text[last:]
    chunk = DOUBLE_ENTITY_RE.sub(r"&\1;", chunk)
    parts.append(chunk)
    return "".join(parts)


def unescape_code(raw: str) -> str:
    code = html.unescape(raw)
    # Strip valid highlight spans
    code = re.sub(r'<span class="[^"]+">', '', code)
    code = re.sub(r'</span>', '', code)
    # Strip legacy corrupted span markup
    code = re.sub(r'span class="(?:kw|fn|str|num|cm)"&gt;', '', code)
    code = re.sub(r'&lt;/span&gt;', '', code)
    code = re.sub(r'&lt;span class="(?:kw|fn|str|num|cm)"&gt;', '', code)
    return code


def process_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    text = fix_double_entities(text)

    def repl(m: re.Match[str]) -> str:
        hinted = m.group(1)
        raw = m.group(2)
        code = unescape_code(strip_spans(raw) if already_highlighted(raw) else raw)
        lang = detect_lang(code, hinted)
        inner = highlight(code, lang)
        return f"<pre><code>{inner}</code></pre>"

    text = BLOCK_RE.sub(repl, text)
    text = HLJS_HEAD_RE.sub("\n", text)
    text = CODE_HIGHLIGHT_SCRIPT_RE.sub("", text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def html_targets(arg: Path) -> list[Path]:
    if arg.is_file():
        return [arg]
    if arg.is_dir():
        return sorted(arg.rglob("index.html")) if arg.name in ("posts", "solutions") else sorted(arg.glob("*.html"))
    return []


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    target = Path(argv[1]) if len(argv) > 1 else root / "blog" / "posts"
    paths = html_targets(target)
    if not paths:
        print(f"no HTML files at {target}", file=sys.stderr)
        return 1
    changed = 0
    for path in paths:
        if process_html(path):
            print(f"updated {path}")
            changed += 1
    print(f"done — {changed} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
