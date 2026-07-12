# Snowflake to BigQuery Migration — ELT Platform on Google Cloud

**By Amar Kumar**

This brief proposes a phased **Snowflake to BigQuery migration** for an ELT-heavy analytics platform: rebuild streaming and batch ingestion on Google Cloud, port Snowflake-native SQL (Streams, Tasks, dynamic tables, stored procedures) into **dbt** incremental models, replace cron with **Cloud Composer**, run a historical backfill and parallel reconciliation, then cut over BI, reverse-ETL, and AI pipelines with Snowflake decommissioned.

**Proposed outcome:** A production BigQuery platform with rebuilt Kafka and CDC ingestion, dbt-native transformations, Composer orchestration, IAM / row- and column-level security, cost visibility in GCP billing, and a validated freeze / final-delta / cutover with minimal downtime.

---

## Scenario

**Proposed solution** for a data platform team migrating an analytics warehouse from Snowflake to BigQuery over roughly six months, running dual-warehouse until cutover.

- **Current stack:** Streaming + batch into Snowflake; Snowflake SQL + Python/shell transforms; cron orchestration; BI, reverse-ETL, and AI insight consumers
- **Target:** BigQuery foundation; Kafka BigQuery Sink; open-source or managed CDC (Airbyte / Datastream); Cloud Composer (or Scheduler + Workflows); native connectors
- **Owner profile:** Hands-on data engineer alongside a Data Architect / PM and internal DE team; AI-assisted SQL translation in the workflow
- **Environment:** Google Cloud with data-residency boundaries; PII-redaction and secret-scanning before any sample leaves the environment
- **Definition of done:** Reconciled BigQuery platform, rebuilt ingestion, Composer DAGs, legacy Snowflake / managed ELT tool decommissioned

## Problem

- **Dialect lock-in** — Streams, Tasks, dynamic tables, zero-copy clones, and JS stored procedures have no 1:1 BigQuery equivalent
- **Cron fragility** — dependency-blind schedules, weak retries/backfills, and opaque failure alerting
- **Managed ELT tax** — current tool may not map cleanly to BigQuery destinations or residency constraints
- **Security remapping** — Snowflake RBAC / row-access policies must become IAM, authorized views, policy tags, and column masking
- **Cost model shift** — scan-based on-demand vs Editions/slots requires deliberate partitioning, clustering, and reservation planning
- **Cutover risk** — large-table backfills and downstream repointing without parallel reconciliation invite silent drift

## Requirements

### Functional

- Port incremental transforms (Streams+Tasks CDC, procedures, dynamic tables) to BigQuery / dbt
- Bulk-translate Snowflake SQL via BigQuery Migration Service; manual fixes for non-auto-translatable constructs
- Re-architect no-equivalent patterns into BigQuery SQL, scheduled queries, or Cloud Run jobs
- Kafka → BigQuery Sink (Storage Write API) on existing Kubernetes; replace managed ELT with Airbyte OSS / Datastream CDC
- Dataset / region / partition / cluster design; IAM, row-level policies, column controls, authorized views
- Cloud Composer DAGs (or Scheduler + Workflows) with dependencies, retries, backfills, alerting
- Historical unload → GCS → BigQuery loads / Data Transfer Service
- Parallel-run reconciliation, freeze / final-delta / cutover, consumer repointing

### Non-functional

- Data residency honored; PII samples redacted before export
- Idempotent loads and incremental models; safe re-runs
- Cost controls: partition pruning, clustering, slot reservations where justified
- Observability: row-count / aggregate reconciliation, DAG SLAs, billing dashboards
- Minimal downtime cutover with documented rollback to Snowflake until freeze window closes

## Architecture

Published HTML includes Mermaid diagrams (target platform architecture, cutover sequence), pipeline strip, and Chart.js charts (component map, phase effort, reconciliation KPIs, cost model).

