# SSE vs WebSocket vs REST API for Live AI

AI products need the server to push live updates — task progress, tool calls, LLM tokens, and **“need your input”** prompts. This guide compares **regular REST APIs**, **SSE streaming endpoints**, and **WebSockets** with working code, then shows how to build a **browser agent** that asks for input and continues.

**Companion:** [How SSE streaming works in chatbots](./how-sse-streaming-works-chatbots-llm-tokens.html)

## Table of contents

1. [Mental model](#mental-model)
2. [Regular REST API](#regular-rest-api)
3. [SSE streaming API](#sse-streaming-api)
4. [WebSocket API](#websocket-api)
5. [Side-by-side comparison](#side-by-side-comparison)
6. [The hybrid stack](#the-hybrid-stack-websocket--sse)
7. [Browser agent: ask input and continue](#browser-agent-ask-input-and-continue)
8. [Wire formats](#wire-formats)
9. [Production checklist](#production-checklist)
10. [FAQ](#faq)

## Mental model

- **REST** — short request/response: create a run, fetch JSON status.
- **SSE** — one HTTP response stays open; server pushes `data:` events (tokens, logs, progress).
- **WebSocket** — bidirectional session: server can emit `need_input` and wait for `user_reply`.

## Regular REST API

### When REST is enough

- CRUD (`POST /documents`, `GET /runs/{id}`)
- Short LLM calls where time-to-first-token does not matter
- Server-to-server webhooks

### Polling anti-pattern

```javascript
async function waitForTask(taskId) {
  while (true) {
    const task = await (await fetch(`/api/tasks/${taskId}`)).json();
    renderStatus(task.status, task.progress);
    if (task.status === "done" || task.status === "failed") return task;
    await new Promise((r) => setTimeout(r, 1000));
  }
}
```

Problems: latency, wasted load, no natural mid-task push.

## SSE streaming API

`Content-Type: text/event-stream`. Server yields `data: {...}\n\n` frames.

### FastAPI SSE endpoint

```python
from fastapi.responses import StreamingResponse

@app.get("/api/tasks/{task_id}/stream")
async def stream_task(task_id: str):
    return StreamingResponse(
        task_event_stream(task_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

### Browser — EventSource (GET) or fetch stream (POST chat)

SSE is **server → client only**. User input requires a separate POST or WebSocket.

## WebSocket API

Full-duplex — ideal for agents that pause and ask questions.

### Server events

- `tool_call`, `progress`, `need_input`, `done`

### Client reply

```json
{"type": "user_reply", "text": "yes", "resume_token": "step-7"}
```

## Side-by-side comparison

| | REST | SSE | WebSocket |
|---|------|-----|-----------|
| Direction | Request → response | Server → client | Bidirectional |
| LLM tokens | Poor | Excellent | Good |
| Mid-task input | Awkward | Awkward | Natural |
| Live progress | Polling | Excellent | Excellent |
| Complexity | Lowest | Low | Medium |

## The hybrid stack (WebSocket + SSE)

1. `POST /api/runs` (REST) — create run
2. `WebSocket /ws/runs/{id}` — control: `need_input`, `tool_call`
3. `GET /api/runs/{id}/tokens` (SSE) — LLM token stream

## Browser agent: ask input and continue

Enable the input box only on `need_input`. Send `user_reply` on the same WebSocket. Server resumes the agent loop.

## Wire formats

**SSE:** `event: progress\ndata: {"pct": 60}\n\n`

**WebSocket:** `{"type": "need_input", "prompt": "..."}`

**REST:** `{"status": "done", "result": {...}}`

## Production checklist

- SSE: `no-cache`, `X-Accel-Buffering: no`, flush per event
- WebSocket: heartbeat, auth on connect, idle timeout
- REST: `202 Accepted` for async jobs
- Propagate `AbortSignal` to stop LLM billing on cancel

## FAQ

**Stream tokens on WebSocket?** Possible; SSE is simpler for one-way text.

**Is SSE the same as HTTP streaming?** SSE is a standard line format on top of chunked HTTP.

**When is REST correct?** Always for one-shot CRUD; streaming complements it.
