#!/usr/bin/env bash
# run.sh — domestic-drama 一键演示（爆款短剧 3 集流水线）
set -uo pipefail
cd "$(dirname "$0")"

echo "🎬 domestic-drama 一键演示：选题 → 脚本 → 分镜 → 成片流水线"
OUT="demo_out"
rm -rf "$OUT"

python3 drama_workflow.py --topic "战神归来" --episodes 3 --duration 90 --out "$OUT" 2>&1 | tail -8

echo
echo "✅ 输出目录：$(pwd)/$OUT"
ls "$OUT"