```
Sources → Kafka Sink / CDC → BigQuery raw
dbt incremental models → curated / marts
Cloud Composer → schedule + deps + alerts
Unload Snowflake → GCS → historical load
Parallel reconcile → freeze → cutover → decommission
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| Warehouse | BigQuery (Editions) | Target platform; Standard SQL, partitioning, clustering, IAM |
| Transform | dbt Core / Cloud + macros | Versioned incremental models; replaces Tasks/dynamic tables patterns |
| SQL assist | BigQuery Migration Service | Bulk dialect translation; human review for VARIANT/JS/clones |
| Streaming | Kafka Connect BigQuery Sink | Storage Write API; fits existing K8s footprint |
| CDC / batch ELT | Airbyte OSS or Datastream | Replace managed ELT; native BigQuery destinations |
| Orchestration | Cloud Composer (Airflow) | DAGs, retries, backfills vs cron |
| Non-SQL jobs | Cloud Run + Python | Port shell/JS procedure logic |
| History | GCS + BQ load / Data Transfer | One-time backfill with partition design on land |
| IaC (preferred) | Terraform + Helm / ArgoCD | Ingestion connectors and Composer env |
| Security | IAM, policy tags, authorized views | Row/column controls; residency-aware datasets |
| Cost | Billing export + slot planning | Realize savings vs Snowflake credit model |

## Component design

1. **Foundation & security** — datasets, regions, IAM, RLS, policy tags, authorized views
2. **Ingestion rebuild** — Kafka Sink, CDC connectors, native BI destinations
3. **SQL translation factory** — Migration Service + dbt staging/incremental/mart layers
4. **Re-architecture jobs** — Cloud Run for non-SQL / JS procedure logic
5. **Composer orchestration** — DAG packs with sensors, retries, SLAs
6. **Backfill & reconcile** — unload/load, row-count and aggregate checks, delta sync
7. **Cutover runbook** — freeze, final delta, consumer repoint, decommission checklist

## Implementation plan

1. **Weeks 1–4** — BigQuery foundation, security, inventory of Snowflake objects
2. **Weeks 3–8** — Ingestion rebuild (Kafka Sink + CDC); dual-write where needed
3. **Weeks 5–14** — dbt port of transforms; Migration Service + manual fixes
4. **Weeks 10–16** — Cloud Composer DAGs replace cron
5. **Weeks 14–20** — Historical backfill + parallel-run reconciliation
6. **Weeks 20–24** — Freeze / cutover / decommission Snowflake and managed ELT

## Reporting & ops

- DAG success/failure, duration, SLA breach
- Ingestion lag (Kafka offsets, CDC freshness)
- Reconciliation dashboards (row counts, key aggregates, hash samples)
- BigQuery slot utilization and scanned bytes
- Policy-tag / access audit exports
- Cost dashboards from GCP billing export

## Proposed deliverables

- Dataset/region/IAM design doc and Terraform baseline
- Kafka BigQuery Sink + CDC connector deployments
- dbt project with incremental models and macros
- SQL translation inventory (auto vs manual)
- Cloud Composer DAG pack and alert wiring
- Historical backfill runbooks and partition/cluster specs
- Parallel-run reconciliation suite and cutover checklist
- Cost model (on-demand vs reservations) and billing dashboard
- Decommission plan for Snowflake and managed ELT tool

## Effort estimate

Indicative **720–1,000 hrs** over ~6 months at 30+ hrs/week (foundation through cutover). Ongoing ops **20–40 hrs/month** post-cutover for DAG care, cost tuning, and model changes.

## Glossary

| Term | Meaning |
|------|---------|
| ELT | Extract-Load-Transform — load raw then transform in-warehouse |
| CDC | Change Data Capture — incremental source changes |
| dbt | Data build tool — SQL modeling with tests and docs |
| Cloud Composer | Managed Apache Airflow on GCP |
| Storage Write API | High-throughput BigQuery streaming write path |
| Authorized view | BigQuery view granting selective access without table grants |
| Parallel run | Dual Snowflake + BigQuery until metrics match for cutover |
| Freeze / final delta | Stop source writes briefly; apply last changes; cut over |
