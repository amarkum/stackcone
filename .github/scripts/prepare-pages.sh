#!/usr/bin/env bash
# Build a clean public artifact for GitHub Pages (Actions deploy).
# Keep exclusions in sync with robots.txt Disallow rules.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

OUT="_site"
rm -rf "$OUT"
mkdir -p "$OUT"

# Copy published site files only (exclude sources, tooling, and repo docs).
rsync -a \
  --exclude '.git/' \
  --exclude '.github/' \
  --exclude '.cursor/' \
  --exclude '_dev/' \
  --exclude '_site/' \
  --exclude 'blog/md/' \
  --exclude 'solutions/md/' \
  --exclude 'scripts/' \
  --exclude 'README.md' \
  --exclude '.gitignore' \
  --exclude '.DS_Store' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  ./ "$OUT/"

# Ensure GitHub Pages serves files as-is (no Jekyll processing).
touch "$OUT/.nojekyll"

echo "public site artifact ready in $OUT/"
find "$OUT" -maxdepth 2 -type d | sort | head -40
