# Persistent Reasoning Engine for Evolving Enterprise Knowledge Models

By Amar Kumar

A proposed **persistent reasoning engine** that ingests evolving public documents — SEC filings, annual reports, shareholder letters, earnings transcripts, and news — and maintains a **continuous enterprise knowledge model** over time. Each new document would update existing enterprise state rather than produce an isolated summary. Version 1 would validate the architecture on multi-year Microsoft and Amazon annual reports using Python, FastAPI, PostgreSQL, and LLM-driven structured extraction.

**Proposed outcome:** A working prototype that extracts doctrine, capabilities, obligations, risks, management decisions, and causal relationships into a versioned enterprise graph — with year-over-year diffs and trajectory views, not stock recommendations.

## Scenario

This brief describes a **proposed solution** — not a delivered engagement. It maps a pattern for builders who need organizational continuity across documents, not per-document RAG answers.

- **Platform:** Research or intelligence product maintaining evolving enterprise models from public filings
- **Owner profile:** Technical founder or systems engineer who values architecture over API glue; prototype is validation for a larger multi-domain reasoning platform
- **Scope:** SEC 10-K, 10-Q, 8-K; shareholder letters; earnings transcripts; PDF and HTML parsing; persistent state; temporal comparison
- **V1 milestone:** Ingest Microsoft and Amazon annual reports across multiple years; extract structured enterprise objects; demonstrate state evolution

## Problem

Document summarization and RAG pipelines fail the continuity requirement:

- **Isolated summaries** — each filing becomes a standalone blob; no merge semantics when Q3 guidance contradicts Q1 statements
- **No enterprise ontology** — free-text summaries do not encode doctrine, obligations, or causal links in queryable form
- **Lost temporal context** — systems cannot answer "how did stated risk posture change from 2022 to 2024?"
- **Re-ingestion amnesia** — re-summarizing all documents on each update is expensive and non-deterministic; diffs are unexplainable
- **Entity drift** — the same capability described differently across years is not reconciled to a stable enterprise object ID
- **Wrong output shape** — buyers need a structured enterprise model and trajectory, not investment advice or bullet-point abstracts

### Summarization vs persistent reasoning

| Dimension | Document summarization | Persistent reasoning engine |
|-----------|------------------------|----------------------------|
| Unit of output | Per-document summary | Evolving enterprise state |
| On new input | Generate new text | Merge, supersede, or extend existing objects |
| Memory | Stateless or retrieval-only | Authoritative state store with provenance |
| Queries | "What does this filing say?" | "What changed in obligations since last year?" |
| Time | Implicit in document date | First-class versioning and trajectory |

## Requirements

### Functional

- Ingest SEC filings (10-K, 10-Q, 8-K), shareholder letters, earnings transcripts from PDF and HTML
- LLM extraction into typed enterprise objects: doctrine, capabilities, active states, active obligations, risks, management decisions, causal relationships, enterprise trajectory
- Persistent enterprise record per organization with stable object IDs and provenance (source doc, section, span)
- Temporal comparison: current state vs prior years; change log with add/update/supersede/retire events
- Reconciliation when new documents conflict with or refine prior extractions
- Query API returning structured state and diffs — not recommendations

### Non-functional

- Deterministic merge rules where possible; LLM used for extraction, not ad-hoc state mutation
- Full audit trail: every object field links to source evidence
- Idempotent ingestion (re-run same filing does not duplicate state)
- PostgreSQL as system of record; optional graph layer for causal edges
- FastAPI services with OpenAPI contracts for prototype consumers
- Eval harness on extraction quality and merge correctness

## Architecture

Four layers: **ingestion** normalizes source documents; **extraction** produces candidate objects; **reconciliation** merges into authoritative enterprise state; **temporal API** serves state snapshots and diffs.

### End-to-end flow

Fetch filing → Parse PDF/HTML → Chunk with structure → LLM extract → Reconcile to enterprise state → Version snapshot → Diff vs prior year

## Recommended stack

| Layer | Technology | Why |
|-------|------------|-----|
| API | FastAPI (Python 3.11) | Async ingestion jobs, OpenAPI, Pydantic models |
| LLM | OpenAI / Anthropic with structured outputs | Reliable JSON schema extraction at scale |
| System of record | PostgreSQL | Relational enterprise objects, versions, provenance |
| Graph (causal edges) | Apache AGE on PostgreSQL or Neo4j | Native traversal for causal relationships without a second ops burden (AGE) |
| Vectors (optional) | pgvector | Evidence retrieval for reconciliation context, not primary memory |
| Parsing | Unstructured, pdfplumber, BeautifulSoup | PDF tables, HTML SEC exhibits |
| SEC source | EDGAR full-text search API / RSS | Official filing metadata and URLs |
| Queue | Celery + Redis or ARQ | Async multi-document ingestion |
| Observability | OpenTelemetry + structured logs | Trace extraction and merge decisions |

