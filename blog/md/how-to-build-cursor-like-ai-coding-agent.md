# How to Build a Cursor-Like AI Coding Agent — Complete Guide

August 2026 · Published by Amar Kumar

Cursor Agent mode, Claude Code, and Windsurf share the same core pattern: an LLM in a **tool-calling loop** that reads a real codebase, edits files, runs shell commands, and streams progress back to an IDE. You do not need LangChain, a vector database, or a cloud orchestration platform to build one. I built **[LiveCode](https://github.com/amarkum/livecode-ai)** — a self-hosted browser IDE with Monaco, an integrated terminal, and a full agent harness — entirely in Python and vanilla JavaScript. This guide walks through every layer with architecture diagrams, comparison tables, and pseudocode you can adapt.

> **Who is this for?** Engineers who want to understand how Cursor-style agentic coding works under the hood — and who want a step-by-step blueprint to ship their own.

## Table of contents

1. [What makes an agent "Cursor-like"](#what-makes-an-agent-cursor-like)
2. [Architecture at a glance](#architecture-at-a-glance)
3. [Phase 1 — HTTP endpoint and SSE streaming](#phase-1--http-endpoint-and-sse-streaming)
4. [Phase 2 — The agent harness loop](#phase-2--the-agent-harness-loop)
5. [Phase 3 — Tool system design](#phase-3--tool-system-design)
6. [Phase 4 — Context compaction (three tiers)](#phase-4--context-compaction-three-tiers)
7. [Phase 5 — Dual-channel real-time UI](#phase-5--dual-channel-real-time-ui)
8. [Phase 6 — Permissions and safety](#phase-6--permissions-and-safety)
9. [Phase 7 — Agent, Plan, and Ask modes](#phase-7--agent-plan-and-ask-modes)
10. [Phase 8 — Subagents and delegation](#phase-8--subagents-and-delegation)
11. [Phase 9 — Session persistence and memory](#phase-9--session-persistence-and-memory)
12. [Phase 10 — Frontend IDE shell](#phase-10--frontend-ide-shell)
13. [LiveCode vs Cursor — comparison](#livecode-vs-cursor--comparison)
14. [Implementation checklist](#implementation-checklist)
15. [FAQ](#faq)
16. [Related guides](#related-guides)

## What makes an agent "Cursor-like"

A Cursor-like coding agent is not a chatbot with code snippets. It is a **closed loop** between an LLM and a filesystem:

| Capability | Why it matters |
|------------|----------------|
| **Tool calling** | The model decides *when* to grep, read, edit, or run commands — not the UI |
| **Iteration loop** | One user message may require 5–50 tool rounds before the task is done |
| **Streaming progress** | Users see thinking, tool activity, diffs, and shell output in real time |
| **Context management** | Long sessions exceed the context window; compaction is mandatory |
| **Permission gates** | Destructive shell commands require explicit user approval |
| **Modes** | Agent (edit), Plan (draft only), Ask (read-only) filter available tools |
| **Project rules** | `AGENTS.md`, `.cursor/rules`, and similar files steer behavior |

The minimum viable stack: **one HTTP endpoint**, **one Python generator function**, **a tool dispatch table**, and **JSONL session files on disk**.

## Architecture at a glance

LiveCode splits into a Python backend (`livecode-ai`) and a browser frontend. Runtime data lives in `~/livecode/` — settings, sessions, indexes, and memory — separate from the source repo.

```
livecode-ai/                    ~/livecode/  (runtime)
├── src/livecode/
│   ├── server.py               ├── settings.json
│   ├── harness/turn.py         └── projects/{slug}/
│   ├── tools.py                    ├── sessions/{id}/chat_history.jsonl
│   ├── runtime.py                  ├── index/workspace.json
│   ├── session.py                  ├── symbols/symbols.json
│   └── memory/                     └── memory/index.sqlite
├── templates/index.html
└── static/js/bundle.js
```

## Phase 1 — HTTP endpoint and SSE streaming

The turn endpoint accepts a POST with the user message, project path, session ID, and mode. It returns `text/event-stream` — not because SSE is the only option, but because it works over a single long-lived HTTP connection without WebSocket upgrade complexity for the *final answer path*.

```python
@app.post("/livecode-agent")
def agent_turn():
    body = request.get_json()
    question = body["question"]
    project_path = body["project_path"]
    session_id = body.get("session_id") or uuid.uuid4().hex
    mode = body.get("mode", "agent")

    def generate():
        bridge = SSEProgressBridge(socketio=socketio, room=socket_id)
        turn_thread = threading.Thread(
            target=lambda: run_turn_in_queue(run_livecode_turn(...), chunk_queue),
            daemon=True,
        )
        turn_thread.start()

        while not turn_finished:
            yield from bridge.drain_as_sse()          # progress + command_stream
            chunk = chunk_queue.get(timeout=0.05)     # harness yields "data: {...}\n\n"
            if chunk.get("done"):
                append_turn_messages(project_path, session_id, chunk["turn_messages"])
                yield f"data: {json.dumps(chunk)}\n\n"
                break
            yield chunk

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

**Why not EventSource?** The browser's built-in `EventSource` only supports GET. The frontend uses `fetch()` + `ReadableStream`, decodes SSE `data:` lines manually, and handles progress, command output, and the final `done` payload in one loop.

## Phase 2 — The agent harness loop

The harness is a **Python generator** — `run_livecode_turn()` — that yields SSE chunks and emits Socket.IO events. Up to **100 iterations** per user message (`LIVECODE_MAX_ITERATIONS`).

```python
def run_livecode_turn(project_path, question, *, mode="agent", session_id, ...):
    classification = classify_turn(question)           # fast model JSON
    messages = build_base_messages(project_path, question, session_id)
    tools = filter_tools_for_mode(get_livecode_tools(), mode)

    for iteration in range(1, LIVECODE_MAX_ITERATIONS + 1):
        # --- Anti-loop nudges (inject as internal user messages) ---
        if stationarity_detected(tool_history):
            messages.append(nudge("same tool+args repeated — try a different approach"))
        if search_scatter_detected(tool_history):
            messages.append(nudge("broaden grep — use glob or alternation"))
        if exploration_streak_without_edit(tool_history):
            messages.append(nudge("you have enough context — edit or finish"))

        # --- Context budget ---
        messages = compact_stale_tool_messages(messages, keep_last=6)

        # --- Mid-turn user interjection ---
        if interjection := drain_interjection(session_id):
            messages.append(format_interjection(interjection))

        # --- Last 2 iterations: force closure tool only ---
        iter_tools = tools
        if iteration > LIVECODE_MAX_ITERATIONS - CLOSURE_ITERATIONS:
            iter_tools = attempt_completion_only_tools(tools)

        response = call_with_tools(
            model=pick_auto_model(classification),
            messages=messages,
            tools=iter_tools,
            on_thought_delta=lambda delta: emit("agent_thinking_delta", delta),
        )

        if not response.tool_calls:
            yield sse_done(answer=response.content)
            return

        for result in execute_tool_calls_batch(response.tool_calls):
            messages.append(assistant_tool_message(response))
            messages.append(tool_result_message(result))
            emit_progress(result)

            if result.tool == "attempt_completion":
                if goal_verifier_passed(question, tool_history):
                    yield sse_done(answer=result.summary)
                    return
                else:
                    messages.append(nudge("user asked for code change but no edit succeeded"))

    yield sse_done(answer=summarize_exhaustion(messages))
```

### Anti-loop guardrails

These are the difference between a demo and something you can leave running on a real repo:

| Pattern | Trigger | Action |
|---------|---------|--------|
| **Stationarity** | Same tool + identical args 8× | Inject nudge; hard stop at 16× |
| **Search scatter** | 6+ narrow greps hunting one thing | Nudge to broaden (glob, regex alternation) |
| **Directory drill** | Sequential `list_repo_dir` | Nudge to use `glob_files` / `find_files` |
| **Exploration streak** | 8 read-only steps, no edit | Nudge to edit or `attempt_completion` |
| **Edit no-match** | `edit_file` old_string not found | Nudge to re-read file |
| **Iteration budget** | 75%, 90%, 95% of max iterations | Escalating urgency nudges |
| **Goal verifier** | `attempt_completion` but no successful edit when user asked for code change | Reject completion |

Constants from `prompts.py`:

```python
LIVECODE_MAX_ITERATIONS = 100
LIVECODE_CONTEXT_WINDOW = 128_000
STATIONARITY_NUDGE_AFTER = 8
STATIONARITY_HARD_STOP = 16
CLOSURE_ITERATIONS = 2
```

## Phase 3 — Tool system design

Tools use **OpenAI function-calling format**. Gemini receives the same schemas translated to `functionDeclarations` in `runtime.py`.

### Tool inventory (18 core)

| Category | Tools |
|----------|-------|
| Search / read | `grep_repo`, `read_repo_file`, `list_repo_dir`, `glob_files`, `find_files`, `git_log`, `ast_symbols` |
| Symbol index | `find_symbol`, `find_references`, `list_symbols` |
| Edit | `write_file`, `edit_file` (exact search-replace) |
| Shell | `run_command` (PTY streaming) |
| Memory | `update_memory`, `memory_search`, `memory_get` |
| Delegation | `spawn_subagent` |
| Web (optional) | `web_search`, `web_fetch` |
| Plan mode | `create_plan` |
| Termination | `attempt_completion` |

### Dispatch pattern

```python
def dispatch_tool(project_path, name, args, *, mode, session_id, ...):
    if mode_blocks_tool(mode, name):
        return {"error": mode_rejection_message(mode, name)}

    if name == "run_command" and requires_permission(args["command"]):
        request_id = create_permission_request(session_id, name, args)
        emit_permission_prompt(request_id, args)
        approved = wait_for_permission(request_id)  # blocks up to 120s
        if not approved:
            return {"error": "User denied command"}

    if name == "grep_repo":
        return repo_grep_fn(project_path, pattern=args["pattern"], ...)
    if name == "edit_file":
        return apply_search_replace(project_path, args["file_path"],
                                    old=args["old_string"], new=args["new_string"])
    # ... one branch per tool
```

### Batch execution rules

When the LLM returns multiple tool calls in one response:

1. **Read-only tools** (`grep`, `read`, `list`, `glob`) run **in parallel** via `ThreadPoolExecutor`
2. **Same-file `edit_file` calls** are **coalesced** into one search-replace pass
3. **Mutating tools** run serially after reads complete
4. Tool results are **truncated** before returning to the LLM (`grep` → 30 matches, reads → 16k chars)

### Why exact-match `edit_file`

Ambiguous search-replace (multiple occurrences of `old_string`) is worse than a retry. LiveCode rejects edits where `old_string` matches more than once — forcing the model to include more surrounding context, exactly like Cursor's apply model.

## Phase 4 — Context compaction (three tiers)

Long agent sessions blow past 128k tokens quickly. LiveCode uses **three compaction tiers**:

| Tier | Trigger | Strategy |
|------|---------|----------|
| **Intra-turn** | >70% of context window during a turn | `compact_stale_tool_messages()` — truncate old tool results, keep last 6 |
| **Inter-turn** | >65% between turns | `maybe_inter_turn_compact()` — shrink before next user message |
| **Session (full-replace)** | >85% or forced | LLM summarizes entire prefix → replaces old messages with one summary block |

```python
LIVECODE_AUTO_COMPACT_RATIO = 0.85      # full LLM summarization
LIVECODE_IN_TURN_COMPACT_RATIO = 0.70   # cheap truncation
LIVECODE_INTER_COMPACT_RATIO = 0.65     # between turns
LIVECODE_KEEP_RECENT_TOOL_MSGS = 6
```

Before full-replace compaction, a **memory flush** runs: important facts are written to `MEMORY.md` and indexed in SQLite (FTS + local embeddings) so they survive summarization.

## Phase 5 — Dual-channel real-time UI

Two channels, clean separation:

| Channel | Carries | Why |
|---------|---------|-----|
| **SSE** (HTTP POST response) | `progress`, `command_stream`, `done`, `answer` | Simple unidirectional pipe; works through proxies |
| **Socket.IO** (WebSocket) | Tool chips, diff blocks, permission modals, terminal PTY | Rich JSON payloads, bidirectional |

Frontend SSE consumer:

```javascript
const resp = await fetch("/livecode-agent", {
  method: "POST",
  headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
  body: JSON.stringify({ project_path, question, session_id, mode }),
});

const reader = resp.body.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buffer += decoder.decode(value, { stream: true });

  for (const line of buffer.split("\n")) {
    if (!line.startsWith("data: ")) continue;
    const payload = JSON.parse(line.slice(6));
    if (payload.progress) handleProgress(payload.progress);
    if (payload.command_stream) appendTerminalOutput(payload.command_stream);
    if (payload.done) finalizeTurn(payload);
  }
}
```

## Phase 6 — Permissions and safety

Destructive shell patterns (`git reset --hard`, `rm -rf`, force push) trigger a **blocking permission gate**:

```python
def create_permission_request(session_id, tool_name, tool_args, timeout_s=120):
    request_id = f"perm_{uuid.uuid4().hex[:16]}"
    event = threading.Event()
    _PERMISSIONS[request_id] = {
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_args": tool_args,
        "event": event,
        "approved": None,
    }
    return request_id

def wait_for_permission(request_id) -> bool | None:
    entry = _PERMISSIONS[request_id]
    if not entry["event"].wait(timeout=entry["timeout_s"]):
        return None  # timed out → deny
    return bool(entry["approved"])
```

The frontend shows a modal; the user POSTs to `/livecode/permission` with `{request_id, approved}`; `resolve_permission()` calls `event.set()` and unblocks the harness thread.

Path safety: all file operations go through `resolve_safe_path()` — no traversal outside the project root.

## Phase 7 — Agent, Plan, and Ask modes

Modes filter the tool list and inject mode-specific system prompts:

```python
LIVECODE_MODES = ("agent", "plan", "ask")

def filter_tools_for_mode(tools, mode):
    if mode == "agent":
        return tools  # all 18 tools
    allowed = READ_ONLY_TOOLS | {"attempt_completion"}
    filtered = [t for t in tools if t["function"]["name"] in allowed]
    if mode == "plan":
        filtered.append(CREATE_PLAN_TOOL)
    return filtered
```

| Mode | Can edit files | Can run shell | Special tool |
|------|----------------|---------------|--------------|
| **Agent** | Yes | Yes (with permission) | — |
| **Plan** | No | No | `create_plan` → writes markdown plan |
| **Ask** | No | No | — |

## Phase 8 — Subagents and delegation

`spawn_subagent` launches a **nested mini-loop** with its own ephemeral session:

```python
def run_subagent_turn(project_path, goal, parent_session_id, read_only=True, max_iterations=5):
    child_session = f"{parent_session_id}_sub_{uuid.uuid4().hex[:8]}"
    question = f"[Subagent — read_only={read_only}]\n{goal}\nCall attempt_completion when done."

    for chunk in run_livecode_turn(
        project_path, question,
        session_id=child_session,
        max_iterations=max_iterations,
        mode="ask" if read_only else "agent",
    ):
        collect_answer_from_sse_chunk(chunk)

    return {"success": True, "result": answer, "child_session_id": child_session}
```

The parent receives a single summarized result — useful for "explore the codebase and report back" without polluting the main context.

## Phase 9 — Session persistence and memory

### JSONL sessions

Each turn appends to `chat_history.jsonl`:

```jsonl
{"role":"user","content":"Add health check endpoint","ts":1725000000}
{"role":"assistant","content":null,"tool_calls":[{"id":"call_1","function":{"name":"grep_repo","arguments":"{\"pattern\":\"router\"}"}}]}
{"role":"tool","tool_call_id":"call_1","content":"{\"matches\":[{\"file\":\"app.py\",\"line\":12}]}"}
```

Sidecar files: `summary.json` (title, model, edit snapshots), `compaction.json` (boundary index + summary hash), `diffs.jsonl`, `tool_artifacts.jsonl`.

### Intelligent classifier

Before the loop, a fast model classifies the turn:

```python
class IntelligentClassification(TypedDict):
    goal_kind: str          # code_change, analysis, research, meta
    edit_scope: str         # none, single_line, single_file, multi_file, bulk
    needs_flagship_model: bool
    complexity: str         # simple, medium, complex
    expects_multi_step: bool
```

This drives `pick_livecode_auto_model()` — cheap model for simple reads, flagship for multi-file refactors.

### Project rules discovery

```python
RULES_FILES = ["AGENTS.md", "CLAUDE.md", ".cursor/rules", ".livecode/rules"]

def discover_project_rules(project_path):
    for directory in path_chain(git_root, project_path):
        for rules_file in RULES_FILES:
            if exists(join(directory, rules_file)):
                found.append(read(candidate))
    return wrap_in_system_reminder(found)
```

Injected as a follow-up system message — same convention Cursor and Claude Code use.

## Phase 10 — Frontend IDE shell

The browser loads a single-page IDE:

- **Left:** file tree (Socket.IO file browser)
- **Center:** Monaco Editor 0.45 (multi-tab, syntax highlighting)
- **Bottom:** xterm.js terminal (PTY via Socket.IO)
- **Right:** agent chat (tool activity chips, inline diffs, permission modals)

No npm build step — one `bundle.js` (~9k lines) loaded from Flask static assets.

## LiveCode vs Cursor — comparison

| Aspect | LiveCode (self-hosted) | Cursor |
|--------|------------------------|--------|
| Agent loop | Python harness, 100 iter max, rich nudges | Proprietary cloud harness |
| Tools | ~18 built-in, hardcoded schemas | Built-in + **MCP** dynamic namespaces |
| MCP | Flag exists, not implemented yet | First-class `GetDynamicTools` / `CallDynamicTool` |
| Streaming | SSE + Socket.IO dual channel | SSE throughout, rich step timeline |
| Modes | Agent / Plan / Ask | Agent / Plan / Ask / Debug + skills |
| Context | 128k, 3-tier compaction, SQLite memory | Larger windows, cloud compaction, `@` attachments |
| Permissions | In-app approve/deny modal | Smart mode approval cards, sandbox |
| Subagents | `spawn_subagent`, max 5 iter | Task tool with specialized subagents |
| IDE | Browser Monaco + terminal | VS Code fork, deep LSP integration |
| Deployment | Local Flask :5050 | Cloud + desktop app |

**Closest parallels:** harness nudges, `attempt_completion` termination, mode gating, compaction layers, and permission prompts are clearly modeled after Cursor/Claude-agent patterns. LiveCode is a **self-hosted, simplified reimplementation** with full control over tools, persistence, and model routing.

**Main gap vs Cursor:** MCP. Dynamic tool discovery from external servers is the architectural piece LiveCode does not have yet.

## Implementation checklist

Use this as a build order for your own agent:

1. [ ] Flask route returning SSE from a generator
2. [ ] OpenAI/Gemini `call_with_tools()` adapter with streaming thoughts
3. [ ] Tool schemas: `grep`, `read`, `edit_file`, `run_command`, `attempt_completion`
4. [ ] `dispatch_tool()` with path safety and result truncation
5. [ ] Harness loop with iteration cap and stationarity detection
6. [ ] JSONL session persistence
7. [ ] Intra-turn tool message compaction
8. [ ] Permission gate for destructive shell commands
9. [ ] Socket.IO progress events + frontend activity feed
10. [ ] Mode filtering (Agent / Ask at minimum)
11. [ ] Project rules discovery (`AGENTS.md`, `.cursor/rules`)
12. [ ] Full-replace LLM compaction at 85% threshold
13. [ ] Subagent delegation (optional)
14. [ ] Monaco + terminal IDE shell (optional but expected)

**Reference implementation:** [github.com/amarkum/livecode-ai](https://github.com/amarkum/livecode-ai) — `pip install -e ".[dev]" && python -m livecode` → http://127.0.0.1:5050

## FAQ

### Do you need LangChain to build a coding agent?

No. A generator function, OpenAI tool schemas, JSONL session files, and tiered context management are sufficient for production-quality agentic coding.

### Why SSE and WebSocket together?

SSE streams the turn lifecycle over a single HTTP POST. WebSocket carries structured tool progress, diffs, permission modals, and terminal PTY output — payloads that would be painful to encode in a flat text stream.

### How do you stop infinite tool loops?

Stationarity detection on identical tool-call fingerprints, escalating nudges at 75%/90%/95% iteration budget, a hard 100-iteration cap, and forced `attempt_completion`-only tools in the last 2 iterations.

### How is this different from the Cursor desktop app?

Same agent pattern — tools, iteration loop, streaming UI. LiveCode is self-hosted: you control tools, permissions, persistence format, model routing, and deployment. Cursor adds MCP, cloud orchestration, LSP integration, and a VS Code fork.

### What about vector search / RAG for the codebase?

LiveCode uses ripgrep, a symbol index (Python AST + JS/TS regex), and targeted file reads instead of embeddings. For most coding tasks, grep + read beats semantic search on stale indexes — and it is vastly simpler to operate.

### Can I add MCP later?

Yes. The `enable_mcp` flag exists in LiveCode as a stub. The integration point is `get_livecode_tools()` — append dynamically discovered MCP tool schemas alongside the built-in set, and route `dispatch_tool()` calls through an MCP client.

## Related guides

- [How I Built a Live-Browser AI Coding Agent with Flask and Monaco](/blog/posts/how-i-built-mini-cursor-agentic-ide-in-browser/)
- [How SSE Streaming Works in Chatbots](/blog/posts/how-sse-streaming-works-chatbots-llm-tokens/)
- [SSE vs WebSocket vs REST API for Live AI](/blog/posts/sse-websocket-rest-api-compared/)
- [Skills vs MCP vs Subagents](/blog/posts/skills-vs-mcp-vs-subagents/)

Generator loop. Tool dispatch. JSONL on disk. That is the whole trick.
