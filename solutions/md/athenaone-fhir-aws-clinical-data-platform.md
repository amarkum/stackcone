# AthenaOne FHIR Integration — HIPAA AWS Clinical Data Platform

A proposed **AthenaOne FHIR integration** for a U.S. medical specialty practice that would extract clinical data on a daily incremental schedule, land raw FHIR and Data View payloads in a **HIPAA-compliant AWS** environment, normalize records into a searchable clinical warehouse, and lay groundwork for AI-powered chart search, summarization, and cohort analysis.

**Proposed outcome:** A specialty practice would run a daily AthenaOne sync into AWS, query full patient charts in seconds, retain versioned clinical history, and use AI tools for chart summaries and research cohorts — all within HIPAA guardrails and with a complete audit trail.

## Scenario

This brief describes a **proposed solution** — not a delivered engagement.

- **Organization:** U.S. medical specialty practice on AthenaOne; clinical leadership wants cloud analytics without replacing the EHR
- **Source systems:** AthenaOne REST APIs, FHIR R4 endpoints, and Athena Data View for bulk/tabular extracts
- **Scope:** Phase 1 daily incremental sync; Phases 2–3 normalize, index, and enable AI workflows
- **Owner profile:** Healthcare integration engineer or small data platform team; compliance officer involved in BAA and access reviews
- **Regulatory context:** HIPAA Security and Privacy Rules; PHI never leaves the BAA-covered AWS account

## Problem

AthenaOne holds the practice's clinical truth, but native reporting and ad-hoc exports do not scale to cross-chart search, longitudinal analysis, or AI-assisted review.

- **Data trapped in the EHR** — cross-patient queries require chart-by-chart review
- **No incremental sync** — full exports are expensive and duplicate unchanged records
- **API surface fragmentation** — FHIR plus Data View needed for full coverage
- **HIPAA complexity** — cloud storage without encryption and BAA creates compliance exposure
- **No version history** — medication and diagnosis changes need SCD2-style history
- **AI without governance** — consumer LLM tools violate policy for PHI

## Requirements

### Functional

- AthenaOne connectivity via OAuth2, FHIR R4, and Data View
- Daily incremental sync with `_lastUpdated` watermarks
- Resource coverage: Patient, Encounter, Condition, Medication, Allergy, Observation, DiagnosticReport, Procedure, ServiceRequest, DocumentReference
- Raw S3 landing zone; normalized Aurora warehouse; OpenSearch full-text index
- Version history (SCD2); audit logging; Phase 3 AI (summarization, timelines, cohorts)

### Non-functional

- HIPAA: BAA, KMS encryption, TLS, no PHI in logs
- Idempotent sync; observability with SNS alerts; least-privilege IAM

## Architecture

Four tiers: extraction (AthenaOne → S3), transformation (dbt → Aurora), search (OpenSearch + API), clinical AI (Bedrock + LangGraph).

### Recommended stack

| Layer | Technology | Why |
|-------|------------|-----|
| EHR source | AthenaOne FHIR R4 + Data View | Official APIs; incremental FHIR plus bulk gaps |
| Extraction | Lambda + EventBridge | Serverless per-resource parallelism |
| Raw storage | S3 (SSE-KMS) | Immutable replayable archive |
| Transform | dbt + Glue/ECS | Version-controlled SCD2 models |
| Warehouse | Aurora PostgreSQL | ACID joins for cohort SQL |
| Search | OpenSearch | Full-text across notes and reports |
| AI | Bedrock + LangGraph | HIPAA-eligible inference in BAA account |

## Component design

1. **Athena API connector** — watermark-driven FHIR extract to S3
2. **Document fetcher** — Binary attachments, Textract OCR
3. **Normalization engine (dbt)** — dim/fact tables with SCD2
4. **Search indexer** — OpenSearch bulk index on warehouse CDC
5. **Clinical search API** — FastAPI, audit-logged patient access
6. **Clinical AI orchestrator** — retriever, summarizer, cohort analyst, safety reviewer

## Implementation plan

1. **Weeks 1–2** — HIPAA AWS foundation, Athena OAuth, connectivity validation
2. **Weeks 3–5** — Incremental FHIR extractors, Data View jobs, backfill
3. **Weeks 6–9** — Aurora warehouse, dbt models, OpenSearch, internal API
4. **Weeks 8–10** — Document/attachment pipeline
5. **Weeks 11–14** — Bedrock RAG workflows, safety gates
6. **Weeks 14–16** — Pen test, compliance review, runbooks, handoff

## Reporting & ops

Daily sync health, row-count anomaly alerts, watermark lag, audit log exports, weekly unmapped-code review, monthly access audit.

## Proposed deliverables

- HIPAA AWS baseline, Athena OAuth integration, nightly FHIR extractors
- dbt project, Aurora warehouse, OpenSearch index, FastAPI
- LangGraph AI workflows, CloudWatch dashboard, runbooks, training

## Effort estimate

| Scope | Hours |
|-------|-------|
| Phases 1–6 total | 440–620 hrs |
| Ongoing maintenance | 16–24 hrs/month |

~14–18 weeks at 25–35 hrs/week.

## Glossary

- **FHIR R4** — HL7 clinical data exchange standard
- **Athena Data View** — athenahealth bulk export service
- **SCD2** — Slowly Changing Dimension Type 2 history pattern
- **RAG** — Retrieval-Augmented Generation for grounded AI answers
