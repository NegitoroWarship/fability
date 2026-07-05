# fable-harness

Claude Opus 4.8 上で Claude Fable 5 級の厳密さ・正確性・洞察を引き出す Claude Code 用 harness。

## 原理
Fable 5 のプロンプティングガイドは「Fable 5 が自然に行う挙動」のカタログである。
Opus 4.8 は指示を字義通り忠実に実行する。よって Fable 5 の行動カタログを明示的な
プロトコルに変換し、Opus 4.8 の指示追従を配達機構として使う。

## 構成
- `kernel/kernel.md` — 毎セッション注入される 6 つの常時規律+スキルディスパッチ表
- `skills/` — 6 つのプロトコルスキル(deep-insight, spec-first, fresh-verify, long-run, session-memory, grounded-report)
- `agents/` — verifier(fresh-context 敵対的検証者)/ investigator(並列仮説検証者)
- `eval/` — 効果計測ツール(タスク×モデル×harness有無で実行し、5観点rubricで採点)

## インストール
1. `./install.sh` を実行(~/.claude/skills, ~/.claude/agents へ symlink)
2. 表示される settings フラグメントを ~/.claude/settings.json にマージ
3. 新しいセッションを開始

## 評価の実行
eval/README 節を参照(`eval/run.sh <task-dir> <model> <on|off> <rep>` → `eval/grade.py <run-dir>`)

## 設計文書
docs/specs/2026-07-05-fable-harness-design.md
