# 本科毕业版

`undergraduate` 面向毕业论文和刚开始做科研的用户。它不承诺自动写出可提交论文，而是把老师给出的课题拆成一条能逐步核验、能随时停下询问导师的路径。

## 适合的任务

- 老师已经给出方向，需要完成综述、方案比较和小规模实验；
- 希望了解一篇毕业论文从问题定义到结果讨论的基本结构；
- 需要保存文献、实验配置和修改记录，避免最后阶段找不到依据；
- 想做本地相似度筛查和 AI 使用披露整理，但不寻求规避学校检测。

## 工作流

```text
老师课题 -> 本地资料/文献 -> 综述矩阵 -> 可检验方案
        -> 导师批准的 baseline 实验 -> 证据检查 -> 草稿与完整性检查
```

`undergraduate-guide` 产出 `undergraduate_plan`，明确研究范围、对照组、变量、指标和四个人工检查点。它的目标是降低无基础用户的决策负担，而不是替代导师的选题和结论判断。

## 初次运行

```bash
python -m paper_harness.cli init examples/stem_project/project.json --output ./runs/my-thesis --edition undergraduate
python -m paper_harness.cli run ./runs/my-thesis/project.json
```

遇到 `approval-required` 后，先查看 `artifacts/` 里的文献、计划和审查记录，再批准下一阶段。逐阶段教程见 [getting-started-zh.md](getting-started-zh.md)。

## 诚实边界

- `similarity_report` 是本地五元组重合筛查，不是学校系统的正式查重报告；
- `authorship_review` 只提示贡献表达和 AI 使用披露，不实现“去 AI 检测”；
- 任何文献、实验和结论都要由学生与导师人工确认；
- toy experiment 仅验证工作流，不能作为毕业论文实验结论。
