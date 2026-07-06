# Multi-Agent AI Platform for Interior Design, Product Data, and Project Workflows

By Amar Kumar

A proposed **multi-agent interior design AI** platform for a product team building customer-facing experiences in 3D modeling, interior design, architecture, and procurement. The architecture would use **Mastra** orchestration with TypeScript services, Python data pipelines, and PostgreSQL — three specialized agents (SKU ingestion, design selection, project coordination) sharing memory, tool registries, and eval gates so outputs are reliable enough for production workflows, not demo chat.

**Proposed outcome:** Observable Mastra agents that reason over structured product catalogs, call internal APIs with retries and handoffs, and ship measurable quality improvements through traces, evals, and regression suites.

## Scenario

This brief describes a **proposed solution** — not a delivered engagement. It maps a pattern common to design-tech products: an existing codebase, a growing SKU catalog, and a need for agents that integrate with real systems rather than generic chat wrappers.

- **Platform:** Interior design / architecture product with 3D modeling, room planning, and procurement
- **Owner profile:** Product engineering team with production TypeScript apps; agents must be observable, testable, and safe to deploy incrementally
- **Scope:** SKU ingestion agent, design agent, project agent — plus shared orchestration, memory, evals, and voice/SMS surfaces
- **Stack direction:** TypeScript + Mastra for orchestration and APIs; Python for bulk data normalization; AWS + PostgreSQL for state

## Problem

Generic LLM chat does not survive contact with structured product data, budget constraints, or procurement handoffs:

- **Catalog chaos** — SKUs arrive from vendors with inconsistent attributes, missing dimensions, and duplicate variants; manual cleanup blocks new product launches
- **Design hallucination** — agents pick products that do not exist in catalog, violate room constraints, or ignore budget without grounded retrieval
- **Project drift** — scope, budget, and status live in separate systems; users get stale updates unless an agent coordinates across project, design, and procurement APIs
- **No shared memory** — each chat session forgets prior room context, approved selections, and open procurement tasks
- **Unobservable failures** — without traces and evals, tool-call errors, retry storms, and prompt regressions surface only in customer complaints
- **Unsafe automation** — publishing unvalidated SKU records or placing procurement actions without permission gates risks revenue and trust

## Requirements

### Functional

- **SKU ingestion agent** — gather vendor feeds, validate schema, enrich attributes, flag gaps, stage records for human review, publish to catalog API
- **Design agent** — select products from catalog given room context, style preferences, constraints (dimensions, budget, availability); explain tradeoffs; persist selections to project state
- **Project agent** — track scope and budget, coordinate status updates via text or voice, support procurement workflows, hand off to design or catalog agents when needed
- **Shared orchestration** — Mastra workflows with explicit handoffs, retries, and dead-letter handling
- **Tool layer** — typed tools for catalog search, project CRUD, procurement quotes, 3D asset metadata, notifications (SMS/voice)
- **Evals & regression** — golden datasets for SKU validation, design constraint satisfaction, and project status accuracy

### Non-functional

- Production-grade logging, tracing (OpenTelemetry-compatible), and structured audit trails
- Human-in-the-loop gates for catalog publish and procurement commits
- Role-based permissions on tools (read-only vs write vs approve)
- P95 agent turn latency targets for customer-facing surfaces; async jobs for bulk SKU ingestion
- Idempotent tool calls with dedupe keys on writes
- AWS deployment with secrets in Parameter Store or Secrets Manager

## Architecture

Three layers: **customer surfaces** (web/voice) call a **Mastra orchestration plane** that routes to specialized agents; agents read/write **PostgreSQL** shared memory and call **internal product/design/project APIs** via typed tools. Python workers handle heavy SKU normalization off the hot path.

### End-to-end flow

Scheduler / user intent → Router → SKU | Design | Project agent → Shared memory → Internal APIs → Eval gate → Customer or ops notification

## Recommended stack

| Layer | Technology | Why |
|-------|------------|-----|
| Agent orchestration | Mastra (TypeScript) | Native tool calling, workflows, memory, observability hooks; fits existing TS codebase |
| Customer API | Node.js / Hono or Next.js route handlers | Low-latency streaming for design sessions |
| Data processing | Python 3.11 (Pandas, Pydantic) | Vendor feed parsing, attribute normalization, bulk validation |
| State & memory | PostgreSQL + pgvector | Relational project/SKU state; optional embeddings for semantic catalog search |
| Queue | AWS SQS + Lambda or BullMQ on ECS | Async SKU ingestion batches, retry with backoff |
| LLM | Claude / GPT-4.1 (configurable per agent) | Strong tool use; swap via Mastra model config |
| Observability | OpenTelemetry → CloudWatch / Langfuse | Traces per tool call, eval score trends |
| Voice / SMS | Twilio + optional Vapi | Project status updates and procurement confirmations |
| Deploy | AWS ECS Fargate or EKS | Co-locate TS API and Python workers in VPC |

**Why Mastra over LangGraph-only?** The job context expects TypeScript-first agent code alongside existing apps. Mastra provides agent primitives, memory, and workflow composition in TS without splitting orchestration into a separate Python service. Python remains for data-heavy SKU pipelines where the ecosystem is stronger.

