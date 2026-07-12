# Enterprise GRC Vendor Risk Management — Multi-Tenant SaaS Module

**By Amar Kumar**

This brief proposes a **Vendor Risk Management (VRM)** and compliance extension for an established multi-tenant **GRC SaaS** platform: supplier onboarding with inherent risk scoring, framework questionnaires (ISO 27001, SOC 2, NIST CSF, CIS), external security-rating adapters, AI evidence validation, and a full risk treatment lifecycle — delivered as gated milestones on the existing Python / SQLModel / React stack, including an on-premise Docker Compose deployment profile.

**Proposed outcome:** An enterprise client would run end-to-end vendor risk, compliance lifecycle automation, and risk treatment inside the platform — with tenant isolation, RBAC, auditable AI verdicts, OpenAPI-documented APIs, executive dashboards, and a clean-VM on-prem install runbook.

---

## Scenario

**Proposed solution** for a product owner extending a multi-tenant GRC platform for an enterprise/regulatory client — not greenfield; extend existing domain models, services, and repository patterns.

- **Platform:** Multi-tenant GRC (Governance, Risk & Compliance) SaaS
- **Feature set:** VRM module, compliance lifecycle automation, risk management & treatment workflow
- **Stack in place:** Python, SQLModel, PostgreSQL 16, Alembic, asyncpg, pytest; React (hooks); Docker Compose; Grafana
- **Constraints:** Sequential milestone gates, change maps before structural changes, no unapproved dependencies, product owner owns scoring/prompt semantics
- **Deploy:** Cloud multi-tenant plus on-premise Docker Compose profile

## Problem

- Vendor risk lives in spreadsheets and email — no same-day inherent scoring or tier-gated approvals
- Framework questionnaires (ISO/SOC/NIST/CIS) lack automated dispatch, reminders, and response tracking
- External security ratings and CVE signals are not continuous inside the GRC system of record
- Evidence collection and AI validation lack auditable attempts and human confidence gates
- Risk registers lack a five-stage lifecycle, configurable matrices, KRIs, and treatment → residual recalculation loop
- Enterprise buyers need on-prem deployability with operational runbooks

## Requirements

### Functional

- Supplier profiles, inherent risk on create, per-tenant tiers/weights/thresholds
- Framework questionnaire templates, dispatch, reminders, response tracking
- Ports/adapters for SecurityScorecard/BitSight-class providers + monitoring signals
- Evidence repository, certification expiry alerts, dashboards + PDF/XLSX export, OpenAPI
- Framework XLSX/CSV importer; evidence orchestrator; AI validation/assessment stages
- Gap records, compliance-rate recalculation, confidence-gated human review
- Risk dashboard, five-stage lifecycle, configurable L×I matrix, KRIs
- Gap-to-risk + AI treatment → remediation → re-test → residual → gated closure

### Non-functional

- Strict tenant isolation + RBAC; secrets only in backend env
- Performance at 500+ vendors/tenant (pagination, indexes, no N+1)
- pytest green per milestone; change maps for domain/structure changes
- On-prem Compose profile + clean-VM runbook; Grafana observability

## Architecture

Published HTML includes Mermaid diagrams (module architecture, compliance AI sequence), pipeline strip, and Chart.js charts.

```
Vendor create → inherent risk → questionnaires → ratings adapter
Evidence legs → AI validate → confidence gate → gaps / compliance rate
Risk lifecycle → treatment → remediation → AI re-test → residual
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| Backend | Existing Python + SQLModel + asyncpg | Extend domain; no greenfield |
| Migrations | Alembic | Schema evolution per milestone |
| Frontend | React hooks + CSS | Match platform conventions |
| Isolation | Multi-tenant + RBAC | Enterprise GRC requirement |
| Integrations | Ports/adapters | Swap SecurityScorecard/BitSight without domain coupling |
| AI stages | LLM validation/assessment | Structured verdicts + confidence gate |
| Deploy | Docker Compose on-prem | Clean-VM enterprise install |
| Observability | Grafana | Ops dashboards |

## Component design

1. Vendor profile & inherent risk engine  
2. Questionnaire & notification service  
3. Security-ratings adapter + signal pipeline  
4. Evidence orchestrator + AI judges  
5. Framework importer  
6. Risk lifecycle & matrix/KRI engine  
7. Treatment → remediation → residual loop  
8. On-prem Compose + runbook  

## Implementation plan

1. **Weeks 1–2** — Domain extensions, vendor profiles, inherent risk, tenant config  
2. **Weeks 2–4** — Questionnaires, ratings adapter, alerts, dashboards, on-prem Compose  
3. **Weeks 5–6** — Framework import + evidence orchestrator  
4. **Weeks 6–7** — AI validation stages, gaps, notifications  
5. **Weeks 8–9** — Risk lifecycle, matrix, KRIs, dashboards  
6. **Weeks 9–10** — Treatment workflow, scoring engine, hardgate acceptance  

## Reporting & ops

- Vendor risk tiers, questionnaire SLAs, rating signal drops  
- AI confidence / human-review queue depth  
- Gap closure and residual risk trends  
- On-prem Compose health + Grafana panels  

## Proposed deliverables

- VRM module with OpenAPI and exports  
- Compliance lifecycle + AI stages  
- Risk & treatment workflow  
- On-prem Docker Compose + runbook  
- pytest suite green per milestone  
- Change maps and PR-reviewed branches  

## Effort estimate

Indicative **320–400 hrs** over 10 weeks for a senior full-stack IC against an existing codebase (milestone-gated). Ongoing maintenance **12–20 hrs/month**.

## Glossary

| Term | Meaning |
|------|---------|
| GRC | Governance, Risk & Compliance |
| VRM | Vendor Risk Management |
| Inherent risk | Risk before controls/treatment |
| Residual risk | Risk remaining after treatment |
| KRI | Key Risk Indicator |
| Ports & adapters | Hexagonal pattern for external providers |
