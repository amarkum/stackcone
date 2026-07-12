# Enterprise Agentic AI System for Financial Services

**By Amar Kumar**

This brief proposes a **production enterprise agentic AI system** for financial services: role-specific LangGraph agents that reason over governed enterprise data via a credential-isolated access layer, integrate Snowflake Cortex and MCP tool servers, and ship with eval gates on every agent before production release.

**Proposed outcome:** A multi-agent platform where business users interact with specialist agents (research, operations, client servicing) that retrieve answers and take approved actions through API-mediated data access — never raw database credentials — with CI eval regression, full audit traces, and cloud deployment on AWS or Azure.

---

## Scenario

**Proposed solution** for an enterprise financial services client with an existing architecture spec — execution-focused build, not greenfield strategy.

- **Users:** Business analysts, relationship managers, operations staff — non-technical consumers of agent outputs
- **Data estate:** Governed warehouse (Snowflake), CRM (Salesforce), internal APIs, document repositories, semantic/knowledge layer
- **Agent types:** Role-specific agents — e.g. portfolio research, client onboarding assist, compliance Q&A — orchestrated by a supervisor graph
- **Constraints:** Regulated industry — audit logs, PII masking, tool allowlists, human approval for write actions
- **Delivery model:** Fixed-scope agent builds against defined design; ongoing iteration on evals and new role agents
- **Cloud:** AWS Bedrock and/or Azure AI Foundry for model hosting; Snowflake Cortex for governed SQL and search

## Problem

- **Credential sprawl risk** — early agent prototypes embed database connection strings in prompts or env vars agents can leak
- **Ungoverned retrieval** — RAG over raw tables bypasses row-level policies and licensed data terms
- **Demo vs production gap** — LangChain notebooks do not survive SOC review, eval requirements, or multi-agent failure modes
- **Tool chaos** — each agent implements ad-hoc API clients; no standard protocol for discovery, auth, or versioning
- **No eval discipline** — agents ship on vibe checks; regression when models or prompts change
- **Role blur** — single generalist bot hallucinates on domain tasks specialist agents would handle with narrower tools
- **Multi-cloud friction** — model hosting, secrets, and observability split across AWS, Azure, and Snowflake without unified tracing

## Requirements

### Functional

- **Role-specific agents:** Distinct LangGraph graphs per business role with scoped tools and system prompts
- **Supervisor orchestration:** Route user intent to correct agent; support handoff and A2A delegation
- **Governed RAG:** Retrieval via semantic layer / Cortex Search — queries respect entitlements
- **Tool/function calling:** MCP servers exposing approved internal APIs (read-first; write with approval node)
- **Snowflake Cortex:** Analyst for natural-language-to-governed-SQL; Search for document/chunk retrieval
- **Human-in-the-loop:** Approval checkpoint before irreversible actions (CRM updates, report submission)
- **Eval suite per agent:** Golden tasks with expected tool calls, answer patterns, and refusal cases
- **Audit trail:** Log prompts, retrieved sources, tool invocations, model ID, user ID, timestamp

### Non-functional

- **Security:** Zero raw DB credentials in agent runtime; OAuth/service principals via access layer only
- **Latency:** Interactive agent turns p95 &lt; 8 s; long research workflows async with streaming
- **Availability:** 99.9% target on agent API tier; graceful degradation when Cortex or MCP tool unavailable
- **Eval gate:** No agent promotes to prod without passing offline eval threshold (e.g. ≥90% task success)
- **Observability:** OpenTelemetry + Langfuse traces across LangGraph nodes and MCP calls
- **Portability:** Model router abstracts Bedrock vs Azure Foundry vs Cortex LLM functions

## Architecture

Published HTML includes Mermaid diagrams (enterprise agent architecture, governed tool-call sequence), pipeline strip, and five Chart.js charts.

```
User → Agent API → LangGraph supervisor → role agents
Role agents → MCP tools + Cortex Analyst/Search → governed access layer → Snowflake / APIs
Eval CI + Langfuse observability on every deploy
```

## Recommended stack

| Layer | Tech | Why |
|-------|------|-----|
| Orchestration | LangGraph | Production state graphs, checkpoints, HITL, parallel agent branches |
| Tool protocol | MCP (Model Context Protocol) | Standard agent-to-tool discovery; versioned servers per domain |
| Governed data | Snowflake Cortex Analyst + Search | NL→SQL with warehouse RLS; vector search without credential export |
| Access layer | FastAPI gateway + policy engine | Service accounts, entitlements, query allowlists — agents call APIs only |
| LLM hosting | AWS Bedrock + Azure AI Foundry | Enterprise contracts, private endpoints, model choice per task |
| RAG / indexing | LlamaIndex or custom on Cortex Search | Chunk pipelines aligned to semantic layer entities |
| Semantic layer | dbt metrics + knowledge graph (optional Neo4j) | Consistent entity definitions for agents and Cortex |
| Runtime | Python 3.11+, FastAPI, Celery/Temporal | Async long workflows; familiar stack for agent developers |
| Evals | pytest + Langfuse datasets + LLM-as-judge | Per-agent golden tasks in CI |
| Infra | AWS ECS/EKS or Azure Container Apps | Terraform modules; secrets in AWS SM / Azure Key Vault |
| Observability | Langfuse + CloudWatch / Azure Monitor | Cross-agent trace correlation |

