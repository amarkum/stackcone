# Marketing Attribution Pipeline — S3, BigQuery, and Looker Studio

A proposed **marketing attribution pipeline** extension for an agency or analytics team that already moves lead and case-intake data from Lead Docket through AWS S3 into BigQuery, surfaced in Looker Studio via a scheduled Cloud Function refresh. The build would add daily Google Ads and Meta campaign ingestion, a matching layer tying each lead to its driving campaign (gclid, UTMs, source mapping), and pre-aggregated BigQuery views at campaign and ad-group grain — all wired into the existing Looker dashboard with consistent styling.

**Proposed outcome:** One law-firm client dashboard showing which campaigns drive leads, cost per lead, lead quality, and signed/referred case breakdown by campaign — with unmatched leads handled explicitly, not dropped.

## Scenario

This brief describes a **proposed solution** — not a delivered engagement.

- **Organization:** Analytics or marketing ops team serving law-firm clients; attribution strategy and KPI definitions already scoped internally
- **Existing pipeline:** Lead Docket → AWS S3 → BigQuery → Looker Studio (Cloud Function on Cloud Scheduler)
- **Extension scope:** Google Ads + Meta spend/clicks/impressions; join to intake data for one client initially
- **Owner profile:** Contract data engineer owning the build against a provided spec — SQL, ETL, and dashboard work
- **Attribution inputs:** gclid for Google; UTMs + client-provided source-to-campaign mapping for both platforms
- **Downstream consumers:** Client stakeholders reviewing campaign ROI and lead quality in Looker Studio

## Problem

The intake pipeline works — leads land in BigQuery and appear in Looker. But marketing spend data lives in separate silos (Google Ads, Meta Ads Manager), so the team cannot answer basic attribution questions without manual exports and spreadsheet joins.

- **No spend-to-lead join** — campaign cost and lead volume require manual reconciliation across platforms
- **Fragmented click identifiers** — gclid on Google leads, fbclid on Meta, UTMs inconsistently captured in Lead Docket
- **Lead quality invisible at campaign grain** — signed cases and referred outcomes not tied back to ad spend
- **Existing pipeline undocumented** — extending S3 → BigQuery without an audit risks breaking the intake refresh
- **Looker performance** — blending raw tables at query time is slow; pre-aggregated views are needed
- **Unmatched leads** — not every lead carries a clean gclid or UTM; ignoring them skews attribution; including them requires an explicit bucket

## Requirements

### Functional

- **Pipeline audit** — document existing S3 → BigQuery → Looker flow, schemas, schedules, and Cloud Function logic
- **Google Ads ingestion** — daily load of spend, clicks, impressions, campaign/ad-group metadata, click IDs where available (Google Ads → BigQuery transfer or API)
- **Meta ingestion** — daily load of equivalent Meta campaign metrics via Marketing API or connector
- **Attribution matching layer** — join leads to campaigns via gclid (Google), UTMs + source mapping (both platforms); graceful handling of unmatched records
- **BigQuery modeling** — clean views at campaign and ad-group grain; pre-aggregated for Looker speed
- **Lead quality metrics** — signed cases, referred cases, and quality flags broken down by campaign per scoped KPI definitions
- **Looker Studio extension** — new pages/views on existing dashboard matching styling and naming conventions
- **Documentation & handoff** — pipeline diagram, schema docs, runbook for daily ops

### Non-functional

- **Consistency** — ad data lands on the same schedule and naming pattern as existing intake loads
- **Idempotency** — daily jobs safe to re-run without duplicate rows
- **Observability** — row counts, match rates, and ingestion failures logged and alertable
- **Cost control** — partitioned BigQuery tables, clustered on date and campaign ID
- **Extensibility** — client-agnostic attribution logic where possible; client-specific mapping in config tables

## Architecture

Three layers: **ingestion** (S3 intake unchanged + new ad platform loads), **attribution warehouse** (matching + marts in BigQuery), and **reporting** (Looker Studio on pre-aggregated views).

### Recommended stack

| Layer | Technology | Why |
|-------|------------|-----|
| Intake landing | AWS S3 (existing) | Lead Docket export path already proven |
| Intake load | Cloud Function + Cloud Scheduler (existing) | Matches current refresh pattern |
| Google Ads | BigQuery Data Transfer Service or Google Ads API → GCS → BQ | Native transfer is lowest ops for standard metrics; API for click-level detail |
| Meta Ads | Marketing API → Cloud Function → BigQuery | No native BQ transfer; scheduled API pull with pagination |
| Warehouse | BigQuery | Already in use; views and scheduled queries for marts |
| Attribution logic | BigQuery SQL views + mapping tables | Transparent, version-controlled, auditable joins |
| Reporting | Looker Studio (existing dashboard) | Client already uses it; extend with blended sources on marts |
| Orchestration | Cloud Scheduler | Daily cadence aligned with intake refresh |
| Config | BigQuery mapping tables | Source-to-campaign rules client provides; no hardcoded joins |

**Why BigQuery Data Transfer for Google Ads?** Zero-maintenance daily loads of campaign metrics. Supplement with API pull only if click-level gclid-to-campaign mapping requires ad-group report granularity the transfer lacks.

**Why mapping tables over hardcoded CASE?** Client source-to-campaign rules will change; a `dim_source_campaign_map` table lets ops update mappings without redeploying SQL.

## Component design

### 1 — Pipeline auditor & documenter

- **Input:** existing S3 buckets, Cloud Function source, BigQuery datasets, Looker data sources
- **Output:** architecture diagram, schema catalog, schedule matrix, dependency map
- **QA gate:** sign-off before any schema changes to intake tables

### 2 — Google Ads ingestion job

