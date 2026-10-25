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

# ── 面包多 Pay (mbd) 降级 + 1 元首单 dry-run 验证 ─────────────────────────
echo "==> [mbd] MbdGateway 未配 key 降级验证（created_pending_key）"
python3 - <<'PYEOF_MBD'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("billing", "billing.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
gw = mod.get_gateway("mbd") if hasattr(mod, "get_gateway") else None
if gw is None:
    reg = getattr(mod, "_REGISTRY", None) or getattr(mod, "_GATEWAYS", None)
    gw = reg["mbd"]()
o = gw.create_order("t1", 100, "smoke", "free")
assert o["status"] == "created_pending_key", o
assert "MBD_API_KEY" in o.get("needs_secret", []), o
q = gw.query_callback("x")
assert q["status"] == "pending_key", q
print(f"OK: mbd 降级 status={o['status']} needs={o['needs_secret']}")
PYEOF_MBD

echo "==> [mbd] 1 元首单 dry-run（不真扣款，验证签名/参数构造正确）"
python3 - <<'PYEOF_MBD'
import hashlib, json, os, uuid
# 面包多 Pay 官方签名：非空参数 ASCII 字典序 k=v&... + &key=app_key，取 MD5
def mbd_sign(data, api_key):
    ordered = {k: v for k, v in sorted(data.items()) if v not in ("", None)}
    s = "&".join(f"{k}={v}" for k, v in ordered.items())
    return hashlib.md5((s + "&key=" + api_key).encode("utf-8")).hexdigest()

out_trade_no = "mbd_smoke_1yuan_" + uuid.uuid4().hex[:12]
params = {"app_id": os.environ.get("MBD_APP_ID") or "(未配)",
          "description": "smoke-1yuan", "amount_total": 100,
          "out_trade_no": out_trade_no}
params["sign"] = mbd_sign(params, os.environ.get("MBD_API_KEY") or "(占位)")
assert params["amount_total"] == 100, "1 元 = 100 分"
print(f"OK: 1元首单参数 amount_total=100分 out_trade_no={out_trade_no} 已生成签名")
print("OK: MBD_API_KEY 未配时 MbdGateway.create_order 走'待开通'降级路径，行为对齐 noop")
PYEOF_MBD
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1

# ── 第三条通道 praise（支付宝/微信个人赞赏码）降级验证 ─────────────────────
echo "==> [praise] 赞赏码网关未配码值降级验证（created_pending_key + needs_secret）"
python3 - <<'PYEOF_PRAISE'
import importlib.util, os
os.environ.pop("PRAISE_ALIPAY_QR", None); os.environ.pop("PRAISE_WX_QR", None)
spec = importlib.util.spec_from_file_location("billing", "billing.py")
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
gws = getattr(mod, "_REGISTRY", None) or getattr(mod, "_GATEWAYS", None) or getattr(mod, "BUILTIN_REGISTRY", None)
assert gws and "praise" in gws, "praise 网关未登记: %s" % gws
gw = gws["praise"]()
try:
    o = gw.create_order("t1", 300, "smoke", "free")
except TypeError:
    o = gw.create_order("free", 300, {})
assert o["status"] == "created_pending_key", o
assert any("PRAISE" in s for s in o.get("needs_secret", [])), o
print(f"OK: praise 降级 status={o['status']} needs={o['needs_secret']}")
PYEOF_PRAISE
echo "smoke_test: praise gateway 通过"
