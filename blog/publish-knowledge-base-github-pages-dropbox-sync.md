# Publishing a Knowledge Base to GitHub Pages from Dropbox

**June 2026 · Published by Amar Kumar**

A production pipeline for keeping a RAG chatbot and a public docs site in sync — with Dropbox as the editorial source of truth and GitHub Pages as the published output.

---

Your team needs one place to edit docs, a chatbot that stays current, and a public site users can browse. This article describes a **repeatable production pipeline**: staged content in `raw/`, published markdown in `master/`, a sync job that indexes only what changed, and a MkDocs build pushed to GitHub Pages.

Dropbox is used here as the shared drive — the same pattern works with S3, Google Drive, or any folder your editors already use.

If you are new to RAG itself, start with our companion guide: [How to Build a Production RAG Chatbot](how-to-build-a-production-rag-chatbot.html).

> **Who is this for?** Engineers shipping a doc-backed chatbot who want a repeatable publish path — not a one-off script that re-indexes everything on every run.

---

## Table of contents

1. [Why this layout](#why-this-layout)
2. [Recommended folder layout](#folder-layout)
3. [Two pipelines: ingest and publish](#two-pipelines)
4. [Sync job flow](#sync-job-flow)
5. [Support content → KB](#support-to-kb)
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

The fix is a strict separation: `raw/` for drafts, `master/` as the sole sync source for published markdown, and `site/` as a generated mirror for the static site.

---

## Recommended folder layout

Use a single root folder (example: `kb/` on Dropbox). The names below are conventions — adapt subfolders to your content types.

| Path | Purpose | Synced by job? |
|------|---------|----------------|
| `kb/raw/` | Staging: drafts, imports, AI-generated Q&A awaiting review | No |
| `kb/raw/support/` | Q&A drafts from support tickets or chat transcripts | No |
| `kb/raw/imports/` | PDFs, specs, one-pagers awaiting review | No |
| `kb/raw/notes/` | Internal notes to distill into articles | No |
| `kb/master/` | Published `.md` — **sole source** for sync job | Yes (read) |
| `kb/site/` | Mirror of master, formatted for MkDocs nav | Yes (write) |
| `kb/metadata/sync-state.json` | Incremental sync state (content hashes, chunk IDs) | Yes (read/write) |
| `kb/assets/` | Images and files referenced by markdown | Copied to site on sync |

```
kb/
├── raw/                          ← staging (never indexed directly)
│   ├── support/
│   │   ├── ticket-1042.md
│   │   └── ticket-1087.md
│   ├── imports/
│   │   └── product-spec-v3.md
│   └── notes/
│       └── 2026-05-kickoff.md
├── master/                       ← published .md — SOLE sync source
│   ├── getting-started.md
│   ├── billing-faq.md
│   └── integrations/
│       └── slack.md
├── site/                         ← mirror for docs site (generated)
│   ├── docs/
│   │   └── ...
│   └── mkdocs.yml
├── metadata/
│   └── sync-state.json           ← incremental sync state
└── assets/
    ├── screenshot-dashboard.png
    └── logo-partner.svg
```

**Conceptual file counts by folder:** raw/ ~180, master/ ~45, mkdocs/ ~45, metadata/ ~3, images/ ~120.

**Published articles in master/ by source type:** support Q&A 28, imports 12, notes 8, other 5.

---

## Two pipelines: ingest and publish

Content enters through human or AI-assisted review. Only the publish pipeline touches Pinecone and GitHub.

### Offline — raw content to master (editorial)

```
Raw sources → AI summarize / draft → Human review → Publish to master/
```

Tickets, imports, and notes land in `raw/`. An editor (or AI + editor) promotes approved content into `master/`. Nothing in `raw/` is embedded or published.

### Sync — master to vectors and GitHub Pages

```
master/ .md → Sync job → Chunk + embed → Pinecone upsert → Mirror site/ → MkDocs build → Git push → GitHub Pages
```

The sync job reads **only** `master/**/*.md` (plus tracker state). Changed files are chunked, embedded, upserted to Pinecone, copied into the MkDocs tree, built, and pushed.

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

1. **List files** — walk `master/`, compare against `sync-state.json`  
2. **Load markdown** — download changed `.md` from storage (pooled HTTP)  
3. **Chunk + embed** — split text, call embedding API in batches  
4. **Pinecone upsert** — write vectors; delete stale chunk IDs for removed sections  
5. **Mirror site/** — copy changed pages + assets into MkDocs tree  
6. **Build + push** — `mkdocs build`, commit `site/`, push to `gh-pages` branch  

---

## Support content → KB pipeline

Resolved support conversations are a strong KB source — if you turn them into structured Q&A instead of dumping raw threads into search.

```
Closed ticket → AI summarize → Q&A markdown → raw/support/ → Review → master/
```

Each item becomes a markdown file with a clear question heading, a concise answer, and metadata (source ID, topic, date). Editors fix tone and redact PII before moving the file to `master/`. The next sync run picks it up automatically.

```markdown
# raw/support/ticket-1042.md (draft)
---
source_id: ticket-1042
topic: billing
status: draft
---

## How do I change my subscription plan mid-cycle?

You can upgrade or downgrade from **Settings → Billing**. Changes prorate
immediately for upgrades; downgrades take effect at the next renewal date.

# After review → copied/renamed to master/billing-change-plan.md
```

---

## Incremental sync

Full re-index on every run does not scale. `sync-state.json` stores a content hash per master file. Only files whose hash changed (or are new) go through embed + upsert.

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

The storage API is called dozens of times per sync — list folder, download each changed file, upload site mirror, update tracker. Without connection reuse, every call pays a fresh TCP + TLS handshake (~150–300 ms per request on top of API latency).

Use a shared HTTP session with keep-alive for all storage calls in a run. Teams often see roughly **150–300 ms saved per API call**, which adds up when listing and downloading 20+ files.

| Operation | Without pooling (ms) | With pooling (ms) |
|-----------|---------------------|-------------------|
| List folder | 480 | 280 |
| Download file | 520 | 240 |
| Upload file | 510 | 260 |
| Update metadata | 470 | 250 |

```python
import requests

# One session per sync run — reuse across all storage API calls
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {STORAGE_TOKEN}",
    "Content-Type": "application/json",
})

def download_file(path: str) -> bytes:
    return session.get(f"{STORAGE_API_BASE}/files/download", params={"path": path}).content
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
| 1 | Load `sync-state.json` from storage | Read |
| 2 | List all `master/**/*.md` paths and content hashes | — |
| 3 | Diff: new, changed, deleted vs tracker | — |
| 4 | Download changed files (pooled HTTP) | — |
| 5 | Chunk + embed changed content only | — |
| 6 | Upsert vectors to Pinecone; delete removed chunk IDs | — |
| 7 | Mirror changed pages + assets to `site/` | — |
| 8 | Run `mkdocs build`; push `site/` to GitHub Pages | — |
| 9 | Write updated hashes and chunk IDs to tracker | Write |
| 10 | Emit SSE `complete` event with summary stats | — |

---

## Code snippets

### Sync job pseudocode

```python
def run_sync(emit):
    tracker = load_tracker()                    # download sync-state.json
    session = create_storage_session()        # pooled HTTP

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
        mirror_to_site(path, text)
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
| **sync-state.json** | JSON state file tracking content hashes and vector chunk IDs per file |
| **Incremental sync** | Re-index only files whose hash changed since last run |
| **Connection pooling** | Reusing TCP/TLS connections across HTTP requests to the same host |
| **SSE** | Server-Sent Events — one-way stream of progress updates to the browser |
| **Site mirror** | Generated copy of master content laid out for MkDocs navigation |
| **GitHub Pages** | Static site hosting from a repo branch (typically `gh-pages`) |
| **Support-to-KB** | Pipeline that turns resolved support threads into reviewed Q&A articles |

---

Treat `master/` as a contract: if it is in master, it is searchable *and* publishable. Everything else stays in raw until a human approves it.
