# AI-Native Intelligence Platform for Private Markets Dealmaking

**By Amar Kumar**

This brief proposes an **AI-native private markets intelligence platform** that would combine retrieval-augmented generation, entity-normalized data pipelines, and agentic research workflows to help deal teams discover opportunities, counterparties, pricing references, and market signals from proprietary and licensed sources — with evaluation harnesses and user feedback loops that compound system quality over time.

**Proposed outcome:** A production-grade wedge product — starting with deal intelligence Q&A and market research copilot — backed by hybrid vector + structured retrieval, auditable agent traces, and institutional-grade access controls, with every user interaction feeding a proprietary data flywheel.

---

## Scenario

**Proposed solution** for an early-stage private-markets intelligence startup (2–9 people) building a B2B platform for institutional dealmakers, analysts, and operating partners.

- **Users:** Investment professionals sourcing deals, conducting diligence, and tracking market signals across PE, VC, credit, and secondary markets
- **Data mix:** Proprietary deal memos and CRM notes; licensed market data feeds; public filings and news; user-generated annotations and feedback
- **Wedge use case:** AI-assisted deal research — "find comparable transactions, summarize sector activity, surface counterparty history" — before expanding to matching and ranking
- **Team shape:** Senior AI engineer as technical/product owner; separate UX, backend, data engineering, and DevOps hires on parallel tracks
- **Constraints:** Licensed data usage terms, audit trails for institutional buyers, PII/financial sensitivity, low tolerance for hallucinated deal terms

## Problem

- **Fragmented research** — analysts jump between CRM, email, data rooms, Excel comps, and news terminals; no single query surface
- **Stale proprietary knowledge** — past deal memos and IC notes sit in SharePoint without semantic retrieval
- **Entity chaos** — same company appears as "Acme Inc.", "Acme Holdings LLC", and "Project Falcon" with no resolution graph
- **Generic LLM answers** — ChatGPT-style tools lack access to licensed comps and internal deal history; hallucinate multiples and dates
- **No quality loop** — early AI features ship without evals; thumbs-down feedback never reaches retrieval or prompt layers
- **Compliance gap** — institutional buyers require source citations, access logs, and data-lineage for every AI-generated insight
- **Prototype trap** — demos work on 50 documents; production needs ingestion at scale, schema evolution, and latency SLAs

## Requirements

### Functional

- **Deal intelligence Q&A:** Natural-language queries over proprietary + licensed corpus with cited sources and confidence scores
- **Market research workflows:** Agentic multi-step research — sector scan → comp selection → summary memo with structured output
- **Ranking & matching:** Score deals against mandate criteria (sector, size, geography, stage); suggest counterparties from relationship graph
- **Classification:** Auto-tag documents (CIM, term sheet, IC memo, news) and extract entities (company, sponsor, sector, EV, multiple)
- **Summarization:** Deal teasers, sector briefs, and meeting prep packs with editable drafts
- **Agentic discovery:** Tools for deal search, counterparty lookup, pricing reference retrieval, and market signal alerts
- **Data pipelines:** Ingestion from CRM exports, data room uploads, licensed API feeds, and scheduled news/filing pulls
- **Feedback loop:** Thumbs, edits, and "mark incorrect" flow back to eval sets and retrieval tuning
- **Entity normalization:** Canonical company/investor/deal IDs with alias resolution and merge audit

### Non-functional

- **Retrieval latency:** p95 &lt; 3 s for interactive Q&A; agent workflows may run 30–90 s async
- **Accuracy:** Eval harness targeting ≥85% citation relevance on golden QA set before feature GA
- **Security:** Row-level access by fund/mandate; encrypted at rest; SSO (SAML/OIDC); full query audit log
- **Auditability:** Every answer stores retrieved chunk IDs, model version, prompt hash, and user ID
- **Observability:** Langfuse or Phoenix traces; pipeline freshness dashboards; eval regression on deploy
- **Extensibility:** Schema versioning for extracted entities; pluggable embedding and LLM providers

## Architecture

Published HTML includes Mermaid diagrams (platform architecture, agent research sequence), pipeline strip, and five Chart.js charts.

