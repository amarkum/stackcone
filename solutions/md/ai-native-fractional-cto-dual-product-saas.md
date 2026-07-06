# Fractional CTO Product Leadership for AI-Native Dual-Product SaaS

**By Amar Kumar**

A proposed **embedded fractional CTO and product engineering** model for an AI-native operating company running two products at equal priority: a revenue-generating customer SaaS platform and an internal agent fleet that runs finance, operations, engineering oversight, and coaching. The approach would treat both surfaces as real products — with discovery, specs, CI gates, observability, and feedback loops — rather than shipping customer features while internal automation stays as throwaway scripts.

> **Proposed outcome:** One embedded technical leader who owns product direction, hands-on delivery, and engineering standards across **app.storscale.ai** and the internal Claude/MCP agent layer — compounding reusable foundations instead of project-by-project contractor churn.

## Table of contents

1. [Scenario](#scenario)
2. [Problem](#problem)
3. [Requirements](#requirements)
4. [Architecture](#architecture)
5. [Recommended stack](#recommended-stack)
6. [Agent and component design](#agent-design)
7. [Implementation plan](#implementation)
8. [Reporting and ops](#reporting)
9. [Proposed deliverables](#deliverables)
10. [Effort estimate](#estimate)
11. [Glossary](#glossary)

## Scenario

This brief describes a **proposed solution** for **StorScale** (StorScale.ai) — the Storage Intelligence Platform for self-storage operators — not a delivered engagement.

| Dimension | Detail |
|-----------|--------|
| **Company** | StorScale — AI-native operating company; small human team, large agent fleet |
| **Customer product** | `app.storscale.ai` — marketing, customer, and pricing intelligence command center for operators |
| **Internal product** | Claude-based agents + MCP tooling on Render/GitHub Actions — finance, ops, engineering, coaching |
| **Engagement model** | Fractional embedded leadership (~2–3 days/week), Central time zone overlap, retainer not project SOW |
| **Reality today** | Live product, paying operators, working codebase, running agent fleet, real business signal |
| **Standard** | Enterprise-grade customer UX; internal agents held to the same reliability bar as external SaaS |

## Problem

StorScale's dual-product model creates leadership gaps that agencies and gig contractors rarely close:

- **Split attention** — Customer roadmap and internal agent reliability compete; without one owner, internal workflows become scripts while SaaS gets polish (or vice versa).
- **Agent sprawl** — Claude/MCP workflows start as experiments; without production gates they lack tests, idempotency, dead-letter handling, and audit trails.
- **Standards drift** — TypeScript strict mode, TDD, and green CI are stated values but erode under speed pressure without someone holding the line.
- **Product vs engineering tension** — Features ship without measurement; specs skip discovery; operators and internal users both feel the gap.
- **Contractor churn** — Scoped projects hand off context; the harness, migration discipline, and agent registry never compound.
- **Human/agent boundary blur** — Without explicit handoff design, humans redo agent work or agents run unchecked on finance and ops tasks.

## Requirements

### Functional

- Unified product backlog spanning customer platform and internal agent workflows, prioritized by business impact.
- Full delivery loop: discovery → spec → build → PR review → deploy → measure (PostHog + Sentry).
- Internal agent registry: named workflows, schedules, inputs/outputs, owner, rollback path.
- Human-in-the-loop gates for finance, pricing recommendations, and customer-facing intelligence outputs.
- Stripe billing integrity; Supabase RLS policies reviewed per feature.

### Non-functional

- TypeScript `strict: true` across Next.js and Node agent services.
- CI must stay green; coverage gates on critical paths (auth, billing, agent side-effects).
- Branch-based Supabase migrations; no schema changes without review.
- Agent jobs idempotent; safe retries; structured logs to Sentry.
- Central-time overlap for standups and architecture decisions; async Slack for everything else.

## Architecture

### Dual-product topology

```
Operators (app.storscale.ai)
    → Next.js on Vercel → Supabase/Postgres (RLS) → Stripe
    → PostHog product analytics

Internal team (Slack / Notion)
    → Scheduled agent fleet (Render + GitHub Actions)
    → Claude agents + MCP tools → Supabase / APIs / Notion
    → Sentry + run logs + morning digests

Fractional CTO layer (embedded)
    → Product roadmap (both surfaces)
    → PR review + architecture + hiring input
    → Shared CI, observability, agent registry standards
```

### End-to-end delivery loop

Discovery → Spec (Notion) → TDD implementation → PR + review → Vercel/Render deploy → PostHog/Sentry measure → retro

## Recommended stack

| Layer | Choice | Why (vs alternatives) |
|-------|--------|------------------------|
| Customer frontend | Next.js + TypeScript strict on Vercel | SSR/ISR for dashboard performance; team already on Vercel; vs Remix — ecosystem fit |
| Data | Supabase + Postgres + RLS | Branch migrations, auth built-in; vs raw RDS — faster iteration with guardrails |
| Payments | Stripe | Operator subscriptions; vs Paddle — US self-storage market fit |
| Agent runtime | Node.js on Render + GitHub Actions cron | Long-running and scheduled jobs; vs Lambda — simpler agent sessions |
| AI layer | Claude agents + MCP | Production workflows with tool access; vs raw API scripts — composable, auditable |
| Observability | Sentry + PostHog | Errors + product funnels; vs Datadog-only — cost-aware at fractional scale |
| PM / comms | Notion + Slack | Roadmap and standups; low ceremony |

## Agent and component design

### Customer platform components

| Component | Responsibility | QA gate |
|-----------|----------------|---------|
| Intelligence dashboard | Marketing, customer, pricing views for operators | Visual regression + E2E on critical paths |
| Data ingestion | Facility/operator data into Supabase | Migration review + RLS test suite |
| Billing portal | Stripe subscription lifecycle | Webhook idempotency tests |
| Feature flags | Gradual rollout of intelligence modules | PostHog funnel before GA |

### Internal agent workflows

| Agent / workflow | Responsibility | Inputs | Outputs | QA gate |
|------------------|----------------|--------|---------|---------|
| Finance agent | Reconciliation, reporting drafts | Stripe, bank exports, Notion | Summary + flagged anomalies | Human approve before send |
| Engineering oversight | CI digest, dependency drift, incident summary | GitHub, Sentry | Slack digest | No auto-merge |
| Operations agent | Runbook execution, vendor checks | Schedules, API keys | Ticket + log | Idempotent + dead-letter queue |
| Coaching agent | Team feedback synthesis | Meeting notes, goals | Private draft | PII scrub + human review |

### Human vs agent boundary

| Task type | Owner | Handoff |
|-----------|-------|---------|
| Product prioritization | Human (+ CTO input) | Notion roadmap |
| Code merge to main | Human PR approval | CI green required |
| Routine finance reports | Agent draft → human send | Approval button in Slack |
| Customer pricing suggestions | Agent analysis → operator confirms | In-app acknowledge |
| Incident response | Human lead; agent gathers context | Sentry → agent summary → human action |

## Implementation plan

### Phase 1 — Embed and audit (weeks 1–2)

Join Slack standups; map customer app, agent fleet, CI, Supabase branches, and Notion roadmap. Produce architecture memo and risk register.

**Risk:** Audit paralysis. **Rollback:** Time-box to 10 days; ship memo with top 5 fixes.

### Phase 2 — Engineering standards (weeks 2–4)

Enforce TypeScript strict, PR template, coverage gates on auth/billing/agents, Supabase migration checklist.

**Risk:** Team friction on new gates. **Rollback:** Gate new code only; grandfather legacy with ticket backlog.

### Phase 3 — Customer product loop (weeks 4–8)

Run one full discovery-to-measure cycle on highest-impact operator feature; improve dashboard craft toward "intelligence platform" bar.

**Risk:** Scope creep. **Rollback:** Single vertical slice; defer nice-to-haves to next cycle.

### Phase 4 — Internal agent hardening (weeks 6–10)

Agent registry, idempotent schedules, Sentry instrumentation, human approval paths for finance/ops outputs.

**Risk:** Agents break silently on API changes. **Rollback:** Feature-flag each workflow; keep manual fallback runbook.

### Phase 5 — Unified observability (weeks 8–12)

PostHog dashboards for operator activation; Sentry release tracking; weekly agent reliability report in Slack.

**Risk:** Metric overload. **Rollback:** Start with 5 KPIs per product surface.

### Phase 6 — Scale runway (weeks 12+)

Hiring rubric, interview loop, documentation for second engineer; CTO role expands or transitions based on traction.

**Risk:** Premature hire. **Rollback:** Contract-to-hire after 90-day engineering standard proof.

## Reporting and ops

| Surface | Dashboard / channel | Cadence |
|---------|---------------------|---------|
| Customer SaaS | PostHog — activation, feature adoption, churn signals | Weekly product review |
| Reliability | Sentry — error budget, release health | Daily glance; weekly deep dive |
| Agent fleet | Agent registry + run success rate | Daily digest to Slack |
| Engineering | CI green rate, PR cycle time, coverage trend | Weekly |
| Roadmap | Notion — dual backlog with RICE or impact tags | Bi-weekly prioritization |

Alert cadence: P1 Sentry → Slack immediately; agent failure → retry then dead-letter + morning summary; Stripe webhook failures → page within 15 minutes.

## Proposed deliverables

1. Architecture and risk memo (customer + internal products)
2. Engineering standards doc (TDD, CI, TypeScript, migrations)
3. Agent registry (YAML or Notion DB) with owners and rollback paths
4. One shipped customer feature with PostHog measurement plan
5. Hardened internal agent workflow with tests and human approval gate
6. Weekly product/engineering review template
7. Hiring rubric and onboarding checklist for next engineer

## Effort estimate

| Phase | Indicative hours | Notes |
|-------|------------------|-------|
| Embed + audit | 40–60 | Weeks 1–2 at 2–3 days/week |
| Standards + CI | 30–50 | Overlaps with audit fixes |
| Customer feature cycle | 60–100 | Depends on feature scope |
| Agent hardening | 50–80 | Per workflow; parallelizable |
| Observability | 20–40 | Dashboards + alerts |
| Ongoing fractional | 16–24 hrs/week | Product + code + review |

Ongoing maintenance: ~20% of fractional time on agent fleet health, dependency updates, and CI hygiene.

## Glossary

| Term | Meaning |
|------|---------|
| Dual-product model | Customer SaaS and internal agent layer treated as equal product surfaces |
| Agent registry | Catalog of scheduled workflows with inputs, outputs, owners, and rollback |
| RLS | Row-level security in Supabase/Postgres |
| MCP | Model Context Protocol — tool interfaces for Claude agents |
| Human-in-the-loop | Agent produces draft; human approves before external effect |
| Fractional embedded | Team member with real ownership, not agency SOW execution |
