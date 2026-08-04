#!/usr/bin/env bash
# Commit + push state.json if changed (race-safe).
set -euo pipefail

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git add -A
if git diff --staged --quiet; then
  echo "no state change"
  exit 0
fi

cp state.json /tmp/oil-alert-state.json
for i in 1 2 3 4 5; do
  git fetch -q origin main || true
  git reset -q --hard origin/main
  cp /tmp/oil-alert-state.json state.json
  git add -A
  if git diff --staged --quiet; then
    echo "state already current on remote"
    exit 0
  fi
  git commit -q -m "state: $(date -u +%FT%TZ)"
  if git push -q origin main; then
    echo "pushed (attempt $i)"
    exit 0
  fi
  echo "push race, retry $i"
done
echo "WARN: could not push state after retries"
exit 0
