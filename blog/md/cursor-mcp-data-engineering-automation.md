# Automate Data Engineering Fixes with Cursor MCP

A typical data-engineering Jira ticket is not “change three lines and merge.” You read the ticket and linked Confluence spec, find the DAG and config files, fix Python until **flake8**, **pylint**, and **SonarQube** pass in GitHub CI, trigger **Airflow**, read task logs when something fails, run a **MongoDB** or Snowflake validation query, and repeat until the pipeline is green. That loop used to mean six browser tabs and a lot of copy-paste.

This guide documents how I automated that loop end to end with **Cursor**, the **CodeBench app** that stores API keys and exposes integrations via **MCP**, plus an **`ai-engineer.md`** playbook that tells the agent which tools to call and when to retry.

## Table of contents

1. [The manual loop](#the-manual-loop)
2. [Architecture](#architecture)
3. [Centralize API keys](#centralize-api-keys)
4. [Expose integrations as MCP tools](#expose-integrations-as-mcp-tools)
5. [GitHub CI gates](#github-ci-gates)
6. [Cursor rules for Jira and Confluence](#cursor-rules-for-jira-and-confluence)
7. [The ai-engineer.md playbook](#the-ai-engineermd-playbook)
8. [Wire MCP in Cursor](#wire-mcp-in-cursor)
9. [End-to-end agent loop](#end-to-end-agent-loop)
10. [What to automate first](#what-to-automate-first)
11. [FAQ](#faq)

## The manual loop

| Step | Tool | Pain |
|------|------|------|
| Understand work | Jira + Confluence | Context scattered across comments and wiki pages |
| Implement | IDE + git | Agent has no live CI or pipeline feedback |
| Quality gates | GitHub Actions (flake8, pylint, Sonar) | Failures discovered only after push |
| Run pipeline | Airflow (MWAA) | Trigger, poll, dig through task logs manually |
| Validate data | MongoDB / warehouse | Ad-hoc queries in a separate client |
| Retry | All of the above | No single “done” condition |

The goal is one agent session that can **read the ticket**, **edit code**, **check CI**, **trigger and debug Airflow**, **run validation queries**, and **loop until every gate passes**.

## Architecture

```
Jira / Confluence ──► Cursor rules (context)
                           │
                           ▼
                    Cursor Agent
                           │
              MCP (streamable-http) ──► CodeBench app
                           │              │
                           │    ┌─────────┼─────────┐
                           │    ▼         ▼         ▼
                           │ GitHub    Airflow   MongoDB
                           │ + Sonar   + logs    + query
                           ▼
                    ai-engineer.md (retry until green)
```

**Components:**

| Piece | Role |
|-------|------|
| **CodeBench app** | Local Flask (or similar) app; stores encrypted API keys; REST + MCP surface |
| **MCP server** | Exposes typed tools: `airflow_trigger_dag`, `sonar_list_issues`, `mongodb_find`, etc. |
| **Cursor rules** | Pull Jira issue + Confluence page into agent context at session start |
| **`ai-engineer.md`** | Operational playbook: tool order, success criteria, retry policy |
| **GitHub CI** | flake8, pylint, SonarQube — objective “build green” signal |

## Centralize API keys

Scattering tokens across `.env`, shell exports, and Cursor config breaks quickly. I added a **settings panel in the CodeBench app** where a data engineer stores credentials once:

| Integration | Keys / config |
|-------------|----------------|
| GitHub | PAT or app token, repo allowlist |
| SonarQube | host URL, project key, token |
| Airflow (MWAA) | environment, DAG prefix, AWS SSO profile |
| MongoDB | connection URI or Atlas API |
| Jira / Confluence | base URL, email, API token |

The MCP server reads from the same secure store the UI uses — no duplicate secrets in the repo. Cursor only needs the MCP endpoint (`http://127.0.0.1:9193/mcp` or similar), not raw tokens in `mcp.json`.

## Expose integrations as MCP tools

Instead of one giant “do everything” tool, split by domain so the agent can plan:

| Domain | Example MCP tools |
|--------|-------------------|
| **Jira** | `jira_get_issue`, `jira_search`, `jira_add_comment` |
| **Confluence** | `confluence_get_page`, `confluence_search` |
| **GitHub** | `github_list_prs`, `github_get_check_runs`, `github_get_file` |
| **SonarQube** | `sonar_list_issues`, `sonar_get_hotspots` |
| **Airflow** | `airflow_trigger_dag`, `airflow_get_run_status`, `airflow_get_task_logs` |
| **MongoDB** | `mongodb_list_databases`, `mongodb_list_collections`, `mongodb_find`, `mongodb_aggregate` |
| **CloudWatch** | `cloudwatch_search_logs` (when MWAA logs land in CW) |

Each tool returns **structured JSON** (status, error message, log excerpt) so the model can branch without parsing HTML consoles.

Minimal MCP tool registration pattern (Python):

```python
@mcp.tool()
def airflow_trigger_dag(dag_id: str, conf: dict | None = None) -> dict:
    """Trigger an Airflow DAG run and return run_id."""
    run_id = mwaa_client.trigger(dag_id, conf=conf or {})
    return {"dag_id": dag_id, "run_id": run_id, "state": "queued"}

@mcp.tool()
def sonar_list_issues(project_key: str, severities: list[str] | None = None) -> dict:
    """List open SonarQube issues for a project."""
    issues = sonar_client.issues_search(project_key, severities=severities or ["BLOCKER", "CRITICAL"])
    return {"count": len(issues), "issues": issues[:50]}
```

## GitHub CI gates

CI is the objective signal for “code is acceptable.” My pipeline runs on every push and PR:

```yaml
name: data-pipeline-ci
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install flake8 pylint
      - run: flake8 cdm_dags/ ads_dags/ --max-line-length=120
      - run: pylint cdm_dags/ ads_dags/ --fail-under=8.0

  sonar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: SonarSource/sonarqube-scan-action@v4
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

The agent calls `github_get_check_runs` (or polls the Checks API via MCP) after push. **Do not mark the task done** until `conclusion == "success"` for lint and Sonar jobs.

## Cursor rules for Jira and Confluence

A project rule (`.cursor/rules/jira-context.mdc`) tells the agent to load ticket context before coding:

```markdown
---
description: Load Jira and Confluence context for data engineering tasks
globs: cdm_dags/**,ads_dags/**,**/*.py
alwaysApply: false
---

# Jira + Confluence context

When the user gives a Jira key (e.g. DATA-1234):

1. Call MCP `jira_get_issue` with the key.
2. If the description links a Confluence page, call `confluence_get_page`.
3. Summarize: acceptance criteria, affected DAGs, tables, and validation steps.
4. Do not start edits until context is loaded.

Follow `ai-engineer.md` for the full fix-and-verify loop.
```

Trigger with: *“Implement DATA-1234”* — the agent fetches spec first instead of guessing from filenames.

## The ai-engineer.md playbook

`ai-engineer.md` lives at the repo root (or `.cursor/`). It is the **retry contract** — what “done” means and which MCP tools to use in order.

```markdown
# AI Engineer — data pipeline fix loop

## Done criteria (ALL required)

1. GitHub CI: flake8, pylint, and SonarQube checks green on the PR branch.
2. Airflow: target DAG run `success` for the environment under test.
3. Data: validation query returns expected row counts or schema per Jira/Confluence.
4. No new Sonar BLOCKER/CRITICAL issues on touched files.

## Tool order

1. `jira_get_issue` + `confluence_get_page` — requirements
2. Edit code locally
3. `github_get_check_runs` after push — if failed, read logs, fix, recommit
4. `sonar_list_issues` — fix or justify each BLOCKER/CRITICAL
5. `airflow_trigger_dag` — note `run_id`
6. Poll `airflow_get_run_status` until `success` or `failed`
7. On failure: `airflow_get_task_logs` → locate file/line → fix → back to step 3
8. `mongodb_find` or warehouse query tool — run validation from ticket
9. `jira_add_comment` with run_id, PR link, validation summary

## Retry policy

- NEVER stop after a single failed DAG run — read logs and fix root cause.
- NEVER stop while CI is red — iterate until green unless blocked on secrets/access.
- Max 5 full loops per session; then summarize blockers for the human.
- Prefer small commits per fix attempt so CI history is readable.
```

This file is referenced from Cursor rules so every agent session shares the same definition of finished.

## Wire MCP in Cursor

Add the CodeBench MCP server to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "codebench": {
      "url": "http://127.0.0.1:9193/mcp",
      "transport": "streamable-http"
    }
  }
}
```

Start the CodeBench app (and MCP listener) before opening Cursor. Confirm tools appear in **Settings → MCP** — you should see domains like Airflow, Sonar, MongoDB, GitHub.

## End-to-end agent loop

Typical session for *“Fix DATA-1234 — vendor file schema drift”*:

1. **Ingest** — Jira issue + Confluence validation table via MCP.
2. **Locate** — agent searches repo for DAG id and parser referenced in ticket.
3. **Fix** — edit Python/SQL; run local flake8 if available.
4. **Push** — user or agent pushes branch; MCP polls GitHub checks.
5. **Sonar** — list new issues on changed files; fix smell/blockers.
6. **Airflow** — trigger DAG with `conf` from ticket; poll to completion.
7. **Logs** — on task failure, pull last 200 lines, map stack trace to file.
8. **Validate** — MongoDB count query: `db.vendor_staging.countDocuments({day: "2026-06-18"})`.
9. **Close loop** — comment on Jira with evidence; ask human to merge if policy requires.

```
Jira ticket → code fix → push → CI green → trigger DAG → logs OK → query OK → Jira comment
     ↑___________________________________________________________________|
                    retry on any failure (ai-engineer.md)
```

## What to automate first

| Priority | Integration | Why |
|----------|-------------|-----|
| 1 | GitHub check runs | Cheapest feedback loop |
| 2 | Airflow trigger + logs | Highest time savings vs MWAA UI |
| 3 | Sonar issues | Catches quality before review |
| 4 | Jira read + comment | Closes the ticket loop |
| 5 | MongoDB read-only queries | Safe validation without write risk |

Add write tools (S3 upload, MongoDB insert) only after read paths are stable.

## FAQ

### Why MCP instead of custom Cursor tools only?

MCP gives a **standard tool schema** reusable across Cursor, Claude Desktop, and other agents. One CodeBench server serves every client.

### Is it safe to give an agent Airflow and MongoDB access?

Use **read-only** MongoDB credentials for validation, **scoped** GitHub tokens, and **dev/stage** Airflow environments for agent-triggered runs. Keep production triggers human-gated.

### What if CI passes but the DAG still fails?

That is expected — `ai-engineer.md` requires both. Logs + validation queries bridge code correctness and runtime behavior.

### Do I need a full CodeBench app?

No. A minimal Flask app with MCP + encrypted key store is enough. The pattern matters more than the UI.

### How is this different from Lazie / generic AI assistants?

Generic chat cannot **poll CI**, **trigger DAGs**, or **query MongoDB** without wired tools. MCP turns the assistant into an operator with APIs.

## Related

- [How to Migrate Cursor Chat to Claude Code](./migrate-cursor-chat-to-claude-code.html)
- [SSE vs WebSocket vs REST API for Live AI](./sse-websocket-rest-api-compared.html)
