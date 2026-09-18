#!/usr/bin/env python3
"""Add any generated /learn/ pages missing from sitemap.xml."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sm = ROOT / "sitemap.xml"
text = sm.read_text()
urls = ["https://stackcone.com/learn/%s/" % p.parent.relative_to(ROOT / "learn").as_posix()
        for p in sorted((ROOT / "learn").rglob("index.html")) if p.parent != ROOT / "learn"]
add = "".join(f"  <url>\n    <loc>{u}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n"
              for u in urls if f"<loc>{u}</loc>" not in text)
if add:
    sm.write_text(text.replace("</urlset>", add + "</urlset>"))
print("added", add.count("<url>"))
