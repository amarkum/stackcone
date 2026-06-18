#!/usr/bin/env bash
# Strip dev-only paths before GitHub Pages upload. Keep in sync with robots.txt Disallow rules.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PATHS=(
  _dev
  .cursor
  .github
  blog/md
  solutions/md
  scripts
  README.md
)

for path in "${PATHS[@]}"; do
  if [[ -e "$path" ]]; then
    rm -rf "$path"
    echo "removed $path"
  fi
done

find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete 2>/dev/null || true

echo "public site artifact ready"
