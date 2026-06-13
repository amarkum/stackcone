# How to Set Up MkDocs for GitHub Pages — Complete Guide

**June 2026 · Published by Amar Kumar**

MkDocs turns a folder of Markdown files into a fast, searchable documentation site. This guide walks through installation, configuration, the Material theme, navigation, plugins, local preview, and production deployment to GitHub Pages — with patterns that also work when your docs feed a RAG chatbot.

---

You have Markdown in a repo (or synced from cloud storage). You want a polished docs site with search, mobile layout, and a URL like `docs.yourproduct.com` — without maintaining a custom frontend. **MkDocs** is the standard answer: Python-based, config-driven, and designed exactly for technical documentation.

This article is a **step-by-step setup guide**, not a feature overview. By the end you will have a working site locally and a repeatable path to GitHub Pages.

If you are wiring docs into a vector search pipeline, see the companion guide: [Publish a Knowledge Base to GitHub Pages](publish-knowledge-base-github-pages-dropbox-sync.html).

> **Who is this for?** Developers and technical writers who want a maintainable docs site from Markdown — especially teams already using GitHub for source control.

---

## Table of contents

1. [Why MkDocs](#why-mkdocs)
2. [Prerequisites and installation](#prerequisites)
3. [Project structure](#project-structure)
4. [Create your first site](#first-site)
5. [mkdocs.yml in detail](#mkdocs-yml)
6. [Material for MkDocs theme](#material-theme)
7. [Navigation patterns](#navigation)
8. [Markdown extensions and admonitions](#markdown-extensions)
9. [Images, assets, and static files](#assets)
10. [Local development workflow](#local-dev)
11. [Build and inspect output](#build)
12. [Deploy to GitHub Pages](#github-pages)
13. [Custom domain and HTTPS](#custom-domain)
14. [Useful plugins](#plugins)
15. [Docs + RAG: keeping HTML and vectors aligned](#docs-and-rag)
16. [CI checklist](#ci-checklist)
17. [Common mistakes](#common-mistakes)
18. [Glossary](#glossary)

---

## Why MkDocs

| Option | Pros | Cons |
|--------|------|------|
| **MkDocs + Material** | Fast builds, great search, minimal JS, huge community | Python toolchain required |
| Docusaurus | React ecosystem, versioning | Heavier stack, more config |
| Hugo / Jekyll | Very fast, no Python | Less doc-specific defaults |
| Notion / Confluence export | Easy for writers | Weak SEO, poor version control |

MkDocs wins when your source of truth is **Markdown in Git** and you want **minutes-to-live** deployment. The [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme adds professional navigation, dark mode, and built-in search without a Node build step.

---

## Prerequisites and installation

You need **Python 3.9+** and `pip`. Use a virtual environment so MkDocs does not pollute system Python.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install mkdocs mkdocs-material
```

Verify:

```bash
mkdocs --version
# mkdocs, version 1.6.x
```

**Pin versions in production.** Create `requirements-docs.txt`:

```text
mkdocs>=1.6,<2
mkdocs-material>=9.5,<10
mkdocs-minify-plugin>=0.8,<1
mkdocs-redirects>=1.2,<2
```

Install with `pip install -r requirements-docs.txt`. Pinning avoids surprise breakage when Material ships a major release.

---

## Project structure

MkDocs expects a config file at the repo root (or a path you pass with `-f`). Markdown lives under `docs/` by default.

```
my-docs/
├── docs/                          ← all published .md pages
│   ├── index.md                   ← site homepage (/)
│   ├── getting-started/
│   │   ├── index.md
│   │   └── installation.md
│   ├── guides/
│   │   └── api-authentication.md
│   └── assets/
│       ├── logo.svg
│       └── screenshots/
│           └── dashboard.png
├── mkdocs.yml                     ← site configuration
├── requirements-docs.txt
├── .github/
│   └── workflows/
│       └── docs.yml               ← optional CI deploy
└── site/                          ← build output (gitignored)
```

**Rules of thumb:**

- One `.md` file = one page. Folder `index.md` becomes a section landing page.
- Keep images under `docs/assets/` and reference them with **relative paths**.
- Never commit `site/` unless you deploy by pushing the build folder to `gh-pages` (Method B below).

---

## Create your first site

From an empty folder:

```bash
mkdocs new my-docs
cd my-docs
mkdocs serve
```

Open `http://127.0.0.1:8000`. Edit `docs/index.md` — the browser auto-reloads.

Replace the default `mkdocs.yml` with a minimal production-ready config:

```yaml
site_name: My Product Docs
site_url: https://yourorg.github.io/my-docs/
repo_url: https://github.com/yourorg/my-docs
edit_uri: edit/main/docs/

theme:
  name: material

nav:
  - Home: index.md
  - Getting started:
      - Overview: getting-started/index.md
      - Installation: getting-started/installation.md
```

Add `docs/getting-started/index.md` and `docs/getting-started/installation.md`. Refresh — navigation updates from `nav:` automatically.

---

## mkdocs.yml in detail

The config file controls **everything**: theme, nav, plugins, extensions, metadata, and build behavior.

### Site metadata

```yaml
site_name: My Product Docs
site_url: https://docs.example.com/       # trailing slash matters for canonical URLs
site_description: Official documentation for My Product API and SDK.
site_author: Example Inc.

copyright: Copyright &copy; 2026 Example Inc.

repo_url: https://github.com/yourorg/my-docs
repo_name: yourorg/my-docs
edit_uri: edit/main/docs/                  # "Edit on GitHub" link target
```

`site_url` is used for sitemap generation, Open Graph tags (via Material), and absolute links. Set it to your **final public URL**, not localhost.

### Theme block

```yaml
theme:
  name: material
  language: en
  logo: assets/logo.svg
  favicon: assets/favicon.png
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.action.edit
```

Common `features` explained:

| Feature | Effect |
|---------|--------|
| `navigation.tabs` | Top-level sections as horizontal tabs |
| `navigation.sections` | Sidebar groups with section headers |
| `navigation.expand` | Expand all sections by default |
| `navigation.indexes` | Section index pages from folder `index.md` |
| `content.code.copy` | Copy button on code blocks |
| `content.action.edit` | Edit-on-GitHub button per page |

### Navigation

Explicit `nav` gives you full control. Omit it and MkDocs auto-discovers files alphabetically (usually not what you want).

```yaml
nav:
  - Home: index.md
  - Getting started:
      - getting-started/index.md
      - Install: getting-started/installation.md
      - Quick start: getting-started/quickstart.md
  - Guides:
      - guides/api-authentication.md
      - guides/webhooks.md
  - Reference:
      - reference/config.md
      - reference/errors.md
  - Changelog: changelog.md
```

**External links** in nav:

```yaml
nav:
  - API (Swagger): https://api.example.com/docs
```

**Hide a file from nav** — do not list it. The page is still built if linked elsewhere; add to `not_in_nav` plugin or use `.pages` files (via `mkdocs-awesome-pages-plugin`) for advanced control.

### Markdown extensions

Material enables rich Markdown via `markdown_extensions`:

```yaml
markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.tabbed:
      alternate_style: true
  - attr_list
  - md_in_html
  - tables
  - toc:
      permalink: true
      toc_depth: 3
```

With these enabled you get callouts, tabbed code samples, syntax highlighting, and deep TOCs.

### Plugins

```yaml
plugins:
  - search:
      lang: en
  - minify:
      minify_html: true
  - redirects:
      redirect_maps:
        old-page.md: new-page.md
        deprecated/guide.md: guides/replacement.md
```

`search` builds a client-side lunr index (no server needed on GitHub Pages). `minify` shrinks HTML. `redirects` preserves old URLs after renames.

### Strict mode (recommended for CI)

```yaml
strict: true
```

With `strict: true`, warnings (broken links, missing nav targets) fail the build. Catch errors in CI instead of on your users.

---

## Material for MkDocs theme

Material is not bundled with core MkDocs — install it separately (`pip install mkdocs-material`). It replaces the default theme entirely.

**Why teams choose Material:**

- Instant full-text search with highlighting
- Responsive layout and dark mode
- Admonitions, diagrams (Mermaid via superfences), tabbed content
- Versioning support (multiple doc versions side by side)
- Excellent accessibility defaults

**Minimal Material config** (copy-paste starting point):

```yaml
theme:
  name: material
  features:
    - navigation.tabs
    - search.suggest
    - content.code.copy
  palette:
    - scheme: default
      primary: blue
      accent: blue
    - scheme: slate
      primary: blue
      accent: blue
```

For branding, add custom CSS:

```yaml
extra_css:
  - stylesheets/extra.css
```

Create `docs/stylesheets/extra.css`:

```css
:root {
  --md-primary-fg-color: #2563eb;
}
.md-header__title {
  font-weight: 600;
}
```

---

## Navigation patterns

### Flat docs (small projects)

```yaml
nav:
  - Home: index.md
  - Install: install.md
  - FAQ: faq.md
```

### Multi-section (most products)

Use folders + `index.md` per section. Enable `navigation.sections` and `navigation.indexes`.

### Reference vs guides split

Keep **narrative guides** separate from **API/reference** pages. Users search differently; nav structure should match mental models.

### Auto-generated nav (large repos)

For 50+ pages, maintain `nav` in CI from a script, or use `mkdocs-awesome-pages-plugin` with `.pages` YAML files inside each folder:

```yaml
# docs/guides/.pages
title: Guides
nav:
  - ...
```

---

## Markdown extensions and admonitions

### Admonitions (callouts)

```markdown
!!! note "Beta feature"
    This endpoint is available on Pro plans only.

!!! warning
    Rotating your API key invalidates active sessions immediately.

!!! tip
    Use environment variables instead of hard-coding secrets.
```

Renders as styled boxes — no HTML required.

### Tabbed code blocks

````markdown
=== "Python"
    ```python
    import requests
    r = requests.get("https://api.example.com/v1/users")
    ```

=== "curl"
    ```bash
    curl -H "Authorization: Bearer $TOKEN" \
      https://api.example.com/v1/users
    ```
````

### Mermaid diagrams

Enable in `mkdocs.yml`:

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

Then in Markdown:

````markdown
```mermaid
flowchart LR
  A[Markdown in Git] --> B[mkdocs build]
  B --> C[Static HTML]
  C --> D[GitHub Pages]
```
````

---

## Images, assets, and static files

Place files under `docs/` (e.g. `docs/assets/`). Reference with relative paths from the current page:

```markdown
![Dashboard overview](assets/screenshots/dashboard.png)
```

For pages in nested folders, adjust the path:

```markdown
<!-- from docs/guides/api-authentication.md -->
![Auth flow](../assets/diagrams/oauth-flow.png)
```

**Do not** use absolute `/assets/...` paths unless you configure `use_directory_urls` and understand how MkDocs rewrites URLs.

Optional: set a default image alt text behavior via extensions; always write meaningful alt text for accessibility.

Extra static files (PDFs, downloads) go in `docs/` and link normally:

```markdown
[Download SDK (PDF)](assets/downloads/sdk-reference.pdf)
```

---

## Local development workflow

| Command | Purpose |
|---------|---------|
| `mkdocs serve` | Dev server at `127.0.0.1:8000` with live reload |
| `mkdocs serve -a 0.0.0.0:8000` | Listen on all interfaces (Docker / remote VM) |
| `mkdocs serve --dirty` | Faster reload — only rebuild changed pages |
| `mkdocs build --strict` | Production build; fail on warnings |
| `mkdocs build -d /tmp/out` | Custom output directory |

**Typical loop:**

1. `mkdocs serve` in one terminal
2. Edit Markdown in your editor
3. Preview in browser — reload is automatic
4. Before commit: `mkdocs build --strict` locally or rely on CI

Add to `.gitignore`:

```gitignore
site/
.venv/
```

---

## Build and inspect output

```bash
mkdocs build --strict
# INFO - Documentation built in 2.34 seconds
# site/ now contains static HTML
```

Open `site/index.html` directly or serve with any static server:

```bash
python3 -m http.server --directory site 8080
```

Inspect:

- `site/search/search_index.json` — lunr index (Material search)
- `site/sitemap.xml` — generated if `site_url` is set
- Broken internal links surface as warnings (errors with `--strict`)

**Build time scales roughly linearly** with page count. A 50-page site typically builds in 2–5 seconds; 500 pages may take 30–60 seconds. Minify adds a few seconds.

---

## Deploy to GitHub Pages

Three common methods. Pick one and stick with it.

### Method A — GitHub Actions (recommended)

Build in CI; deploy the `site/` artifact to GitHub Pages. No `gh-pages` branch clutter, reproducible builds.

`.github/workflows/docs.yml`:

```yaml
name: Deploy docs
on:
  push:
    branches: [main]
    paths:
      - "docs/**"
      - "mkdocs.yml"
      - "requirements-docs.txt"
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements-docs.txt
      - run: pip install -r requirements-docs.txt
      - run: mkdocs build --strict
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

In the repo: **Settings → Pages → Build and deployment → GitHub Actions**.

Set `site_url` in `mkdocs.yml` to `https://yourorg.github.io/my-docs/` (project site) or `https://docs.example.com/` (custom domain).

### Method B — `mkdocs gh-deploy`

One command pushes `site/` to the `gh-pages` branch:

```bash
mkdocs gh-deploy --force
```

MkDocs commits build output and force-pushes to `gh-pages`. Simple for solo devs; harder to review diffs and easy to accidentally overwrite.

Configure Pages: **Settings → Pages → Deploy from branch → gh-pages / root**.

### Method C — Manual push of `site/`

Some teams commit `site/` to a dedicated branch or subdirectory. Works but couples source and build artifacts — generally avoid unless you have a legacy reason.

| Method | Best for | Trade-off |
|--------|----------|-----------|
| GitHub Actions | Teams, CI, strict builds | Initial workflow setup |
| `mkdocs gh-deploy` | Solo, quick start | Opaque force-push to gh-pages |
| Manual site/ commit | Legacy repos | Merge conflicts, bloated history |

---

## Custom domain and HTTPS

1. Add a `CNAME` file to your published root (Material can generate this):

```yaml
# mkdocs.yml — not built-in; add via extra step or plugin
# Common pattern: echo "docs.example.com" > docs/CNAME
# Material copies docs/CNAME to site root on build
```

Create `docs/CNAME` containing only:

```text
docs.example.com
```

2. DNS: `CNAME` record `docs` → `yourorg.github.io` (or A records for apex — see GitHub docs).
3. In GitHub repo **Settings → Pages → Custom domain**, enter `docs.example.com`.
4. Enable **Enforce HTTPS** once certificate provisions (can take up to 24 hours).
5. Update `site_url` to `https://docs.example.com/`.

Wrong `site_url` breaks canonical URLs and sitemap — always match the live domain.

---

## Useful plugins

| Plugin | Purpose |
|--------|---------|
| `search` | Full-text search index (built into Material workflow) |
| `minify` | Smaller HTML/CSS/JS |
| `redirects` | 301-style meta redirects for renamed pages |
| `git-revision-date-localized` | "Last updated" from Git history |
| `mkdocstrings` | Auto API docs from Python docstrings |
| `privacy` | Self-host Google fonts (GDPR-friendly) |

Example with revision dates:

```yaml
plugins:
  - search
  - git-revision-date-localized:
      enable_creation_date: true
```

Requires Git history in CI (`fetch-depth: 0` on checkout).

---

## Docs + RAG: keeping HTML and vectors aligned

If the same Markdown powers a **chatbot** and a **public site**, treat one folder as the publish contract (e.g. `master/` or `docs/`). A sync job can:

1. Chunk and embed changed pages for vector search
2. Run `mkdocs build` on the same sources
3. Deploy HTML to GitHub Pages

See [Publish a Knowledge Base to GitHub Pages](publish-knowledge-base-github-pages-dropbox-sync.html) for the full pipeline. The key idea: **one source of Markdown, two outputs** — vectors and static HTML — so users and the bot never disagree on content.

---

## CI checklist

- [ ] Python version pinned in workflow (3.11 or 3.12)
- [ ] `requirements-docs.txt` with pinned MkDocs + Material versions
- [ ] `mkdocs build --strict` in CI
- [ ] `site_url` matches production URL
- [ ] `docs/CNAME` present if using custom domain
- [ ] Path filters on workflow (only run when docs change)
- [ ] `.gitignore` includes `site/` and `.venv/`
- [ ] Internal links checked (strict mode)
- [ ] Search index builds (`site/search/search_index.json` exists)

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Wrong `site_url` (localhost or old domain) | Set to HTTPS production URL with trailing slash |
| Images 404 on GitHub Pages | Use relative paths from `docs/`, not filesystem absolutes |
| Nav points to missing file | Run `mkdocs build --strict` locally |
| `gh-pages` deploy but Pages points to `main` | Align Settings → Pages source with your method |
| Huge repo from committed `site/` | Gitignore `site/`; deploy via Actions artifact |
| Material not installed | `pip install mkdocs-material` — default theme is not Material |
| Broken search on project sites | Ensure `site_url` includes repo path for subpath hosting |

---

## Glossary

| Term | Meaning |
|------|---------|
| **MkDocs** | Static site generator for Markdown documentation |
| **Material** | Popular MkDocs theme with search, tabs, and admonitions |
| **mkdocs.yml** | Site configuration file at repo root |
| **docs/** | Default folder for Markdown source pages |
| **site/** | Build output directory (static HTML) |
| **lunr** | Client-side search index used by Material |
| **gh-pages** | Git branch GitHub Pages can serve |
| **strict mode** | Fail build on warnings (broken links, etc.) |
| **nav** | Explicit sidebar/table-of-contents structure in config |

---

Start with `mkdocs new`, swap in Material, define `nav`, enable `strict`, and deploy via GitHub Actions. You will have a maintainable docs site that scales from ten pages to hundreds — and stays compatible with RAG indexing if you add that later.

Related: [Publish a Knowledge Base to GitHub Pages](publish-knowledge-base-github-pages-dropbox-sync.html) · [How to Build a RAG Chatbot](how-to-build-a-production-rag-chatbot.html)
