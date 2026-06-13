# Publishing a Knowledge Base to GitHub Pages from Dropbox

**June 2026 · Published by Amar Kumar**

A production pipeline for keeping a RAG chatbot and a public docs site in sync — with Dropbox as the editorial source of truth and GitHub Pages as the published output.

---

Your team already lives in Dropbox. Your chatbot needs fresh vectors. Your users need a browsable docs site. This article walks through the pipeline we run in production: staged content in `/raw/`, published markdown in `/master/`, a sync job that indexes only what changed, and a MkDocs build pushed to GitHub Pages.

If you are new to RAG itself, start with our companion guide: [How to Build a Production RAG Chatbot](how-to-build-a-production-rag-chatbot.html).

> **Who is this for?** Engineers shipping a doc-backed chatbot who want a repeatable publish path — not a one-off script that re-indexes everything on every run.

---

## Table of contents

1. [Why this layout](#why-this-layout)
2. [Dropbox folder layout](#dropbox-folder-layout)
3. [Two pipelines: ingest and publish](#two-pipelines)
4. [Sync job flow](#sync-job-flow)
5. [Ticket-to-KB pipeline](#ticket-to-kb)
6. [Incremental sync](#incremental-sync)
7. [HTTP connection pooling](#connection-pooling)
8. [SSE progress streaming](#sse-progress)
9. [Sync step checklist](#sync-checklist)
10. [Code snippets](#code-snippets)
11. [Glossary](#glossary)

---

## Why this layout

Three problems to solve at once:

- **Editorial control** — not everything in Dropbox should be searchable or public  
- **Dual output** — vectors for the chatbot *and* HTML for humans  
- **Speed** — re-embedding 200 docs when one paragraph changed is wasteful  

The fix is a strict separation: `/raw/` for drafts and source material, `/master/` as the sole sync source for published markdown, and `/mkdocs/` as a generated mirror for the static site.

---

## Dropbox folder layout

| Path | Purpose | Synced by job? |
|------|---------|----------------|
| `/knowledgebase/raw/` | Staging: tickets, documents, meeting notes, videos (transcripts) | No |
| `/knowledgebase/raw/tickets/` | AI-generated Q&A from archived support tickets (`CS-n.md`) | No |
| `/knowledgebase/raw/documents/` | Imported PDFs, specs, one-pagers awaiting review | No |
| `/knowledgebase/raw/meeting-notes/` | Internal notes distilled into KB articles | No |
| `/knowledgebase/raw/videos/` | Transcripts and show notes from training videos | No |
| `/knowledgebase/master/` | Published `.md` — **sole source** for sync job | Yes (read) |
| `/knowledgebase/mkdocs/` | Mirror of master, formatted for MkDocs nav | Yes (write) |
| `/knowledgebase/metadata/file-sync-tracker.json` | Incremental sync state (content hashes, last run) | Yes (read/write) |
| `/knowledgebase/images/` | Shared assets referenced by markdown | Copied to mkdocs on sync |

```
knowledgebase/
├── raw/                          ← staging (never indexed directly)
│   ├── tickets/
│   │   ├── CS-1042.md
│   │   └── CS-1087.md
│   ├── documents/
│   │   └── product-spec-v3.md
│   ├── meeting-notes/
│   │   └── 2026-05-kickoff.md
│   └── videos/
│       └── onboarding-transcript.md
├── master/                       ← published .md — SOLE sync source
│   ├── getting-started.md
│   ├── billing-faq.md
│   └── integrations/
│       └── slack.md
├── mkdocs/                       ← mirror for docs site (generated)
│   ├── docs/
│   │   └── ...
│   └── mkdocs.yml
├── metadata/
│   └── file-sync-tracker.json    ← incremental sync state
└── images/
    ├── screenshot-dashboard.png
    └── logo-partner.svg
```

**Conceptual file counts by folder:** raw/ ~180, master/ ~45, mkdocs/ ~45, metadata/ ~3, images/ ~120.

**Published articles in master/ by source type:** tickets 28, documents 12, meeting-notes 8, videos 5.

---

## Two pipelines: ingest and publish

Content enters through human or AI-assisted review. Only the publish pipeline touches Pinecone and GitHub.

### Offline — raw content to master (editorial)

```
Raw sources → AI summarize / draft → Human review → Publish to master/
```

Tickets, meeting notes, and imports land in `/raw/`. An editor (or AI + editor) promotes approved content into `/master/`. Nothing in `/raw/` is embedded or published.

### Sync — master to vectors and GitHub Pages

```
master/ .md → Sync job → Chunk + embed → Pinecone upsert → Mirror mkdocs/ → MkDocs build → Git push → GitHub Pages
```

The sync job reads **only** `/master/*.md` (plus tracker state). Changed files are chunked, embedded, upserted to Pinecone, copied into the MkDocs tree, built, and pushed.

**Editorial funnel:** Raw 100 → Reviewed 60 → Master 45 → Indexed 45 → GitHub Pages 45.

---

## Sync job flow

A typical run processes six stages. Embedding dominates wall time; listing and git push are comparatively cheap.

| Stage | Time % |
|-------|--------|
| List files | 5% |
| Load MD | 10% |
| Embed | 45% |
| Pinecone upsert | 25% |
| MkDocs | 10% |
| GitHub | 5% |

1. **List files** — walk `/master/`, compare against `file-sync-tracker.json`  
2. **Load markdown** — download changed `.md` from Dropbox (pooled HTTP)  
3. **Chunk + embed** — split text, call embedding API in batches  
4. **Pinecone upsert** — write vectors; delete stale chunk IDs for removed sections  
5. **Mirror mkdocs/** — copy changed pages + images into MkDocs tree  
6. **Build + push** — `mkdocs build`, commit `site/`, push to `gh-pages` branch  

---

## Ticket-to-KB pipeline

Support tickets are a gold mine — if you turn them into structured Q&A instead of dumping raw threads into search.

```
Archived ticket → AI summarize → Q&A → raw/tickets/CS-n.md → Review → master/
```

Each ticket becomes a markdown file with a clear question heading, a concise answer, and metadata (ticket ID, product area, date). Editors fix tone and redact PII before moving the file to `/master/`. The next sync run picks it up automatically.

```markdown
# raw/tickets/CS-1042.md (draft)
---
ticket_id: CS-1042
product: billing
status: draft
---

## How do I change my subscription plan mid-cycle?

You can upgrade or downgrade from **Settings → Billing**. Changes prorate
immediately for upgrades; downgrades take effect at the next renewal date.

# After review → copied/renamed to master/billing-change-plan.md
```

---

## Incremental sync

Full re-index on every run does not scale. `file-sync-tracker.json` stores a content hash per master file. Only files whose hash changed (or are new) go through embed + upsert.

```json
{
  "last_sync": "2026-06-12T14:30:00Z",
  "files": {
    "/master/getting-started.md": {
      "hash": "sha256:a3f9...",
      "chunk_ids": ["getting-started_0", "getting-started_1"],
      "indexed_at": "2026-06-10T09:00:00Z"
    },
    "/master/billing-faq.md": {
      "hash": "sha256:b71c...",
      "chunk_ids": ["billing-faq_0"],
      "indexed_at": "2026-06-12T14:30:00Z"
    }
  }
}
```

On delete: remove the file entry from the tracker, delete its chunk IDs from Pinecone, and drop the mirrored MkDocs page. Unchanged files are skipped entirely.

**Relative sync duration:** full re-index 100 units vs incremental (2 files changed) 15 units.

---

## HTTP connection pooling

The Dropbox API is called dozens of times per sync — list folder, download each changed file, upload mkdocs mirror, update tracker. Without connection reuse, every call pays a fresh TCP + TLS handshake (~150–300 ms per request on top of API latency).

Use a shared `requests.Session()` (or equivalent HTTP client with keep-alive) for all Dropbox calls in a run. In production we saw roughly **150–300 ms saved per API call**, which adds up when listing and downloading 20+ files.

| Operation | Without pooling (ms) | With pooling (ms) |
|-----------|---------------------|-------------------|
| List folder | 480 | 280 |
| Download file | 520 | 240 |
| Upload file | 510 | 260 |
| Update metadata | 470 | 250 |

```python
import requests

# One session per sync run — reuse across all Dropbox calls
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {DROPBOX_TOKEN}",
    "Content-Type": "application/json",
})

def dropbox_download(path: str) -> bytes:
    return session.post(
        "https://content.dropboxapi.com/2/files/download",
        headers={"Dropbox-API-Arg": json.dumps({"path": path})},
    ).content
```

---

## SSE progress streaming

Sync jobs can run several minutes. Expose progress via **Server-Sent Events (SSE)** so the admin UI shows live status without polling.

Each stage emits a JSON event: stage name, percent complete, files processed, and optional error detail. The client opens `EventSource('/sync/stream')` and updates a progress bar.

```
// SSE events during sync
event: progress
data: {"stage":"embed","file":"billing-faq.md","done":3,"total":5,"pct":60}

event: progress
data: {"stage":"pinecone","file":"billing-faq.md","chunks":4,"pct":72}

event: complete
data: {"files_indexed":2,"files_skipped":43,"duration_s":94}
```

Stages map cleanly to the sync pipeline: `list` → `load` → `embed` → `pinecone` → `mkdocs` → `github` → `complete`.

---

## Sync step checklist

| Step | Action | Updates tracker? |
|------|--------|------------------|
| 1 | Load `file-sync-tracker.json` from Dropbox | Read |
| 2 | List all `/master/**/*.md` paths and content hashes | — |
| 3 | Diff: new, changed, deleted vs tracker | — |
| 4 | Download changed files (pooled HTTP) | — |
| 5 | Chunk + embed changed content only | — |
| 6 | Upsert vectors to Pinecone; delete removed chunk IDs | — |
| 7 | Mirror changed pages + images to `/mkdocs/` | — |
| 8 | Run `mkdocs build`; push `site/` to GitHub Pages | — |
| 9 | Write updated hashes and chunk IDs to tracker | Write |
| 10 | Emit SSE `complete` event with summary stats | — |

---

## Code snippets

### Sync job pseudocode

```python
def run_sync(emit):
    tracker = load_tracker()                    # Dropbox download
    session = create_dropbox_session()          # pooled HTTP

    master_files = list_master_md(session)
    diff = compute_diff(master_files, tracker)  # new | changed | deleted

    emit("list", total=len(diff.changed) + len(diff.new))

    for path in diff.deleted:
        delete_pinecone_chunks(tracker.files[path].chunk_ids)
        remove_mkdocs_page(path)
        del tracker.files[path]

    for path in diff.new + diff.changed:
        text = download_md(session, path)
        chunks = chunk_and_embed(text)
        upsert_pinecone(path, chunks)
        mirror_to_mkdocs(path, text)
        tracker.files[path] = {"hash": hash(text), "chunk_ids": [c.id for c in chunks]}

    build_and_push_github_pages()
    save_tracker(tracker)
    emit("complete", indexed=len(diff.new) + len(diff.changed))
```

### Incremental diff logic

```python
def compute_diff(remote_files, tracker):
    remote_paths = {f.path for f in remote_files}
    tracked_paths = set(tracker.files.keys())

    deleted = tracked_paths - remote_paths
    new = [f for f in remote_files if f.path not in tracked_paths]
    changed = [
        f for f in remote_files
        if f.path in tracked_paths
        and f.hash != tracker.files[f.path].hash
    ]
    return Diff(new=new, changed=changed, deleted=deleted)
```

---

## Glossary

| Term | Meaning |
|------|---------|
| **master/** | Published markdown — only folder the sync job reads for indexing |
| **raw/** | Staging area; content must be reviewed before promotion to master |
| **file-sync-tracker.json** | JSON state file tracking content hashes and Pinecone chunk IDs per file |
| **Incremental sync** | Re-index only files whose hash changed since last run |
| **Connection pooling** | Reusing TCP/TLS connections across HTTP requests to the same host |
| **SSE** | Server-Sent Events — one-way stream of progress updates to the browser |
| **MkDocs mirror** | Generated copy of master content laid out for MkDocs navigation |
| **GitHub Pages** | Static site hosting from a repo branch (typically `gh-pages`) |
| **Ticket-to-KB** | Pipeline that turns support tickets into reviewed Q&A articles |

---

Treat `/master/` as a contract: if it is in master, it is searchable *and* publishable. Everything else stays in raw until a human says yes.
