# Production Property-Records Search Platform for NYC Open Data

A proposed **property records search platform** for a New York real-estate services company that already pulls municipal data from NYC's open-data ecosystem. The build would wrap the existing data engine in a production layer — an internal ordering portal, a reconciliation pipeline across 80+ official datasets with verify-links on every result line, human-in-the-loop review before finalization, and branded PDF delivery tracked by internal file number.

**Proposed outcome:** A daily-use internal product that replaces third-party vendor searches for NYC municipal/departmental records — turning raw open data into certified, client-ready reports with one-click source verification on every line item.

## Scenario

This brief describes a **proposed solution** — not a delivered engagement.

- **Organization:** Established NYC real-estate services company (title and settlement) with two decades of domain experience and an internal automation stack (AI pipelines, CRM, financial systems)
- **Existing asset:** Working data engine that already queries NYC open-data sources — the build extends this, not replaces it
- **Owner profile:** Expert-level full-stack engineer (or lead + helper) owning backend pipeline and internal portal UI; long-term multi-phase partnership
- **Geography:** NYC five boroughs for MVP; surrounding counties in later phases (different data model)
- **Users:** Production team ordering searches against properties/files, reviewing results, signing off before delivery
- **Liability context:** Outputs carry certification implications — auto-publish without human gate is unacceptable

## Problem

The company pays third-party vendors for municipal and title searches on properties. The underlying data is largely free from official NYC and NY State sources, and internal proof-of-concept pulls already work. What is missing is the production layer.

- **Vendor cost and latency** — recurring fees for data the organization can access directly; turnaround tied to external queues
- **No unified workflow** — orders, status, review, and delivery live across email, vendor portals, and spreadsheets
- **Messy government data** — 80+ datasets with inconsistent schemas, pagination, rate limits, stale records, and occasional errors
- **Provenance gap** — vendor PDFs rarely expose live links back to the official source record for line-by-line verification
- **Property key fragmentation** — datasets join on address, BBL (borough/block/lot), parcel ID, or agency-specific identifiers inconsistently
- **Liability without gates** — publishing a search result without human review and confidence scoring creates certification risk
- **No file-number spine** — internal title-production software tracks files; search results must map to that identifier for write-back in later phases

## Requirements

### Functional (Phase 1 MVP)

- **Ordering portal** — order a municipal/departmental search against a property and internal file number; select search type (COO, violations, tax/water/sewer, fire, housing, zoning, environmental, etc.)
- **BBL resolution spine** — address → geocode → borough/block/lot (BBL) as the canonical property key tying every dataset
- **Data pipeline** — resilient async jobs querying Socrata/SODA, ArcGIS REST, agency record systems; normalize into one result set per search
- **Verify-link on every line** — each result item includes a live URL to the official source record (non-negotiable)
- **Reconciliation** — merge duplicates, flag conflicts between sources, preserve raw provenance
- **Status dashboard** — searches grouped under files with green / needs-review / problem states
- **Human-in-the-loop review** — confidence scoring + sign-off gate before finalization
- **Branded PDF reports** — dynamic generation stored and retrievable by file number
- **Audit trail** — who ordered, when data was fetched, reviewer sign-off, PDF version history

### Functional (later phases)

- Title-chain module — recorded documents, judgments, liens, lis pendens, tax warrants, estate/probate, owner-name searches
- Write-back into existing title-production software via its API
- Slack-based approval/notification workflows
- Surrounding county expansion (ordering/intake automation where no unified open-data API exists)

### Non-functional

- **Reliability** — 80+ external APIs must not silently break; health checks, schema drift alerts, circuit breakers
- **Provenance** — immutable fetch metadata (source API, query, timestamp, raw payload hash) per result line
- **Security** — role-scoped portal access; secrets outside repo; R2 signed URLs for PDFs
- **Performance** — queue-backed parallel fetches; search completes in minutes, not hours
- **Observability** — per-dataset success rates, latency, error taxonomy
- **Extensibility** — new datasets added via config + adapter module, not forked pipeline code

