# How to Evaluate RAG Retrieval (Before You Touch the Prompt)

**June 2026 · Practical guide**

Most teams tune the system prompt when answers are wrong. In production RAG, the problem is usually retrieval — and no prompt fix will save you if the right chunk never reached the model.

This guide shows how to build a golden eval set, measure **hit@k**, classify failures, and run a weekly loop that actually improves answer quality.

> **Who is this for?** Teams with a working RAG chatbot who want measurable retrieval quality, not gut feel.

---

## Table of contents

1. [The prompt tuning trap](#the-prompt-tuning-trap)
2. [What to measure](#what-to-measure)
3. [Build a golden eval set](#build-a-golden-eval-set)
4. [Run hit@k eval](#run-hitk-eval)
5. [Failure taxonomy](#failure-taxonomy)
6. [Fix order that works](#fix-order-that-works)
7. [Weekly eval loop](#weekly-eval-loop)
8. [Sample eval script](#sample-eval-script)
9. [Checklist](#checklist)
10. [Glossary](#glossary)

---

## The prompt tuning trap

User says: "The bot gave a wrong answer."

Default reaction: rewrite the system prompt.

Better reaction: ask **did the right document chunk appear in the top-k results?**

| If retrieval failed | If retrieval succeeded |
|---------------------|------------------------|
| Fix chunking, embeddings, top-k, rerank, or KB gaps | Then look at prompt, model, or context formatting |

Rough rule from production deployments: **more than half of "bad answers" are retrieval misses**, not generation errors. You cannot know which without eval.

---

## What to measure

Focus on retrieval metrics first. Generation quality (LLM-as-judge, human rating) comes second.

| Metric | What it tells you | Target to start |
|--------|-------------------|-----------------|
| **hit@k** | Expected source doc in top-k results | ≥ 85% at k=10 after rerank |
| **MRR** | How high the first relevant chunk ranks | ≥ 0.7 |
| **Rerank lift** | hit@k after rerank minus before | +10–25 points |
| **Empty retrieval rate** | Queries with zero usable chunks | < 5% |
| **Latency p95** | End-to-end retrieval time | Track, don't optimize day one |

Do **not** start with BLEU, ROUGE, or generic "answer similarity" — they hide retrieval failures.

---

## Build a golden eval set

A **golden eval set** is a fixed list of questions with known correct source documents.

### How many questions?

- **Minimum:** 30 (covers main topics)
- **Good:** 50–100 (includes edge cases)
- **Grow from prod:** add every user-reported failure

### Where questions come from

1. Real support tickets / chat logs (anonymized)
2. FAQ and onboarding docs ("how do I…")
3. Error codes and SKU lookups
4. Follow-up phrasing ("what about step 2?", "explain more")
5. Adversarial: typos, abbreviations, wrong product names

### Each row needs

```json
{
  "id": "eval-014",
  "question": "How do I reset my password?",
  "expected_doc_id": "account-settings",
  "expected_section": "Password reset",
  "tags": ["account", "password"],
  "notes": "Users often say 'forgot login'"
}
```

Store as JSON or CSV in git. Version it. Never edit silently — add rows, don't overwrite history.

---

## Run hit@k eval

**hit@k** = fraction of questions where the expected doc (or chunk) appears in the top-k retrieved results.

```python
def hit_at_k(results: list[list[str]], expected: list[str], k: int = 10) -> float:
    hits = 0
    for retrieved, gold in zip(results, expected):
        if gold in retrieved[:k]:
            hits += 1
    return hits / len(expected) if expected else 0.0
```

Run eval:

1. **After every KB sync** — catch ingest regressions
2. **After chunk size / embedding model changes**
3. **Before and after adding reranker**

Compare vector-only vs vector+rerank. If rerank adds 15+ points, it was worth the cost.

---

## Failure taxonomy

When a question fails, label it:

| Label | Symptom | Fix |
|-------|---------|-----|
| **Retrieval miss** | Right doc not in top-k | Chunking, top-k, rerank, hybrid search |
| **Wrong chunk** | Right doc, wrong section | Smaller chunks, heading-aware split |
| **Ambiguous query** | Multiple valid topics tied | Disambiguation prompt, ask clarifying question |
| **KB gap** | Answer not in docs | Add content, don't prompt-engineer |
| **Generation error** | Good context, wrong answer | Prompt, model tier, context template |
| **Out of scope** | Not in KB domain | Router or polite refusal |

Log the label in your eval spreadsheet. After 20 failures, the pattern is obvious.

---

## Fix order that works

Do not randomize. This order matches what actually moves hit@k in production:

1. **KB completeness** — missing docs beat every algorithm
2. **Chunking** — size, overlap, split on headings
3. **Same embedding model** at ingest and query
4. **Increase top-k** (30–40 before rerank)
5. **Add reranker** (Cohere, cross-encoder)
6. **Query rewrite** for multi-turn
7. **Hybrid BM25 + vector** for SKUs and error codes
8. **Prompt and model** — only after hit@k ≥ 85%

---

## Weekly eval loop

```
Monday:  Run golden set → export hit@k + failures
Tuesday: Triage top 5 retrieval misses (chunk? doc missing?)
Wed:     Fix + re-index if needed
Thursday: Re-run eval
Friday:  Add 3 new questions from prod failures
```

Track hit@k in a spreadsheet or dashboard. One number, one chart, every week.

---

## Sample eval script

```python
import json
from your_app.retrieve import retrieve  # your pipeline

def load_golden(path: str) -> list[dict]:
    return json.load(open(path))

def eval_retrieval(cases: list[dict], k: int = 10) -> dict:
    hits, mrr_sum = 0, 0.0
    for case in cases:
        docs = retrieve(case["question"], top_k=k)
        doc_ids = [d["metadata"]["doc_id"] for d in docs]
        gold = case["expected_doc_id"]
        if gold in doc_ids:
            hits += 1
            rank = doc_ids.index(gold) + 1
            mrr_sum += 1.0 / rank
    n = len(cases)
    return {
        "hit@k": hits / n,
        "mrr": mrr_sum / n,
        "n": n,
    }

if __name__ == "__main__":
    cases = load_golden("eval/golden.json")
    print(eval_retrieval(cases, k=10))
```

Wire this into CI as a smoke test (hit@k must not drop more than 2 points vs baseline).

---

## Checklist

**Must have**
- [ ] 30+ golden questions with expected doc IDs
- [ ] hit@k script runnable in one command
- [ ] Baseline hit@k recorded before changes
- [ ] Failure labels on every miss

**Should have**
- [ ] Eval runs after KB sync
- [ ] Separate vector-only vs rerank metrics
- [ ] Weekly triage ritual
- [ ] Prod failures added to golden set

**Later**
- [ ] LLM-as-judge on answer quality
- [ ] Per-topic hit@k breakdown
- [ ] Automated regression alerts in CI

---

## Glossary

| Term | Meaning |
|------|---------|
| **Golden eval set** | Fixed test questions with known correct sources |
| **hit@k** | % of queries where gold doc appears in top-k results |
| **MRR** | Mean reciprocal rank — rewards higher placement |
| **Retrieval miss** | Expected doc not returned in top-k |
| **Rerank lift** | hit@k improvement after cross-encoder rerank |
| **Regression** | hit@k drops after a change — roll back |

---

Measure retrieval first. Prompts are the last lever, not the first.

*See also: [How to Build a RAG Chatbot](how-to-build-a-production-rag-chatbot.html) · [Cohere Reranking in Production RAG](cohere-reranking-production-rag-retrieval.html)*
