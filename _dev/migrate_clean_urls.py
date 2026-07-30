#!/usr/bin/env python3
"""Migrate blog/solution .html files to slug/index.html with redirect stubs."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BLOG_POSTS = ROOT / "blog" / "posts"
SOLUTIONS = ROOT / "solutions"
SITEMAP = ROOT / "sitemap.xml"
LLMS = ROOT / "llms.txt"
POSTS_JSON = ROOT / "blog" / "posts.json"
SOLUTIONS_JSON = ROOT / "solutions" / "solutions.json"


def blog_redirect_stub(slug: str) -> str:
    dest = f"/blog/posts/{slug}/"
    canonical = f"https://stackcone.com{dest}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Redirecting…</title>
  <link rel="canonical" href="{canonical}">
  <meta http-equiv="refresh" content="0;url={dest}">
  <script>location.replace("{dest}");</script>
</head>
<body><p><a href="{dest}">Continue to article</a></p></body>
</html>
"""


def solution_redirect_stub(slug: str) -> str:
    dest = f"/solutions/{slug}/"
    canonical = f"https://stackcone.com{dest}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Redirecting…</title>
  <link rel="canonical" href="{canonical}">
  <meta http-equiv="refresh" content="0;url={dest}">
  <script>location.replace("{dest}");</script>
</head>
<body><p><a href="{dest}">Continue to solution brief</a></p></body>
</html>
"""


def fix_blog_paths(html: str, slug: str) -> str:
    html = html.replace(f"/blog/posts/{slug}.html", f"/blog/posts/{slug}/")
    html = html.replace(f"https://stackcone.com/blog/posts/{slug}.html", f"https://stackcone.com/blog/posts/{slug}/")
    replacements = [
        ('href="../../styles.css"', 'href="../../../styles.css"'),
        ('href="../../blog/blog.css"', 'href="../../../blog/blog.css"'),
        ('src="../../logo/', 'src="../../../logo/'),
        ('href="/assets/analytics.js"', 'href="/assets/analytics.js"'),
        ('src="../images/', 'src="../../images/'),
        ('href="../images/', 'href="../../images/'),
        ('src="../site-nav.js"', 'src="../../../site-nav.js"'),
        ('src="../script.js"', 'src="../../../script.js"'),
        ('src="../../site-nav.js"', 'src="../../../site-nav.js"'),
        ('src="../../script.js"', 'src="../../../script.js"'),
    ]
    for old, new in replacements:
        html = html.replace(old, new)
    return html


def fix_solution_paths(html: str, slug: str) -> str:
    html = html.replace(f"/solutions/{slug}.html", f"/solutions/{slug}/")
    html = html.replace(f"https://stackcone.com/solutions/{slug}.html", f"https://stackcone.com/solutions/{slug}/")
    replacements = [
        ('href="../styles.css"', 'href="../../styles.css"'),
        ('href="../blog/blog.css"', 'href="../../blog/blog.css"'),
        ('href="solutions.css"', 'href="../solutions.css"'),
        ('src="../favicon/', 'src="../../favicon/'),
        ('src="../logo/', 'src="../../logo/'),
        ('src="icons/', 'src="../icons/'),
        ('src="diagrams.js', 'src="../diagrams.js'),
        ('src="../site-nav.js"', 'src="../../site-nav.js"'),
        ('src="../script.js"', 'src="../../script.js"'),
    ]
    for old, new in replacements:
        html = html.replace(old, new)
    return html


def migrate_html_file(src: Path, dest_dir: Path, slug: str, *, kind: str) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "index.html"
    html = src.read_text(encoding="utf-8")
    if kind == "blog":
        html = fix_blog_paths(html, slug)
        stub = blog_redirect_stub(slug)
    else:
        html = fix_solution_paths(html, slug)
        stub = solution_redirect_stub(slug)
    dest.write_text(html, encoding="utf-8")
    src.write_text(stub, encoding="utf-8")
    print(f"migrated {kind} {slug}")


def migrate_posts_and_solutions() -> list[tuple[str, str]]:
    migrated: list[tuple[str, str]] = []
    for path in sorted(BLOG_POSTS.glob("*.html")):
        slug = path.stem
        if (BLOG_POSTS / slug / "index.html").exists():
            continue
        migrate_html_file(path, BLOG_POSTS / slug, slug, kind="blog")
        migrated.append(("blog", slug))

    for path in sorted(SOLUTIONS.glob("*.html")):
        if path.name == "index.html":
            continue
        slug = path.stem
        if (SOLUTIONS / slug / "index.html").exists():
            continue
        migrate_html_file(path, SOLUTIONS / slug, slug, kind="solution")
        migrated.append(("solution", slug))
    return migrated


def rewrite_urls_in_text(text: str, file_path: Path | None = None) -> str:
    text = re.sub(
        r"https://stackcone\.com/blog/posts/([a-z0-9-]+)\.html",
        r"https://stackcone.com/blog/posts/\1/",
        text,
    )
    text = re.sub(
        r"https://stackcone\.com/solutions/([a-z0-9-]+)\.html",
        r"https://stackcone.com/solutions/\1/",
        text,
    )
    text = re.sub(
        r"(?<![/\w])blog/posts/([a-z0-9-]+)\.html",
        r"blog/posts/\1/",
        text,
    )
    text = re.sub(
        r"(?<![/\w])solutions/([a-z0-9-]+)\.html",
        r"solutions/\1/",
        text,
    )
    text = re.sub(
        r'href="\./posts/([a-z0-9-]+)\.html"',
        r'href="./posts/\1/"',
        text,
    )
    text = re.sub(
        r'href="\./([a-z0-9-]+)\.html"',
        r'href="./\1/"',
        text,
    )
    text = re.sub(
        r'href="/blog/posts/([a-z0-9-]+)\.html"',
        r'href="/blog/posts/\1/"',
        text,
    )
    text = re.sub(
        r'href="/solutions/([a-z0-9-]+)\.html"',
        r'href="/solutions/\1/"',
        text,
    )
    if file_path and "blog" in file_path.parts and "posts" in file_path.parts:
        text = re.sub(
            r'href="([a-z0-9-]+)\.html"',
            r'href="/blog/posts/\1/"',
            text,
        )
    elif file_path and "solutions" in file_path.parts and file_path.name == "index.html":
        text = re.sub(
            r'href="([a-z0-9-]+)\.html"',
            r'href="/solutions/\1/"',
            text,
        )
    return text


def rewrite_all_links() -> None:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in ("_dev", ".cursor", ".github", ".git"):
            continue
        if path.suffix not in (".html", ".json", ".xml", ".txt", ".js", ".md", ".mdc"):
            continue
        text = path.read_text(encoding="utf-8")
        new = rewrite_urls_in_text(text, file_path=path)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"rewrote links in {rel}")


def update_json_manifests() -> None:
    for json_path, key, href_pattern in [
        (POSTS_JSON, "posts", "./posts/{id}/"),
        (SOLUTIONS_JSON, "solutions", "./{id}/"),
    ]:
        if not json_path.exists():
            continue
        data = json.loads(json_path.read_text(encoding="utf-8"))
        for item in data[key]:
            item["href"] = href_pattern.format(id=item["id"])
        json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"updated {json_path.name}")


def main() -> None:
    migrated = migrate_posts_and_solutions()
    if not migrated:
        print("no new files to migrate (already done?)")
    rewrite_all_links()
    update_json_manifests()
    print("migration complete")


if __name__ == "__main__":
    main()
