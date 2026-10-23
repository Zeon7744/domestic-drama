import billing

def gate_access(plan="free"):
    """有偿授权门控：免费版限次，Pro 解锁（接 billing.check_access）"""
    return billing.check_access(plan)
"""
domestic-drama: 爆款短剧工作流（选题 → 脚本 → 分镜 → 成片 一键流水线）

将"爆款率 0.47%"的痛点转化为工具化卖点：
- 输入一句话想法（主题词）→ 输出选题卡 + 脚本（3集×90秒）+ 分镜表（JSON+Markdown）
- 全程零依赖（标准库），可离线运行；接入 LLM 平台后可替换模板引擎升级为智能生成
- 内置平台合规检查（复用 drama_engine.DramaEngine 的 PLATFORM_RULES / check_content）

用法：
    python drama_workflow.py --topic 重生都市修仙 --episodes 3 --duration 90
    python drama_workflow.py --topic 战神归来 --platform douyin --duration 120
    python drama_workflow.py --input idea.json --out ./out

输出（默认 --out 自动创建）：
    idea_card.json    选题卡（钩子/受众/付费点/平台）
    script.md         完整脚本（markdown）
    storyboard.json   分镜表（逐镜头，含景别/时长/台词/情绪标签）
    storyboard.md     人读分镜表
"""
import argparse
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from typing import List, Optional

# 复用核心引擎（同仓）
import drama_engine as de


# ---------- 模板库（可替换为 LLM 调用） ----------

# 钩子模板：前3秒抓人（爆款短剧共性）
HOOK_TEMPLATES = [
    "你以为她是你的前妻？三年后她回来复仇，而你只是她棋局里的一颗棋子。",
    "重生回2026年，他手握未来10年的风口，第一件事就是找上曾经瞧不起他的公司。",
    "战神归来，发现女儿被软禁，他一个电话，全城势力跪了。",
    "婚礼现场，新娘被换，新郎是当年他救过的人。",
]

HOOK_BY_TOPIC_KEYWORD = {
    "重生": HOOK_TEMPLATES[1],
    "战神": HOOK_TEMPLATES[2],
    "复仇": HOOK_TEMPLATES[0],
    "豪门": "她的身份不是豪门千金，而是当年被豪门抛弃的私生女。",
    "甜宠": "她以为他讨厌她，直到他把她抱进怀里说：我找了你三年。",
}

# 结构模板：三幕（钩子/冲突/付费点钩子）
BEATS = [
    ("开场钩子", 3, "0-3秒：直接给冲突画面+一句悬念台词（用 HOOK）。"),
    ("世界观", 8, "用1-2句交代时间/地点/主角身份，不啰嗦。"),
    ("冲突升级", 10, "主角目标受阻，反派露出獠牙。"),
    ("高潮/反转", 5, "主角亮出底牌或局势逆转，给爽点。"),
    ("付费点钩子", 2, "结尾卡在最关键一秒：\"他抬手，下一秒——\"，诱导付费解锁。"),
]


def pick_hook(topic: str) -> str:
    for k, h in HOOK_BY_TOPIC_KEYWORD.items():
        if k in topic:
            return h
    return HOOK_TEMPLATES[0]


def pick_platform(topic: str, platform: str) -> str:
    # 国内爆款题材（都市/玄幻）首选抖音；甜宠/复仇类快手也可
    if platform in ("douyin", "kuaishou"):
        return platform
    return "douyin" if any(k in topic for k in ("重生", "战神", "都市", "玄幻")) else "kuaishou"


@dataclass
class IdeaCard:
    """选题卡：从一句话想法到可执行生产计划"""
    topic: str
    hook: str
    audience: str
    platform: str
    genres: List[str]
    paywall_beat: int            # 付费卡在第几集（通常第1集末尾）
    target_length_sec: int
    est_episodes: int
    notes: str

    def to_dict(self):
        return asdict(self)


