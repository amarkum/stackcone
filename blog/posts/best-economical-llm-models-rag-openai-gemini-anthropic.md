# Best Economical LLM Models for RAG

**June 2026 · Published by Amar Kumar**

Picking a chat model is not just a quality decision — it is a **unit economics** decision. In RAG, every turn sends **system prompt + chat history + retrieved chunks + user query** to the API. A model that costs 10× more per token can turn a $5/month side project into a $200/month bill at the same traffic.

This guide compares **OpenAI**, **Google Gemini 3** (and budget 2.5 tiers), and **Anthropic Claude** for general chat and production RAG — with list-price tables, a worked cost model that includes **chat history and context**, and charts showing what you actually pay per 10,000 queries.

> **Pricing note:** Figures use each provider's published API list prices as of **June 2026**. Google's current lineup is the **Gemini 3 family** ([Gemini 3 docs](https://ai.google.dev/gemini-api/docs/gemini-3), [API pricing](https://ai.google.dev/gemini-api/docs/pricing)). Verify before budgeting — rates change with model versions, caching, batch tiers, and thinking tokens.

## Who is this for?

Teams building RAG chatbots, internal knowledge assistants, or customer-support bots who need **good-enough answers at the lowest sustainable cost**.

## Gemini 3 lineup (current)

| Model | Model ID | Input / 1M | Output / 1M | Context | Role |
|-------|----------|------------|-------------|---------|------|
| **Gemini 3.1 Flash-Lite** | `gemini-3.1-flash-lite` | $0.25 | $1.50 | 1M | Cheapest **3-series** — high-volume RAG |
| **Gemini 3 Flash Preview** | `gemini-3-flash-preview` | $0.50 | $3.00 | 1M | Pro-level intelligence at Flash speed |
| **Gemini 3.5 Flash** | `gemini-3.5-flash` | $1.50 | $9.00 | 1M | Latest fast flagship (Google I/O 2026) |
| **Gemini 3.1 Pro Preview** | `gemini-3.1-pro-preview` | $2.00 / $4.00* | $12 / $18* | 1M | Deepest reasoning in 3 family |

\*Pro pricing doubles above 200k input tokens.

**Still available (2.5 budget tier):** **Gemini 2.5 Flash-Lite** at **$0.10 / $0.40** per 1M — often the **absolute cheapest** Google option for text RAG today, even below 3.1 Flash-Lite.

## General chat comparison (all three providers)

| Model | Provider | Input / 1M | Output / 1M | Context | Best for general chat |
|-------|----------|------------|-------------|---------|------------------------|
| **Gemini 2.5 Flash-Lite** | Google | $0.10 | $0.40 | 1M | Lowest $/token chat |
| **Gemini 3.1 Flash-Lite** | Google | $0.25 | $1.50 | 1M | Cheap 3-series chat + agents |
| **GPT-5.4 nano** | OpenAI | $0.20 | $1.25 | 400K | Cheapest OpenAI 5.x |
| **Gemini 3 Flash Preview** | Google | $0.50 | $3.00 | 1M | Smart default in Gemini 3 |
| **GPT-5.4 mini** | OpenAI | $0.75 | $4.50 | 400K | OpenAI volume workhorse |
| **Claude Haiku 4.5** | Anthropic | $1.00 | $5.00 | 200K | Careful answers + caching |
| **Gemini 3.5 Flash** | Google | $1.50 | $9.00 | 1M | Latest fast flagship |
| **GPT-5.4** | OpenAI | $2.50 | $15.00 | 1M | OpenAI production default |
| **Gemini 3.1 Pro Preview** | Google | $2.00 | $12.00 | 1M | Hard multimodal + agents |
| **Claude Sonnet 4.6** | Anthropic | $3.00 | $15.00 | 1M | Coding, agents, precision |
| **GPT-5.5** | OpenAI | $5.00 | $30.00 | 1M | Frontier reasoning |
| **Claude Opus 4.7** | Anthropic | $5.00 | $25.00 | 1M | Hardest tasks only |

Sources: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [OpenAI pricing](https://openai.com/api/pricing/), [Anthropic pricing](https://www.anthropic.com/pricing).

## Budget-tier by provider

| Tier | OpenAI | Google Gemini | Anthropic |
|------|--------|---------------|-----------|
| Ultra-cheap | GPT-5.4 nano ($0.20 / $1.25) | 2.5 Flash-Lite ($0.10 / $0.40) | — |
| Cheap 3-series / modern | — | 3.1 Flash-Lite ($0.25 / $1.50) | — |
| Mid-budget | GPT-5.4 mini ($0.75 / $4.50) | 3 Flash Preview ($0.50 / $3.00) | Haiku 4.5 ($1.00 / $5.00) |
| Fast flagship | GPT-5.4 ($2.50 / $15.00) | 3.5 Flash ($1.50 / $9.00) | Sonnet 4.6 ($3.00 / $15.00) |
| Frontier | GPT-5.5 ($5.00 / $30.00) | 3.1 Pro ($2.00 / $12.00) | Opus 4.7 ($5.00 / $25.00) |

## What a RAG request actually bills

Typical **single RAG turn** token budget:

| Component | Tokens | Notes |
|-----------|--------|-------|
| System prompt | 400 | Citations, persona, safety |
| Chat history (last 8 turns) | 1,800 | Grows every turn — trim or summarize |
| Retrieved chunks (5 × ~450) | 2,250 | Main cost driver after history |
| User query | 80 | — |
| **Total input** | **~4,530** | Billed as input tokens |
| Assistant reply | 350 | Billed as output tokens |

**Add-ons:** embeddings (~$0.000002/query), optional rerank (~$0.001/search), optional query rewrite (cheap LLM call).

**Chat history tip:** A 20-turn thread can add **5,000+ tokens** before retrieval — summarize older turns.

## Cost per RAG turn (with history + context)

Using **4,530 input + 350 output tokens**:

| Model | Cost / RAG turn | vs cheapest |
|-------|-----------------|-------------|
| **Gemini 2.5 Flash-Lite** | **~$0.00059** | — |
| Gemini 3.1 Flash-Lite | ~$0.00166 | +181% |
| GPT-5.4 nano | ~$0.00134 | +127% |
| Gemini 3 Flash Preview | ~$0.00332 | +463% |
| GPT-5.4 mini | ~$0.00497 | +743% |
| Claude Haiku 4.5 | ~$0.00628 | +964% |
| Gemini 3.5 Flash | ~$0.00995 | +1,586% |
| GPT-5.4 | ~$0.0166 | +2,712% |
| Claude Sonnet 4.6 | ~$0.0188 | +3,089% |

*List prices, standard tier. Context caching and batch API (50% off on Gemini) reduce effective cost.*

## Monthly cost at 10,000 RAG queries

| Model | ~$/month (10k queries) |
|-------|------------------------|
| Gemini 2.5 Flash-Lite | **~$5.90** |
| GPT-5.4 nano | ~$13.40 |
| Gemini 3.1 Flash-Lite | ~$16.60 |
| Gemini 3 Flash Preview | ~$33.20 |
| GPT-5.4 mini | ~$49.70 |
| Claude Haiku 4.5 | ~$62.80 |
| Gemini 3.5 Flash | ~$99.50 |
| GPT-5.4 | ~$166 |
| Claude Sonnet 4.6 | ~$188 |

At **100k queries/month**, Sonnet-default RAG ≈ **$1,880** vs **~$59** on 2.5 Flash-Lite.

## Best economical picks for RAG

| Use case | Our pick | Why |
|----------|----------|-----|
| **Cheapest RAG (any provider)** | Gemini 2.5 Flash-Lite | $0.10/$0.40, 1M context, free tier for dev |
| **Cheapest Gemini 3** | Gemini 3.1 Flash-Lite | Current 3-series budget model; better quality than 2.5 |
| **Balanced Gemini 3 RAG** | Gemini 3 Flash Preview | Stronger answers; still 5× cheaper than 3.5 Flash on output |
| **OpenAI-only stack** | GPT-5.4 nano → mini | Nano for volume; mini when reasoning matters |
| **Precision / compliance** | Claude Haiku 4.5 + caching | Instruction adherence; cache static system + docs |
| **Hard queries only** | Gemini 3.1 Pro / GPT-5.4 / Sonnet | Route &lt;10% of traffic — never as default RAG generator |

**Production pattern:** 2.5 Flash-Lite or 3.1 Flash-Lite for **answer generation**, optional rerank gate, frontier model only on escalation. See [Cohere reranking in production](cohere-reranking-production-rag-retrieval.html).

## FAQ

### Is Gemini 3 cheaper than Gemini 2.5 for RAG?

**Not always.** Gemini **3.1 Flash-Lite** ($0.25/$1.50) costs more than **2.5 Flash-Lite** ($0.10/$0.40). Use 3-series when you need newer reasoning; use 2.5 Flash-Lite when **cost per query** is the priority.

### What is Gemini 3.5 Flash for?

Google's **latest fast flagship** (May 2026) — best for agents, coding, and search-grounded chat. For high-volume RAG with retrieved chunks, it is usually **overkill on price** ($1.50/$9.00) unless answer quality justifies ~10× the cost of Flash-Lite.

### Does chat history increase RAG cost?

Yes — linearly. Every prior turn is billed as input tokens. Cap or summarize history.

## Related guides

- [How to Build a RAG Chatbot](how-to-build-a-production-rag-chatbot.html)
- [How to Evaluate RAG Retrieval](how-to-evaluate-rag-retrieval.html)
- [Cohere Reranking in Production RAG](cohere-reranking-production-rag-retrieval.html)
