# domestic-drama 部署指南

## 1. 本地运行

```bash
# 克隆 + 运行（零第三方依赖，纯标准库）
git clone https://gitee.com/Zeon7744/domestic-drama.git
cd domestic-drama
chmod +x run.sh smoke_test.sh

# 一行出片
./run.sh "战神归来发现女儿被软禁"

# 或手动传参
python3 drama_workflow.py --topic "重生都市修仙" --episodes 5 --duration 120 --platform douyin

# 跑冒烟测试
./smoke_test.sh
```

输出文件：
- `idea_card.json` — 选题卡（钩子/受众/付费点/平台）
- `script.md` — 分集剧本（Markdown）
- `storyboard.json` — 分镜表（JSON 结构化）
- `storyboard.md` — 人读分镜表
- `compliance.json` — 平台合规检查结果

## 2. 微信小程序接入

1. **后端部署**：将 `drama_workflow.py` 包装为 HTTP API（Flask/FastAPI），部署到云函数（腾讯云 SCF / 阿里云 FC）
2. **小程序前端**：用户输入一句话 → 调后端 API → 展示选题卡 + 剧本预览 + 分镜表
3. **支付**：接入微信支付（JSAPI），Free 限 1 集/天，Pro ¥79/月解锁 5 集/天
4. **审核注意**：小程序简介注明"AI 辅助创作工具，生成内容仅供参考"；避免"自动生成"等暗示内容审核缺失的措辞

## 3. 爆款率 0.47% → 2%+ A/B 验证方法

**实验设计**：
- **对照组**：传统人工选题（编辑经验判断）出 10 部短剧上线
- **实验组**：用 `drama_workflow.py` 生成选题卡+分镜出 10 部短剧上线（同平台/同时段/同制作团队）
- **核心指标**：
  - 3 日播放完成率（>70% 为及格）
  - 付费转化率（付费集/总播放）
  - 7 日破亿率（破亿部数/总上线部数）
- **周期**：4 周（含 2 周生产 + 2 周数据回收）
- **统计方法**：双样本 t 检验，p<0.05 判定显著差异

**预期结果**：实验组爆款率从 0.47% 提升到 2%+（4 倍），核心靠钩子模板+付费卡点优化
