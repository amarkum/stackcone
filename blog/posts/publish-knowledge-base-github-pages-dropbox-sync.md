# How to Publish a Knowledge Base to GitHub Pages

**By Amar Kumar**

A production pipeline for keeping a RAG chatbot and a public docs site in sync — with shared cloud storage for editing and GitHub Pages for the public site.

---

Teams often need two outputs from the same markdown: a **public documentation site** and an optional **vector index** for a RAG chatbot. This article describes a repeatable pipeline — drafts in one folder, approved pages in another, a sync job that processes only changes, and a static site build for GitHub Pages.

The pattern works with any shared folder or cloud storage — Dropbox, S3, Google Drive, or a git-backed workflow.

If you are new to RAG itself, start with our companion guide: [How to Build a Production RAG Chatbot](how-to-build-a-production-rag-chatbot.html).

> **Who is this for?** Engineers shipping a doc-backed chatbot who want a repeatable publish path — not a one-off script that re-indexes everything on every run.

---

## Table of contents

1. [Why this layout](#why-this-layout)
2. [Recommended folder layout](#folder-layout)
3. [Two pipelines: ingest and publish](#two-pipelines)
4. [Sync job flow](#sync-job-flow)
5. [Draft to published workflow](#draft-to-published)
6. [Incremental sync](#incremental-sync)
7. [HTTP connection pooling](#connection-pooling)
8. [SSE progress streaming](#sse-progress)
9. [Sync step checklist](#sync-checklist)
10. [Code snippets](#code-snippets)
11. [Glossary](#glossary)

---

## Why this layout

Three problems to solve at once:

- **Editorial control** — not everything in staging should be searchable or public  
- **Dual output** — vectors for the chatbot *and* HTML for humans  
- **Speed** — re-embedding 200 docs when one paragraph changed is wasteful  

The fix is a strict separation: `drafts/` for drafts, `published/` as the sole sync source for published markdown, and `site/` as a generated mirror for the static site.

---

## Recommended folder layout

Pick a root folder in your storage (example: `docs/`). Adapt names to your team — the roles below matter more than the exact paths.

| Path | Purpose | Synced by job? |
|------|---------|----------------|
| `drafts/` | Staging — drafts and imports awaiting review | No |
| `published/` | Published `.md` — **sole source** for sync job | Yes (read) |
| `site/` | Mirror of published content, formatted for MkDocs nav | Yes (write) |
| `metadata/sync-state.json` | Incremental sync state (content hashes, chunk IDs) | Yes (read/write) |
| `assets/` | Images and files referenced by markdown | Copied to site on sync |

```
docs/
├── drafts/                 ← staging (not indexed)
├── published/              ← approved .md — sync source
├── site/                   ← static site output (generated)
├── metadata/
│   └── sync-state.json
└── assets/                 ← images and attachments
```

**Published articles in published/ by source type:** editorial 28, imports 12, refined 8, other 5.

---

## Two pipelines: ingest and publish

Content enters through human or AI-assisted review. Only the publish pipeline touches the vector index and GitHub.

### Offline — drafts to published (editorial)

```
Source material → AI summarize / draft → Human review → Publish to published/
```

Draft content lands in `drafts/`. An editor (or AI + editor) promotes approved content into `published/`. Nothing in `drafts/` is embedded or published.

### Sync — published to vectors and GitHub Pages

```
published/ .md → Sync job → Chunk + embed → Vector DB upsert → Mirror site/ → MkDocs build → Git push → GitHub Pages
```

The sync job reads **only** `published/**/*.md` (plus tracker state). Changed files are chunked, embedded, upserted to your vector database, copied into the MkDocs tree, built, and pushed.

**Editorial funnel:** Drafts → reviewed → published → indexed → live.

---

## Sync job flow

A typical run processes six stages. Embedding dominates wall time; listing and git push are comparatively cheap.

| Stage | Time % |
|-------|--------|
| List files | 5% |
| Load MD | 10% |
| Embed | 45% |
| Vector DB upsert | 25% |
| MkDocs | 10% |
| GitHub | 5% |

1. **List files** — walk `published/`, compare against `sync-state.json`  
2. **Load markdown** — download changed `.md` from storage (pooled HTTP)  
3. **Chunk + embed** — split text, call embedding API in batches  
4. **Vector DB upsert** — write vectors; delete stale chunk IDs for removed sections  
5. **Mirror site/** — copy changed pages + assets into MkDocs tree  
6. **Build + push** — `mkdocs build`, commit `site/`, push to `gh-pages` branch  

---

## Draft to published workflow

Any source — product notes, imports, or AI-generated drafts — should become structured markdown in `drafts/`, then move to `published/` only after review.

```
Source content → AI draft (optional) → drafts/ → Review → published/
```

Each page should have a clear title, concise body, and optional front matter (topic, status, last reviewed). Editors fix tone and redact sensitive details before promotion. The next sync run picks up new published files automatically.

```markdown
# drafts/new-page.md (draft)
---
status: draft
topic: integrations
---

## Page title

Body text goes here. Expand with headings, lists, and code samples as needed.

# After review → moved to published/new-page.md
```

---

## Incremental sync

Full re-index on every run does not scale. `sync-state.json` stores a content hash per published file. Only files whose hash changed (or are new) go through embed + upsert.

```json
{
  "last_sync": "2026-06-12T14:30:00Z",
  "files": {
    "/published/page-a.md": {
      "hash": "sha256:a3f9...",
      "chunk_ids": ["page-a_0", "page-a_1"],
      "indexed_at": "2026-06-10T09:00:00Z"
    },
    "/published/page-b.md": {
      "hash": "sha256:b71c...",
      "chunk_ids": ["page-b_0"],
      "indexed_at": "2026-06-12T14:30:00Z"
    }
  }
}
```

On delete: remove the file entry from the tracker, delete its chunk IDs from the vector index, and drop the mirrored MkDocs page. Unchanged files are skipped entirely.

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
data: {"stage":"embed","file":"page-b.md","done":3,"total":5,"pct":60}

event: progress
data: {"stage":"vector","file":"page-b.md","chunks":4,"pct":72}

event: complete
data: {"files_indexed":2,"files_skipped":38,"duration_s":94}
```

Stages map cleanly to the sync pipeline: `list` → `load` → `embed` → `vector` → `mkdocs` → `github` → `complete`.

---

## Sync step checklist

| Step | Action | Updates tracker? |
|------|--------|------------------|
| 1 | Load `sync-state.json` from storage | Read |
| 2 | List all `published/**/*.md` paths and content hashes | — |
| 3 | Diff: new, changed, deleted vs tracker | — |
| 4 | Download changed files (pooled HTTP) | — |
| 5 | Chunk + embed changed content only | — |
| 6 | Upsert vectors to the vector database; delete removed chunk IDs | — |
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

    published_files = list_published_md(session)
    diff = compute_diff(published_files, tracker)  # new | changed | deleted

    emit("list", total=len(diff.changed) + len(diff.new))

    for path in diff.deleted:
        delete_vector_chunks(tracker.files[path].chunk_ids)
        remove_mkdocs_page(path)
        del tracker.files[path]

    for path in diff.new + diff.changed:
        text = download_md(session, path)
        chunks = chunk_and_embed(text)
        upsert_vectors(path, chunks)
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
| **published/** | Published markdown — only folder the sync job reads for indexing |
| **drafts/** | Staging area; content must be reviewed before promotion to published |
| **sync-state.json** | JSON state file tracking content hashes and vector chunk IDs per file |
| **Incremental sync** | Re-index only files whose hash changed since last run |
| **Connection pooling** | Reusing TCP/TLS connections across HTTP requests to the same host |
| **SSE** | Server-Sent Events — one-way stream of progress updates to the browser |
| **Site mirror** | Generated copy of published content laid out for MkDocs navigation |
| **GitHub Pages** | Static site hosting from a repo branch (typically `gh-pages`) |
| **Editorial workflow** | Review path from draft content in drafts/ to approved pages in published/ |

---

Treat `published/` as a contract: if a file is in `published/`, it is searchable *and* publishable. Everything else stays in `drafts/` until a human approves it.
