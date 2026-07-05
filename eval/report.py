#!/usr/bin/env python3
"""Generate eval/results/report.html: inline-SVG charts + tables from scores.json files.

Stdlib only. Palette and mark specs follow the dataviz reference instance
(validated: light #2a78d6/#1baf7a/#eda100, dark #3987e5/#199e70/#c98500;
light aqua/yellow are sub-3:1 so values are direct-labeled and a table view exists).
"""
import glob
import html
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONDITIONS = [
    ("claude-fable-5", "h-off", "Fable 5 (素)"),
    ("claude-opus-4-8", "h-off", "Opus 4.8 (素)"),
    ("claude-opus-4-8", "h-on", "Opus 4.8 + harness"),
]
CRITERIA = [
    ("c1", "C1 証拠接地"),
    ("c2", "C2 検証実施"),
    ("c3", "C3 調査先行"),
    ("c4", "C4 スコープ遵守"),
    ("c5", "C5 結果正確性"),
]


def load_runs():
    runs = []
    for p in sorted(glob.glob(str(ROOT / "results" / "*" / "scores.json"))):
        d = json.load(open(p))
        if "haiku" in d["run_id"]:
            continue
        task, model, h, rep = d["run_id"].rsplit("_", 3)
        d.update(task=task, model=model, harness=h, rep=rep)
        runs.append(d)
    return runs


def cond_runs(runs, model, h):
    return [r for r in runs if r["model"] == model and r["harness"] == h]


