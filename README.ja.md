# paper-harness

**言語:** [简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

> 卒業論文・研究入門向けの汎用版と、CV・具身知能・電力網制御向けの専門版からなる論文研究ワークベンチです。

## 2 つの版

- 汎用版: [paper-harness-undergraduate](https://github.com/ace-trump-tech/paper-harness-undergraduate)
- 専門版: [paper-harness-professional](https://github.com/ace-trump-tech/paper-harness-professional)

両方とも再開可能性、監査可能性、人間の承認を重視しますが、依存関係とワークフローは独立しています。主リポジトリのオフライン Demo は次で実行できます。

```bash
python3 -m demo.run_demo
open demo/index.html        # macOS
```

専門版には、検証済み PDF、抽出テキスト、研究カード、実験計画を含む [電力網具身知能 Demo](https://github.com/ace-trump-tech/paper-harness-professional/tree/main/demo/self-learn) があります。

```bash
./scripts/bootstrap-versions.sh
```

本プロジェクトはブラックボックス、自動投稿ツール、または自律的な電力網制御システムではありません。数値ソルバー、シミュレータ、安全ゲート、人間の承認が最終権限を持ちます。
