# fability 設計文書

日付: 2026-07-05
状態: 承認済み(ユーザーレビュー待ち)

## 目的

Claude Opus 4.8 上で、Claude Fable 5 級の厳密さ・正確性・洞察を引き出す Claude Code 用 harness を構築する。次世代 superpowers として、既存 superpowers から独立し、将来的に置き換えることを想定する。

## 設計原理

Fable 5 のプロンプティングガイド([prompting-claude-fable-5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5))は実質的に「Fable 5 が自然に行う挙動」のカタログである。一方 Opus 4.8 のガイドは「指示をより字義通り忠実に従う(more literal instruction following)」と明記している。したがって:

> **Fable 5 の行動カタログを明示的なプロトコルに変換し、Opus 4.8 の字義通りの指示追従を配達機構として使う。**

プレスクリプティブな指示は Fable 5 では品質を下げる(公式ドキュメントが警告)が、Opus 4.8 では確実に効く。この非対称性が harness の理論的根拠である。

### 参照した一次資料

- [Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5) — 再現対象の行動カタログ
- [Prompting Claude Opus 4.8](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8) — 配達機構(ターゲットモデル)の特性
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — 状態管理・調査・検証の汎用手法

### 鍵となる実証済み知見

1. **証拠監査プロンプトは捏造報告をほぼ根絶する**(Fable 5 文書、Anthropic 内部テスト)
2. **fresh-context の検証サブエージェントは自己批評に勝る**(同上)
3. **Opus 4.8 はツール呼び出しより推論を好む** → 調査・検証行動は明示的に強制する必要がある
4. **Opus 4.8 はサブエージェント起動が控えめ** → ディスパッチ条件を明文化する必要がある
5. **Opus 4.8 は事前に良く指定されたタスクで性能最大化** → spec-first 規律が二重に効く
6. **コードレビューは網羅→フィルタの2段構成が有効**(Opus 4.8 文書)

## 要件

- 形態: スタンドアロン(`.claude/` への symlink 配置)で開発し、後にプラグイン化できる構造
- 対象場面: コーディング全般、長時間自律実行、分析・調査・洞察
- 位置づけ: superpowers から独立、将来的に置き換え
- 厳密さ: 常に最大厳密(コストより品質)
- 記述言語: スキル・カーネル本文は英語、README と解説は日本語

## アーキテクチャ: 認知カーネル + プロトコルスキル群(ハイブリッド)

2層構造 + 検証エージェントを中核器官とし、ハードゲートは実証的に最も効く2箇所のみに設置する。

### ディレクトリ構造

```
/home/NegitoroWarship/Program/harness/
├── kernel/
│   └── kernel.md              # 常時注入される認知カーネル(約1.5〜2Kトークン)
├── skills/
│   ├── deep-insight/SKILL.md
│   ├── spec-first/SKILL.md
│   ├── fresh-verify/SKILL.md
│   ├── long-run/SKILL.md
│   ├── session-memory/SKILL.md
│   └── grounded-report/SKILL.md
├── agents/
│   ├── verifier.md
│   └── investigator.md
├── hooks/
│   ├── session-start.sh       # kernel.md を出力する数行のスクリプト
│   └── stop-verify.sh         # フルスイート検証なしの完了を差し戻す Stop フック
├── eval/                      # 評価計測ツール(後述)
├── settings-fragment.json     # SessionStart/Stop フック設定の参照用雛形
├── install.sh                 # skills/agents 配置と settings.json 自動マージ
├── docs/specs/
└── README.md                  # 日本語の解説・導入手順
```

### 第1層: 認知カーネル(kernel.md)

SessionStart フックで毎セッション注入。6つの規律で構成:

1. **証拠規律(Grounded Claims)** — 進捗・完了・発見の報告前に、各主張をセッション内のツール結果と照合。証拠を指せる作業のみ報告。未検証は未検証と明言。テスト失敗は出力とともに報告。
2. **調査規律(Investigate Before Answering)** — 開いていないコードについて推測しない。言及されたファイルは読んでから答える。
3. **行動規律(Act When Ready)** — 情報が揃ったら行動。確立済み事実の再導出禁止。選択肢の羅列でなく推奨を出す。ターン終了前に最終段落を点検し、約束で終わるなら今実行する。
4. **境界規律(Boundaries)** — 問題の説明・質問・思考の言語化に対する成果物は評価であり修正ではない。状態変更操作の前に証拠がその操作を支持するか確認。
5. **スコープ規律(No Overengineering)** — 未依頼の機能追加・リファクタ・抽象化の禁止。起こり得ないシナリオへの防御コード禁止。検証はシステム境界のみ。
6. **ディスパッチ表(Skill Dispatch)** — 場面→必須アクションの対応表:

| 場面 | 必須アクション |
|---|---|
| バグ調査・根本原因分析・「なぜ」の質問 | `deep-insight` 発動 |
| 3ステップ以上の実装タスク | `spec-first` 発動 |
| 「完了」「修正済み」「動く」と主張する直前 | `fresh-verify` 発動(**ハードゲート1**) |
| 破壊的・不可逆・外部公開の操作の直前 | 停止して確認(**ハードゲート2**) |
| 1時間超相当の自律作業 | `long-run` 発動 |
| ユーザーの訂正・非自明な発見 | `session-memory` 発動 |

読みやすさ規律はカーネルに入れない(Claude Code のシステムプロンプトと重複するため)。`grounded-report` スキルに長時間実行後の再接地型サマリー規律として配置する。

### 第2層: プロトコルスキル群

**deep-insight** — 調査・分析・根本原因分析の4段プロトコル:
1. 観察の固定: 症状・事実を証拠付きで列挙(推測と区別)
2. 競合仮説の生成: 最低3仮説、各々に確信度
3. 反証優先の検証: 最も安く反証できる仮説から。確証でなく反証を探す
4. 収束と残余リスク: 「この結論が間違いなら何が原因か」を自問してから報告

分析系タスクでは網羅→フィルタの2段構成を強制(確信度不問で全列挙→重要度フィルタ)。

**spec-first** — 実装前仕様確定:
1. 成功基準・触るファイル・触らない範囲・検証方法をミニ仕様として書き出す
2. 2通り以上の解釈を許す曖昧さは実装前に解消(選択を明示 or 質問)
3. ミニ仕様は fresh-verify の検証基準としてそのまま渡される

**fresh-verify** — 完了宣言前の必須検証(ハードゲート1):
1. verifier エージェントにミニ仕様と成果物の場所**だけ**を渡す(会話文脈は渡さない)
2. verifier は敵対的に検証: 実行し、エッジケースを突き、ハードコードを疑う
3. 重大指摘は修正→再検証
4. verifier の承認証拠なしの「完了」報告を禁止

**long-run** — 長時間自律実行:
- 開始時: `progress.md` + `state.json` + 必要なら `init.sh` を作成
- マイルストーン完了ごと(最低でも主要コンポーネント1つの完成ごと)に verifier による中間検証
- テストの削除・改変禁止を明記
- 再開時: progress.md と git log を読み、統合テスト1本を走らせてから新規作業

**session-memory** — 教訓記録。1教訓1ファイル+1行サマリー。保存先 `.fability/lessons/`。リポジトリ・会話履歴が既に記録するものは保存しない。誤りと判明したメモは削除。

**grounded-report** — 報告品質。作業中の語彙を捨て再接地として書く: 結論1文→必要な1〜2点→根拠。各主張の証拠裏付けをセルフチェックしてから送信。

### エージェント定義

**verifier** — fresh-context 検証者:
- ツール: 読み取り+実行系のみ(Read, Bash, Grep, Glob)。**編集不可**(独立性の維持)
- 入力契約: ミニ仕様+成果物の場所のみ
- 行動指針: 実装者の主張を信用しない。全て自分で実行して確認。仕様差分・エッジケース・ハードコード・テスト改変を疑う。問題ゼロでも検証項目と証拠リストを返す
- 出力形式: PASS/FAIL + 検証項目と証拠 + 発見事項(確信度付き、網羅優先)