**Why MCP over bespoke tool JSON?** Tool schemas, auth, and versioning live in MCP servers owned by domain teams — agents stay thin orchestrators.

**Why governed access layer?** Financial services requires entitlements enforced outside the LLM. Agents receive scoped tokens valid for one session, not warehouse passwords.

**Why LangGraph over CrewAI?** Explicit graph state, checkpoint resume, and conditional edges map to approval flows and supervisor routing in regulated environments.

## Agent & component design

1. **Supervisor router agent** — classify intent, select role agent, manage A2A handoffs; no direct data access
2. **Research analyst agent** — Cortex Analyst + Search tools; cite sources; refuse when entitlements block data
3. **Operations agent** — MCP tools for workflow APIs; write actions behind HITL approval node
4. **Compliance Q&A agent** — narrow corpus (policy docs only); high refusal precision; no external tools
5. **MCP server: snowflake-governed** — wraps Cortex APIs; validates SQL against allowlist; logs every query
6. **MCP server: salesforce-read** — read-only CRM lookups via OAuth; field-level redaction
7. **Eval runner** — per-agent test package; blocks deploy on regression
8. **Model router** — route simple classification to Haiku/Small model; synthesis to Sonnet/Opus or GPT-4o

## Implementation plan

1. **Phase 1 — Foundation (week 1–3):** Access layer API, MCP server scaffold, LangGraph monorepo, CI eval harness, Langfuse project
2. **Phase 2 — First role agent (week 4–6):** Research analyst agent, Cortex Analyst + Search integration, golden eval set (30 tasks)
3. **Phase 3 — Supervisor + A2A (week 7–9):** Multi-agent routing, handoff protocol, streaming UX contract with frontend
4. **Phase 4 — Additional role agents (week 10–13):** Operations + compliance agents, HITL approval nodes, write-tool MCP servers
5. **Phase 5 — Production hardening (week 14–16):** Pen test remediation, audit export, load test, runbooks, model router for Bedrock/Azure
6. **Phase 6 — Eval flywheel (week 17–18):** Production trace sampling into eval datasets, weekly regression, prompt version registry

## Reporting & ops

| Signal | Source | Cadence |
|--------|--------|---------|
| Eval pass rate per agent | CI + weekly prod sample | Every deploy |
| Tool call error rate | MCP server logs | Real-time alert |
| Cortex query denial rate | Access layer policy logs | Daily |
| HITL approval latency | LangGraph checkpoint metrics | Weekly |
| User thumbs-down → eval | Feedback API | Weekly triage |
| p95 turn latency | OpenTelemetry | Dashboard |
| Model cost by agent | Langfuse cost tracking | Monthly |

## Proposed deliverables

- Governed access layer API with entitlement middleware and audit log
- MCP server suite (Snowflake Cortex, CRM read, internal workflow APIs)
- LangGraph supervisor + 3 role-specific agent graphs
- Snowflake Cortex Analyst and Search integration with semantic layer alignment
- Per-agent eval packages (30+ golden tasks each) in CI
- Model router config for Bedrock and Azure AI Foundry
- HITL approval UI contract and checkpoint persistence
- Langfuse dashboards — traces, eval trends, tool failures
- Terraform modules for AWS/Azure deployment
- Security and ops runbooks — credential rotation, agent rollback, Cortex outage mode

## Effort estimate

| Scope | Hours (range) |
|-------|---------------|
| Phases 1–6 (platform + 3 role agents + hardening) | 400–560 hrs |
| Additional role agent (each) | +60–90 hrs |
| Knowledge graph semantic layer | +80–120 hrs |
| Ongoing eval maintenance + model updates | 12–20 hrs/month |

## Glossary

| Term | Meaning |
|------|---------|
| **MCP** | Model Context Protocol — standard for agents to discover and invoke tool servers |
| **A2A** | Agent-to-agent — delegation and handoff between specialist agents |
| **Governed access layer** | API middleware enforcing entitlements; agents never hold warehouse credentials |
| **Cortex Analyst** | Snowflake feature translating natural language to governed SQL |
| **Cortex Search** | Snowflake managed vector/search over approved document corpora |
| **HITL** | Human-in-the-loop — approval checkpoint before high-risk tool execution |
| **LangGraph** | Framework for stateful agent workflows as directed graphs with checkpoints |
| **Semantic layer** | Defined metrics and entities (dbt) ensuring consistent agent and SQL semantics |
| **Eval gate** | CI threshold blocking production deploy when agent regression detected |