- **Input:** Google Ads account credentials, date range (daily incremental)
- **Output:** `raw_google_ads` partitioned table — campaign_id, ad_group_id, date, spend, clicks, impressions
- **Schedule:** daily after midnight account timezone; idempotent MERGE on date + campaign + ad_group

### 3 — Meta ingestion job

- **Input:** Meta Marketing API token, ad account ID
- **Output:** `raw_meta_ads` partitioned table — parallel schema to Google for union downstream
- **Schedule:** same daily window; handle API rate limits with exponential backoff

### 4 — Attribution matching engine

- **Input:** `fact_leads` (from intake), `raw_google_ads`, `raw_meta_ads`, `dim_source_campaign_map`
- **Matching priority:** (1) gclid exact match → Google campaign, (2) UTM campaign + source match via mapping table, (3) source-only fallback, (4) `unmatched` bucket
- **Output:** `fact_lead_attribution` with `match_method`, `match_confidence`, `campaign_id`, `platform`
- **Edge cases:** duplicate gclids, expired click IDs, leads with partial UTMs — each gets explicit match_method, never silent drop

### 5 — Campaign mart views

- **Grain:** campaign-day and ad-group-day pre-aggregates
- **Metrics:** spend, clicks, impressions, leads, cost per lead, signed cases, referred cases, match rate
- **Output:** `mart_campaign_daily`, `mart_ad_group_daily` — Looker connects here, not raw tables

### 6 — Looker Studio layer

- **Input:** mart views + existing intake dashboard styling reference
- **Output:** campaign performance page, lead quality breakdown, unmatched leads report
- **QA gate:** client stakeholder review against scoped KPI definitions before publish

## Implementation plan

### Phase 1 — Audit & baseline (week 1)

Document existing S3 → BigQuery → Looker pipeline. Export current schemas, Cloud Function code review, Looker data source inventory. Establish dev/staging datasets.

**Risk:** Undocumented Cloud Function edge cases — pair with whoever built the intake load. **Rollback:** read-only audit; no production changes.

### Phase 2 — Ad platform ingestion (week 2–3)

Google Ads transfer or API job into `raw_google_ads`. Meta Marketing API Cloud Function into `raw_meta_ads`. Daily scheduler, row-count monitoring, 7-day backfill validation.

**Risk:** Meta API pagination on large accounts — batch by campaign. **Rollback:** disable scheduler; raw tables isolated from intake.

### Phase 3 — Attribution matching layer (week 4–5)

Load client source-to-campaign mapping into `dim_source_campaign_map`. Build `fact_lead_attribution` with match priority logic. Report match-rate KPI (% gclid, % UTM, % unmatched).

**Risk:** Low gclid capture rate in Lead Docket — quantify before modeling; may need UTM fallback as primary. **Rollback:** attribution views only; intake pipeline untouched.

### Phase 4 — BigQuery marts (week 6)

Pre-aggregated `mart_campaign_daily` and `mart_ad_group_daily`. Partition by date, cluster by campaign_id. Scheduled query refresh after daily ingestion completes.

**Risk:** Cartesian join inflating spend — enforce grain tests in CI. **Rollback:** drop mart views; raw + attribution tables remain.

### Phase 5 — Looker Studio & handoff (week 7–8)

Extend existing dashboard: campaign ROI, cost per lead, signed/referred breakdown, unmatched leads table. Documentation, runbook, recorded walkthrough.

**Risk:** Looker blend limits on wide marts — connect to pre-aggregated views only. **Rollback:** hide new pages until data validated.

## Reporting & ops

| Signal | Source | Cadence |
|--------|--------|---------|
| Ingestion row counts (Google, Meta, intake) | Cloud Function logs | Daily; alert on zero rows |
| Attribution match rate | `fact_lead_attribution` | Daily dashboard tile |
| Unmatched lead volume | match_method = 'unmatched' | Weekly review |
| Cost per lead by campaign | `mart_campaign_daily` | Real-time in Looker |
| Signed case rate by campaign | mart + intake join | Weekly client report |
| Pipeline job failures | Cloud Scheduler + error reporting | Immediate alert |

## Proposed deliverables

- Pipeline audit document with architecture diagram and schema catalog
- Daily Google Ads ingestion into BigQuery (transfer or API)
- Daily Meta Ads ingestion Cloud Function
- `dim_source_campaign_map` config table and loader
- `fact_lead_attribution` matching layer with explicit unmatched bucket
- `mart_campaign_daily` and `mart_ad_group_daily` pre-aggregated views
- Looker Studio pages on existing dashboard (campaign ROI, lead quality, unmatched report)
- Runbook: daily ops, re-run failed jobs, update source mappings, add new client
- Handoff session with recorded walkthrough

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| Phases 1–5 (full build) | 120–180 hrs |
| Ongoing maintenance (mapping updates, API changes) | 4–8 hrs/month |
| Additional law-firm clients (reuse marts) | 20–40 hrs each |

At 15–25 hrs/week, delivery in roughly 6–10 weeks. Milestone pricing aligned to phases 1–5.

## Glossary

| Term | Meaning |
|------|---------|
| **gclid** | Google Click Identifier — ties a lead session to a specific Google Ads click |
| **UTM parameters** | Urchin Tracking Module tags (utm_source, utm_campaign, etc.) appended to landing URLs |
| **Lead Docket** | Legal intake platform capturing lead and case data |
| **Attribution matching** | Logic linking a lead record to the ad campaign that drove it |
| **Mart** | Pre-aggregated BigQuery view optimized for reporting grain |
| **Looker Studio** | Google's free BI tool (formerly Data Studio) for dashboard building |
| **MERGE** | BigQuery upsert — insert new rows, update existing on key match |
| **Match rate** | Percentage of leads successfully tied to a campaign vs unmatched bucket |
