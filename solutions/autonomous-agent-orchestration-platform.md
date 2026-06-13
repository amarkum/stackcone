# Autonomous Agent Orchestration Platform for Multi-Brand Operations

**By Amar Kumar**

A proposed **autonomous agent orchestration** platform for a US-based operator running multiple brands — AI video production, real-estate technology, and regulated medical-compliance clinics. The harness (routing, skills, MCP, hooks, observability) would be the product, with Claude Code, Kimi, GLM, Minimax, and Qwen routed like an orchestra.

**Proposed outcome:** One standing platform where overnight planner / generator / evaluator workflows, Supabase data pipelines, custom MCP servers, and operator dashboards share a model router, security layer, and observability stack.

---

## Scenario

**Proposed solution** for a multi-brand operator needing long-term AI engineering capacity, not project-by-project contractors.

- **Brands:** AI video; real-estate tech (MLS/HUD); medical compliance clinics
- **Owner profile:** Direct ownership access, fast weekly briefs, infra budget, paid model access
- **Operating model:** 30–40 hrs/week standing capacity; harness amortized across brands
- **Scope:** Overnight multi-agent jobs, Supabase ETL, MCP fleet, operator UI, voice/video automation, WordPress/Next.js

## Problem

- Single-shot prompts with no evaluator loop; silent overnight failures
- Ad hoc model selection without router rules
- Siloed per-brand stacks; no shared observability or security
- Contract churn loses harness knowledge
- Regulated flows need injection guards and audit trails
- Non-technical operators lack dashboards

## Requirements

### Functional

- YAML model router (orchestrator / coder / fallback)
- Overnight planner → generator → evaluator LangGraph workflows
- MLS/HUD/public → Supabase with webhooks
- Custom MCP servers per domain
- Operator approval inbox and run replay
- Whisper, FFmpeg, fal.ai media pipelines
- WordPress/Next.js via MCP (draft-first)

### Non-functional

- Langfuse traces; cost per brand
- Lethal trifecta mitigation; sandboxed MCP
- Idempotent ETL; dead-letter queues
- Skills/hooks/router in git
- Clinic flows: audit logs, human-in-the-loop

## Architecture

Published HTML includes Mermaid diagrams (platform architecture, overnight sequence), pipeline strip, and four Chart.js charts.

```
Model Router + Scheduler + Langfuse
    → Claude Code harness + MCP fleet
    → Brand LangGraphs (real-estate · video · clinic)
    → Supabase + object storage + Runpod workers
External: MLS/HUD, fal.ai, WordPress/Next.js
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| Harness | Claude Code + skills/hooks/MCP | Daily driver; subagents and repo context |
| Router | YAML rules service | Explicit orchestrator/coder/evaluator routing |
| Orchestration | LangGraph + Python | Checkpointed overnight graphs |
| Scheduling | Temporal or pg_cron | Reliable retries |
| Data | Supabase + Edge Functions | Multi-tenant RLS, webhooks |
| MCP | TS/Python monorepo | Uniform tools for harness and headless agents |
| Media | Runpod + FFmpeg + fal.ai | GPU bursts, batch transcode |
| Web | Next.js + WordPress REST | Fast surfaces + existing estates |
| Observability | Langfuse | Traces, scores, cost attribution |

## Agent & component design

1. **Planner** — brief + backlog → task DAG with model hints and acceptance criteria
2. **Generator** — domain variants: ETL, video render, clinic docs, web drafts via MCP
3. **Evaluator** — rubric JSON; different model family than generator; dead-letter after N retries
4. **MCP fleet** — mls-bridge, supabase-ops, media-queue, wordpress-mcp, clinic-docs
5. **Security envelope** — sanitize untrusted input; scoped JWT per brand; secret-scan hooks

### Example routing rules

| Role | Default | Fallback | Rule |
|------|---------|----------|------|
| Orchestrator | Claude Sonnet/Opus | GPT-4.1 | Planning under daily cost cap |
| Coder | Claude Code | Kimi K2 / Qwen | Open model when `bulk_etl` or >80k tokens |
| Evaluator | Different family | GLM / Minimax | Reject same model as generator |

## Implementation plan

| Phase | Weeks | Focus |
|-------|-------|--------|
| 1 Harness & router | 1–2 | Monorepo, YAML router, Langfuse, RLS skeleton |
| 2 MCP v1 | 3–4 | supabase-ops, wordpress-mcp, mls-bridge stub |
| 3 Real-estate ETL | 5–6 | Overnight ingest graph, operator dashboard |
| 4 Video pipeline | 7–8 | Whisper, fal.ai, FFmpeg, evaluator rubrics |
| 5 Operator console | 9–10 | Next.js inbox, clinic human-in-the-loop |
| 6 Hardening | 11–12 | Runbooks, load test, tenant onboarding playbook |

## Reporting & ops

- Langfuse: traces, latency, token cost (daily Slack rollup)
- Supabase `job_runs`: overnight pass/fail
- `ingest_watermarks`: ETL freshness alerts
- Router logs: fallback frequency
- Morning digest: completed jobs, approvals pending, cost vs budget, dead-letter links

## Proposed deliverables

- YAML model router with cost caps
- Claude Code skill pack
- MCP monorepo with contract tests
- LangGraph overnight graphs (RE, video, clinic)
- Supabase multi-tenant schema
- Next.js operator console
- Runpod worker images + fal.ai integration
- Security hooks and on-call runbooks

## Effort estimate

| Scope | Hours |
|-------|-------|
| Platform foundation (phases 1–6) | 280–360 hrs |
| Standing weekly engineering | 30–40 hrs/week ongoing |
| Platform maintenance | 12–20 hrs/month |

## Glossary

| Term | Meaning |
|------|---------|
| Agent harness | Skills, hooks, MCP, subagents, router — durable product layer |
| MCP | Model Context Protocol for agent tools |
| Model router | Picks orchestrator/coder/evaluator from explicit rules |
| Lethal trifecta | Untrusted input + privileged tools + external comms without guards |
| Dead-letter queue | Jobs that exhausted retries |
| Langfuse | LLM observability — traces, scores, cost |