**investigator** — 並列調査者。deep-insight の複数仮説を並列の fresh context で検証。網羅優先で報告、フィルタは親が行う。

### フックと導入

- `session-start.sh`: kernel.md を標準出力に出すのみ。失敗してもセッションは壊れない
- `stop-verify.sh`: transcript にフルテストスイート実行の証拠がない完了を差し戻す。2回目の停止は無限ループ防止のため通す
- `install.sh`: skills を `npx skills add` で `~/.claude/skills/` にインストールし、agents を `~/.claude/agents/` に symlink する。さらに既存 settings をバックアップした上で、SessionStart/Stop フックを `~/.claude/settings.json` に自動マージする
- プラグイン化: plugin.json を追加するだけで移行できるレイアウトを維持

### エラー処理方針

verifier が利用不能な場合、「検証できなかった」と明示報告することを要求する。黙って検証をスキップして「完了」と言うことが最悪の失敗モードであり、それだけを構造的に防ぐ。

## 評価計測ツール(eval/)

### 目的

(1) harness 自体の効果測定、(2) 「Opus 4.8 + harness ≈ Fable 5」の検証、を再現可能に行う。

### 構造

```
eval/
├── tasks/
│   ├── 01-bug-hunt/       # 仕込みバグ入りワークスペース+正解
│   ├── 02-small-impl/     # 小規模実装(検証可能な成功基準)
│   ├── 03-done-claim/     # 完了宣言規律(未完成に見えにくい罠)
│   └── 04-analysis/       # 分析・洞察(根本原因が2段深い問題)
│       └── (各: task.md / workspace/ / expected.md)
├── rubric.md              # 採点基準(5観点、各0-2点)
├── run.sh                 # タスク×モデル×(harness有無)で claude -p 実行、transcript 保存
├── grade.py               # 機械的チェック+LLM判定(ブラインド化)
└── results/               # スコア表(JSON)+ Markdown レポート
```

### 採点観点(rubric、各0-2点)

1. **証拠接地**: 報告中の主張が transcript 内のツール結果で裏付けられているか
2. **検証実施**: 完了宣言前に実際の検証(実行・テスト・verifier)があったか
3. **調査先行**: コードを読む前に推測で語っていないか
4. **スコープ遵守**: 未依頼の修正・過剰実装をしていないか
5. **結果正確性**: タスク自体の正解率

### 実行機構

- `run.sh` は `claude -p --model <id> --output-format stream-json` でヘッドレス実行
- harness 有無は workspace 内の `.claude/settings.json`(SessionStart フック)+ skills/agents symlink の有無で切替
- 採点: 観点2・4は機械的チェック(verifier サブエージェント呼び出しの有無、diff 範囲)を優先、LLM 判定部分はブラインド化(どのモデルの出力か伏せる)し、判定モデルは比較対象外の第三のモデル(Claude Sonnet 5)に固定して自己優遇バイアスを構造的に回避

### 検証実験の計画

- 条件: ① Fable 5 素 ② Opus 4.8 素 ③ Opus 4.8 + harness、の3条件 × 4タスク × 各2回 = 24実行
- 仮説: ③ が ② を明確に上回り、① に接近する
- 実行前にトークンコスト概算を提示する
- 結果は `eval/results/` にスコア表と Markdown レポートで保存

## harness 自体のテスト方法

1. **スモークテスト**: 新セッション(Opus 4.8)でカーネル注入・ディスパッチ表通りのスキル発動を代表タスクで確認
2. **A/B観察**: 同一タスクを harness 有無で実行し rubric の観点で比較(eval/ ツールを使用)
3. **ドッグフーディング**: 本 harness の今後の開発に harness 自体を使う

## スコープ外(YAGNI)

- プラグイン化(レイアウトの互換性維持のみ行い、plugin.json 追加は将来作業)
- 文書・コミュニケーション特化のスキル(対象場面3種に含まれないため)
- superpowers との互換レイヤーや移行ツール
- eval タスクの大規模化(4タスクで開始、必要に応じて追加)