```
Licensed + proprietary ingest → normalize entities → chunk + embed → hybrid retrieval
User query → router → RAG or agent workflow → cited answer → feedback → eval flywheel
PostgreSQL (structured) + pgvector/Qdrant (semantic) + optional knowledge graph
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| API | FastAPI + Pydantic v2 | Async, typed contracts, OpenAPI for frontend/admin integration |
| Orchestration | LangGraph | Stateful agent workflows with checkpoints, human-in-the-loop, tool routing |
| LLM | OpenAI GPT-4o + Anthropic Claude (router) | GPT-4o for extraction speed; Claude for long-context research memos |
| Embeddings | OpenAI text-embedding-3-large | Strong semantic recall; dimension reduction optional for pgvector |
| Vector store | PostgreSQL pgvector (MVP) → Qdrant (scale) | Single DB ops early; migrate when &gt;5M chunks or need hybrid filters at scale |
| Structured data | PostgreSQL | Deals, companies, investors, mandates, user feedback, audit logs |
| Entity resolution | Custom resolver + Splink (batch) | Deterministic rules for known IDs; probabilistic merge for fuzzy names |
| Pipelines | Dagster or Prefect | Scheduled ingest, backfill, data quality checks, lineage metadata |
| Object storage | S3 / GCS | Raw documents, parsed text, embedding cache |
| Evals | Langfuse + custom pytest harness | Online traces + offline golden-set regression |
| Auth | Auth0 or Clerk (SSO) | Institutional SAML; row-level security in app layer |
| Infra | AWS (ECS/Fargate) or GCP Cloud Run | Managed containers, secrets manager, VPC for licensed feed access |

**Why LangGraph over bare LangChain?** Explicit graph state, retry branches, and human approval nodes map cleanly to multi-step research workflows with audit checkpoints.

**Why pgvector before Qdrant?** Early team avoids operating two databases; PostgreSQL row-level security aligns with mandate-scoped access. Migrate when ANN latency or filter complexity demands it.

**Why Dagster over Airflow?** Asset-centric lineage fits "document → chunks → embeddings → eval set" dependencies; easier for a small data eng hire to reason about.

## Agent & component design

1. **Ingestion worker** — parse PDF/DOCX/XLSX, OCR fallback, document classifier, chunk with structure-aware splitter (headers, tables)
2. **Entity extractor** — LLM structured output → company, deal, sector, financials; write to `entities` + `entity_aliases` with provenance
3. **Hybrid retriever** — dense vector + BM25 keyword + metadata filters (fund, date, doc type); reciprocal rank fusion
4. **Q&A agent (wedge)** — single-turn RAG with citation formatter; refusal when confidence below threshold
5. **Research agent** — LangGraph loop: plan → retrieve → synthesize → self-critique → optional human review
6. **Matching/ranking service** — mandate vector + rule filters → scored deal list with explainability features
7. **Feedback processor** — capture edits and ratings → append to eval dataset → weekly retrieval weight tuning
8. **Eval runner** — CI job on golden 200-QA set: citation match, answer relevance (LLM-judge), latency p95

## Implementation plan

1. **Phase 1 — Wedge definition + data model (week 1–3):** Stakeholder workshops, canonical schema (deals, companies, documents), access model, 50-doc pilot corpus
2. **Phase 2 — Ingestion + entity normalization (week 4–7):** Dagster pipelines, parser library, entity resolver v1, freshness monitoring
3. **Phase 3 — Hybrid RAG layer (week 8–10):** Embeddings, pgvector indexes, retriever API, citation UX contract with frontend
4. **Phase 4 — Agentic research workflows (week 11–14):** LangGraph research agent, async job queue, memo export templates
5. **Phase 5 — Ranking, matching, evals (week 15–18):** Mandate matcher, eval harness in CI, Langfuse dashboards, feedback loop
6. **Phase 6 — Production hardening (week 19–22):** SSO, audit logs, licensed-data compliance review, load test, runbooks

## Reporting & ops

| Signal | Source | Cadence |
|--------|--------|---------|
| Retrieval recall@k | Offline eval suite | Every deploy |
| Citation accuracy | Golden QA + user "incorrect" flags | Weekly |
| Agent workflow success rate | LangGraph checkpoint outcomes | Daily |
| Pipeline freshness | Dagster asset materialization timestamps | Hourly alert if stale &gt; 6 h |
| Query latency p50/p95 | OpenTelemetry on FastAPI | Real-time dashboard |
| Feedback volume | `user_feedback` table | Weekly product review |
| Entity merge conflicts | Resolver audit queue | Weekly data quality review |
| Cost per query | Token + embedding usage by feature | Monthly |

## Proposed deliverables

- Canonical data model (ERD) for deals, companies, investors, documents, mandates
- Dagster ingestion pipelines with lineage and data quality tests
- Entity resolution service with merge audit trail
- Hybrid retrieval API (FastAPI) with mandate-scoped access
- Deal intelligence Q&A feature with source citations
- LangGraph research agent with async memo generation
- Matching/ranking module with explainability output
- Eval harness (200+ golden QAs) integrated in CI
- Langfuse/Phoenix observability dashboards
- Institutional security package: SSO, audit logs, encryption, access documentation
- Operator runbook: reindex, model rotation, licensed feed outage mode

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| Phases 1–6 (MVP platform through production hardening) | 320–480 hrs |
| Additional licensed feed integrations (each) | +40–80 hrs |
| Knowledge graph layer (Neo4j) | +60–100 hrs |
| Ongoing eval tuning + pipeline maintenance | 8–16 hrs/month |

## Glossary

| Term | Meaning |
|------|---------|
| **RAG** | Retrieval-augmented generation — LLM answers grounded in retrieved documents |
| **Hybrid retrieval** | Combining dense vector search with keyword (BM25) and metadata filters |
| **Entity resolution** | Matching varied names/references to one canonical company or deal record |
| **Data flywheel** | User interactions and feedback that improve models, retrieval, and proprietary dataset |
| **Mandate** | Investor criteria profile used to filter and rank deal opportunities |
| **CIM** | Confidential Information Memorandum — common private-markets deal document |
| **LangGraph** | Framework for building stateful, multi-step LLM agent workflows as graphs |
| **Golden eval set** | Curated question-answer pairs with expected citations for regression testing |
| **Row-level security** | Per-user or per-fund access restrictions on documents and derived entities |
