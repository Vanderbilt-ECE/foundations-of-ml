#!/usr/bin/env bash
# Builds every Presentations/*/slides.md deck into site/public/decks/<unit>/<deck>/,
# so `astro build` (and `astro dev`, which serves public/ directly) can find them.
# Used by both the deploy workflow and local dev — keeps the slug scheme in one place.
set -e

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
slidev_bin="$root_dir/slidev_template/node_modules/.bin/slidev"

slugify() { echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g'; }

npm ci --prefix "$root_dir/slidev_template"

find "$root_dir" -path "*/Presentations/*/slides.md" -print0 | while IFS= read -r -d '' slides; do
  deck_dir=$(dirname "$slides")
  unit_dir=$(dirname "$(dirname "$deck_dir")")
  unit_slug=$(slugify "$(basename "$unit_dir")")
  deck_slug=$(slugify "$(basename "$deck_dir")")
  out="$root_dir/site/public/decks/$unit_slug/$deck_slug"
  echo "Building $(basename "$unit_dir") / $(basename "$deck_dir") -> decks/$unit_slug/$deck_slug"
  (cd "$deck_dir" && "$slidev_bin" build \
    --base "/foundations-of-ml/decks/$unit_slug/$deck_slug/" \
    --router-mode hash \
    --out "$out")
done
