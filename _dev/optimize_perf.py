#!/usr/bin/env python3
"""Move AdSense to body end and add defer to site scripts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ADS_PATTERN = re.compile(
    r"\s*<script async src=\"https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^\"]*\"[^>]*></script>\s*",
    re.IGNORECASE,
)
ADS_SNIPPET = (
    '  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4080297219638785"\n'
    "     crossorigin=\"anonymous\"></script>\n"
)

DEFER_SCRIPTS = ("site-nav.js", "script.js", "scroll-reveal.js", "contact-form.js")


def optimize_html(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    original = html

    ads_match = ADS_PATTERN.search(html)
    if ads_match:
        html = ADS_PATTERN.sub("\n", html, count=1)
        if "adsbygoogle.js" not in html:
            html = html.replace("</body>", ADS_SNIPPET + "</body>", 1)

    for name in DEFER_SCRIPTS:
        html = re.sub(
            rf'(<script src="[^"]*{re.escape(name)}")>',
            r'\1 defer>',
            html,
        )
        html = re.sub(
            rf'(<script src="{re.escape(name)}")>',
            r'\1 defer>',
            html,
        )

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> None:
    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        if path.parts[0] in ("_dev", ".cursor", ".github") if len(path.relative_to(ROOT).parts) else False:
            continue
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in ("_dev", ".cursor", ".github"):
            continue
        if optimize_html(path):
            print(f"updated {rel}")
            updated += 1
    print(f"done — {updated} file(s) updated")


if __name__ == "__main__":
    main()
