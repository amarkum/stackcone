#!/usr/bin/env bash
# Strip unpublished paths before GitHub Pages upload. Keep in sync with robots.txt Disallow.
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

# Ensure GitHub Pages serves files as-is (no Jekyll processing of {{ in HTML).
touch .nojekyll

find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete 2>/dev/null || true

echo "public site artifact ready"
