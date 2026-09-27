#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver) which pages changed in this push,
so they recrawl in minutes instead of weeks. Google does not use IndexNow; it reads sitemap.xml."""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = "stackcone.com"
KEY = "091cdacb85cb8b9d2fa95dd664990534"  # must match /<KEY>.txt at the site root
SKIP = ("blog/md/", "solutions/md/", ".github/", "scripts/", "404.html", "login/", "signup/")

before = os.environ.get("BEFORE", "")
if os.environ.get("ALL") == "true":
    # Manual run with "submit every page": use every URL in the sitemap.
    with open("sitemap.xml", encoding="utf-8") as fh:
        diff = []
        sitemap_urls = re.findall(r"<loc>(.*?)</loc>", fh.read())
elif before and set(before) != {"0"}:
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

if os.environ.get("ALL") == "true":
    urls = sitemap_urls

if not urls:
    print("IndexNow: no changed pages")
    sys.exit(0)

# The search engine checks /<KEY>.txt, so wait until GitHub Pages is serving it.
key_url = f"https://{HOST}/{KEY}.txt"
for _ in range(20):
    try:
        with urllib.request.urlopen(key_url, timeout=15) as resp:
            if resp.read().decode("utf-8", "replace").strip() == KEY:
                break
    except (urllib.error.URLError, TimeoutError):
        pass
    print("waiting for the key file to go live...")
    time.sleep(30)

body = json.dumps({
    "host": HOST,
    "key": KEY,
    "keyLocation": f"https://{HOST}/{KEY}.txt",
    "urlList": urls[:10000],
}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
for attempt in range(4):
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow: HTTP {resp.status} for {len(urls)} URLs")
            break
    except urllib.error.HTTPError as err:
        # 403: key not verified yet, 429: rate limited. Anything else is a real error.
        if err.code not in (403, 429) or attempt == 3:
            raise
        print(f"IndexNow: HTTP {err.code}, retrying in 60s")
        time.sleep(60)
