# How to Build a Production RAG Chatbot — Complete Guide

**June 2026 · Published by Amar Kumar**

A practical guide to building a production RAG chatbot from scratch: concepts, stack, architecture, code, and launch.

---

You want a chatbot that answers from **your** docs — not from the model's memory. That's a RAG chatbot.

This guide shows how to build a production RAG chatbot: ingest documents, store them in a vector database, retrieve relevant chunks on each question, and generate answers with an LLM.

> **Who is this for?** Developers with basic Python and an API key. No ML background required.

---

## Table of contents

1. [What is an LLM?](#what-is-an-llm)
2. [What is RAG?](#what-is-rag)
3. [What are embeddings?](#what-are-embeddings)
4. [What is a vector database?](#what-is-a-vector-database)
5. [Chunking](#chunking)
6. [RAG vs fine-tuning vs plain LLM](#rag-vs-fine-tuning-vs-plain-llm)
7. [Tools & stack](#tools--stack)
8. [Which vector database?](#which-vector-database)
9. [Architecture](#architecture)
10. [Build a production RAG chatbot step by step](#build-step-by-step)
11. [Going to production](#going-to-production)
12. [Launch checklist](#launch-checklist)
13. [API reference](#api-reference)
14. [Glossary](#glossary)

---

## What is an LLM?

An **LLM (Large Language Model)** generates text — answers, summaries, code. Examples: GPT-4o, Gemini, Claude, Llama.

It only knows training data plus what you send in the prompt. It does **not** automatically know your wiki, PDFs, or tickets. RAG feeds it the right text at question time.

---

## What is RAG?

**RAG (Retrieval-Augmented Generation)** = search your knowledge base, then ask the LLM to answer using what was found.

| Step | What happens |
|------|--------------|
| **Retrieve** | Find document chunks related to the question |
| **Augment** | Add those chunks to the LLM prompt |
| **Generate** | LLM writes the answer from that context |

Like an open-book exam: the model reads the relevant pages you hand it, then responds.

---

## What are embeddings?

Text is converted to a **vector** (a list of numbers). Similar meaning → similar vectors.

- "Reset password" and "forgot login" → close vectors  
- "Reset password" and "weather forecast" → far apart  

An **embedding model** (separate from your chat LLM) creates these vectors. You embed all docs at ingest time and embed each user question at query time, then find the closest doc vectors.

```text
"How do I reset my password?"  →  [0.12, -0.45, 0.88, ...]
"Password recovery steps"      →  [0.11, -0.42, 0.91, ...]   ← relevant
"Weather in Tokyo"             →  [-0.67, 0.22, -0.11, ...]  ← not relevant
```

---

## What is a vector database?

Stores millions of vectors and returns **nearest neighbors** quickly.

Each record usually has:

- **ID** — chunk identifier  
- **Vector** — embedding  
- **Metadata** — title, URL, doc id, text snippet  

Regular SQL is for exact matches (`WHERE id = 5`). Vector DBs are for **similar meaning**.

**Query flow:** embed question → vector DB returns top-k chunks → pass chunks to LLM.

---

## Chunking

Documents are too large for one prompt. **Chunking** splits them into pieces (often 800–1200 characters) with 10–20% overlap.

| Setting | Recommendation |
|---------|----------------|
| Size | 800–1200 chars (~400–800 tokens) |
| Overlap | 10–20% |
| Split on | Headings, then paragraphs |
| Metadata | `title`, `doc_id`, `source_url`, `section` |

Bad chunks → bad search → bad answers. Worth reviewing samples after first ingest.

---

## RAG vs fine-tuning vs plain LLM

| Approach | Use when |
|----------|----------|
| **Plain LLM** | General questions, no private docs |
| **RAG** | Answers must come from your docs that change over time |
| **Fine-tuning** | Tone, format, domain language — not as a substitute for live docs |

For doc Q&A and support bots, **start with RAG**.

---

## Tools & stack

| Component | Role | Common choices |
|-----------|------|----------------|
| Chat LLM | Generates answers | GPT-4o-mini, Gemini Flash, Claude Haiku |
| Embedding model | Text → vectors | OpenAI embed-3-small, Gemini embedding |
| Vector database | Store & search vectors | Pinecone, Chroma, pgvector, Qdrant |
| Reranker (optional) | Improve search ranking | Cohere Rerank |
| API | `/chat` endpoint | FastAPI, Express |
| Ingest | Parse, chunk, embed, store | Python script + cron |
| UI | Chat interface | HTML/JS, React |

**Beginner stack (copy this):**

| Layer | Pick |
|-------|------|
| Language | Python |
| API | FastAPI |
| Vector DB | Pinecone or Chroma (local) |
| Embeddings | OpenAI `text-embedding-3-small` |
| Chat | GPT-4o-mini or Gemini Flash |
| Deploy | Docker + Cloud Run / Railway |

**Project layout:**

```text
docs/           ← your source markdown/PDF exports
ingest/         ← chunk.py, index.py (run when docs change)
app/            ← retrieve.py, main.py (chat API)
frontend/       ← chat UI
.env            ← API keys (never commit)
```

**LangChain?** Optional. Plain Python is fine for v1 — you'll see every step clearly.

---

## Which vector database?

| Database | Best for | Beginner? |
|----------|----------|-----------|
| **Pinecone** | Managed, fast start, scales | ★ Easiest cloud option |
| **Chroma** | Local dev, small projects | ★ Easiest to learn |
| **pgvector** | Already on PostgreSQL | Medium |
| **Qdrant** | Performance, filters, hybrid search | Medium |
| **Weaviate** | Hybrid BM25 + vector built-in | Medium |

Start with **Pinecone** or **Chroma**. Switch when you outgrow free tier or need hybrid search at scale.

---

## Architecture

Two pipelines share one vector index.

### Offline — when docs change

```text
Sources → Parse → Chunk + metadata → Embed → Vector DB
```

Run on upload, git push, or schedule.

### Online — when user asks

```text
Question → Embed query → Vector search (top-k) → [Rerank] → Build prompt → LLM → Answer + sources
```

### End-to-end (one question)

1. User sends message to your API  
2. API embeds the question  
3. Vector DB returns top 20–40 similar chunks  
4. (Optional) Reranker keeps best 5–10  
5. API builds prompt: system instructions + chunks + question  
6. LLM returns answer  
7. API responds with answer and source links  

### Typical latency

| Stage | ~ms |
|-------|-----|
| Embed query | 80 |
| Vector search | 120 |
| Rerank | 200 |
| LLM response | 1500–2500 |

---

## Build a Production RAG Chatbot Step by Step

### Step 1 — Environment

**.env**

```env
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
DEFAULT_MODEL=gpt-4o-mini

PINECONE_API_KEY=...
PINECONE_INDEX=kb-prod
PINECONE_NAMESPACE=default

RETRIEVAL_TOP_K=30
MAX_CONTEXT_CHUNKS=8
```

**requirements.txt**

```text
fastapi
uvicorn
python-dotenv
openai
pinecone-client
tiktoken
```

Add `cohere` if you use reranking.

---

### Step 2 — Chunk documents

**ingest/chunk.py**

```python
from pathlib import Path

CHUNK_SIZE = 1000
OVERLAP = 200

def chunk_text(text: str, doc_id: str, title: str) -> list[dict]:
    chunks, start, idx = [], 0, 0
    while start < len(text):
        piece = text[start : start + CHUNK_SIZE].strip()
        if piece:
            chunks.append({
                "id": f"{doc_id}_{idx}",
                "text": piece,
                "metadata": {"doc_id": doc_id, "title": title, "chunk_index": idx},
            })
            idx += 1
        start += CHUNK_SIZE - OVERLAP
    return chunks

def load_docs(folder: str) -> list[dict]:
    out = []
    for path in Path(folder).glob("**/*.md"):
        out.extend(chunk_text(path.read_text(encoding="utf-8"), path.stem, path.stem))
    return out
```

---

### Step 3 — Embed and index

**ingest/index.py**

```python
import os
from openai import OpenAI
from pinecone import Pinecone
from chunk import load_docs

client = OpenAI()
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX"])

def embed(texts: list[str]) -> list[list[float]]:
    r = client.embeddings.create(model=os.environ["EMBEDDING_MODEL"], input=texts)
    return [d.embedding for d in r.data]

def upsert_chunks(chunks: list[dict], batch_size=50):
    ns = os.environ.get("PINECONE_NAMESPACE", "default")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vecs = embed([c["text"] for c in batch])
        index.upsert(
            vectors=[
                {"id": c["id"], "values": v, "metadata": {**c["metadata"], "text": c["text"]}}
                for c, v in zip(batch, vecs)
            ],
            namespace=ns,
        )

if __name__ == "__main__":
    upsert_chunks(load_docs("docs"))
    print("Indexed.")
```

Run after docs change: `python ingest/index.py`

---

### Step 4 — Retrieve relevant chunks

**app/retrieve.py**

```python
import os
from openai import OpenAI

client = OpenAI()

def embed_query(text: str) -> list[float]:
    r = client.embeddings.create(model=os.environ["EMBEDDING_MODEL"], input=text)
    return r.data[0].embedding

def retrieve(query: str, index, top_k: int | None = None) -> list[dict]:
    k = top_k or int(os.environ.get("RETRIEVAL_TOP_K", "30"))
    hits = index.query(vector=embed_query(query), top_k=k, include_metadata=True)
    return [{"text": m.metadata["text"], **m.metadata} for m in hits.matches]
```

**Optional rerank** (Cohere) — call after vector search, keep top 8. Big quality win for little code.

---

### Step 5 — Chat API

**app/main.py**

```python
import os
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from retrieve import retrieve

app = FastAPI()
client = OpenAI()
# index = init pinecone on startup

SYSTEM = """You are a helpful assistant. Answer using only the context below.
If the context does not contain the answer, say so clearly."""

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []

def format_context(docs: list[dict]) -> str:
    max_chunks = int(os.environ.get("MAX_CONTEXT_CHUNKS", "8"))
    parts = [f"Source: {d.get('title', 'doc')}\n{d['text']}" for d in docs[:max_chunks]]
    return "\n---\n".join(parts)

@app.post("/chat")
async def chat(req: ChatRequest):
    docs = retrieve(req.message, index)

    if not docs:
        return {"response": "I couldn't find anything relevant in the knowledge base.", "sources": []}

    ctx = format_context(docs)
    messages = [
        {"role": "system", "content": SYSTEM},
        *req.conversation_history,
        {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {req.message}"},
    ]
    out = client.chat.completions.create(model=os.environ["DEFAULT_MODEL"], messages=messages)
    return {
        "response": out.choices[0].message.content,
        "sources": [{"title": d.get("title")} for d in docs[:5]],
    }
```

Run: `uvicorn app.main:app --reload --port 8000`

---

### Step 6 — Chat UI

**frontend/chat.js**

```javascript
async function sendMessage(message, history = []) {
  const res = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_history: history }),
  });
  return res.json();
}
```

Render `response` as markdown. Show `sources` as links below the answer.

---

## Going to production

### Improve retrieval

- **Rerank** top vector hits before sending to LLM  
- **Query rewrite** for follow-ups ("what about step 2?") using a cheap model  
- **Hybrid search** (BM25 + vector) if users search error codes and SKUs  
- **Re-sync** docs on a schedule or webhook when content changes  

### Multi-turn chat

Send last N messages in `conversation_history`. Retrieve fresh chunks each turn — don't rely only on old answers.

### Multiple models

| Task | Model tier |
|------|------------|
| Embeddings | Embedding API |
| Main answers | Mid (Flash, 4o-mini) |
| Rewrite / summary | Cheapest tier |

Use env vars for model IDs.

### Evaluation

Build 30+ test questions with expected source docs. Measure **hit@k** after every KB update. If search fails, no prompt fix will save you.

### Deploy

- Dockerize the API  
- Secrets in env / vault — never in frontend  
- Auth + rate limits on `/chat`  
- Log token usage per request  

### When search returns nothing

Return a clear message ("no relevant docs found"). Optionally skip the LLM call. That's a one-line check — not a separate system to build on day one.

---

## Launch checklist

**Must have**
- [ ] Docs ingested and vector index populated  
- [ ] Same embedding model at ingest and query  
- [ ] `/chat` API working  
- [ ] System prompt + context template  
- [ ] Basic UI  
- [ ] API keys server-side only  

**Should have**
- [ ] Reranker  
- [ ] Sources shown in UI  
- [ ] Incremental re-index when docs change  
- [ ] Auth on API  
- [ ] 30+ test questions  

**Later**
- [ ] Query rewrite for follow-ups  
- [ ] Hybrid search  
- [ ] Streaming  
- [ ] Usage/cost dashboards  

---

## API reference

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my password?"}'
```

**Request**

```json
{
  "message": "How do I reset my password?",
  "conversation_history": []
}
```

**Response**

```json
{
  "response": "To reset your password, go to Settings → Account...",
  "sources": [{ "title": "account-settings" }]
}
```

---

## Glossary

| Term | Meaning |
|------|---------|
| **LLM** | Large language model that generates text |
| **RAG** | Retrieve docs, add to prompt, generate answer |
| **Embedding** | Numeric vector representing text meaning |
| **Vector database** | DB optimized for similarity search on embeddings |
| **Chunk** | Small piece of a document stored in the index |
| **top-k** | Number of similar chunks to retrieve (e.g. 30) |
| **Reranker** | Model that re-orders retrieved chunks by relevance |
| **System prompt** | Instructions that define bot behavior |
| **Ingest** | Offline pipeline: parse → chunk → embed → store |
| **Context window** | Max tokens the LLM can read in one request |

---

You're building a **search layer** plus a **chat layer**. Get search right first — the rest follows.
