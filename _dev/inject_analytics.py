#!/usr/bin/env python3
"""Inject GA4 analytics snippet into all public HTML pages."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GA_ID = "G-B29M3GX6QM"

ANALYTICS_SNIPPET = f"""  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
  <script src="/assets/analytics.js" defer></script>
"""

REDIRECT_SCRIPT = re.compile(
    r"\s*<script>\s*if \(location\.protocol === \"http:\"\)[^<]*</script>\s*",
    re.DOTALL,
)
INDEX_REDIRECT = re.compile(
    r"\s*<script>\s*\(function \(\) \{[^<]*index\.html[^<]*\}\)\(\);\s*</script>\s*",
    re.DOTALL,
)
ANALYTICS_MARKER = "assets/analytics.js"


def inject_into_html(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    original = html

    html = REDIRECT_SCRIPT.sub("\n", html)
    html = INDEX_REDIRECT.sub("\n", html)

    if ANALYTICS_MARKER not in html:
        if "</head>" in html:
            html = html.replace("</head>", ANALYTICS_SNIPPET + "</head>", 1)
        else:
            return False

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main() -> None:
    updated = 0
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in ("_dev", ".cursor", ".github"):
            continue
        if inject_into_html(path):
            print(f"updated {rel}")
            updated += 1
    print(f"done — {updated} file(s) updated")


if __name__ == "__main__":
    main()
