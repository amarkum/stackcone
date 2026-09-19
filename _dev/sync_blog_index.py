#!/usr/bin/env python3
"""Rebuild the static post cards in blog/index.html from blog/posts.json.

The listing is duplicated as real <a> tags so crawlers see every post without
executing JavaScript; posts.json alone is not enough.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START, END = "<!-- STATIC_BLOG_LISTING_START -->", "<!-- STATIC_BLOG_LISTING_END -->"


def card(p: dict) -> str:
    e = lambda s: html.escape(str(s), quote=True)
    tags = p.get("tags", [])
    search = " ".join([p["title"], p["description"], p.get("category", ""), *tags]).lower()
    return (
        f'            <a class="post-card" href="{e(p["href"].lstrip("."). lstrip("/") and p["href"])}"'
        f' data-category="{e(p.get("category",""))}" data-year="{e(p["date"][:4])}"'
        f' data-tags="{e(",".join(tags))}" data-search="{e(search)}">'
        f'<div class="post-meta">By {e(p.get("author","Amar Kumar"))}</div>'
        f'<h2>{e(p["title"])}</h2><p>{e(p["description"])}</p>'
        f'<div class="tags">{"".join(f"<span class=\"tag\">{e(t)}</span>" for t in tags)}</div></a>'
    )


def sync_from_pages(posts: list) -> int:
    """Each post page owns its own title and description; posts.json follows."""
    changed = 0
    for p in posts:
        page = ROOT / "blog" / p["href"].lstrip("./").strip("/") / "index.html"
        if not page.is_file():
            print(f"  ! missing page for {p['id']}")
            continue
        s = page.read_text()
        h1 = html.unescape(re.sub("<[^>]+>", "", re.search(r"<h1>(.*?)</h1>", s, re.S).group(1))).strip()
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
        if p["title"] != h1 or p["description"] != desc:
            p["title"], p["description"] = h1, desc
            changed += 1
    return changed


def main() -> None:
    data = json.loads((ROOT / "blog/posts.json").read_text())
    posts = data["posts"]
    n = sync_from_pages(posts)
    if n:
        (ROOT / "blog/posts.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"blog/posts.json: {n} entries synced from their pages")
    index = ROOT / "blog/index.html"
    s = index.read_text()
    listing = "\n".join(card(p) for p in posts)
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        f"{START}\n{listing}\n                    {END}",
        s,
        flags=re.S,
    )
    index.write_text(new)
    print(f"blog/index.html: {len(posts)} post cards")


if __name__ == "__main__":
    main()