**Why not RAG-only?** Retrieval returns chunks; it does not maintain authoritative merged state. Vectors support evidence lookup during reconciliation, not replace the enterprise record.

**Why PostgreSQL-first?** Enterprise objects are relational (obligations reference capabilities; decisions reference risks). Temporal versioning maps cleanly to snapshot tables. Graph extension adds causal edges without abandoning SQL ops.

## Agent / component design

### 1 — Ingestion service

- **Input:** CIK or ticker, filing type, date range
- **Output:** normalized `documents` rows with parsed sections, tables, metadata
- **Tools:** EDGAR fetch, PDF/HTML parser, section classifier (Item 1A Risk Factors, MD&A, etc.)

### 2 — Extraction agent

- **Input:** document sections + current enterprise state summary (for coreference)
- **Output:** candidate objects per schema with confidence and evidence spans
- **QA gates:** schema validation, required fields, citation to source offset

### 3 — Reconciliation engine

- **Input:** candidate objects + existing enterprise state
- **Output:** merge plan: create, update, supersede, retire; no orphan objects
- **Rules:** stable IDs via embedding similarity + human-readable label match; explicit supersession chains

### 4 — Temporal diff service

- **Input:** organization ID, two snapshot dates
- **Output:** structured diff — added/removed/changed objects per category; trajectory narrative (optional LLM, grounded in diff JSON only)

## Implementation plan

### Phase 1 — Schema and ingestion (week 1–2)

PostgreSQL schemas for organizations, documents, enterprise objects, versions, provenance. EDGAR fetch + PDF parse for 10-K on MSFT and AMZN (2 years each).

### Phase 2 — Extraction pipelines (week 3–4)

Pydantic enterprise schemas, per-section LLM prompts, structured output validation, golden-section eval set.

### Phase 3 — Reconciliation and versioning (week 5–6)

Merge engine, object ID stability, snapshot on each ingestion, supersession logic for doctrine and obligations.

### Phase 4 — Temporal diff API (week 7)

FastAPI endpoints: `GET /enterprise/{id}/state`, `GET /enterprise/{id}/diff?from=&to=`, causal graph export.

### Phase 5 — Expanded sources (week 8)

8-K, shareholder letters, earnings transcripts; cross-document entity linking.

### Phase 6 — Evals and prototype hardening (week 9–10)

Regression suite, ingestion idempotency tests, documentation for V1 demo.

## Reporting & ops

| Metric | Source | Cadence |
|--------|--------|---------|
| Extraction schema pass rate | validation logs | Per document |
| Merge conflict rate | reconciliation audit | Per ingestion |
| Object provenance coverage | DB constraint checks | Daily |
| Ingestion latency | job traces | Per run |
| Eval regression | CI suite | Per PR |

## Proposed deliverables

- FastAPI service with ingestion, state, and diff endpoints
- PostgreSQL schema for versioned enterprise objects and provenance
- LLM extraction pipelines for SEC 10-K sections (extensible to 10-Q, 8-K)
- Reconciliation engine with supersession and stable object IDs
- Microsoft and Amazon multi-year prototype dataset with demonstrated trajectory
- Eval harness with golden extractions and merge scenarios
- Architecture doc contrasting summarization vs persistent reasoning

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| V1 prototype (phases 1–6) | 200–280 hrs |
| Ongoing schema tuning, new filing types | 15–25 hrs/month |

Assumes two companies × 3+ years of 10-K as validation corpus; human review of merge rules during first month.

## Glossary

| Term | Meaning |
|------|---------|
| **Enterprise state** | Authoritative structured model of an organization at a point in time |
| **Doctrine** | Stated principles, values, or strategic beliefs expressed by leadership |
| **Active obligation** | Commitment or constraint the enterprise is bound to fulfill |
| **Supersession** | New object replaces prior version while preserving lineage |
| **Provenance** | Source document, section, and text span supporting an extracted fact |
| **Temporal diff** | Structured comparison between two enterprise snapshots |
| **EDGAR** | SEC Electronic Data Gathering, Analysis, and Retrieval system |
