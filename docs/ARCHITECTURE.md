# domestic-drama 架构

```
run.sh / smoke_test.sh
        │
        ▼
  drama_workflow.py   工作流编排：角色一致性引擎 + 四维风格矩阵
        │  调用
        ▼
  drama_engine.py     核心引擎：选题拆解 → 分镜 → 角色卡 → 台词 → BGM
        │  门控
        ▼
  billing.py          爱发电 afdian 网关 + PAYWALL_RULES + check_access
```

## 数据流
选题素材 → 引擎拆解分镜/角色 → 工作流编排一致性 → 样片产出（HTML/脚本）
付费门控：免费版限次，Pro 解锁完整剧本 + 模板库（对齐 billing.py）。
