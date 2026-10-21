# 🎬 Domestic Drama — 国产短剧资源库

> **国产精品短剧精选集** — 都市·玄幻·古装题材  
> 适合AI短剧创作参考与改编素材

[![GitHub Stars](https://img.shields.io/github/stars/Zeon7744/domestic-drama?style=social)](https://github.com/Zeon7744/domestic-drama)
[![GitHub Forks](https://img.shields.io/github/forks/Zeon7744/domestic-drama?style=social)](https://github.com/Zeon7744/domestic-drama/forks)
[![GitHub License](https://img.shields.io/github/license/Zeon7744/domestic-drama)](https://github.com/Zeon7744/domestic-drama/blob/main/LICENSE)
[![Gitee Stars](https://gitee.com/Zeon7744/domestic-drama/badge/star.svg?theme=gvp)](https://gitee.com/Zeon7744/domestic-drama)
[![红果Ready](https://img.shields.io/badge/红果-ready-success.svg)](https://www.shortdramas.com)

---

## 📌 这是 GitHub 官方主仓

> **Gitee 镜像**: [gitee.com/Zeon7744/domestic-drama](https://gitee.com/Zeon7744/domestic-drama)

Issues 和 PR 请在 GitHub 提交。

---

## 📊 内容概览

| 类别 | 数量 | 说明 |
|------|------|------|
| 🎭 短剧剧本 | 待补充 | 符合红果平台规范 |
| 📖 参考案例 | 待补充 | 爆款短剧分析 |
| 🛠️ 创作工具 | 1 | `drama_workflow.py` 爆欽短剧工作流（选题→脚本→分镜→合规） |

---

## 🚀 为什么用本工具

> 短剧市场半年 220 亿、增速 138%，但**单部爆欽率仅 0.47%** —— 绝大多数团队输在“选题-钩子-分镜”三个上游环节，而非后期制作。
> 本工具把爆欽共性提炼成可复用流水线：一句话想法进，选题卡 + 分集脚本 + 竖屏分镜表 + 平台合规结果 出，
> 全流程零依赖、离线可跑，10 分钟出样片级生产资料，直接把“拍前决策”门槛从“经验”降到“命令”。

### 一行命令

```bash
python drama_workflow.py --topic 重生都市例亚 --episodes 3 --duration 90 --platform douyin
# → out_XXXXXX/{idea_card.json, script.md, storyboard.json, storyboard.md, compliance.json}
```

| 痛点 | 工具对策 |
|---|---|
| 选题玄学、命中率 0.47% | 内置钩子库 + 平台匹配 + 付费点卡点（第1集末），结构化选题卡 |
| 脚本/分镜靠人工对表 | 节拍化模板（3-5-2-8-10s 竖屏节奏）+ 自动时长对齐 + Markdown/JSON 双格式 |
| 平台合规事后被下架 | 复用 `drama_engine.DramaEngine.check_content`，出片前自动扫敏感词/超长 |
| 工具学习成本高 | 纯标准库，无 pip 安装，Windows/Mac 开箱即用；LLM 可替换升级 |

---

## 🎬 短剧类型

- **都市异能** — 战神、赘婿、神医
- **玄幻重生** — 穿越、重生、逆袭
- **古装权谋** — 宫斗、穿越、权臣
- **甜宠恋爱** — 豪门、契约、暗恋

---

## 📁 项目结构

```
domestic-drama/
├── scripts/             # 短剧剧本
├── stories/             # 参考故事
├── tools/               # 创作工具
├── docs/                # 方法论文档
└── README.md           # 项目文档
```

---

## ⚠️ 注意事项

- 本库仅供学习研究使用
- 剧本改编需遵守平台规范

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

**开发者**: Zeon7744  
**最后更新**: 2026-09-25  
**GitHub**: https://github.com/Zeon7744/domestic-drama