## Architecture

Three tiers: a **portal + workflow layer** (React + Workers API), an **async data plane** (Queues + fetch workers + existing engine), and a **provenance + delivery layer** (D1 registry, R2 PDFs, review queue).

```
Address + file # → BBL resolver → Queue fan-out (80+ datasets)
       → Normalize + reconcile + provenance → Confidence score
       → Review queue → Sign-off → PDF → R2 + D1 registry
```

### Recommended stack

| Layer | Technology | Why |
|-------|------------|-----|
| Compute | Cloudflare Workers | Edge-native, consistent with client's newer systems; fast cold start for API routes |
| Database | D1 (SQLite) | Search orders, file registry, result lines, provenance, review state — relational fits audit model |
| Object storage | R2 | PDF reports, raw fetch snapshots, large JSON payloads |
| Async jobs | Queues + Cron Triggers | Parallel dataset pulls; scheduled health checks and stale-data refresh |
| Frontend | React (Vite) on Pages | Internal portal — order form, file dashboard, review UI |
| PDF | `@react-pdf/renderer` or Puppeteer on Worker (Browser Rendering) | Branded templates with verify-link QR/URLs per line |
| Geocoding | NYC Geoclient / GeoSearch + PLUTO join | Official NYC address → BBL resolution |
| Existing engine | Wrapped via Worker service binding or HTTP | Do not rebuild proven pull logic — adapter layer only |

**Why Cloudflare over AWS Lambda?** Client has standardized on Cloudflare for newer systems — one vendor, Workers + D1 + R2 + Queues co-located, no cross-AZ latency for metadata joins. AWS remains viable if team has deep existing investment, but consistency wins here.

**Why D1 over DynamoDB?** Search results are relational (files → searches → result_lines → provenance_records). SQL queries for dashboard filters and audit reports are simpler than single-table Dynamo patterns.

## Component design

### 1 — Order & workflow service

- **Input:** file number, address or BBL, search type checklist, requester
- **Output:** `search_id`, status transitions (`queued` → `fetching` → `reconciling` → `review` → `approved` → `delivered`)
- **QA gate:** validate file number format; reject duplicate in-flight search for same file+property+type

### 2 — Property key resolver

- **Input:** street address + borough, or raw BBL
- **Output:** normalized BBL, lat/lon, PLUTO attributes (building class, units, etc.)
- **Tools:** Geoclient API, PLUTO dataset, fallback manual BBL entry with reviewer flag

### 3 — Dataset fetch orchestrator

- **Input:** BBL + enabled dataset adapters for search type
- **Output:** raw payloads enqueued per adapter; fetch metadata logged
- **Pattern:** one Queue consumer per adapter family (SODA batch, ArcGIS, scraper-backed) with shared retry/backoff config

### 4 — Reconciliation & provenance engine

- **Input:** raw adapter results
- **Output:** normalized `result_lines` with `source_url`, `source_api`, `fetched_at`, `confidence_factors`
- **Rules:** dedupe by agency record ID; flag address mismatches; never drop provenance on merge

### 5 — Confidence scorer + review queue

- **Input:** reconciled result set
- **Output:** per-line and per-search confidence; route low-confidence or conflict items to review inbox
- **QA gate:** no PDF generation until reviewer sign-off (or auto-approve above threshold for low-risk line types if policy allows)

### 6 — PDF report generator

- **Input:** approved result set + branding template
- **Output:** PDF in R2; verify-link rendered as clickable URL per line
- **Versioning:** new PDF version on re-run; prior versions retained

### 7 — File & search registry (D1)

- Tables: `files`, `searches`, `result_lines`, `provenance_records`, `review_events`, `pdf_artifacts`
- Index on file number for retrieval; full audit log for certification defense

## Implementation plan

### Phase 1 — Foundation & engine wrap (week 1–3)

Provision Workers, D1 schema, R2 buckets, Queues. HTTP adapter wrapping existing data engine with health endpoint. BBL resolver service with PLUTO join. Basic REST API: create search, get status.