def build_idea_card(topic: str, episodes: int, duration: int,
                    platform: Optional[str] = None, audience: str = "18-35") -> IdeaCard:
    plat = pick_platform(topic, platform or "douyin")
    return IdeaCard(
        topic=topic,
        hook=pick_hook(topic),
        audience=audience,
        platform=plat,
        genres=[topic],  # 后续可接 NER/LLM 分类
        paywall_beat=1,
        target_length_sec=duration,
        est_episodes=episodes,
        notes=f"单集{duration}秒，共{episodes}集；第1集末尾付费卡点",
    )


# ---------- 脚本生成（模板引擎） ----------

def _script_for_episode(card: IdeaCard, ep_num: int) -> str:
    beats = BEATS
    lines = [
        f"### 第{ep_num}集 · {card.topic}（{card.target_length_sec}s）",
        f"- 钩子：{card.hook}",
        f"- 平台：{card.platform}（竖屏9:16）",
        f"- 目标受众：{card.audience}",
        "",
        "## 分场（按时长节奏）",
    ]
    for name, w, desc in beats:
        lines.append(f"- {name}（{w}s）：{desc}")
    if ep_num == card.paywall_beat:
        lines.append("")
        lines.append(f"> 付费点钩子：本集结尾必须卡在 '{card.hook}' 的未揭晓部分。")
    return "\n".join(lines)


# ---------- 分镜表生成 ----------

# 镜头节奏模板（按 9:16 竖屏爆款经验：3-5-2-8-10 秒节拍）
SHOT_PLAN_SEC = [(3, "特写-钩子"), (5, "近景-世界观"), (10, "中景-冲突"),
                 (15, "全景-高潮"), (3, "特写-付费钩子")]


def build_storyboard(card: IdeaCard, ep_num: int) -> List[dict]:
    shots = []
    for i, (sec, kind) in enumerate(SHOT_PLAN_SEC, 1):
        beat = BEATS[i - 1]
        shots.append({
            "shot_no": i,
            "sec": sec,
            "kind": kind,
            "beat": beat[0],
            "description": f"{beat[0]}镜头：{beat[2].split('：', 1)[-1][:40]}",
            "dialogue": card.hook if i == 1 else "",
            "emotion": "悬念" if i <= 2 else ("爽点" if i == 4 else "钩子"),
        })
    # 校验总时长
    total = sum(s["sec"] for s in shots)
    if total != card.target_length_sec:
        # 将差值挂到第4镜（高潮）
        shots[3]["sec"] = shots[3]["sec"] + (card.target_length_sec - total)
    return shots


def render_storyboard_md(card: IdeaCard, ep_num: int, shots: List[dict]) -> str:
    rows = [f"| 镜号 | 景别 | 时长 | 节拍 | 画面描述 | 台词 | 情绪 |",
            "|---|---|---|---|---|---|---|"]
    for s in shots:
        rows.append(
            f"| {s['shot_no']} | {s['kind']} | {s['sec']}s | {s['beat']} | "
            f"{s['description']} | {s['dialogue']} | {s['emotion']} |"
        )
    return f"### 第{ep_num}集分镜表（{card.target_length_sec}s）\n" + "\n".join(rows) + "\n"


# ---------- 合规检查（复用 DramaEngine） ----------

def compliance_check(card: IdeaCard, script_text: str, storyboard_text: str) -> dict:
    engine = de.DramaEngine(de.DramaPlatform(card.platform))
    r1 = engine.check_content(script_text)
    r2 = engine.check_content(storyboard_text)
    return {
        "script_passed": r1["passed"],
        "storyboard_passed": r2["passed"],
        "issues": r1["issues"] + r2["issues"],
    }


# ---------- 主流程 ----------

