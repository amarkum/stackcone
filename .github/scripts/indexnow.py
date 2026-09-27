#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver) which pages changed in this push,
so they recrawl in minutes instead of weeks. Google does not use IndexNow; it reads sitemap.xml."""
import json
import os
import re
import subprocess
import sys
import urllib.request

HOST = "stackcone.com"
KEY = "091cdacb85cb8b9d2fa95dd664990534"  # must match /<KEY>.txt at the site root
SKIP = ("blog/md/", "solutions/md/", ".github/", "scripts/", "404.html", "login/", "signup/")

before = os.environ.get("BEFORE", "")
if before and set(before) != {"0"}:
    diff = subprocess.run(["git", "diff", "--name-only", before, "HEAD"],
                          capture_output=True, text=True, check=True).stdout.split()
else:
    diff = ["index.html"]  # manual run or first push: just ping the homepage

urls = []
for path in diff:
    if not path.endswith(".html") or path.startswith(SKIP) or not os.path.exists(path):
        continue
    with open(path, encoding="utf-8", errors="replace") as fh:
        head = fh.read().split("</head>", 1)[0]
    if 'http-equiv="refresh"' in head or re.search(r'name="robots" content="[^"]*noindex', head):
        continue  # redirect stubs and noindex pages
    url = "/" + path
    if url.endswith("/index.html") or url == "/index.html":
        url = url[: -len("index.html")]
    urls.append(f"https://{HOST}{url}")

if not urls:
    print("IndexNow: no changed pages")
    sys.exit(0)

body = json.dumps({
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": urls[:10000],
}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as resp:
    print(f"IndexNow: HTTP {resp.status} for {len(urls)} URLs")