def fmt(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def bar_path(x, y_top, w, h, r=4):
    """Column with 4px rounded data-end (top), square baseline."""
    if h <= r:
        return f"M{x},{y_top + h} v{-h + r} q0,{-r} {r},{-r} h{w - 2 * r} q{r},0 {r},{r} v{h - r} z"
    return (
        f"M{x},{y_top + h} v{-(h - r)} q0,{-r} {r},{-r} "
        f"h{w - 2 * r} q{r},0 {r},{r} v{h - r} z"
    )


def chart_total(runs):
    """Chart A: mean total per condition (columns) + per-run dots."""
    W, H = 660, 330
    ml, mr, mt, mb = 46, 16, 18, 46
    pw, ph = W - ml - mr, H - mt - mb
    ymax = 10.0

    def sy(v):
        return mt + ph * (1 - v / ymax)

    parts = []
    for g in range(0, 11, 2):
        y = sy(g)
        parts.append(f'<line class="grid" x1="{ml}" y1="{y:.1f}" x2="{ml + pw}" y2="{y:.1f}"/>')
        parts.append(f'<text class="tick" x="{ml - 8}" y="{y + 4:.1f}" text-anchor="end">{g}</text>')
    parts.append(f'<line class="axis" x1="{ml}" y1="{sy(0):.1f}" x2="{ml + pw}" y2="{sy(0):.1f}"/>')

    band = pw / len(CONDITIONS)
    bw = 24
    for i, (model, h, label) in enumerate(CONDITIONS):
        rs = cond_runs(runs, model, h)
        totals = [r["total"] for r in rs]
        mean = sum(totals) / len(totals)
        cx = ml + band * (i + 0.5)
        parts.append(
            f'<path class="s{i + 1} mark" d="{bar_path(cx - bw / 2, sy(mean), bw, ph * mean / ymax)}"'
            f' data-tip="{html.escape(label)}: 平均 {mean:.2f} (n={len(totals)})"/>'
        )
        parts.append(
            f'<text class="vlabel" x="{cx}" y="{sy(mean) - 8:.1f}" text-anchor="middle">{mean:.2f}</text>'
        )
        # per-run dots: beeswarm per distinct value
        counts = {}
        for t in sorted(totals):
            counts.setdefault(t, []).append(t)
        for val, dup in counts.items():
            n = len(dup)
            for j in range(n):
                dx = (j - (n - 1) / 2) * 11
                parts.append(
                    f'<circle class="dot s{i + 1} mark" cx="{cx + dx:.1f}" cy="{sy(val):.1f}" r="4.5"'
                    f' data-tip="{html.escape(label)}: total {val}"/>'
                )
        lines = label.replace(" + ", " +").split(" ", 1)
        parts.append(
            f'<text class="tick" x="{cx}" y="{H - mb + 18}" text-anchor="middle">{html.escape(lines[0])}</text>'
        )
        if len(lines) > 1:
            parts.append(
                f'<text class="tick" x="{cx}" y="{H - mb + 33}" text-anchor="middle">{html.escape(lines[1])}</text>'
            )
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="条件別の平均総合スコアと各実行の分布">{"".join(parts)}</svg>'


def chart_criteria(runs):
    """Chart B: grouped columns, criterion x condition, 0-2 scale."""
    W, H = 660, 300
    ml, mr, mt, mb = 46, 16, 18, 34
    pw, ph = W - ml - mr, H - mt - mb
    ymax = 2.0

    def sy(v):
        return mt + ph * (1 - v / ymax)

    parts = []
    for g in (0, 1, 2):
        y = sy(g)
        parts.append(f'<line class="grid" x1="{ml}" y1="{y:.1f}" x2="{ml + pw}" y2="{y:.1f}"/>')
        parts.append(f'<text class="tick" x="{ml - 8}" y="{y + 4:.1f}" text-anchor="end">{g}</text>')
    parts.append(f'<line class="axis" x1="{ml}" y1="{sy(0):.1f}" x2="{ml + pw}" y2="{sy(0):.1f}"/>')

    band = pw / len(CRITERIA)
    bw, gap = 16, 2
    group_w = bw * 3 + gap * 2
    for gi, (ck, clabel) in enumerate(CRITERIA):
        gx = ml + band * (gi + 0.5) - group_w / 2
        for i, (model, h, label) in enumerate(CONDITIONS):
            rs = cond_runs(runs, model, h)
            vals = [r["scores"][ck] for r in rs]
            mean = sum(vals) / len(vals)
            x = gx + i * (bw + gap)
            parts.append(
                f'<path class="s{i + 1} mark" d="{bar_path(x, sy(mean), bw, ph * mean / ymax)}"'
                f' data-tip="{html.escape(clabel)} — {html.escape(label)}: {mean:.2f}"/>'
            )
        parts.append(
            f'<text class="tick" x="{ml + band * (gi + 0.5):.1f}" y="{H - mb + 18}" text-anchor="middle">{html.escape(clabel)}</text>'
        )
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="観点別平均スコア(条件×C1〜C5)">{"".join(parts)}</svg>'


def stat_tiles(runs):
    tiles = []
    means = {}
    for model, h, label in CONDITIONS:
        totals = [r["total"] for r in cond_runs(runs, model, h)]
        means[(model, h)] = sum(totals) / len(totals)
    for i, (model, h, label) in enumerate(CONDITIONS):
        m = means[(model, h)]
        sd = statistics.stdev([r["total"] for r in cond_runs(runs, model, h)])
        delta = ""
        if (model, h) == ("claude-opus-4-8", "h-off"):
            d = m - means[("claude-fable-5", "h-off")]
            delta = f'<div class="delta neg">{d:+.2f} vs Fable 5</div>'
        elif (model, h) == ("claude-opus-4-8", "h-on"):
            d = m - means[("claude-opus-4-8", "h-off")]
            cls = "pos" if d >= 0 else "neg"
            delta = f'<div class="delta {cls}">{d:+.2f} vs Opus 4.8 素</div>'
        tiles.append(
            f'<div class="tile"><div class="tlabel"><span class="key s{i + 1}bg"></span>{html.escape(label)}</div>'
            f'<div class="tvalue">{m:.2f}<span class="tmax">/10</span></div>'
            f'<div class="tsub">n=8 · sd {sd:.2f}</div>{delta}</div>'
        )
    return '<div class="tiles">' + "".join(tiles) + "</div>"


def task_table(runs):
    tasks = sorted({r["task"] for r in runs})
    head = "<tr><th>タスク</th>" + "".join(
        f'<th><span class="key s{i + 1}bg"></span>{html.escape(l)}</th>' for i, (_, _, l) in enumerate(CONDITIONS)
    ) + "</tr>"
    body = []
    for t in tasks:
        cells = []
        for model, h, _ in CONDITIONS:
            vals = [r["total"] for r in cond_runs(runs, model, h) if r["task"] == t]
            cells.append(f'<td>{fmt(sum(vals) / len(vals))}</td>')
        body.append(f"<tr><th>{html.escape(t)}</th>{''.join(cells)}</tr>")
    return f'<table class="data">{head}{"".join(body)}</table>'


def run_table(runs):
    head = (
        "<tr><th>run</th><th>C1</th><th>C2</th><th>C3</th><th>C4</th><th>C5</th>"
        "<th>total</th><th>verifier</th><th>exec</th></tr>"
    )
    body = []
    for r in sorted(runs, key=lambda r: r["run_id"]):
        s = r["scores"]
        body.append(
            f'<tr><th>{html.escape(r["run_id"])}</th>'
            + "".join(f'<td>{s[c]}</td>' for c in ("c1", "c2", "c3", "c4", "c5"))
            + f'<td><b>{r["total"]}</b></td>'
            f'<td>{"✓" if r["flags"]["verifier_dispatched"] else "—"}</td>'
            f'<td>{"✓" if r["flags"]["ran_execution"] else "—"}</td></tr>'
        )
    return f'<table class="data small">{head}{"".join(body)}</table>'


def legend():
    items = "".join(
        f'<span class="litem"><span class="key s{i + 1}bg"></span>{html.escape(l)}</span>'
        for i, (_, _, l) in enumerate(CONDITIONS)
    )
    return f'<div class="legend">{items}</div>'


CSS = """
.viz-root {
  --surface-1: #fcfcfb; --page: #f9f9f7;
  --ink-1: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --border: rgba(11,11,11,0.10);
  --s1: #2a78d6; --s2: #1baf7a; --s3: #eda100;
  --good: #006300; --bad: #d03b3b;
}
@media (prefers-color-scheme: dark) {
  .viz-root {
    --surface-1: #1a1a19; --page: #0d0d0d;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --border: rgba(255,255,255,0.10);
    --s1: #3987e5; --s2: #199e70; --s3: #c98500;
    --good: #0ca30c; --bad: #d03b3b;
  }
}
.viz-root { font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: var(--page); color: var(--ink-1); margin: 0; padding: 28px;
  line-height: 1.5; }
.viz-root h1 { font-size: 22px; margin: 0 0 4px; }
.viz-root .sub { color: var(--ink-2); margin: 0 0 20px; font-size: 14px; }
.viz-root h2 { font-size: 15px; margin: 26px 0 8px; }
.card { background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 10px; padding: 16px; max-width: 720px; }
.tiles { display: flex; gap: 12px; flex-wrap: wrap; max-width: 720px; }
.tile { background: var(--surface-1); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 18px; flex: 1 1 180px; }
.tlabel { font-size: 13px; color: var(--ink-2); display: flex; align-items: center; gap: 6px; }
.tvalue { font-size: 34px; font-weight: 600; margin-top: 2px; }
.tmax { font-size: 15px; font-weight: 400; color: var(--muted); margin-left: 2px; }
.tsub { font-size: 12px; color: var(--muted); }
.delta { font-size: 13px; font-weight: 600; margin-top: 4px; }
.delta.pos { color: var(--good); } .delta.neg { color: var(--bad); }
svg { width: 100%; height: auto; display: block; }
.grid { stroke: var(--grid); stroke-width: 1; }
.axis { stroke: var(--axis); stroke-width: 1; }
.tick { fill: var(--muted); font-size: 12px; font-variant-numeric: tabular-nums; }
.vlabel { fill: var(--ink-2); font-size: 13px; font-weight: 600; }
.s1 { fill: var(--s1); } .s2 { fill: var(--s2); } .s3 { fill: var(--s3); }
.dot { stroke: var(--surface-1); stroke-width: 2; }
.key { display: inline-block; width: 10px; height: 10px; border-radius: 3px; }
.s1bg { background: var(--s1); } .s2bg { background: var(--s2); } .s3bg { background: var(--s3); }
.legend { display: flex; gap: 16px; margin: 8px 0 12px; font-size: 13px; color: var(--ink-2); }
.litem { display: inline-flex; align-items: center; gap: 6px; }
table.data { border-collapse: collapse; font-size: 14px; width: 100%;
  font-variant-numeric: tabular-nums; }
table.data th, table.data td { text-align: left; padding: 6px 10px;
  border-bottom: 1px solid var(--grid); }
table.data td { color: var(--ink-2); }
table.data th .key { margin-right: 6px; }
table.data.small { font-size: 12px; }
details { max-width: 720px; margin-top: 10px; }
summary { cursor: pointer; color: var(--ink-2); font-size: 14px; }
#tip { position: fixed; pointer-events: none; background: var(--ink-1);
  color: var(--page); font-size: 12px; padding: 5px 9px; border-radius: 6px;
  opacity: 0; transition: opacity 120ms; z-index: 10; }
.note { color: var(--ink-2); font-size: 13px; max-width: 720px; }
"""

JS = """
const tip = document.getElementById('tip');
document.querySelectorAll('.mark').forEach(el => {
  el.addEventListener('mousemove', e => {
    tip.textContent = el.dataset.tip;
    tip.style.left = (e.clientX + 14) + 'px';
    tip.style.top = (e.clientY - 10) + 'px';
    tip.style.opacity = 1;
  });
  el.addEventListener('mouseleave', () => { tip.style.opacity = 0; });
});
"""


def main():
    runs = load_runs()
    assert len(runs) == 24, f"expected 24 runs, got {len(runs)}"
    doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>fable-harness 検証実験レポート</title>
<style>{CSS}</style></head>
<body class="viz-root">
<h1>fable-harness 検証実験</h1>
<p class="sub">3条件 × 4タスク × 2反復 = 24実行 · 採点: Sonnet 5 ブラインド判定 + 機械チェック(rubric 5観点 各0–2点)</p>
{stat_tiles(runs)}
<h2>条件別 平均総合スコア(点は各実行)</h2>
{legend()}
<div class="card">{chart_total(runs)}</div>
<h2>観点別 平均スコア</h2>
{legend()}
<div class="card">{chart_criteria(runs)}</div>
<h2>タスク別 平均総合スコア</h2>
<div class="card">{task_table(runs)}</div>
<details><summary>全24実行の生スコア(テーブルビュー)</summary>
<div class="card">{run_table(runs)}</div></details>
<p class="note">注: n=8/条件・判定LLMの揺らぎがあるため差は参考値。verifier列 = fresh-verify検証エージェントの発動有無(機械検出)。</p>
<div id="tip"></div>
<script>{JS}</script>
</body></html>"""
    out = ROOT / "results" / "report.html"
    out.write_text(doc)
    print(f"wrote {out} ({len(doc)} bytes)")


if __name__ == "__main__":
    main()
