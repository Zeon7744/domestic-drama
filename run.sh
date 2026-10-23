#!/usr/bin/env bash
# domestic-drama（已归档）：仅验证 billing 层可用
set -euo pipefail
cd "$(dirname "$0")"
python3 -c "import billing; print(billing.get_pricing())"
