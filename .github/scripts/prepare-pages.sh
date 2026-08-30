#!/usr/bin/env bash
# Strip unpublished paths before GitHub Pages upload. Keep in sync with robots.txt Disallow.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Drop legacy *.html redirect stubs (canonical URLs are slug/index.html only).
for dir in blog/posts solutions; do
  [[ -d "$dir" ]] || continue
  while IFS= read -r -d '' file; do
    if grep -qE 'location\.replace\(|http-equiv="refresh"' "$file" 2>/dev/null; then
      rm -f "$file"
      echo "removed redirect stub $file"
    fi
  done < <(find "$dir" -maxdepth 1 -name '*.html' -print0 2>/dev/null || true)
done

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
