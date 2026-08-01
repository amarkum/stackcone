# How I Built a Live-Browser AI Coding Agent with Flask and Monaco

## Overview

**LiveCode Agent** is an in-browser AI coding agent that works like Cursor Agent mode or Claude Code: an LLM gets tools to read, search, edit, and run commands against a real project on disk, iterates in a controlled loop, and streams diffs, tool activity, and shell output back to a browser UI in real time.

No LangChain. No vector database. No webpack build pipeline. The stack is:

- A Python package (`livecode/`) — agent loop, tools, sessions, compaction (~4,400 lines)
- A Flask route module — turn endpoint + session CRUD (~280 lines)
- A frontend JS file — Monaco, terminal, chat, streaming (~3,600 lines)
- Two CSS files and HTML templates

This post is a technical deep-dive with pseudocode for every major subsystem.

## Table of contents

1. [System architecture](#system-architecture)
2. [Backend package layout](#backend-package-layout)
3. [The agent harness loop](#the-agent-harness-loop)
4. [Tool system](#tool-system)
5. [Codebase indexing](#codebase-indexing)
6. [Session persistence](#session-persistence)
7. [Context compaction — three tiers](#context-compaction)
8. [Memory, routing, permissions](#memory-routing-permissions)
9. [Sub-agents](#sub-agents)
10. [Real-time: SSE + WebSocket](#real-time-communication)
11. [Frontend: Monaco, terminal, chat](#frontend-architecture)
12. [Diff generation](#diff-generation)
13. [Project rules discovery](#project-rules)
14. [Design decisions](#design-decisions)
15. [FAQ](#faq)

## System architecture

### Two halves, two channels

```
Browser
  │
  ├── fetch() + ReadableStream ──► POST /livecode-agent (SSE)
  │         token │ answer │ done
  │
  └── WebSocket / Socket.IO ◄──── tool_call │ diff_block │ permission_request
```

**SSE** streams the model's final answer text. **WebSocket** (or Socket.IO) carries structured progress: tool labels, diffs, shell streams, permission prompts.

### Why fetch() instead of EventSource

`EventSource` only supports GET. The turn endpoint needs a JSON body (message, session id, model). The client uses `fetch()` + manual `ReadableStream` parsing (~60 lines).

### Flask turn endpoint (pseudocode)

```python
@app.post("/livecode-agent")
def agent_turn():
    body = request.get_json()
    session_id = body["session_id"]
    question = body["question"]
    model = body.get("model", "auto")

    def generate():
        for chunk in run_livecode_turn(
            question=question,
            project_path=body["project_path"],
            session_id=session_id,
            model=model,
        ):
            yield chunk  # already formatted as "data: {...}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
```

After the generator finishes, append canonical messages to `chat_history.jsonl`.

## Backend package layout

| Module | Responsibility |
|--------|----------------|
| `harness.py` | Generator loop, classification, LLM calls, tool dispatch |
| `tools.py` | 14 tool schemas + `dispatch_tool()` |
| `prompts.py` | System prompts, compaction prompts, constants |
| `session.py` | JSONL persistence, projection, sanitization |
| `codebase_index.py` | AST + regex symbol index |
| `workspace.py` | File manifest, safe path resolution |
| `compaction/` | Intra, inter, full-replace compaction |
| `memory.py` | Flat markdown memory per project |
| `routing.py` | Heuristic + LLM classification |
| `permissions.py` | Blocking gate for write/edit/shell |
| `subagent.py` | Nested 5-iteration child runs |
| `rules.py` | AGENTS.md / CLAUDE.md discovery |

### Key constants

```python
MAX_ITERATIONS = 20
CONTEXT_WINDOW = 128_000
AUTO_COMPACT_RATIO = 0.85      # 108,800 tokens
INTER_COMPACT_RATIO = 0.65     # 83,200 tokens
IN_TURN_COMPACT_RATIO = 0.70 # 89,600 tokens
KEEP_RECENT_TOOL_MSGS = 6
STATIONARITY_NUDGE_AFTER = 8
STATIONARITY_HARD_STOP = 16
TOOL_RESULT_MAX_CHARS = 16_000
```

## The agent harness loop

`run_livecode_turn()` is a **generator** yielding SSE strings.

### Turn setup

```python
def run_livecode_turn(question, project_path, session_id, model):
    classification = classify_turn(question)  # heuristics, then LLM fallback
    build_workspace_index(project_path)
    get_codebase_index(project_path)
    maybe_compact_session(session_dir)
    messages = build_base_messages(
        system=build_system_prompt(project_path),
        history=get_projected_messages(session_dir),
        user=question,
        rules=discover_project_rules(project_path),
    )
    turn_persist = []
    # ... enter loop
```

### Iteration loop (pseudocode)

```python
for iteration in range(1, MAX_ITERATIONS + 1):
    if stationarity_tracker.should_hard_stop():
        yield sse_done("Stopped: repeated identical tool calls.")
        return

    if stationarity_tracker.should_nudge():
        messages.append({"role": "user", "content": STATIONARITY_NUDGE})

    messages = compact_stale_tool_messages(messages, budget=89600)
    messages.extend(drain_interjection_queue(session_id))
    messages = sanitize_messages_for_api(messages)

    response = call_llm_with_tools(
        model=pick_model(classification, iteration),
        messages=messages,
        tools=LIVECODE_TOOLS,
        tool_choice=pick_tool_choice(classification, iteration),
    )

    if response.tool_calls:
        results = dispatch_tools_parallel_or_serial(response.tool_calls)
        for tc, result in zip(response.tool_calls, results):
            messages.append(tool_message(tc, compact(result)))
            turn_persist.append(tool_message(tc, result))
            if tc.name in ("write_file", "edit_file"):
                emit_diff_over_websocket(result)
        continue

    if iteration == 1 and needs_codebase_evidence(question) and not used_tools:
        messages.append({"role": "user", "content": CODEBASE_RECOVERY_PROMPT})
        force_tool_choice = True
        continue

    if response.content:
        yield stream_answer(response.content)
        yield sse_done(answer=response.content, turn_messages=turn_persist)
        return

# Exhaustion fallback
messages.append({"role": "user", "content": "Summarize without more tools."})
yield sse_done(answer=call_llm_no_tools(messages))
```

### Stationarity detection

```python
def fingerprint(tool_name, arguments):
    return f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"

class IdenticalToolCallRun:
    def __init__(self):
        self.last = None
        self.count = 0

    def observe(self, tool_name, arguments):
        fp = fingerprint(tool_name, arguments)
        self.count = self.count + 1 if fp == self.last else 1
        self.last = fp
        return self.count
```

At 8 repeats: inject nudge. At 16: force-terminate.

## Tool system

### Tool list (14 core tools)

| Tool | Purpose |
|------|---------|
| `find_symbol` | Substring search on symbol index |
| `find_references` | Regex `\bname\b` across indexed files |
| `list_symbols` | Filter symbols by path prefix |
| `grep_repo` | ripgrep subprocess |
| `read_repo_file` | Max 300 numbered lines |
| `list_repo_dir` | Tree or directory listing |
| `write_file` | Full file write + diff |
| `edit_file` | SEARCH/REPLACE with ambiguity rejection |
| `run_command` | Shell with blocklist + stream |
| `git_log` | Structured commit list |
| `ast_symbols` | Python AST for one file |
| `update_memory` | Append project memory note |
| `spawn_subagent` | Nested child agent |
| `attempt_completion` | Sentinel to end turn |

### edit_file — ambiguity rejection

```python
def edit_file(path, old_string, new_string):
    content = read_file(path)
    count = content.count(old_string)
    if count == 0:
        return error("old_string not found")
    if count > 1:
        return error("ambiguous match — add more context")
    new_content = content.replace(old_string, new_string, 1)
    write_file(path, new_content)
    return success(diff=create_diff_html(content, new_content))
```

### run_command — safety

```python
BLOCKED = ["rm -rf /", "mkfs", ":(){ :|:& };:"]

def run_command(command):
    if any(p in command for p in BLOCKED):
        return error("blocked pattern")
    if "git log" in command:
        return error("use git_log tool instead")
    if is_quick_command(command):
        return subprocess.run(..., timeout=90)
    return stream_subprocess_over_websocket(command, timeout=600)
```

### Parallel tool dispatch

```python
if len(tool_calls) > 1:
    with ThreadPoolExecutor(max_workers=min(len(tool_calls), 6)) as pool:
        futures = [pool.submit(execute_tool, tc) for tc in tool_calls]
        results = [f.result() for f in futures]  # preserve order
else:
    results = [execute_tool(tool_calls[0])]
```

## Codebase indexing

### File manifest

- Cached at `~/.livecode/index/<project_hash>.json`
- Invalidated by max mtime of project root + top-level entries
- Caps: 8,000 files, 512 KB per file
- Every path goes through `resolve_safe_path()` to block traversal

```python
def resolve_safe_path(root, requested):
    resolved = realpath(join(root, requested))
    if not resolved.startswith(realpath(root)):
        raise PermissionError("path traversal")
    return resolved
```

### Symbol index

- Python: `ast.walk()` for ClassDef, FunctionDef, AsyncFunctionDef
- JS/TS: regex on export/function/class declarations
- Disk cache + optional watchdog live updates
- `find_references` re-reads files at call time (grep-like, not true static analysis)

## Session persistence

```
~/.livecode/sessions/<project_hash>/<session_id>/
  chat_history.jsonl    # append-only OpenAI messages
  summary.json          # metadata + reminders
  compaction.json       # boundary + summary + prefix_hash
  compaction_checkpoints/
```

### Projection with hash verification

```python
def get_projected_messages(session_dir):
    messages = load_jsonl("chat_history.jsonl")
    compaction = load_json("compaction.json")
    if compaction and hash_prefix(messages, compaction) == compaction["prefix_hash"]:
        summary_msg = user_msg(f"[Previous conversation summary]\n{compaction['summary']}")
        return [summary_msg] + messages[compaction["boundary_index"]:]
    return sanitize_messages_for_api(messages)
```

## Context compaction

Three tiers:

```
0% ── 65% ── 70% ── 85% ── 100%
      inter      in-turn   full-replace
                (every iteration)
```

### Tier 1: In-turn (no LLM)

- Dedupe stale `read_repo_file` / `grep_repo` results
- Shrink older tool messages: fitted (2k chars) → lossy (stub JSON)
- Protect last 6 tool messages

### Tier 2: Inter-turn (65–85%)

- Summarize older half of conversation
- Keep newer half verbatim

### Tier 3: Full-replace (≥85%)

- LLM seven-section summary prompt
- Keep last 2–6 messages verbatim
- Store `prefix_hash` for staleness detection
- Retry with shorter prompt if summary is degenerate

```python
def is_degenerate_summary(text):
    return len(text) < 40 or unique_chars(text) < 15
```

## Memory, routing, permissions

### Memory (flat markdown)

```python
MEMORY_READ = 2048
MEMORY_STORE = 6144

def load_memory(project):
    return read_file(path)[-MEMORY_READ:]

def append_memory(project, note):
    content = existing + f"\n- {note}"
    write_file(path, content[-MEMORY_STORE:])
```

### Classification fields

```python
{
  "is_actionable": True,
  "needs_shell": False,
  "chat_only": False,
  "complexity": "medium",  # drives model tier when model=auto
  "expects_multi_step": True,
}
```

### Permission gate

```python
SENSITIVE = {"write_file", "edit_file", "run_command"}

def execute_with_permission(session_id, tool_name, args):
    if tool_name not in SENSITIVE:
        return dispatch_tool(tool_name, args)
    emit_websocket("permission_request", tool=tool_name, args=args)
    approved = wait_on_threading_event(session_id, timeout=300)
    if not approved:
        return error("denied by user")
    return dispatch_tool(tool_name, args)
```

## Sub-agents

```python
def spawn_subagent(instruction, parent_session_id):
    child_id = f"{parent_session_id}_sub_{uuid4().hex[:8]}"
    output = []
    for chunk in run_livecode_turn(
        question=instruction,
        session_id=child_id,
        max_iterations=5,
    ):
        if is_answer_chunk(chunk):
            output.append(chunk)
    return {"result": "".join(output)}
```

Parent only sees the final synthesized result — child tool noise stays out of parent context.

## Real-time communication

### SSE client (pseudocode)

```javascript
const res = await fetch("/livecode-agent", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ question, session_id, model }),
});

const reader = res.body.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });
  for (const block of buffer.split("\n\n")) {
    if (block.startsWith("data: ")) {
      handleSSE(JSON.parse(block.slice(6)));
    }
  }
}
```

### WebSocket progress events

```javascript
socket.on("livecode_progress", (event) => {
  switch (event.type) {
    case "tool_call": appendActivityChip(event.label); break;
    case "diff_block": renderDiff(event.diff_html); break;
    case "permission_request": showApproveDeny(event); break;
    case "compaction": showCompactionNotice(); break;
  }
});
```

## Frontend architecture

Single large JS file (~3,600 lines), no npm build step.

### Monaco editor

```javascript
require.config({ paths: { vs: "/static/monaco/vs" } });
require(["vs/editor/editor.main"], () => {
  window.ideEditor = monaco.editor.create(document.getElementById("ide-monaco"), {
    language: "python",
    theme: "vs-dark",
    automaticLayout: true,
    minimap: { enabled: false },
  });
});
```

### Terminal (xterm.js)

```javascript
const term = new Terminal({ fontFamily: "JetBrains Mono", fontSize: 13 });
term.open(document.getElementById("terminal-pane"));
socket.on("terminal_output", (data) => {
  if (data.tab_id === activeTab) term.write(data.content);
});
```

### Multi-tab chat + sessionStorage

Each chat tab persists state to `sessionStorage` so switching tabs restores messages and input.

### Diff blocks

- Small diffs (≤8 changed lines): auto-expanded
- Large diffs: collapsed behind chevron
- Copy button uses unified diff text from backend

## Diff generation

```python
def create_diff_html(before, after, context_lines=2):
    matcher = difflib.SequenceMatcher(None, before.splitlines(), after.splitlines(), autojunk=False)
    blocks = group_opcodes(matcher.get_opcodes(), context=context_lines)
    html = [render_block(b) for b in blocks]
    unified = difflib.unified_diff(before.splitlines(), after.splitlines())
    additions = count_lines(unified, prefix="+")
    deletions = count_lines(unified, prefix="-")
    return "".join(html), unified_text, additions, deletions
```

Each line renders with gutter bar, line number, +/- sign, and syntax-colored content — same visual language as Cursor-style inline diffs.

## Project rules

```python
RULES_FILES = ["AGENTS.md", "CLAUDE.md", ".cursor/rules", ".claude/rules"]

def discover_rules(project_path):
    found = []
    for directory in walk_from_git_root(project_path):
        for name in RULES_FILES:
            if exists(join(directory, name)):
                found.append(read(join(directory, name)))
    return f"<system-reminder>\n{join(found)}\n</system-reminder>"
```

Injected as a follow-up system message — not baked into the main system prompt string.

## Design decisions

1. **Two channels** — SSE stays simple; WebSocket carries rich JSON events.
2. **Three compaction tiers** — cheap passes first; LLM summarization only at 85%.
3. **Hash-verified compaction** — stale summaries discarded after rewind.
4. **Ambiguity-rejecting edits** — wrong-occurrence edits are worse than a retry.
5. **20-iteration cap with graceful exit** — user always gets a closing answer.
6. **Recency-biased memory** — no embeddings; last N chars of markdown.
7. **No orchestration framework** — generator + dispatch table + JSONL is debuggable end-to-end.

## FAQ

**Do you need LangChain to build a coding agent?**  
No. A generator function, tool schemas, session files, and careful context management are enough.

**Why SSE and WebSocket together?**  
SSE is ideal for token streaming over HTTP POST. WebSocket fits structured tool progress, diffs, and permission modals without parsing complex events from a text stream.

**How do you stop infinite tool loops?**  
Stationarity detection (identical call fingerprints), a 20-iteration hard cap, and a forced summarization pass at exhaustion.

**How is this different from Cursor?**  
Same agent pattern (tools + loop + streaming UI). LiveCode Agent is self-hosted in your Flask app with full control over tools, permissions, and persistence format.
