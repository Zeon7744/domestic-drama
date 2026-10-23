#!/usr/bin/env bash
# domestic-drama 冒烟（归档仓）：import + billing.check_access
set -uo pipefail
cd "$(dirname "$0")"
PASS=0; FAIL=0
python3 -c "import billing; r=billing.check_access('free','tool_call'); assert r['allowed'] is True; print('billing.check_access OK', r)" \
  && PASS=$((PASS+1)) || { echo "FAIL: billing"; FAIL=$((FAIL+1)); }
echo "smoke_test: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] && echo "=== SMOKE PASS ===" && exit 0 || { echo "=== SMOKE FAIL ==="; exit 1; }
