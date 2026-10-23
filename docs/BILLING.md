# domestic-drama 收款与定价

爱发电双通道：收款 afdian.net/@Zeon7744 + 社区发布 afdian.com/user/0c59dda8a1bb11f19b9552540025c377。

## 定价（先体验后付费）
- 免费 ¥0 — 素材 CC0 全免费，基础工作流
- Pro ¥79/月 — 完整剧本 + 模板库 + 创作工具
- 工作室 ¥299/月 — 多席位 + 商用授权
- 精品模板/提示词包 ¥99-399/套

## 网关
`AFDIAN_GATEWAY`（缺省 noop 不扣款，配 AFDIAN_SECRET_KEY 后接爱发电开放 API）。
见 `billing.py`：PAYWALL_RULES / check_access / create_order_for_plan。
