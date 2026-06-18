#!/usr/bin/env python3
"""Highlight code blocks for stackcone blog posts (span.kw/fn/str/num/cm)."""
from __future__ import annotations

import html
import re
from typing import Callable

PY_KEYWORDS = frozenset({
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "False", "finally", "for",
    "from", "global", "if", "import", "in", "is", "lambda", "None",
    "nonlocal", "not", "or", "pass", "raise", "return", "True", "try",
    "while", "with", "yield",
})

PY_BUILTINS = frozenset({
    "Any", "bool", "dict", "enumerate", "Exception", "float", "int", "json",
    "len", "list", "max", "min", "open", "Optional", "Path", "print",
    "range", "set", "str", "sum", "tuple", "type", "zip",
})

JS_KEYWORDS = frozenset({
    "async", "await", "const", "function", "if", "else", "for", "in", "let",
    "new", "of", "return", "throw", "try", "var", "while", "yield",
})


def _span(cls: str, text: str) -> str:
    return f'<span class="{cls}">{html.escape(text, quote=False)}</span>'


def _highlight_identifiers(
    text: str,
    keywords: frozenset[str],
    builtins: frozenset[str],
    fn_after_def: bool = True,
) -> str:
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isdigit() or (ch == "." and i + 1 < n and text[i + 1].isdigit()):
            j = i
            while j < n and (text[j].isdigit() or text[j] == "."):
                j += 1
            parts.append(_span("num", text[i:j]))
            i = j
            continue
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            word = text[i:j]
            if word in keywords:
                parts.append(_span("kw", word))
            elif word in builtins:
                parts.append(_span("fn", word))
            elif fn_after_def and i >= 4 and text[i - 4 : i] == "def ":
                parts.append(_span("fn", word))
            else:
                parts.append(html.escape(word, quote=False))
            i = j
            continue
        parts.append(html.escape(ch, quote=False))
        i += 1
    return "".join(parts)


def highlight_python(src: str) -> str:
    chunks: list[str] = []
    pos = 0
    for m in re.finditer(
        r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|#[^\n]*)',
        src,
    ):
        chunks.append(
            _highlight_identifiers(src[pos : m.start()], PY_KEYWORDS, PY_BUILTINS)
        )
        token = m.group(0)
        if token.startswith("#"):
            chunks.append(_span("cm", token))
        else:
            chunks.append(_span("str", token))
        pos = m.end()
    chunks.append(_highlight_identifiers(src[pos:], PY_KEYWORDS, PY_BUILTINS))
    return "".join(chunks)


def highlight_bash(src: str) -> str:
    lines_out: list[str] = []
    for line in src.split("\n"):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            lines_out.append(_span("cm", line))
        else:
            parts: list[str] = []
            indent = len(line) - len(stripped)
            if indent:
                parts.append(html.escape(line[:indent], quote=False))
            if stripped:
                m = re.match(r"^([a-zA-Z0-9_./-]+)", stripped)
                cmds = {
                    "python3", "pip", "npm", "curl", "grep", "find", "ls", "head",
                    "chmod", "cd", "mkdocs", "source", "rm", "wc", "cat",
                }
                if m and m.group(1) in cmds:
                    parts.append(_span("fn", m.group(1)))
                    rest = stripped[m.end() :]
                    if "#" in rest:
                        code, _, comment = rest.partition("#")
                        parts.append(html.escape(code, quote=False))
                        parts.append(_span("cm", "#" + comment))
                    else:
                        parts.append(html.escape(rest, quote=False))
                elif "#" in stripped:
                    code, _, comment = stripped.partition("#")
                    parts.append(html.escape(code, quote=False))
                    parts.append(_span("cm", "#" + comment))
                else:
                    parts.append(html.escape(stripped, quote=False))
            lines_out.append("".join(parts))
    return "\n".join(lines_out)


def highlight_json(src: str) -> str:
    out: list[str] = []
    pos = 0
    for m in re.finditer(
        r'"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|\btrue\b|\bfalse\b|\bnull\b',
        src,
    ):
        out.append(html.escape(src[pos : m.start()], quote=False))
        token = m.group(0)
        if token.startswith('"'):
            out.append(_span("str", token))
        elif token in ("true", "false", "null"):
            out.append(_span("kw", token))
        else:
            out.append(_span("num", token))
        pos = m.end()
    out.append(html.escape(src[pos:], quote=False))
    return "".join(out)


def highlight_javascript(src: str) -> str:
    chunks: list[str] = []
    pos = 0
    for m in re.finditer(
        r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|//[^\n]*',
        src,
    ):
        chunks.append(
            _highlight_identifiers(
                src[pos : m.start()], JS_KEYWORDS, frozenset(), fn_after_def=False
            )
        )
        token = m.group(0)
        if token.startswith("//"):
            chunks.append(_span("cm", token))
        else:
            chunks.append(_span("str", token))
        pos = m.end()
    chunks.append(
        _highlight_identifiers(
            src[pos:], JS_KEYWORDS, frozenset(), fn_after_def=False
        )
    )
    return re.sub(
        r"\b(function|async)\s+([a-zA-Z_$][\w$]*)",
        lambda m: f'{_span("kw", m.group(1))} {_span("fn", m.group(2))}',
        "".join(chunks),
    )


def highlight_text(src: str) -> str:
    lines_out: list[str] = []
    for line in src.split("\n"):
        if "#" in line and not line.strip().startswith("{"):
            code, _, comment = line.partition("#")
            lines_out.append(
                html.escape(code, quote=False) + _span("cm", "#" + comment)
            )
        elif "//" in line:
            code, _, comment = line.partition("//")
            lines_out.append(
                html.escape(code, quote=False) + _span("cm", "//" + comment)
            )
        else:
            lines_out.append(html.escape(line, quote=False))
    return "\n".join(lines_out)


def highlight(src: str, lang: str) -> str:
    lang = lang.lower()
    if lang in ("python", "py"):
        return highlight_python(src)
    if lang in ("bash", "sh", "shell"):
        return highlight_bash(src)
    if lang in ("json",):
        return highlight_json(src)
    if lang in ("javascript", "js", "typescript", "ts"):
        return highlight_javascript(src)
    return highlight_text(src)


def detect_lang(code: str, hinted: str | None) -> str:
    if hinted and hinted not in ("text", "markdown", "md"):
        return hinted
    s = code.lstrip()
    if s.startswith("#!/usr/bin/env python") or re.search(r"^(import |from |def )", s, re.M):
        return "python"
    if s.startswith("{") or s.startswith("["):
        return "json"
    if re.match(r"^(python3|pip |curl |grep |ls |find |chmod |cd |mkdocs )", s):
        return "bash"
    if re.search(r"\b(function|const|let|async)\b", s):
        return "javascript"
    return "text"


def already_highlighted(code: str) -> bool:
    return '<span class="' in code
