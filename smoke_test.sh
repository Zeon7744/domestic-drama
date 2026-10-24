#!/usr/bin/env bash
# smoke_test.sh — domestic-drama 冒烟测试
# 用法：./smoke_test.sh [output_dir]
set -euo pipefail

OUT_DIR="${1:-smoke_test_out}"
echo "=== domestic-drama smoke test ==="
echo "输出目录: $OUT_DIR"

mkdir -p "$OUT_DIR"

cd "$(dirname "$0")"  # 始终在仓根目录执行，避免跨目录调用失败

# 运行 demo 创意
python3 ./drama_workflow.py --topic "战神归来" --episodes 3 --duration 90 --out "$OUT_DIR" 2>&1

PASS=0; FAIL=0

# 断言 1：选题卡存在
if [ -f "$OUT_DIR/idea_card.json" ]; then
  echo "✅ idea_card.json 存在"
  PASS=$((PASS+1))
  # 检查字段完整性
  python3 -c "
import json
with open('$OUT_DIR/idea_card.json') as f:
    card = json.load(f)
required = ['topic','hook','audience','platform','genres','paywall_beat']
missing = [k for k in required if k not in card]
if missing:
    print(f'❌ 选题卡缺少字段: {missing}')
    exit(1)
print(f'✅ 选题卡字段完整 (topic={card[\"topic\"]})')
" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
else
  echo "❌ idea_card.json 不存在"
  FAIL=$((FAIL+1))
fi

# 断言 2：剧本存在且非空
if [ -f "$OUT_DIR/script.md" ] && [ -s "$OUT_DIR/script.md" ]; then
  lines=$(wc -l < "$OUT_DIR/script.md")
  echo "✅ script.md 存在 ($lines 行)"
  PASS=$((PASS+1))
else
  echo "❌ script.md 不存在或为空"
  FAIL=$((FAIL+1))
fi

# 断言 3：分镜表存在且含三集
if [ -f "$OUT_DIR/storyboard.json" ]; then
  count=$(python3 -c "import json;print(len(json.load(open('$OUT_DIR/storyboard.json'))))")
  if [ "$count" = "3" ]; then
    echo "✅ storyboard.json 包含 3 集"
    PASS=$((PASS+1))
  else
    echo "❌ storyboard.json 集数不对 (实际=$count, 期望=3)"
    FAIL=$((FAIL+1))
  fi
else
  echo "❌ storyboard.json 不存在"
  FAIL=$((FAIL+1))
fi

# 断言 4：分镜 Markdown 存在
if [ -f "$OUT_DIR/storyboard.md" ] && [ -s "$OUT_DIR/storyboard.md" ]; then
  echo "✅ storyboard.md 存在"
  PASS=$((PASS+1))
else
  echo "❌ storyboard.md 不存在或为空"
  FAIL=$((FAIL+1))
fi

# 断言 5：合规检查存在
if [ -f "$OUT_DIR/compliance.json" ]; then
  echo "✅ compliance.json 存在"
  PASS=$((PASS+1))
else
  echo "❌ compliance.json 不存在"
  FAIL=$((FAIL+1))
fi

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
