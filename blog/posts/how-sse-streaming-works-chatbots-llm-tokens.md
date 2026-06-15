# How SSE Streaming Works in Chatbots (It's Not a Typing Effect)

**June 2026 · Published by Amar Kumar**

When ChatGPT-style UIs print text word by word, it looks like a **typing animation**. It is not. The browser is receiving **real tokens** from the server as the LLM generates them — usually over **HTTP streaming**, often shaped as **Server-Sent Events (SSE)**.

This guide explains what SSE is, why chatbots use it, how to build a streaming API (backend + frontend), and how OpenAI / Anthropic / Gemini stream tokens through your server to the page.

## Table of contents

1. [The typing effect misconception](#misconception)
2. [What SSE is](#what-is-sse)
3. [SSE vs WebSockets vs polling](#comparison)
4. [End-to-end flow in a chatbot](#e2e-flow)
5. [How LLMs stream tokens](#llm-streaming)
6. [Build an SSE streaming API](#build-api)
7. [Frontend: read the stream](#frontend)
8. [RAG + streaming](#rag-streaming)
9. [SSE for live site updates (non-chat)](#live-updates)
10. [Production checklist](#checklist)
11. [FAQ](#faq)

## The typing effect misconception {#misconception}

**Fake typing:** server returns the full answer in one JSON blob → JavaScript reveals characters with `setInterval` → user waits for the entire generation anyway.

**Real streaming:** server opens a long-lived HTTP response → LLM emits token chunks as they are sampled → each chunk is forwarded to the browser immediately → UI appends text as it arrives.

| | Fake typing | Real SSE / stream |
|--|-------------|-------------------|
| User sees first words | After full response ready | Often &lt;500ms after send |
| Server work | Block until done | Pipeline runs incrementally |
| Cancel mid-answer | Wasted generation | Can abort stream |
| Network | One big download | Many small chunks |

If you built a chatbot and wondered why responses feel slow until the "typing" starts — you may have been waiting on the **full completion** before animating. Streaming fixes **time-to-first-token (TTFT)**, not just aesthetics.

## What SSE is {#what-is-sse}

**Server-Sent Events (SSE)** is a browser standard for **server → client** push over a single HTTP connection.

- Content-Type: `text/event-stream`
- Client API: `EventSource` (or `fetch` + `ReadableStream`)
- Direction: **one-way** (server pushes; client sends messages via separate POST)
- Reconnect: browser auto-reconnects on drop
- Format: lines of `data: ...` (optional `event:` and `id:`)

```
data: {"token":"The"}

data: {"token":" capital"}

data: {"token":" of"}

event: done
data: {"finish_reason":"stop"}
```

Perfect for chat because the user **POSTs** a question, then **GETs or POST-opens** a stream for the answer.

## SSE vs WebSockets vs polling {#comparison}

| Method | Direction | Best for | Chat fit |
|--------|-----------|----------|----------|
| **SSE** | Server → client | LLM token stream, progress bars | Excellent |
| **WebSocket** | Bidirectional | Games, collaborative editors | Overkill for simple chat |
| **Long polling** | Client asks repeatedly | Legacy fallback | Wasteful, higher latency |
| **Short polling** | `setInterval` fetch | Dashboards | Poor for token streams |

Most production RAG chatbots use **HTTP POST + SSE response** (or chunked `fetch` reading `text/event-stream`). WebSockets help when the same socket carries many message types both ways; SSE is simpler behind CDNs and load balancers.

## End-to-end flow in a chatbot {#e2e-flow}

```
Browser                    Your API                  LLM provider
   |  POST /chat {msg}         |                          |
   | ------------------------> |  stream=True completion  |
   |                           | ------------------------> |
   |  SSE connection open      | <----- token chunk ------ |
   | <----- data: {"t":"Hi"} --| <----- token chunk ------ |
   | <----- data: {"t":"!"} ---|                          |
   |  event: done              | <----- [DONE] ----------- |
```

1. User submits message
2. API retrieves RAG context (non-streamed, usually fast)
3. API calls LLM with `stream: true`
4. API **forwards each delta** to the client as SSE `data:` lines
5. Client appends tokens to the message bubble
6. On `done`, client enables input again

## How LLMs stream tokens {#llm-streaming}

Providers don't send "words" — they send **token deltas** (subword pieces). Your server normalizes them into one text stream.

### OpenAI / compatible APIs

```python
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        yield delta  # forward to SSE
```

Wire format: newline-delimited JSON (`data: {...}\n\n`), ends with `data: [DONE]`.

### Anthropic

```python
with client.messages.stream(model="claude-haiku-4-5", messages=messages, max_tokens=1024) as s:
    for text in s.text_stream:
        yield text
```

Events include `content_block_delta` with `text` fragments.

### Google Gemini

```python
for chunk in client.models.generate_content_stream(model="gemini-2.5-flash-lite", contents=prompt):
    if chunk.text:
        yield chunk.text
```

**Your job:** consume provider stream → emit uniform SSE JSON so the frontend doesn't care which model ran.

## Build an SSE streaming API {#build-api}

### FastAPI example

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

async def token_generator(user_message: str):
    # 1. RAG retrieve (optional)
    context = retrieve_chunks(user_message)

    # 2. Stream from LLM
    for token in stream_llm(user_message, context):
        payload = json.dumps({"type": "token", "content": token})
        yield f"data: {payload}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"

@app.post("/api/chat/stream")
async def chat_stream(body: ChatRequest):
    return StreamingResponse(
        token_generator(body.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )
```

### Node / Express sketch

```javascript
app.post("/api/chat/stream", async (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders();

  const stream = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: req.body.messages,
    stream: true,
  });

  for await (const chunk of stream) {
    const text = chunk.choices[0]?.delta?.content ?? "";
    if (text) res.write(`data: ${JSON.stringify({ content: text })}\n\n`);
  }
  res.write(`data: ${JSON.stringify({ done: true })}\n\n`);
  res.end();
});
```

**Critical headers:** `text/event-stream`, `no-cache`, disable proxy buffering (`X-Accel-Buffering: no` on nginx).

## Frontend: read the stream {#frontend}

### Option A — `fetch` + ReadableStream (recommended for POST)

`EventSource` only supports GET. Chat usually POSTs the message, so use `fetch`:

```javascript
async function streamChat(message, onToken) {
  const res = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const data = JSON.parse(line.slice(6));
      if (data.type === "token") onToken(data.content);
    }
  }
}
```

### Option B — `EventSource` (GET progress streams)

```javascript
const es = new EventSource("/api/sync/progress");
es.addEventListener("progress", (e) => {
  const { pct, stage } = JSON.parse(e.data);
  updateBar(pct, stage);
});
es.addEventListener("complete", () => es.close());
```

Append tokens to the DOM — **no fake delay**:

```javascript
let text = "";
streamChat(userMsg, (token) => {
  text += token;
  bubble.textContent = text;  // or markdown renderer incremental
});
```

## RAG + streaming {#rag-streaming}

RAG adds a **retrieval phase** before generation:

| Phase | Streamed? | Typical duration |
|-------|-----------|------------------|
| Embed query | No | 50–200ms |
| Vector search | No | 50–300ms |
| Rerank (optional) | No | 100–500ms |
| LLM generation | **Yes** | 2–15s |

**UX pattern:** show "Searching docs…" spinner during retrieval, then switch to token stream when the LLM starts. Optionally SSE event types:

```
event: status
data: {"phase":"retrieval"}

event: token
data: {"content":"Based"}

event: citation
data: {"source":"docs/api.md","chunk_id":"api_3"}
```

See [How to Build a RAG Chatbot](how-to-build-a-production-rag-chatbot.html) for the retrieval stack.

## SSE for live site updates (non-chat) {#live-updates}

Same transport, different payload — sync jobs, deploy logs, indexing progress:

```
event: progress
data: {"stage":"embed","pct":60,"file":"page-b.md"}

event: complete
data: {"duration_s":94}
```

We use this pattern in our [knowledge base sync pipeline](publish-knowledge-base-github-pages-dropbox-sync.html). Chat tokens and progress events share one mechanism: **one HTTP connection, many `data:` lines**.

## Production checklist {#checklist}

- [ ] Disable reverse-proxy buffering (nginx, Cloudflare) for stream routes
- [ ] Set timeouts &gt; longest expected generation (or heartbeat `:\n\n` comments)
- [ ] Support `AbortController` on client; abort provider stream server-side
- [ ] Normalize errors as SSE `event: error` before closing
- [ ] Don't buffer full response in memory before sending
- [ ] Log TTFT and tokens/sec for monitoring
- [ ] Rate-limit stream endpoints

## FAQ {#faq}

### Is ChatGPT's typing effect fake?

In real streaming implementations, **no** — text arrives as the model generates. Some demo UIs fake it; production APIs stream.

### SSE or WebSocket for chat?

**SSE** (or chunked HTTP) for most chat + RAG. **WebSocket** if you need bidirectional high-frequency events on one socket.

### Why isn't my stream showing live in the browser?

Usually **proxy buffering** — nginx, Apache, or a server framework collecting the full body before flush. Add `X-Accel-Buffering: no` and flush after each `yield`.

### Can I stream markdown safely?

Append raw text incrementally; run markdown parse on a debounced schedule or after `done` to avoid broken partial syntax.

## Related guides

- [How to Build a RAG Chatbot](how-to-build-a-production-rag-chatbot.html)
- [Best Economical LLM Models for RAG](best-economical-llm-models-rag-openai-gemini-anthropic.html)
- [Publish a Knowledge Base with SSE Progress](publish-knowledge-base-github-pages-dropbox-sync.html)
