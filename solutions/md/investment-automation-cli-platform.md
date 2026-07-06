# Investment Automation CLI Platform for Brokerage Account Management

A proposed **investment automation CLI** platform for teams that need to manage brokerage accounts programmatically — not through ad-hoc scripts or spreadsheet-driven workflows. The architecture would center on a scriptable command-line tool and supporting services that integrate with brokerage, market-data, and banking APIs; execute algorithmic strategies with idempotent order routing; enforce pre-trade risk controls; and emit audit-grade logs suitable for systems that move real money.

**Proposed outcome:** One CLI-driven platform where operators and cron jobs can sync positions, submit orders, run strategies, replay historical sessions, and inspect failures — with every outbound trade keyed by a client order ID, every API call traced, and risk gates that block bad orders before they reach the broker.

## Scenario

This brief describes a **proposed solution** — not a delivered engagement.

- **Operator profile:** Senior software engineer with CLI and API integration experience; high ownership over architecture, production code, and runbooks
- **Accounts:** One or more brokerage accounts (REST/WebSocket APIs; FIX optional for institutional brokers)
- **Strategies:** Rules-based rebalancing, scheduled DCA, signal-driven entries/exits, or portfolio drift correction
- **Runtime:** CLI for manual ops and CI; long-running daemon or scheduled jobs for market-hours automation
- **Compliance posture:** Audit trails, least-privilege API keys, encrypted secrets, human approval gates for large orders

## Problem

Managing investment accounts through broker UIs and one-off scripts does not survive production.

- **Duplicate orders** — cron retries resubmit without idempotency keys
- **Stale position state** — local cache diverges after partial fills or manual UI trades
- **Silent API failures** — rate limits and 5xx responses swallowed
- **No pre-trade risk gate** — fat-finger quantity or concentration breach reaches the market
- **Unscriptable ops** — no stable subcommands, exit codes, or JSON output
- **Weak audit trail** — unstructured logs, no correlation IDs
- **Backtest/live drift** — strategy tested with different fill assumptions than live

## Requirements

### Functional

- CLI shell with subcommands, config files, JSON output, documented exit codes
- Brokerage adapters (REST/WebSocket/FIX) with auth, pagination, rate-limit handling
- Market data ingest with WebSocket reconnect
- Order management with idempotent client order IDs
- Position and portfolio sync with drift detection
- Pluggable strategy engine
- Pre-trade risk controls
- Backtesting and replay against historical data
- Paper trading mode before live capital

### Non-functional

- Idempotent order submission
- Bounded concurrency
- Secrets in vault; no credentials in repos
- TLS in transit; encrypted DB at rest
- Structured logging, Prometheus metrics, alerts
- Unit, integration, and replay-based tests

## Architecture

Four layers: CLI & config, domain services (OMS, portfolio, strategy), adapters (broker, market data, banking), persistence & observability (Postgres, metrics, audit).

## Recommended stack

| Layer | Technology | Why |
|-------|------------|-----|
| CLI | Cobra + Viper (Go) | Production CLI standard; subcommands, config merge |
| Core runtime | Go 1.22+ | Static binary, concurrency, low memory for daemons |
| Order store | Postgres | ACID ledger for orders and audit |
| Secrets | AWS Secrets Manager / Vault | Rotation without redeploy |
| Metrics | Prometheus + Grafana | Latency, reject rates, drift gauges |
| Backtest | Go event loop + Parquet | Same strategy interface as live |
| Scheduler | systemd / Cloud Scheduler → CLI | No custom scheduler in v1 |

**Why Go over Python for execution?** Compile-time checks, single-binary deploy, predictable concurrency. Python stays in research notebooks.

## Component design

### 1 — CLI shell (`invctl`)

- Subcommands: sync, order, strategy run, backtest, status
- Exit codes: 0 success, 1 error, 2 risk block, 3 usage

### 2 — Brokerage adapter

- Read/write: positions, orders, fills, balances
- Retry/backoff on 429/5xx; WebSocket order updates

### 3 — Market data adapter

- Bars, quotes, stale-data detection

### 4 — Strategy engine

- Inputs: positions, signals, config → outputs: order intents
- Dry-run, paper, live modes

### 5 — Risk gate

- Allowlist, max notional, concentration, market hours

### 6 — Order manager (OMS)

- Client order ID idempotency; outbox pattern; lifecycle tracking

### 7 — Portfolio sync

- Reconcile local ledger to broker; drift alerts

### 8 — Backtest & replay

- Historical simulation; recorded API replay for CI

## Implementation plan

1. **Phase 1 (week 1–2)** — CLI foundation, broker read path, Postgres schema
2. **Phase 2 (week 3–4)** — OMS, idempotent routing, risk gate v1, paper trading
3. **Phase 3 (week 5–6)** — Strategy engine, scheduler, reconciliation
4. **Phase 4 (week 7–8)** — Market data WebSocket hardening, rate-limit metrics
5. **Phase 5 (week 9–10)** — Backtest, replay tests, Grafana dashboards
6. **Phase 6 (week 11–12)** — Runbooks, threat model, production go/no-go

## Reporting & ops

- Order latency histograms, risk reject rate, portfolio drift, open order age
- Broker API error rate, cron success, audit integrity checks
- Daily pre-market check; weekly risk/drift review; monthly credential rotation drill

## Proposed deliverables

- `invctl` CLI with JSON output and shell completion
- Brokerage adapter with paper/live modes and integration tests
- Postgres order/audit schema
- OMS with idempotency and outbox retry
- Risk gate with break-glass logging
- Reference drift-rebalance strategy
- Backtest/replay CLI with CI fixtures
- Prometheus/Grafana dashboards and alerts
- Architecture doc, threat model, runbooks, Terraform for infra

## Effort estimate

| Scope | Hours |
|-------|-------|
| Phases 1–6 (full v1) | 400–560 |
| Additional broker adapter | 80–120 each |
| FIX integration | 120–180 |
| Ongoing maintenance | 8–16/month |

## Glossary

- **OMS** — Order management system
- **Client order ID** — Idempotency key for duplicate-safe submits
- **FIX** — Financial Information eXchange protocol
- **Paper trading** — Sandbox execution without real capital
- **Pre-trade risk** — Checks before broker submission
- **Reconciliation** — Local vs broker position comparison
- **Outbox pattern** — Persist before external call for safe retry
- **Replay test** — Deterministic integration test from recorded API responses
