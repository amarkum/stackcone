#!/usr/bin/env python3
"""Apply SEO metadata to blog/posts/*.html from blog/posts.json + per-post overrides."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_JSON = ROOT / "blog" / "posts.json"
POSTS_DIR = ROOT / "blog" / "posts"
SITEMAP = ROOT / "sitemap.xml"
BLOG_INDEX = ROOT / "blog" / "index.html"
DATE_MODIFIED = "2026-07-28"

# Per-post SEO: title (page title without " | stackcone"), h1, description, keywords
SEO: dict[str, dict[str, str | list[str]]] = {
    "gpt-5-6-sol-vs-claude-fable-5-vs-kimi-k3": {
        "title": "GPT-5.6 Sol vs Claude Fable 5 vs Kimi K3: Which Should You Use?",
        "h1": "GPT-5.6 Sol vs Claude Fable 5 vs Kimi K3: Which Should You Use?",
        "description": "Compare GPT-5.6 Sol, Claude Fable 5, and Kimi K3 — coding agents, reasoning, pricing, open weights, and which model to use for each job in 2026.",
        "keywords": ["GPT-5.6 Sol", "Claude Fable 5", "Kimi K3", "AI model comparison 2026"],
    },
    "skills-vs-mcp-vs-subagents": {
        "title": "Skills vs MCP vs Subagents: When to Use Each",
        "h1": "Skills vs MCP vs Subagents: When to Use Each",
        "description": "Skills vs MCP vs subagents explained — what each is, when to use them in Cursor and Claude Code, and how to compose all three without over-engineering.",
        "keywords": ["MCP", "Agent Skills", "Subagents", "Cursor", "Claude Code", "AI agents"],
    },
    "sse-websocket-rest-api-compared": {
        "title": "SSE vs WebSocket vs REST API for Live AI (2026)",
        "h1": "SSE vs WebSocket vs REST API for Live AI",
        "description": "Compare SSE vs WebSocket vs REST API for live AI tasks — polling, event streams, FastAPI code, browser agents, and when to use a hybrid stack.",
        "keywords": [
            "sse vs websocket",
            "rest api streaming",
            "server-sent events fastapi",
            "live ai task updates",
            "websocket vs sse",
            "llm streaming api",
            "browser ai agent",
        ],
    },
    "migrate-cursor-chat-to-claude-code": {
        "title": "How to Migrate Cursor Chat to Claude Code (2026)",
        "h1": "How to Migrate Cursor Chat to Claude Code",
        "description": "Migrate Cursor chat history to Claude Code: agent-transcript JSONL, plans, stable session IDs, workspace cwd map, and idempotent import manifest.",
        "keywords": [
            "migrate cursor to claude code",
            "cursor chat migration",
            "claude code import",
            "cursor composer export",
            "agent transcript jsonl",
            "cursor claude migration",
        ],
    },
    "export-cursor-chat-history-vscdb": {
        "title": "Export Cursor Chat History from state.vscdb (2026)",
        "h1": "Export Cursor Chat History from state.vscdb",
        "description": "Export Cursor Composer chat history from state.vscdb SQLite files — schema, key prefixes, and a read-only Python script for JSON and Markdown backup.",
        "keywords": [
            "export cursor chat history",
            "cursor state.vscdb",
            "cursor sqlite export",
            "composer chat backup",
            "cursor chat export script",
            "cursordiskv",
        ],
    },
    "how-sse-streaming-works-chatbots-llm-tokens": {
        "title": "How SSE Streaming Works in Chatbots (2026)",
        "h1": "How SSE Streaming Works in Chatbots",
        "description": "Learn how SSE streaming works in chatbots — real LLM token streams over Server-Sent Events, FastAPI API setup, and wiring OpenAI, Claude, or Gemini.",
        "keywords": [
            "sse streaming chatbot",
            "server-sent events chatbot",
            "llm token streaming",
            "eventsource chat api",
            "fastapi sse streaming",
            "chatbot streaming api",
        ],
    },
    "best-economical-llm-models-rag-openai-gemini-anthropic": {
        "title": "Best Economical LLM Models for RAG (2026)",
        "h1": "Best Economical LLM Models for RAG",
        "description": "Best economical LLM models for RAG in 2026 — compare Gemini, GPT, and Claude API pricing with tables, charts, and cost per turn with chat history.",
        "keywords": [
            "best llm for rag",
            "economical llm models rag",
            "rag llm pricing comparison",
            "cheapest llm for rag",
            "gemini vs gpt rag cost",
            "claude haiku rag",
            "llm api pricing 2026",
        ],
    },
    "how-to-build-a-production-rag-chatbot": {
        "title": "How to Build a Production RAG Chatbot (2026)",
        "h1": "How to Build a Production RAG Chatbot — Complete Guide",
        "description": "Learn how to build a production RAG chatbot: document ingestion, embeddings, vector DB, retrieval pipeline, LLM answers, and step-by-step Python code.",
        "keywords": [
            "how to build a rag chatbot",
            "production rag chatbot",
            "build rag chatbot python",
            "rag chatbot tutorial",
            "vector database chatbot",
            "retrieval augmented generation",
            "fastapi rag api",
        ],
    },
    "cohere-reranking-production-rag-retrieval": {
        "title": "Cohere Reranking for Production RAG (2026)",
        "h1": "Cohere Reranking for Production RAG",
        "description": "Cohere reranking for production RAG retrieval — two-stage vector search, rerank-v3.5, conditional skip, MMR diversity, query rewrite, and cost-aware gates.",
        "keywords": [
            "cohere reranking rag",
            "production rag retrieval",
            "cohere rerank v3.5",
            "two-stage rag retrieval",
            "vector search reranking",
            "pinecone cohere rerank",
            "rag retrieval optimization",
        ],
    },
    "publish-knowledge-base-github-pages-dropbox-sync": {
        "title": "Publish a Knowledge Base to GitHub Pages (2026)",
        "h1": "How to Publish a Knowledge Base to GitHub Pages",
        "description": "How to publish a knowledge base to GitHub Pages — drafts to markdown, vector index, MkDocs site, incremental sync, and editorial review workflow.",
        "keywords": [
            "publish knowledge base github pages",
            "mkdocs github pages",
            "knowledge base pipeline",
            "vector index documentation",
            "docs sync github pages",
            "internal wiki publish",
        ],
    },
    "how-to-evaluate-rag-retrieval": {
        "title": "How to Evaluate RAG Retrieval (2026 Guide)",
        "h1": "How to Evaluate RAG Retrieval",
        "description": "How to evaluate RAG retrieval before tuning prompts — golden eval sets, hit@k, MRR, failure taxonomy, and a weekly loop for measurable search quality.",
        "keywords": [
            "evaluate rag retrieval",
            "rag evaluation metrics",
            "rag hit at k",
            "rag retrieval quality",
            "golden eval set rag",
            "rag mrr",
            "rag debugging",
        ],
    },
    "how-to-set-up-mkdocs-github-pages": {
        "title": "How to Set Up MkDocs for GitHub Pages (2026)",
        "h1": "How to Set Up MkDocs for GitHub Pages",
        "description": "How to set up MkDocs for GitHub Pages — install, mkdocs.yml, Material theme, plugins, GitHub Actions deploy, custom domains, and docs-site best practices.",
        "keywords": [
            "mkdocs github pages",
            "how to set up mkdocs",
            "mkdocs material theme",
            "mkdocs github actions",
            "documentation site github pages",
            "mkdocs deploy",
        ],
    },
    "upwork-hourly-rate-india-new-tax-regime": {
        "title": "Upwork Hourly Rate for India (2026 Calculator)",
        "h1": "How Much Should Your Upwork Hourly Rate Be in India?",
        "description": "Upwork hourly rate for India — monthly in-hand INR after fees, Section 44ADA, new tax regime slabs, ₹12L rebate, and rate tables for common income targets.",
        "keywords": [
            "upwork hourly rate india",
            "upwork rate calculator india",
            "freelancer tax india",
            "section 44ada upwork",
            "new tax regime freelancer",
            "upwork in hand salary india",
        ],
    },
    "stop-upwork-gst-deduction-india-gst-registration": {
        "title": "Stop Upwork GST Deduction in India (2026)",
        "h1": "Stop Upwork GST Deduction (India)",
        "description": "Stop Upwork GST deduction in India — 18% GST on platform fees only, add GSTIN, RCM rules, foreign vs Indian clients, and GST registration from home.",
        "keywords": [
            "stop upwork gst deduction",
            "upwork gst india",
            "upwork gstin",
            "freelancer gst registration india",
            "upwork 18 percent gst",
            "gst registration bangalore",
        ],
    },
    "stop-upwork-usd-best-exchange-rate-india": {
        "title": "Best USD Exchange Rate from Upwork India (2026)",
        "h1": "Best USD Exchange Rate from Upwork (India)",
        "description": "Best USD exchange rate from Upwork for India — free ACH to a US virtual account, then convert with Infinity, Wise, Mulya, or Payoneer.",
        "keywords": [
            "upwork usd exchange rate india",
            "best forex rate upwork india",
            "infinity app upwork",
            "wise upwork ach",
            "payoneer vs infinity",
            "us virtual bank account upwork",
        ],
    },
}


def esc_attr(text: str) -> str:
    return text.replace("&", "&amp;").replace('"', "&quot;")


def esc_json(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)[1:-1]


def replace_meta(html: str, name: str, content: str) -> str:
    pattern = rf'(<meta name="{re.escape(name)}" content=")([^"]*)(")'
    return re.sub(pattern, rf"\1{esc_attr(content)}\3", html, count=1)


def replace_prop(html: str, prop: str, content: str) -> str:
    pattern = rf'(<meta property="{re.escape(prop)}" content=")([^"]*)(")'
    return re.sub(pattern, rf"\1{esc_attr(content)}\3", html, count=1)


def replace_title(html: str, title: str) -> str:
    full = title
    return re.sub(r"<title>[^<]*</title>", f"<title>{esc_attr(full)}</title>", html, count=1)


def replace_h1(html: str, h1: str) -> str:
    return re.sub(
        r"(<article class=\"blog-article\">\s*<h1>)([^<]*)(</h1>)",
        lambda m: f"{m.group(1)}{esc_attr(h1)}{m.group(3)}",
        html,
        count=1,
    )


def replace_json_ld_field(html: str, field: str, value: str, *, is_array: bool = False) -> str:
    if is_array:
        items = ", ".join(esc_json(k) for k in value.split("|"))  # type: ignore[arg-type]
        if isinstance(value, list):
            items = ", ".join(esc_json(k) for k in value)
        replacement = f'"{field}": [{items}]'
        pattern = rf'"{re.escape(field)}":\s*\[[^\]]*\]'
    else:
        replacement = f'"{field}": "{esc_json(value)}"'
        pattern = rf'"{re.escape(field)}":\s*"[^"]*"'
    return re.sub(pattern, replacement, html, count=1)


def update_article_json_ld(html: str, seo: dict, category: str) -> str:
    html = replace_json_ld_field(html, "headline", seo["h1"])  # type: ignore[arg-type]
    html = replace_json_ld_field(html, "description", seo["description"])  # type: ignore[arg-type]
    html = replace_json_ld_field(html, "dateModified", DATE_MODIFIED)
    html = replace_json_ld_field(html, "articleSection", category)
    keywords: list[str] = seo["keywords"]  # type: ignore[assignment]
    kw_json = ", ".join(f'"{esc_json(k)}"' for k in keywords)
    html = re.sub(r'"keywords":\s*\[[^\]]*\]', f'"keywords": [{kw_json}]', html, count=1)
    return html


def update_breadcrumb_name(html: str, slug: str, name: str) -> str:
    url = f"https://stackcone.com/blog/posts/{slug}/"
    pattern = (
        rf'(\{{ "@type": "ListItem", "position": 3, "name": ")([^"]*)("'
        rf', "item": "{re.escape(url)}" \}})'
    )
    return re.sub(pattern, rf"\1{esc_json(name)}\3", html, count=1)


def update_sitemap(slug: str) -> None:
    xml = SITEMAP.read_text(encoding="utf-8")
    loc = f"https://stackcone.com/blog/posts/{slug}/"
    block = re.search(
        rf"<url>\s*<loc>{re.escape(loc)}</loc>\s*<lastmod>[^<]+</lastmod>",
        xml,
    )
    if block:
        xml = xml[: block.start()] + block.group(0).rsplit("<lastmod>", 1)[0] + f"<lastmod>{DATE_MODIFIED}</lastmod>" + xml[block.end() :]
        # simpler replace
        xml = re.sub(
            rf"(<loc>{re.escape(loc)}</loc>\s*)<lastmod>[^<]+</lastmod>",
            rf"\1<lastmod>{DATE_MODIFIED}</lastmod>",
            xml,
            count=1,
        )
        SITEMAP.write_text(xml, encoding="utf-8")


def regenerate_noscript(posts: list[dict]) -> None:
    lines = []
    for post in posts:
        title = esc_attr(post["title"])
        desc = esc_attr(post["description"])
        href = post["href"]
        lines.append(
            f'              <a class="post-card" href="{href}"><h2>{title}</h2><p>{desc}</p></a>'
        )
    block = "\n".join(lines)
    html = BLOG_INDEX.read_text(encoding="utf-8")
    html = re.sub(
        r'(<nav class="blog-posts" aria-label="All blog posts">\n)(.*?)(\n            </nav>)',
        rf"\1{block}\3",
        html,
        count=1,
        flags=re.DOTALL,
    )
    BLOG_INDEX.write_text(html, encoding="utf-8")


def main() -> None:
    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts_by_id = {p["id"]: p for p in data["posts"]}

    for post_id, seo in SEO.items():
        path = POSTS_DIR / post_id / "index.html"
        if not path.exists():
            path = POSTS_DIR / f"{post_id}.html"
        if not path.exists():
            raise SystemExit(f"Missing {path}")

        post = posts_by_id[post_id]
        category = post["category"]
        title = seo["title"]
        h1 = seo["h1"]
        description = seo["description"]
        keywords: list[str] = seo["keywords"]  # type: ignore[assignment]
        kw_str = ", ".join(keywords)

        html = path.read_text(encoding="utf-8")
        html = replace_title(html, title)  # type: ignore[arg-type]
        html = replace_meta(html, "description", description)  # type: ignore[arg-type]
        html = replace_meta(html, "keywords", kw_str)
        html = replace_prop(html, "og:title", title)  # type: ignore[arg-type]
        html = replace_prop(html, "og:description", description)  # type: ignore[arg-type]
        html = replace_meta(html, "twitter:title", title)  # type: ignore[arg-type]
        html = replace_meta(html, "twitter:description", description)  # type: ignore[arg-type]
        html = replace_h1(html, h1)  # type: ignore[arg-type]
        html = update_article_json_ld(html, seo, category)
        html = update_breadcrumb_name(html, post_id, h1)  # type: ignore[arg-type]
        path.write_text(html, encoding="utf-8")

        post["title"] = h1
        post["description"] = description
        update_sitemap(post_id)
        print(f"Updated {post_id}")

    POSTS_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    regenerate_noscript(data["posts"])
    print("Updated posts.json and blog/index.html noscript")


if __name__ == "__main__":
    main()
