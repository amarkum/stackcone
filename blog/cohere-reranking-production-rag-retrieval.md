# Cohere Reranking & Production RAG Retrieval Optimization

**June 2026 · Published by Amar Kumar**

How to tune retrieval in a production RAG system: wide vector recall, Cohere rerank-v3.5 for precision, conditional skip logic, MMR diversity, and cost-aware gates.

---

Vector search alone is fast but imprecise. A reranker fixes ranking — but calling it on every request adds ~200 ms and ~$0.002 per call. This guide covers the patterns we use in production to get rerank quality without burning budget on obvious hits.

Part two of our RAG series. Start with [How to Build a Production RAG Chatbot](how-to-build-a-production-rag-chatbot.html) if you need the foundations.

> **Who is this for?** Engineers who already have a working RAG pipeline and want to improve answer quality, latency, and cost without rewriting everything.

---

## Table of contents

1. [Why rerank at all?](#why-rerank)
2. [Two-stage retrieval](#two-stage-retrieval)
3. [Conditional rerank skip](#conditional-rerank)
4. [Query rewrite heuristics](#query-rewrite)
5. [MMR selection after rerank](#mmr-selection)
6. [Soft no-results gate](#soft-no-results)
7. [Auto model tier upgrade](#model-tier-upgrade)
8. [Per-request cost tracking](#cost-tracking)
9. [Vector-only vs vector + rerank](#vector-vs-rerank)
10. [Production code](#production-code)
11. [Tuning checklist](#tuning-checklist)
12. [Glossary](#glossary)

---

## Why rerank at all?

Embedding models optimize for **recall** — finding anything plausibly related. They compress meaning into a fixed vector, so subtle distinctions ("reset password" vs "change email") get blurred.

A **cross-encoder reranker** (Cohere `rerank-v3.5`) scores each query–document pair jointly. It's slower and more expensive per document, but far more accurate at ordering.

The standard production pattern: cast a wide net with vector search, then let the reranker pick the best handful.

| Stage | Goal | Typical k |
|-------|------|-----------|
| **Vector search** | High recall — don't miss relevant chunks | 30–40 |
| **Cohere rerank** | High precision — best chunks first | 8–10 |
| **MMR** | Diversity — avoid duplicate sections | 8 |
| **LLM prompt** | Context window budget | 8 |

---

## Two-stage retrieval

Stage 1 pulls **top-k ≈ 40** from Pinecone by cosine similarity. Stage 2 sends those 40 chunk texts to Cohere rerank and keeps the top **10** by relevance score.

**Pipeline:** Query → Embed → Pinecone top-40 → Cohere rerank-v3.5 → Top 10 → MMR → 8 → LLM prompt

Why 40 → 10 → 8? Vector top-40 catches chunks that embeddings rank poorly but rerankers love (common with procedural docs and rule tables). Rerank to 10 gives MMR room to swap near-duplicates. Final 8 fits most context budgets without drowning the LLM.

### Typical latency

| Stage | ~ms |
|-------|-----|
| Embed query | 80 |
| Pinecone vector search | 120 |
| Cohere rerank (40 docs) | 200 |
| LLM response | 1800 |

---

## Conditional rerank skip

Cohere rerank costs ~**$0.002 per request**. On a chatbot doing 50k queries/month, that's $100/month just for reranking — reasonable, but wasteful when vector search already found an obvious match.

**Skip rerank** when the top Pinecone hit has cosine similarity ≥ **0.85**. At that threshold, the best chunk is almost always correct; reranking adds little value.

**Always rerank** when:

- The turn is a **follow-up** (conversation history is non-empty)
- **Multi-query** mode is active (query was rewritten or expanded)
- Top cosine score is below 0.85

Follow-ups like "what about step 2?" embed poorly on their own. Forcing rerank on those turns prevents silent quality drops.

Typical rerank invocation mix:

- ~35% skipped on high-confidence first turns
- ~45% conditional rerank (cosine < 0.85)
- ~20% forced on follow-ups

---

## Query rewrite heuristics

Follow-up questions need context from prior turns. A cheap LLM (**Gemini Flash Lite**) rewrites "what about that?" into a standalone search query — but calling it on every turn adds latency and tokens.

Skip rewrite on **first-turn, self-contained questions** using simple heuristics:

- Question length ≥ 8 words
- No pronouns referring to prior context (`it`, `that`, `this`, `they`)
- No ordinal references (`step 2`, `option B`, `the second one`)
- Conversation history is empty

When rewrite runs, treat the result as multi-query — always rerank.

**Pipeline:** User message → Heuristics check → (optional) Flash Lite rewrite → Embed + retrieve

---

## MMR selection after rerank

Rerankers love returning multiple chunks from the same document section — five paragraphs about "password reset" when you need one rule chunk and one exception chunk.

**Maximal Marginal Relevance (MMR)** balances relevance against diversity. After rerank, run MMR with:

| Parameter | Value | Why |
|-----------|-------|-----|
| `k` | 8 | Final chunks in prompt |
| `lambda` | 0.85 | Favor relevance; only swap for clearly redundant chunks |

λ = 0.85 keeps related rule chunks (they're semantically similar but content-distinct) while dropping near-duplicate paragraphs from the same section.

---

## Soft no-results gate

Hard gates ("zero vector hits → return error") miss cases where vector search returns chunks but none are actually relevant.

After rerank, check the **top rerank score**. If it's below **0.05**, skip the LLM call entirely and return a helpful "I couldn't find relevant documentation" message.

This saves an expensive LLM call (~$0.01–0.05) on queries the knowledge base can't answer. It's a soft gate — vector search ran, rerank ran (or was skipped on high cosine), but confidence is too low to hallucinate an answer.

Rerank score vs answer quality: scores below 0.05 rarely produce useful answers. Quality rises sharply above 0.10 and plateaus near 0.30+.

---

## Auto model tier upgrade

Not every question needs your strongest model. Use rerank confidence to pick the LLM tier dynamically:

| Top rerank score | Model tier | Rationale |
|------------------|------------|-----------|
| ≥ 0.30 | Standard (Flash / 4o-mini) | Context is clear; cheap model suffices |
| 0.10 – 0.30 | Mid (Flash thinking / 4o) | Ambiguous context needs better reasoning |
| < 0.10 (but ≥ 0.05) | Pro (Opus / 4o full) | Weak signal — strongest model extracts what it can |
| < 0.05 | Skip LLM | Soft no-results gate |

Typical request distribution: ~55% standard tier, ~25% mid, ~12% pro, ~8% skipped.

---

## Per-request cost tracking

Log cost components on every request. You can't optimize what you don't measure.

| Component | Typical cost | Notes |
|-----------|--------------|-------|
| LLM (input + output) | ~70% of total | Dominates; tier selection matters most |
| Embeddings | ~12% | Query embed every turn; doc embed at ingest |
| Pinecone queries | ~15% | Scales with index size and QPS |
| Cohere rerank | ~3% | $0.002/call; ~65% invoked after conditional skip |

Track these fields per request:

- `embedding_tokens` and cost
- `pinecone_query_units`
- `cohere_rerank_invoked` (bool) and cost ($0.002 flat)
- `llm_input_tokens`, `llm_output_tokens`, model ID, and cost
- `rewrite_invoked` (bool) and rewrite model cost
- `total_cost_usd`

---

## Vector-only vs vector + rerank

| Metric | Vector only (top-8) | Vector (40) + rerank + MMR (8) |
|--------|---------------------|--------------------------------|
| Hit@8 (test set) | ~62% | ~89% |
| Answer quality (human eval) | 3.1 / 5 | 4.3 / 5 |
| Avg latency | ~200 ms retrieval | ~400 ms retrieval |
| Retrieval cost / request | ~$0.0003 | ~$0.0025 |
| Duplicate chunks in prompt | Common | Rare (MMR) |
| Follow-up quality | Poor | Good (forced rerank) |

The quality jump pays for itself in reduced support escalations and fewer "the bot gave wrong info" incidents.

---

## Production code

**app/rerank.py** — Cohere v2 rerank API with conditional skip logic:

```python
import os
import aiohttp

COHERE_RERANK_URL = "https://api.cohere.com/v2/rerank"
RERANK_MODEL = "rerank-v3.5"
VECTOR_TOP_K = 40
RERANK_TOP_N = 10
FINAL_TOP_K = 8
COSINE_SKIP_THRESHOLD = 0.85
RERANK_MIN_SCORE = 0.05
MMR_LAMBDA = 0.85

def should_run_cohere_rerank(
    top_cosine: float,
    is_follow_up: bool,
    is_multi_query: bool,
) -> bool:
    """Skip Cohere when vector confidence is high on a first-turn query."""
    if is_follow_up or is_multi_query:
        return True
    return top_cosine < COSINE_SKIP_THRESHOLD

async def cohere_rerank(
    query: str,
    documents: list[dict],
    top_n: int = RERANK_TOP_N,
) -> list[dict]:
    """Call Cohere v2 rerank API; return docs sorted by relevance score."""
    payload = {
        "model": RERANK_MODEL,
        "query": query,
        "documents": [d["text"] for d in documents],
        "top_n": top_n,
    }
    headers = {
        "Authorization": f"Bearer {os.environ['COHERE_API_KEY']}",
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(COHERE_RERANK_URL, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()

    ranked = []
    for result in data["results"]:
        doc = documents[result["index"]].copy()
        doc["rerank_score"] = result["relevance_score"]
        ranked.append(doc)
    return ranked

def mmr_select(
    docs: list[dict],
    k: int = FINAL_TOP_K,
    lambda_: float = MMR_LAMBDA,
) -> list[dict]:
    """Maximal Marginal Relevance — diversity without dropping related rules."""
    if len(docs) <= k:
        return docs
    selected, remaining = [docs[0]], docs[1:]
    while len(selected) < k and remaining:
        best_idx, best_score = 0, -1
        for i, candidate in enumerate(remaining):
            relevance = candidate["rerank_score"]
            max_sim = max(
                _text_overlap(candidate["text"], s["text"]) for s in selected
            )
            score = lambda_ * relevance - (1 - lambda_) * max_sim
            if score > best_score:
                best_score, best_idx = score, i
        selected.append(remaining.pop(best_idx))
    return selected

def _text_overlap(a: str, b: str) -> float:
    """Jaccard similarity on word sets — fast proxy for chunk redundancy."""
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

async def retrieve_and_rank(
    query: str,
    vector_hits: list[dict],
    is_follow_up: bool = False,
    is_multi_query: bool = False,
) -> dict:
    top_cosine = vector_hits[0]["score"] if vector_hits else 0.0
    cost = {"cohere_rerank": 0.0}

    if should_run_cohere_rerank(top_cosine, is_follow_up, is_multi_query):
        ranked = await cohere_rerank(query, vector_hits)
        cost["cohere_rerank"] = 0.002
    else:
        ranked = vector_hits[:RERANK_TOP_N]
        for d in ranked:
            d["rerank_score"] = d["score"]  # passthrough cosine as proxy

    top_score = ranked[0]["rerank_score"] if ranked else 0.0
    if top_score < RERANK_MIN_SCORE:
        return {"chunks": [], "skip_llm": True, "cost": cost}

    final = mmr_select(ranked) if cost["cohere_rerank"] > 0 else ranked[:FINAL_TOP_K]
    return {"chunks": final, "skip_llm": False, "top_rerank_score": top_score, "cost": cost}
```

**Query rewrite heuristics** — skip Flash Lite on clear first turns:

```python
import re

PRONOUNS = re.compile(r"\b(it|that|this|they|them|those|these|he|she)\b", re.I)
ORDINALS = re.compile(r"\b(step\s+\d|option\s+[a-z]|first|second|third|the\s+other)\b", re.I)

def needs_query_rewrite(message: str, history: list) -> bool:
    if not history:
        return False  # first turn — never rewrite
    if len(message.split()) >= 8 and not PRONOUNS.search(message) and not ORDINALS.search(message):
        return False  # self-contained despite history
    return True
```

---

## Tuning checklist

### Must have

- Two-stage retrieval (wide vector → rerank)
- Cohere rerank-v3.5 on follow-ups
- Soft no-results gate (score < 0.05)
- Per-request cost logging

### Should have

- Conditional rerank skip (cosine ≥ 0.85)
- MMR after rerank (λ = 0.85)
- Query rewrite with skip heuristics
- Model tier by rerank confidence

### Measure

- Hit@8 on 30+ test questions
- Rerank skip rate vs quality delta
- Cost per request by component
- Latency p50 / p95 by stage

---

## Glossary

| Term | Meaning |
|------|---------|
| **Cross-encoder reranker** | Model that scores query–document pairs jointly (Cohere rerank-v3.5) |
| **Bi-encoder** | Embedding model that encodes query and docs separately (vector search) |
| **MMR** | Maximal Marginal Relevance — selects diverse yet relevant results |
| **top-k** | Number of chunks retrieved at each stage |
| **Cosine similarity** | Vector distance metric; 1.0 = identical, 0.0 = orthogonal |
| **Soft no-results gate** | Skip LLM when rerank confidence is too low, even if vector hits exist |
| **Query rewrite** | LLM expands a follow-up into a standalone search query |
| **Conditional rerank** | Skip rerank API call when vector confidence is already high |

---

**Need help optimizing production RAG retrieval?** stackcone designs and ships RAG systems for enterprise and startups — reranking pipelines, cost optimization, evaluation harnesses, and deployment. [Hire us on Upwork](https://www.upwork.com/agencies/2022687811186513260/) or [contact us](../contact/).

Retrieval is where RAG quality is won or lost. Rerank for precision, skip for cost, MMR for diversity — and measure every dollar.

← [How to Build a Production RAG Chatbot](how-to-build-a-production-rag-chatbot.html)
