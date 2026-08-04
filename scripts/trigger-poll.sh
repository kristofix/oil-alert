#!/usr/bin/env bash
# Opcjonalny ręczny trigger (nie jest potrzebny do 24/7).
# Domyślnie jeden poll; pętla: LOOP=1 ./scripts/trigger-poll.sh
set -euo pipefail
REPO="${OIL_ALERT_REPO:-kristofix/oil-alert}"
if [[ "${LOOP:-}" =~ ^(1|true|yes)$ ]]; then
  gh workflow run alert.yml --repo "$REPO" -f once=false
  echo "$(date -u +%FT%TZ) triggered LOOP on $REPO"
else
  gh workflow run alert.yml --repo "$REPO" -f once=true
  echo "$(date -u +%FT%TZ) triggered ONCE on $REPO"
fi
