# domestic-drama 5 分钟跑通

国产短剧 IP 改编工作流：选题拆解 → 分镜脚本 → 角色设定 → 合规审查。

## 安装
```bash
pip install -r requirements.txt
```

## 一键冒烟
```bash
bash smoke_test.sh
```

## 主入口
```bash
bash run.sh        # 生成 30s 短剧样片（分镜+台词+BGM 建议）
```

## 模块
- `drama_engine.py`：核心引擎（选题→分镜→角色→台词）
- `drama_workflow.py`：工作流编排（多角色一致性 + 四维风格矩阵）
- `billing.py`：面包多 Pay收款层 + 先体验后付费门控
