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

SQL_KEYWORDS = frozenset({
    "select", "from", "where", "join", "left", "right", "inner", "outer", "full",
    "cross", "on", "as", "case", "when", "then", "else", "end", "and", "or",
    "not", "null", "is", "in", "group", "by", "order", "having", "limit",
    "offset", "union", "all", "distinct", "insert", "into", "update", "set",
    "delete", "create", "table", "view", "index", "with", "over", "partition",
    "between", "like", "exists", "using", "natural", "merge",
})

SQL_FUNCTIONS = frozenset({
    "coalesce", "count", "sum", "avg", "min", "max", "cast", "concat", "date",
    "timestamp", "ifnull", "nvl", "row_number", "rank", "dense_rank", "lead",
    "lag", "extract", "date_trunc", "safe_cast", "array_agg", "string_agg",
})

DART_KEYWORDS = frozenset({
    "abstract", "as", "assert", "async", "await", "break", "case", "catch",
    "class", "const", "continue", "default", "do", "else", "enum", "extends",
    "factory", "false", "final", "finally", "for", "if", "import", "in", "is",
    "late", "library", "new", "null", "part", "rethrow", "return", "static",
    "super", "switch", "sync", "this", "throw", "true", "try", "var", "void",
    "while", "with", "yield",
})

DART_TYPES = frozenset({
    "Future", "Stream", "Provider", "String", "int", "bool", "double", "num",
    "List", "Map", "Set", "dynamic", "Object", "DateTime", "Widget", "State",
    "DocumentSnapshot", "FirebaseAuth", "FirebaseFirestore", "GoRouter",
    "GoogleSignIn", "FirebaseAuthException", "OAuthProvider", "WidgetRef",
    "StreamProvider", "GoRoute", "UserProfile", "SetOptions", "Timestamp",
})

KOTLIN_KEYWORDS = frozenset({
    "plugins", "android", "namespace", "defaultConfig", "applicationId",
    "version", "apply", "false", "true", "id", "kotlin",
})

RUBY_KEYWORDS = frozenset({
    "target", "do", "end", "use_frameworks", "linkage", "static", "def",
})

RULES_KEYWORDS = frozenset({
    "rules_version", "service", "cloud", "firestore", "match", "allow",
    "read", "write", "if", "request", "auth", "null", "true", "false",
})


def _highlight_quoted(
    src: str,
    keywords: frozenset[str],
    builtins: frozenset[str],
    string_pattern: str,
    line_comments: tuple[str, ...] = ("//", "#"),
) -> str:
    chunks: list[str] = []
    pos = 0
    for m in re.finditer(string_pattern, src):
        chunks.append(
            _highlight_identifiers(
                src[pos : m.start()], keywords, builtins, fn_after_def=False
            )
        )
        token = m.group(0)
        if any(token.startswith(prefix) for prefix in line_comments):
            chunks.append(_span("cm", token))
        else:
            chunks.append(_span("str", token))
        pos = m.end()
    chunks.append(
        _highlight_identifiers(
            src[pos:], keywords, builtins, fn_after_def=False
        )
    )
    return "".join(chunks)


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
                    "flutter", "dart", "keytool",
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


def highlight_dart(src: str) -> str:
    return _highlight_quoted(
        src,
        DART_KEYWORDS,
        DART_TYPES,
        r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*)',
    )


def highlight_kotlin(src: str) -> str:
    return _highlight_quoted(
        src,
        KOTLIN_KEYWORDS,
        frozenset(),
        r'"(?:\\.|[^"\\])*"|//[^\n]*',
    )


def highlight_ruby(src: str) -> str:
    return _highlight_quoted(
        src,
        RUBY_KEYWORDS,
        frozenset({"File"}),
        r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|#[^\n]*',
    )