**Risk:** Undocumented engine APIs — schedule pairing sessions with internal team early. **Rollback:** read-only portal against engine without write path.

### Phase 2 — Dataset adapter library (week 4–7)

Implement adapter interface; port highest-priority datasets (DOB violations, HPD, ECB, tax/lien, COO, zoning). Shared SODA client with pagination, rate-limit handling, schema version pins. Cron health checks per dataset.

**Risk:** API schema drift — pin expected columns; alert on missing fields. **Rollback:** disable adapter via feature flag without stopping other datasets.

### Phase 3 — Portal UI (week 8–10)

React portal: order form, file-grouped dashboard (green/review/problem), search detail with result lines + verify links. Auth via Cloudflare Access or similar.

**Risk:** UX friction slows adoption — embed production team in weekly UAT. **Rollback:** API-only mode for power users.

### Phase 4 — Reconciliation & provenance (week 11–13)

Normalization rules, conflict detection, immutable provenance store. Verify-link validator (HTTP HEAD check that source URL resolves).

**Risk:** Source URLs change format — store agency record ID separately for rebuild. **Rollback:** show raw links even if validator fails; flag for review.

### Phase 5 — Review gate & PDF delivery (week 14–16)

Review queue UI, sign-off workflow, confidence scoring v1. Branded PDF template with per-line verify links. R2 storage + retrieval by file number.

**Risk:** PDF layout breaks on long violation lists — paginate with continuation sheets. **Rollback:** HTML report fallback until PDF stable.

### Phase 6 — Hardening & title-chain prep (week 17–20)

Load testing on 80+ parallel fetches, ops dashboards, runbooks, on-call alerts. Document adapter-add guide. Spike title-chain data sources for phase 2 roadmap.

## Reporting & ops

| Signal | Source | Cadence |
|--------|--------|---------|
| Search completion time | `searches` timestamps | Real-time dashboard |
| Per-dataset fetch success rate | adapter logs | Daily; alert if &lt; 95% |
| Review queue depth | `review_events` | Alert if &gt; N or &gt; 24h |
| Verify-link broken rate | link validator job | Weekly |
| API schema drift | health check cron | Immediate Slack alert |
| PDF generation failures | Worker error logs | Real-time |

## Proposed deliverables

- Cloudflare Workers API with D1 schema, R2 buckets, Queue topology
- Adapter library for 80+ NYC open-data sources with provenance model
- BBL resolution service (Geoclient + PLUTO)
- React internal portal (order, dashboard, review, PDF download)
- Human-in-the-loop review queue with confidence scoring
- Branded PDF report generator with verify-link on every line
- Ops dashboard and dataset health monitoring
- Runbooks: add new dataset, handle API outage, reviewer workflow
- Integration spec for title-production write-back (phase 2)

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| Phase 1 MVP (phases 1–5) | 280–380 hrs |
| Phase 6 hardening | 40–60 hrs |
| Title-chain module (later) | 120–180 hrs |
| Write-back + Slack workflows (later) | 60–90 hrs |
| Ongoing maintenance | 10–16 hrs/month |

Indicative MVP timeline at 25–30 hrs/week: 10–14 weeks. Pricing fits milestone phases aligned to the table above.

## Glossary

| Term | Meaning |
|------|---------|
| **BBL** | Borough-Block-Lot — NYC's canonical parcel identifier |
| **PLUTO** | Primary Land Use Tax Lot Output — NYC tax lot dataset |
| **ACRIS** | Automated City Register Information System — recorded documents |
| **SODA / Socrata** | NYC Open Data API platform |
| **COO** | Certificate of Occupancy |
| **HPD / DOB / ECB** | Housing, Buildings, Environmental Control Board violation systems |
| **Provenance** | Metadata tracing each result line to its official source fetch |
| **Verify-link** | Live URL to the official government record for one-click human confirmation |
| **HITL** | Human-in-the-loop — reviewer sign-off before delivery |
