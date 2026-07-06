# fablity

Claude Opus 4.8 上で Claude Fable 5 級の厳密さ・正確性・洞察を引き出す Claude Code 用 harness。

Fablity は、Fable 5 的な規律を明示プロトコル・system prompt 注入・hook 強制に変換し、Opus 4.8 の挙動を Fable 5 に近づけるための harness です。

English version: [README.md](README.md)

```text
                  Fable 5 の行動カタログ
          (Fable が自然に適用しがちな規律)
                                  |
                                  | 明示化
                                  v
  +----------------------------------------------------------------+
  |                            fablity                             |
  |                                                                |
  |  system-prompt kernel     protocol skills      enforcement     |
  |  常時有効な規律          具体的な手順         Stop hook gate   |
  |          |                      |                    |          |
  |          v                      v                    v          |
  |  spec-first / deep       fresh verification     フルスイート   |
  |  insight / memory        verifier agents        証拠なしの     |
  |  grounded reports        long-run protocol      完了を差し戻す |
  +----------------------------------------------------------------+
                                  |
                                  | Opus 4.8 の字義通りの
                                  | 指示追従性を配達機構にする
                                  v
                         Opus 4.8 + harness v2
                                  |
                                  v
               本ベンチマークで Fable 5 級の規律に近づける
```

Fablity は Opus 4.8 を Fable 5 そのものに変えるものではありません。足りない規律を「願望としてのプロンプト」から、Opus 4.8 が忠実に実行しやすい機構へ移します。

## 結果

規律ベンチマーク(4タスク × 5観点rubric × 各条件8実行、Sonnet 5ブラインド判定):

| 条件 | 平均総合 (/10) | sd |
|---|---|---|
| Fable 5(素) | 9.88 | 0.35 |
| Opus 4.8(素) | 8.62 | 1.30 |
| Opus 4.8 + harness v1(プロンプト注入のみ) | 8.88 | 1.46 |
| **Opus 4.8 + harness v2** | **9.88** | **0.35** |

Opus 4.8 + harness v2 は、本ベンチマークにおいて Fable 5 素と同スコア(5観点の平均値まで一致)。詳細な対話型レポートは [`eval/results/report.html`](eval/results/report.html)(英語、要ブラウザ)、文章での分析は [`eval/results/summary.ja.md`](eval/results/summary.ja.md) を参照。

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

GitHub から `npx skills add` で直接インストールします:

```bash
npx --yes skills@latest add NegitoroWarship/fablity \
  --global \
  --agent claude-code \
  --skill fablity \
  --yes
```

これは `fablity` を Claude Code の skills-directory plugin として `~/.claude/skills` にインストールします。plugin には以下が含まれます:

- 6 つのプロトコルスキル
- verifier / investigator agent
- kernel を注入する SessionStart hook
- 完了宣言前のフルスイート検証証拠を強制する Stop hook

既存の無関係なスキルは残ります。同名の `fablity` が既にある場合は更新される場合があります。`--skill fablity` は、個別のプロトコルスキルではなく同梱plugin packageだけを選ぶために指定しています。インストール後、新しい Claude Code セッションを開始するか、既存セッションで `/reload-plugins` を実行してください。

主な harness 動作のために skill を明示的に呼び出す必要はありません。SessionStart hook が kernel を自動注入し、Stop hook が完了宣言前のフルスイート検証を機構的に強制します。

ローカル checkout から入れる場合は、このリポジトリのルートで同じように実行します:

```bash
npx --yes skills@latest add . \
  --global \
  --agent claude-code \
  --skill fablity \
  --yes
```

`./install.sh` は、ローカルの `npx skills add .` を呼ぶ互換 wrapper として残しています。

## アンインストール

fablity を `npx` で削除する場合:

```bash
npx --yes skills@latest remove fablity \
  --global \
  --agent claude-code \
  --yes
```

全スキルを削除したい場合を除き、`--all` や `--skill '*'` は使わないでください。削除後は Claude Code を再起動するか、`/reload-plugins` を実行してください。

古い pre-plugin 版を入れていた場合は、6 つの standalone skill を以下で削除できます:

```bash
npx --yes skills@latest remove \
  deep-insight fresh-verify grounded-report long-run session-memory spec-first \
  --global \
  --agent claude-code \
  --yes
```

## 評価の実行

```
./eval/run.sh <task-dir> <model> <off|on|on2> <rep>   # 1条件を実行
python3 eval/grade.py <run-dir>                        # 採点(機械チェック+ブラインドLLM判定)
python3 eval/report.py                                 # 集計とグラフ(report.html)の再生成
./eval/matrix.sh                                       # フルマトリクス
```

`off` = harness なし / `on` = v1(SessionStart 注入) / `on2` = v2(system prompt + Stop フック)

## 設計文書

- 設計: `docs/specs/2026-07-05-fablity-design.md`
- 実装計画: `docs/plans/2026-07-05-fablity.md`
- 実験結果と診断: `eval/results/summary.ja.md`
