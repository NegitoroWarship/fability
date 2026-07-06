# fability

Claude Opus 4.8 上で Claude Fable 5 級の厳密さ・正確性・洞察を引き出す Claude Code 用 harness。

Fability は、Fable 5 的な規律を明示プロトコル・system prompt 注入・hook 強制に変換し、Opus 4.8 の挙動を Fable 5 に近づけるための harness です。

English version: [README.md](README.md)

## 結果

規律ベンチマーク(4タスク × 5観点rubric × 各条件8実行、Sonnet 5ブラインド判定):

| 条件 | 平均総合 (/10) | sd |
|---|---|---|
| Fable 5(素) | 9.88 | 0.35 |
| Opus 4.8(素) | 8.62 | 1.30 |
| Opus 4.8 + harness v1(プロンプト注入のみ) | 8.88 | 1.46 |
| **Opus 4.8 + harness v2** | **9.88** | **0.35** |

Opus 4.8 + harness v2 は、本ベンチマークにおいて Fable 5 素と同スコア(5観点の平均値まで一致)。詳細な集計・グラフは [`eval/results/summary.ja.md`](eval/results/summary.ja.md) と `eval/results/report.html`(英語、要ブラウザ)を参照。

v1→v2 の差分が本プロジェクトの中心的知見: **規律は指示ではなく機構として与える。**
- v1(カーネルを additionalContext として注入)は検証ハードゲートがほぼ発火せず、素の Opus 4.8 とほぼ同スコア
- v2 は (a) カーネルを system prompt に注入し、(b) Stop フックが「フルテストスイート実行の証拠がない完了宣言」を機構的に差し戻す。これで検証実施(C2)が 1.25→2.00 に到達

## 原理

Fable 5 のプロンプティングガイドは「Fable 5 が自然に行う挙動」のカタログである。
Opus 4.8 は指示を字義通り忠実に実行する。よって Fable 5 の行動カタログを明示的な
プロトコルに変換し、Opus 4.8 の指示追従——それで足りない箇所はフックによる強制——を
配達機構として使う。

## 構成

- `kernel/kernel.md` — 常時規律6種+スキルディスパッチ表+完了ゲート(v2: system prompt 注入)
- `hooks/stop-verify.sh` — Stop フック。フルスイート実行の証拠なしの完了を差し戻す(v2 の核)
- `hooks/session-start.sh` — SessionStart フック(v1 方式のカーネル注入)
- `skills/` — 6 つのプロトコルスキル(deep-insight, spec-first, fresh-verify, long-run, session-memory, grounded-report)
- `agents/` — verifier(fresh-context 敵対的検証者)/ investigator(並列仮説検証者)
- `eval/` — 効果計測ツール(タスク×モデル×harness条件で実行し、5観点rubricで採点)

## インストール

1. `./install.sh` を実行(`npx skills add` で `~/.claude/skills` にスキルをインストールし、agents は `~/.claude/agents` へ symlink)
2. 表示される settings フラグメントを ~/.claude/settings.json にマージ
3. 新しいセッションを開始

このリポジトリのルートから、スキルだけを `npx` で直接インストールする場合:

```bash
npx --yes skills@latest add . \
  --global \
  --agent claude-code \
  --skill '*' \
  --full-depth \
  --yes
```

既存の無関係なスキルは残ります。同名のインストール済みスキルは更新される場合があります。

## アンインストール

fability のスキルを `npx` で削除する場合:

```bash
npx --yes skills@latest remove \
  deep-insight fresh-verify grounded-report long-run session-memory spec-first \
  --global \
  --agent claude-code \
  --yes
```

全スキルを削除したい場合を除き、`--all` や `--skill '*'` は使わないでください。`npx skills remove` は `~/.claude/agents` の symlink や settings の設定行は削除しないため、必要なら別途削除してください。

## 評価の実行

```
./eval/run.sh <task-dir> <model> <off|on|on2> <rep>   # 1条件を実行
python3 eval/grade.py <run-dir>                        # 採点(機械チェック+ブラインドLLM判定)
python3 eval/report.py                                 # 集計とグラフ(report.html)の再生成
./eval/matrix.sh                                       # フルマトリクス
```

`off` = harness なし / `on` = v1(SessionStart 注入) / `on2` = v2(system prompt + Stop フック)

## 設計文書

- 設計: `docs/specs/2026-07-05-fability-design.md`
- 実装計画: `docs/plans/2026-07-05-fability.md`
- 実験結果と診断: `eval/results/summary.ja.md`
