# 给本科生和初入科研者的上手教程

这份教程对应 `undergraduate` 本科毕业版，假设你只会复制命令，不要求你先理解 Agent、provider 或状态机。第一次请先运行离线 Demo，熟悉后再替换成自己的毕业论文题目。CV 科研人员请阅读 [CV 探索版](cv-exploration-zh.md)。

## 1. 准备环境

需要 Python 3.9 或更高版本：

```bash
python3 --version
cd paper-harness
python3 -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\\Scripts\\Activate.ps1
```

项目不强制依赖外部模型或网络服务，因此不需要先申请 API Key。

## 2. 先跑 Demo

```bash
python3 -m demo.run_demo
```

命令会打印一个临时输出目录。里面的 `artifacts/` 是每个 Agent 的结构化结果，`events.jsonl` 是阶段和执行记录，`research_report.md` 是简报，`stem_pipeline.svg` 是可编辑图示，`visual_manifest.json` 记录图片元素和来源要求，`latex/` 是可继续编辑的 LaTeX 工程。

打开 `demo/index.html` 查看说明面板。Demo 使用合成数据，不能当作你的论文实验结果。

## 3. 用自己的题目创建项目

新建一个 `my_project.json`：

```json
{
  "title": "我的毕业论文题目",
  "edition": "undergraduate",
  "domain": "stem",
  "objective": "用一句话描述要解决的问题",
  "settings": {
    "online": false,
    "require_human_approval": true,
    "adversarial_rounds": 3
  }
}
```

`domain` 可选：`stem`（计算机、电子、机械、数学、实验科学）、`humanities`（历史、语言、教育、社会科学）或 `arts`（视觉设计、文学创作、艺术研究）。

初始化并运行：

```bash
python -m paper_harness.cli init my_project.json --output ./runs/my-thesis
python -m paper_harness.cli run ./runs/my-thesis/project.json
```

系统会先完成低风险阶段，然后在对抗审查前暂停。看到 `approval-required` 是正常现象，表示需要你阅读已有 artifact 后再继续。

## 4. 如何批准下一阶段

```bash
python -m paper_harness.cli approve ./runs/my-thesis/project.json --stage adversarial_review
python -m paper_harness.cli run ./runs/my-thesis/project.json
```

后续阶段依次可能需要批准：`experiment`、`evidence_review`、`draft`、`final_review`。毕业论文最好逐阶段检查，不要盲目批准 `all`。每次运行都会从已保存的 artifact 恢复；中断后直接再次执行 `run` 即可。

## 5. 如何读结果

1. 看 `literature_search`，确认标题、作者、年份和链接真实完整。
2. 看 `innovation_candidates` 和 `adversarial_search`，winner 只是待验证方向，不等于创新已经成立。
3. 批准 `experiment` 前检查 baseline、数据、指标和资源是否可完成。
4. 看 `claim_audit`：`traceable` 只表示找得到来源，仍需亲自阅读来源确认语义支持。
5. 看 `similarity_report`：它是本地五元组重合筛查，不是学校或期刊的正式查重结果。
6. 看 `visual_manifest.json`：理工科图先拆元素再组合；外部素材要补充来源、许可证和人工选择记录。

## 常见问题

### 为什么没有自动生成整篇论文？

这是安全边界。系统生成的是有证据链的 working draft，不自动声称创新成立，也不自动投稿。最终写作、引用和格式要按导师、学校和目标期刊要求人工完成。

### 为什么在线检索没有结果？

默认离线。明确使用 `python -m paper_harness.cli run ./runs/my-thesis/project.json --online` 才会访问 OpenAlex。网络失败会记录在 `provider_errors`，不会用虚构文献填充结果；也可以把自己读过的文献放入 `settings.sources`。

### 为什么图片不是 PNG/JPG？

离线 Demo 生成 SVG，是为了无需配置生图模型也能看到和编辑图的结构。接入真实 `ImageProvider` 后，仍必须保存 prompt、素材来源、模型版本和人工审查结果。

### 可以把结果直接交给学校吗？

不可以。Demo 实验是合成数据，查重是筛查，claim audit 是可追溯性检查。请按学校的格式、伦理、引用、查重和 AI 使用披露要求人工复核。