def highlight_xml(src: str) -> str:
    parts: list[str] = []
    pos = 0
    for m in re.finditer(r"(<\!--[\s\S]*?-->|<\/?[\w:-]+>|[^<]+)", src):
        token = m.group(0)
        if token.startswith("<!--"):
            parts.append(_span("cm", token))
        elif token.startswith("<"):
            parts.append(_span("kw", token))
        else:
            parts.append(html.escape(token, quote=False))
        pos = m.end()
    parts.append(html.escape(src[pos:], quote=False))
    return "".join(parts)


def highlight_rules(src: str) -> str:
    return _highlight_quoted(
        src,
        RULES_KEYWORDS,
        frozenset(),
        r'"(?:\\.|[^"\\])*"|//[^\n]*',
        line_comments=("//",),
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


def _highlight_yaml_tail(tail: str) -> str:
    if not tail:
        return ""
    chunks: list[str] = []
    pos = 0
    for m in re.finditer(
        r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|(?<![A-Za-z0-9_.@])-?\d+(?:\.\d+)?(?![A-Za-z0-9_])|\b(true|false|null)\b',
        tail,
    ):
        chunks.append(html.escape(tail[pos : m.start()], quote=False))
        token = m.group(0)
        if token[0] in "\"'":
            chunks.append(_span("str", token))
        elif token in ("true", "false", "null"):
            chunks.append(_span("kw", token))
        else:
            chunks.append(_span("num", token))
        pos = m.end()
    chunks.append(html.escape(tail[pos:], quote=False))
    return "".join(chunks)


def _highlight_yaml_kv_line(line: str) -> str:
    stripped = line.lstrip()
    indent = line[: len(line) - len(stripped)]
    if stripped.startswith("#"):
        return html.escape(indent, quote=False) + _span("cm", stripped)
    bullet_m = re.match(r"^(-\s+)(.*)$", stripped)
    if bullet_m:
        bullet, rest = bullet_m.groups()
        inner = _highlight_yaml_kv_line(rest) if ":" in rest else html.escape(rest, quote=False)
        return html.escape(indent, quote=False) + html.escape(bullet, quote=False) + inner
    m = re.match(r"^([\w@./$-]+)(\s*:\s*)(.*)$", stripped)
    if m:
        key, colon_space, rest = m.groups()
        return (
            html.escape(indent, quote=False)
            + _span("fn", key)
            + html.escape(colon_space, quote=False)
            + _highlight_yaml_tail(rest)
        )
    return html.escape(line, quote=False)


def highlight_yaml(src: str) -> str:
    return "\n".join(_highlight_yaml_kv_line(line) for line in src.split("\n"))


def _highlight_markdown_inline(text: str) -> str:
    chunks: list[str] = []
    pos = 0
    for m in re.finditer(r"`([^`]+)`", text):
        chunks.append(html.escape(text[pos : m.start()], quote=False))
        chunks.append(_span("str", f"`{m.group(1)}`"))
        pos = m.end()
    chunks.append(html.escape(text[pos:], quote=False))
    return "".join(chunks)


def _highlight_sql_identifiers(text: str) -> str:
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "@" and i + 1 < n and (text[i + 1].isalpha() or text[i + 1] == "_"):
            j = i + 1
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            parts.append(_span("fn", text[i:j]))
            i = j
            continue
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
            lower = word.lower()
            if lower in SQL_KEYWORDS:
                parts.append(_span("kw", word))
            elif lower in SQL_FUNCTIONS:
                parts.append(_span("fn", word))
            else:
                parts.append(html.escape(word, quote=False))
            i = j
            continue
        parts.append(html.escape(ch, quote=False))
        i += 1
    return "".join(parts)


def highlight_sql(src: str) -> str:
    chunks: list[str] = []
    pos = 0
    for m in re.finditer(r"(--[^\n]*|'(?:''|[^'])*')", src):
        chunks.append(_highlight_sql_identifiers(src[pos : m.start()]))
        token = m.group(0)
        if token.startswith("--"):
            chunks.append(_span("cm", token))
        else:
            chunks.append(_span("str", token))
        pos = m.end()
    chunks.append(_highlight_sql_identifiers(src[pos:]))
    return "".join(chunks)


def highlight_markdown(src: str) -> str:
    lines_out: list[str] = []
    in_frontmatter = False
    frontmatter_started = False
    for line in src.split("\n"):
        stripped = line.strip()
        if stripped == "---":
            lines_out.append(_span("kw", "---"))
            if not frontmatter_started:
                frontmatter_started = True
                in_frontmatter = True
            elif in_frontmatter:
                in_frontmatter = False
            continue
        if in_frontmatter:
            lines_out.append(_highlight_yaml_kv_line(line))
            continue
        header = re.match(r"^(#{1,6})\s+(.*)$", line)
        if header:
            hashes, title = header.groups()
            indent = line[: len(line) - len(line.lstrip())]
            lines_out.append(
                html.escape(indent, quote=False)
                + _span("kw", hashes)
                + " "
                + _highlight_markdown_inline(title)
            )
            continue
        lines_out.append(_highlight_markdown_inline(line))
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
    if lang in ("yaml", "yml"):
        return highlight_yaml(src)
    if lang in ("markdown", "md"):
        return highlight_markdown(src)
    if lang in ("sql",):
        return highlight_sql(src)
    if lang in ("dart",):
        return highlight_dart(src)
    if lang in ("kotlin", "gradle", "kts"):
        return highlight_kotlin(src)
    if lang in ("ruby", "rb", "podfile"):
        return highlight_ruby(src)
    if lang in ("xml", "plist"):
        return highlight_xml(src)
    if lang in ("rules", "firestore-rules"):
        return highlight_rules(src)
    return highlight_text(src)


def detect_lang(code: str, hinted: str | None) -> str:
    if hinted:
        hint = hinted.lower()
        if hint in ("yaml", "yml"):
            return "yaml"
        if hint in ("markdown", "md"):
            return "markdown"
        if hint not in ("text",):
            return hint
    s = code.lstrip()
    if s.startswith("#!/usr/bin/env python") or re.search(r"^def ", s, re.M):
        return "python"
    if s.startswith("<") and re.search(r"<\/?[\w:-]+", s):
        return "xml"
    if s.startswith("rules_version") or "service cloud.firestore" in s:
        return "rules"
    if re.search(r"^import '(?:dart|package):", s, re.M) or re.match(
        r"^(class |Future<|final |const |bool get |await )", s
    ):
        return "dart"
    if re.search(r"^plugins\s*\{", s) or re.search(r"^android\s*\{", s):
        return "kotlin"
    if re.match(r"^target ['\"]", s) or "use_frameworks!" in s:
        return "ruby"
    if s.startswith("{") or s.startswith("["):
        return "json"
    if re.match(r"^(flutter |dart pub|keytool |python3|pip |curl |grep |ls |find |chmod |cd |mkdocs )", s):
        return "bash"
    if re.search(r"^\s*SELECT\b", s, re.I) or re.search(
        r"\b(SELECT|FROM|JOIN|WHERE|GROUP BY|ORDER BY)\b", s, re.I
    ):
        return "sql"
    if s.startswith("dependencies:") or re.search(
        r"^[a-z_]+:\s*[\^~]?\d", s, re.M
    ):
        return "yaml"
    if re.search(r"^(const|let|var)\s", s, re.M) or "socket.on" in s or "=>" in s:
        return "javascript"
    if re.search(r"\bfunction\b", s):
        return "javascript"
    if re.search(r"^if len\(", s, re.M) or "ThreadPoolExecutor" in s:
        return "python"
    if re.match(r"^name:\s", s) or re.match(r"^on:\s", s) or re.search(r"^jobs:\s*$", s, re.M):
        return "yaml"
    if s.startswith("---") or re.match(r"^#{1,6}\s", s) or re.search(r"^#{1,6}\s", s, re.M):
        return "markdown"
    return "text"


def already_highlighted(code: str) -> bool:
    return '<span class="' in code
