# CV 探索版

`cv_exploration` 是面向计算机视觉研究者的半自动 Auto-Research profile。它保留本地优先、可恢复、可审计、证据链和人工闭环的内核，在其上加入 A+B+C 创新组合与多 GPU 子 Agent 的实验编排。

## 组件与职责

| 组件 | 实现位置 | 责任 |
| --- | --- | --- |
| MainAgent | `ResearchOrchestrator` | 接收项目状态、分派阶段任务、维护 event/artifact、恢复中断并等待审批 |
| Literature-SubAgent | `literature-scout` + `knowledge-base` | 导入本地资料、结构化文献记录、将长文本切块持久化，避免将完整 PDF 反复放入上下文 |
| Combination Agent | `cv-combination-planner` | 枚举 A、B、C、A+B、A+C、B+C、A+B+C，并要求人类选择可测试方案 |
| GPU-SubAgent | `gpu-subagent[cuda:N]` | 每张配置 GPU 一个实验槽，保存组合、命令、日志、指标、失败和可行性结论 |
| Evaluation-SubAgent | `evaluation-subagent` | 汇总 mAP、mIoU、F1、重建误差等指标，提出下一轮 ablation/训练/数据建议 |
| Composition-Agent | `composition-agent` | 汇总文献、组合、实验和评估为带来源的草稿与 claim review |

目前 MainAgent 的“与人对话”入口是项目配置、artifact 和审批事件，而不是一个伪装成自动科研员的聊天界面。后续接入聊天模型时，聊天内容也应写入 event/artifact，并由人确认后才改变组合或启动下一轮实验。

## 运行方式

```bash
python -m paper_harness.cli init examples/cv_exploration_project.json --output ./runs/cv-demo --edition cv_exploration
python -m paper_harness.cli run ./runs/cv-demo/project.json
```

在 `examples/cv_exploration_project.json` 中设置：

- `gpu_devices`：例如 `["cuda:0", "cuda:1"]`；
- `innovation_components`：A、B、C 的实际改动；
- `cv_metrics`：使用同一数据切分、同一协议比较的指标；
- `knowledge_files`：本地 `.txt` / `.md` 资料路径；
- `execute_cv_experiments`：默认 `false`，防止未经批准运行训练。

## 当前能运行与尚未绑定的部分

现在会创建可恢复的 `knowledge_index`、组合空间、每卡实验槽、评估建议和写作输入，并保存为 JSON artifact。长文本按默认 6000 字符分块保存在 `knowledge/chunks/`，Agent 只读取摘要/元数据，从而限制上下文长度与 token 消耗。

真实的 PDF 下载、PDF 解析、代码仓库拉取、CUDA 训练和 SOTA 数据库比对属于外部 provider/runtime。它们没有在默认配置中自动运行：你需要显式提供合规的数据集、代码、命令、许可证和机器资源，并在 `experiment` 阶段批准后执行。这样避免把“计划好的实验”伪装为“已经验证的结果”。

## 人在环路中的位置

系统不自动接受 innovation winner。研究者应在四处介入：选择组合、批准每轮实验、核验指标与公平对比、确认论文中每条 claim。事件流和 artifact 记录这些决策，使其可回溯、可复现实验设置，也便于后续多轮迭代。
