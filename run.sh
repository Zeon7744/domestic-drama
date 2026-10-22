#!/usr/bin/env bash
# run.sh — domestic-drama 一键启动
# 用法：./run.sh "一句话创意" [--episodes N] [--duration N] [--platform douyin|kuaishou]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

IDEA="${1:-重生都市修仙}"
shift 2>/dev/null || true

echo "🎬 爆款短剧工作流"
echo "💡 创意: $IDEA"
echo "📦 Checking dependencies..."
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt 2>/dev/null || echo "(zero deps needed)"

echo "🚀 Generating..."
python3 drama_workflow.py --topic "$IDEA" "$@"

echo ""
echo "✅ 完成！查看输出目录 out_* 获取完整文件"