**Why not a single mega-agent?** SKU validation, design selection, and project coordination have different tools, eval rubrics, and blast radii. Separate agents with explicit handoffs keep prompts smaller and failures isolated.

## Agent design

### 1 — SKU Ingestion Agent

- **Input:** vendor CSV/JSON/API feed, existing catalog schema, enrichment rules
- **Output:** staged `product_staging` rows with validation report, missing-field checklist, suggested attribute fills
- **Tools:** `parse_vendor_feed`, `validate_sku_schema`, `lookup_existing_variant`, `enrich_from_supplier_api`, `stage_for_review`, `publish_to_catalog` (gated)
- **QA gates:** schema pass, no duplicate SKU collision, required dimensions present, price within sanity bounds; human approve before `publish_to_catalog`

### 2 — Design Agent

- **Input:** user brief, room dimensions, style tags, budget ceiling, project ID
- **Output:** ranked product shortlist with rationale, constraint satisfaction notes, persisted `design_selections`
- **Tools:** `search_catalog` (filtered + vector), `get_room_context`, `check_dimensions_fit`, `estimate_line_total`, `save_selection`, `request_alternative`
- **QA gates:** every SKU must resolve to live catalog ID; budget sum ≤ ceiling unless user override flag; dimensions checked against room bounds

### 3 — Project Agent

- **Input:** project ID, user message (text/voice), notification preferences
- **Output:** status summaries, scope/budget deltas, procurement task updates, handoff payloads to design or SKU agents
- **Tools:** `get_project_state`, `update_milestone`, `create_procurement_request`, `send_sms`, `initiate_voice_call`, `handoff_to_agent`
- **QA gates:** no procurement commit without explicit user confirmation token; budget alerts before threshold breach

### Shared memory model

- **Thread memory** — current session messages and tool results (Mastra memory store)
- **Project memory** — durable rows: room context, selections, budget ledger, open tasks (PostgreSQL)
- **Catalog memory** — normalized SKU index refreshed on publish events (PostgreSQL + optional pgvector)

## Implementation plan

### Phase 1 — Foundation (week 1–2)

Postgres schemas (`projects`, `product_staging`, `design_selections`, `agent_runs`), Mastra project scaffold, OpenTelemetry wiring, catalog read API client with mocked responses.

**Risk:** Undocumented internal APIs — start with read-only stubs and contract tests. **Rollback:** feature-flag agents off; existing product flows unchanged.

### Phase 2 — SKU ingestion pipeline (week 3–4)

Python normalization worker, staging tables, SKU agent with validation tools, ops review UI or CSV export, eval set for schema edge cases.

### Phase 3 — Design agent + catalog retrieval (week 5–6)

pgvector index or filtered SQL search, design agent tools, constraint checker, streaming customer endpoint, golden-room eval scenarios.

### Phase 4 — Project agent + notifications (week 7–8)

Project state machine, Twilio SMS integration, voice webhook stub, handoff protocol between agents, permission matrix on tools.

### Phase 5 — Evals, tracing, regression CI (week 9–10)

Langfuse or OTEL dashboards, nightly eval job, PR gate on critical eval suites, dead-letter replay tooling.

### Phase 6 — Production hardening (week 11–12)

Load testing on design sessions, rate limits, runbooks, on-call alerts, documentation for prompt and tool versioning.

## Reporting & ops

| Metric | Source | Cadence |
|--------|--------|---------|
| Tool call success / latency | OpenTelemetry traces | Real-time dashboard |
| SKU validation pass rate | `agent_runs` + staging table | Daily |
| Design constraint satisfaction | Eval suite scores | Per deploy + nightly |
| Catalog publish cycle time | Staging → published timestamps | Weekly |
| Project notification delivery | Twilio logs | Daily |
| Agent handoff failures | Mastra workflow dead-letter | Alert on threshold |

Weekly engineering digest: eval regressions, top tool errors, SKU backlog age, P95 design session latency.

## Proposed deliverables

- Mastra monorepo with three agents, shared tool registry, and workflow handoff definitions
- PostgreSQL schemas and migrations for project memory, SKU staging, and audit logs
- Python SKU normalization service with vendor adapter pattern
- Customer-facing streaming API for design sessions with session memory
- Twilio SMS/voice integration for project status updates
- Eval harness with golden datasets and CI regression gate
- OpenTelemetry dashboards and on-call runbook for agent failures

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| Initial production build (phases 1–6) | 320–480 hrs |
| Ongoing eval tuning, catalog rule updates | 20–40 hrs/month |

Assumes existing product APIs are documented or discoverable, one staging AWS environment, and human-in-the-loop for catalog publish until eval thresholds are trusted.

## Glossary

| Term | Meaning |
|------|---------|
| **Mastra** | TypeScript framework for building agents with tools, memory, and workflows |
| **SKU** | Stock keeping unit — smallest sellable product variant in the catalog |
| **Handoff** | Explicit transfer of control and context from one agent to another |
| **Staging** | Pre-production product records awaiting validation and approval |
| **Eval** | Automated test of agent output against expected constraints or golden answers |
| **pgvector** | PostgreSQL extension for vector similarity search over embeddings |
| **HITL** | Human-in-the-loop — required approval before high-impact tool calls |