def run(topic: str, episodes: int = 3, duration: int = 90,
        platform: Optional[str] = None, out_dir: Optional[str] = None) -> dict:
    card = build_idea_card(topic, episodes, duration, platform=platform)
    out_dir = out_dir or f"out_{uuid.uuid4().hex[:6]}"
    os.makedirs(out_dir, exist_ok=True)

    scripts, storyboards_md, storyboards_json = [], [], []
    for ep in range(1, card.est_episodes + 1):
        s = _script_for_episode(card, ep)
        shots = build_storyboard(card, ep)
        sb_md = render_storyboard_md(card, ep, shots)
        scripts.append(s)
        storyboards_md.append(sb_md)
        storyboards_json.append({"episode": ep, "shots": shots})

    full_script = f"# 《{card.topic}》完整脚本\n\n" + "\n\n---\n\n".join(scripts)
    full_board = "\n\n---\n\n".join(storyboards_md)

    comp = compliance_check(card, full_script, full_board)

    # 写文件
    idea_p = os.path.join(out_dir, "idea_card.json")
    with open(idea_p, "w", encoding="utf-8") as f:
        json.dump(card.to_dict(), f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "script.md"), "w", encoding="utf-8") as f:
        f.write(full_script)
    with open(os.path.join(out_dir, "storyboard.json"), "w", encoding="utf-8") as f:
        json.dump(storyboards_json, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "storyboard.md"), "w", encoding="utf-8") as f:
        f.write(full_board)
    with open(os.path.join(out_dir, "compliance.json"), "w", encoding="utf-8") as f:
        json.dump(comp, f, ensure_ascii=False, indent=2)

    return {"out_dir": out_dir, "idea_card": card, "compliance": comp,
            "files": [os.path.basename(p) for p in [idea_p, "script.md", "storyboard.json",
                                                    "storyboard.md", "compliance.json"]]}


def main():
    ap = argparse.ArgumentParser(description="爆款短剧工作流（选题→脚本→分镜→合规）")
    ap.add_argument("--topic", default="重生都市修仙", help="一句话主题词（如：重生都市修仙 / 战神归来）")
    ap.add_argument("--episodes", type=int, default=3, help="总集数（默认3）")
    ap.add_argument("--duration", type=int, default=90, help="单集目标秒数（默认90）")
    ap.add_argument("--platform", choices=["douyin", "kuaishou"], default=None)
    ap.add_argument("--out", default=None, help="输出目录（默认 auto）")
    ap.add_argument("--json", action="store_true", help="以 JSON 摘要形式打印结果")
    args = ap.parse_args()

    r = run(args.topic, args.episodes, args.duration, args.platform, args.out)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, default=str))
    else:
        print(f"📦 输出目录: {r['out_dir']}")
        print(f"🎯 选题卡: topic={r['idea_card'].topic} hook={r['idea_card'].hook[:40]}...")
        print(f"🔍 合规: script_passed={r['compliance']['script_passed']} issues={r['compliance']['issues']}")
        for fn in r["files"]:
            print(f"   → {fn}")


if __name__ == "__main__":
    main()


# ---------- 付费墙（Pro Gates） ----------

PRO_GATES = {
    "free":    {"max_episodes_per_day": 1, "character_engine": False, "distribution_share": 0.0,  "label": "免费版 ¥0"},
    "pro":     {"max_episodes_per_day": 5, "character_engine": False, "distribution_share": 0.0,  "label": "Pro 版 ¥79/月"},
    "studio":  {"max_episodes_per_day": 999,"character_engine": True,  "distribution_share": 0.30, "label": "Studio 版 ¥299/月"},
}


def check_gates(plan: str, episode_count: int) -> dict:
    """检查付费墙：返回 {"allowed": bool, "reason": str, "upgrade_hint": str}。
    plan: free/pro/studio
    episode_count: 本次要生成的集数
    """
    gates = PRO_GATES.get(plan, PRO_GATES["free"])
    limit = gates["max_episodes_per_day"]

    if episode_count > limit:
        return {
            "allowed": False,
            "reason": f"当前套餐({gates['label']})每日限 {limit} 集，请求 {episode_count} 集超限",
            "upgrade_hint": "升级 Pro (¥79/月) 解锁 5 集/天，或 Studio (¥299/月) 不限集数 + 角色一致性引擎 + 发行分成",
        }

    return {
        "allowed": True,
        "remaining": limit - episode_count if limit < 999 else -1,
        "character_engine": gates["character_engine"],
        "distribution_share": gates["distribution_share"],
        "reason": "",
    }
