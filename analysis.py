#!/usr/bin/env python3
"""Numbers for the paper: every table, figure and in-text number of paper/paper.tex is computed here.

Reads the per-run results written by `experiment.py --study main report` (results/main/*/results.csv), their
pricing snapshots and attempt logs, and the frozen main-study manifest. Writes paper/generated/numbers.tex
(number macros), paper/generated/tab_*.tex (tables), paper/generated/stats.json and paper/figures/*.pdf.
Offline: no API requests.

    .venv/bin/python analysis.py
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / "results" / "main"
PREP = ROOT / "data" / "prepared_main"
RAW = ROOT / "data" / "raw" / "jit_bug_prediction_splits" / "time" / "test.parquet.gzip"  # the Defectors split
OUT = ROOT / "paper" / "generated"
FIGS = ROOT / "paper" / "figures"
RISKY = "RISKY"
BOOT = 10_000  # paired bootstrap resamples over cases
SEED = 20261118

# run key -> (folder under results/main, model, provider, role)
RUNS = {
    "gv": ("gemini-2.5-flash-lite", "Gemini 2.5 Flash-Lite", "Google Vertex", "main run, all six levels"),
    "ga1": ("gemini-2.5-flash-lite_ai-studio", "Gemini 2.5 Flash-Lite", "Google AI Studio", "S0-S4 + N2"),
    "ga2": ("gemini-2.5-flash-lite_ai-studio_rep2", "Gemini 2.5 Flash-Lite", "Google AI Studio", "repeat of S0, S2"),
    "h1": ("claude-haiku-4.5", "Claude Haiku 4.5", "Anthropic", "S0-S4 + N2"),
    "h2": ("claude-haiku-4.5_rep2", "Claude Haiku 4.5", "Anthropic", "repeat of S0, S2"),
    # second round of follow-ups (Nov 20, 2026): M0 for ga1/h1 (same folders), two more models
    "s1": ("claude-sonnet-4.6", "Claude Sonnet 4.6", "Anthropic", "S0-S4 + N2 + M0"),
    "s2": ("claude-sonnet-4.6_rep2", "Claude Sonnet 4.6", "Anthropic", "repeat of S0, S2"),
    "q1": ("qwen3.8-flash", "Qwen3.8 Flash", "Alibaba", "S0-S4 + N2 + M0"),
    "q2": ("qwen3.8-flash_rep2", "Qwen3.8 Flash", "Alibaba", "repeat of S0, S2"),
}
ROUND2 = "2026-11-20"  # attempts from this date on belong to the second round (M0, Sonnet, Qwen)
LEVEL = {"S0": "Diff", "S1": "Function", "S2": "File", "S3": "Callers", "S4": "Callees", "S5": "Repository",
         "N2": "Unrelated code", "M0": "Commit message", "C0": "Rest of commit", "J0": "Whole commit"}
# names shown in the paper; the codes stay internal. C0: diff + the commit's other files, question about the file.
# J0: the whole commit, question about the commit.
CONTEXT = ("S0", "S1", "S2", "S3", "S4", "S5")
# chart tokens (dataviz reference palette, light surface; validated with validate_palette.js)
SURFACE, INK, INK2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {"gv": "#2a78d6", "h1": "#eb6834", "ga1": "#2a78d6", "s1": "#1baf7a", "q1": "#eda100"}
MARKER = {"gv": "o", "h1": "s", "ga1": "o", "s1": "^", "q1": "D"}
PREFIX = {"gv": "gv", "ga1": "ga", "h1": "h", "s1": "s", "q1": "q"}  # macro prefix per run
MODEL_KEY = {"Gemini": "gv", "Haiku": "h1", "Sonnet": "s1", "Qwen": "q1"}  # figure series per model name


# --------------------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------------------
def mcc_from(tp, fp, tn, fn):
    tp, fp, tn, fn = (np.asarray(v, dtype=float) for v in (tp, fp, tn, fn))
    den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return np.where(den > 0, (tp * tn - fp * fn) / np.where(den > 0, den, 1.0), 0.0)


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    tp, fp = int((y & p).sum()), int((~y & p).sum())
    tn, fn = int((~y & ~p).sum()), int((y & ~p).sum())
    n = len(y)
    return {"n": n, "tp": tp, "fp": fp, "tn": tn, "fn": fn, "acc": (tp + tn) / n,
            "mcc": float(mcc_from(tp, fp, tn, fn)), "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else math.nan,
            "precision": tp / (tp + fp) if tp + fp else math.nan, "recall": tp / (tp + fn) if tp + fn else math.nan,
            "pos_rate": (tp + fp) / n}


def bootstrap(y: np.ndarray, preds: dict, base: str | None = "S0") -> dict:
    """Paired percentile bootstrap over cases: 95% CIs of accuracy and MCC, and of their differences to `base`."""
    n = len(y)
    idx = np.random.default_rng(SEED).integers(0, n, size=(BOOT, n))
    Y = y[idx]
    draws = {}
    for s, p in preds.items():
        P = p[idx]
        tp, fp, tn, fn = (Y & P).sum(1), (~Y & P).sum(1), (~Y & ~P).sum(1), (Y & ~P).sum(1)
        draws[s] = {"acc": (tp + tn) / n, "mcc": mcc_from(tp, fp, tn, fn)}
    ci = {}
    for s in preds:
        ci[s] = {m: np.percentile(draws[s][m], [2.5, 97.5]).tolist() for m in ("acc", "mcc")}
        if base in preds and s != base:
            ci[s].update({f"d_{m}": np.percentile(draws[s][m] - draws[base][m], [2.5, 97.5]).tolist()
                          for m in ("acc", "mcc")})
    return ci


def mcnemar(ca: np.ndarray, cb: np.ndarray) -> tuple[int, int, float]:
    """Exact two-sided McNemar test on per-case correctness: (fixed by b, broken by b, p)."""
    fixed, broken = int((~ca & cb).sum()), int((ca & ~cb).sum())
    m = fixed + broken
    p = 1.0 if m == 0 else min(1.0, 2 * sum(math.comb(m, i) for i in range(min(fixed, broken) + 1)) / 2 ** m)
    return fixed, broken, p


def holm(ps: dict) -> dict:
    out, running = {}, 0.0
    for i, (k, p) in enumerate(sorted(ps.items(), key=lambda kv: kv[1])):
        running = max(running, min(1.0, (len(ps) - i) * p))
        out[k] = running
    return out


def chi2_sf(x: float, k: int) -> float:
    """Upper tail of the chi-square distribution for integer degrees of freedom (closed forms)."""
    if x <= 0:
        return 1.0
    h = x / 2
    if k % 2 == 0:
        return math.exp(-h) * sum(h ** i / math.factorial(i) for i in range(k // 2))
    return math.erfc(math.sqrt(h)) + sum(math.exp(-h) * h ** (i - 0.5) / math.gamma(i + 0.5)
                                         for i in range(1, (k + 1) // 2))


def cochran_q(correct: np.ndarray) -> tuple[float, int, float]:
    """Cochran's Q over k paired binary outcomes (cases x levels)."""
    k = correct.shape[1]
    col, row, tot = correct.sum(0), correct.sum(1), correct.sum()
    den = k * tot - (row ** 2).sum()
    q = (k - 1) * (k * (col ** 2).sum() - tot ** 2) / den if den else 0.0
    return float(q), k - 1, chi2_sf(float(q), k - 1)


def kappa(a: np.ndarray, b: np.ndarray) -> float:
    po = float((a == b).mean())
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def perm_groups(a: np.ndarray, b: np.ndarray) -> float:
    """Two-sided permutation test of the difference between the means of two groups of cases."""
    if not len(a) or not len(b):
        return math.nan
    both, n = np.concatenate([a, b]), len(a)
    order = np.argsort(np.random.default_rng(SEED).random((BOOT, len(both))), axis=1)
    d = np.abs(both[order][:, :n].mean(1) - both[order][:, n:].mean(1))
    return float((1 + int((d >= abs(a.mean() - b.mean()) - 1e-12).sum())) / (BOOT + 1))


# --------------------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------------------
def load_run(key: str) -> dict | None:
    d = MAIN / RUNS[key][0]
    if not (d / "results.csv").exists():
        return None
    res = pd.read_csv(d / "results.csv")
    pricing = json.loads((d / "pricing_snapshot.json").read_text())
    res["list_cost"] = (res.prompt_tokens * pricing["price_prompt_per_token"]
                        + res.completion_tokens * pricing["price_completion_per_token"])
    attempts = [json.loads(line) for line in (d / "attempts.jsonl").read_text().splitlines() if line.strip()]
    return {"key": key, "res": res, "pricing": pricing, "attempts": attempts,
            "levels": tuple(s for s in LEVEL if s in set(res.strategy[res.status != "not_run"]))}


def paired(run: dict, levels) -> tuple[list, np.ndarray, dict, pd.DataFrame]:
    """Cases with a valid prediction at every level in `levels`: ids, truth, predictions, rows."""
    r = run["res"]
    ok = r[(r.status == "ok") & r.strategy.isin(levels)]
    ids = sorted(set.intersection(*(set(ok[ok.strategy == s].sample_id) for s in levels)))
    sub = ok[ok.sample_id.isin(ids)]
    by = {s: sub[sub.strategy == s].set_index("sample_id").loc[ids] for s in levels}
    y = by[levels[0]].reference_label.eq(RISKY).to_numpy(dtype=bool)
    preds = {s: by[s].predicted_label.eq(RISKY).to_numpy(dtype=bool) for s in levels}
    return ids, y, preds, sub


def lines_added(sample_id: str) -> int:
    diff = (PREP / "cases" / sample_id / "diff.txt").read_text(encoding="utf-8")
    return sum(1 for ln in diff.splitlines() if ln.startswith("+") and not ln.startswith("+++"))


# --------------------------------------------------------------------------------------
# formatting
# --------------------------------------------------------------------------------------
def f2(x) -> str:
    return "--" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.2f}"


def fp(p: float) -> str:
    return "$<$0.001" if p < 0.001 else f"{p:.3f}" if p < 0.01 else f"{p:.2f}"


def pct(x: float) -> str:
    return f"{100 * x:.0f}\\%"


def pct1(x: float) -> str:
    """Percent without the sign; one decimal below 10%."""
    v = 100 * x
    return "0" if v == 0 else f"{v:.1f}" if v < 10 else f"{v:.0f}"


def usd_k(x: float) -> str:
    """USD per 1,000 predictions."""
    v = 1000 * x
    return f"{v:,.3f}" if v < 0.1 else f"{v:,.2f}" if v < 100 else f"{v:,.0f}"


def ci(lo_hi, signed=False) -> str:
    lo, hi = lo_hi
    return f"[${lo:+.2f}$, ${hi:+.2f}$]" if signed else f"[{lo:.2f}, {hi:.2f}]"


class Numbers:
    """In-text numbers as LaTeX macros: \\num{key} (undefined keys are a LaTeX error, never silently empty)."""

    def __init__(self):
        self.d = {}

    def __setitem__(self, k, v):
        self.d[k] = str(v)

    def write(self, path: Path):
        lines = ["% generated by analysis.py - do not edit",
                 "\\makeatletter",
                 "\\newcommand{\\num}[1]{\\ifcsname num@#1\\endcsname\\csname num@#1\\endcsname"
                 "\\else\\PackageError{numbers}{undefined number #1}{}\\fi}"]
        lines += [f"\\expandafter\\def\\csname num@{k}\\endcsname{{{v}}}" for k, v in sorted(self.d.items())]
        lines += ["\\makeatother", ""]
        path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------------------
# analyses
# --------------------------------------------------------------------------------------
def level_table(run: dict, levels, la_thr: float) -> dict:
    """Per-level metrics on the paired set, CIs, McNemar vs S0 (Holm), Cochran's Q, cost, baselines."""
    ids, y, preds, sub = paired(run, levels)
    boot = bootstrap(y, preds)
    rows, raw_p = {}, {}
    for s in levels:
        m = metrics(y, preds[s])
        g = sub[sub.strategy == s]
        m.update(tokens=float(g.prompt_tokens.mean()), out_tokens=float(g.completion_tokens.mean()),
                 cost=float(g.list_cost.mean()), latency=float(g.latency_s.mean()), ci=boot[s])
        if s != "S0":
            m["fixed"], m["broken"], raw_p[s] = mcnemar(preds["S0"] == y, preds[s] == y)
        rows[s] = m
    for s, p in holm(raw_p).items():
        rows[s].update(p=raw_p[s], p_holm=p)
    q, df, pq = cochran_q(np.column_stack([preds[s] == y for s in levels]).astype(int))
    la = np.array([lines_added(i) for i in ids])
    base = {"always": metrics(y, np.ones_like(y)), "la": metrics(y, la > la_thr)}
    for s in levels:
        rows[s]["x_cost"] = rows[s]["cost"] / rows["S0"]["cost"]
    ctx = [s for s in levels if s in CONTEXT]
    for s in levels:  # Pareto on accuracy vs list-price cost, among context levels
        r = rows[s]
        rows[s]["pareto"] = s in ctx and not any(
            rows[o]["acc"] >= r["acc"] and rows[o]["cost"] <= r["cost"] and (rows[o]["acc"] > r["acc"] or rows[o]["cost"] < r["cost"])
            for o in ctx if o != s)
    return {"ids": ids, "n": len(ids), "n_risky": int(y.sum()), "rows": rows, "q": q, "q_df": df, "q_p": pq,
            "baselines": base, "levels": list(levels)}


def agreement(ra: dict, rb: dict, la: str, lb: str, cases=None) -> dict:
    """Label agreement between two (run, level) conditions on the cases valid in both."""
    a = ra["res"][(ra["res"].strategy == la) & (ra["res"].status == "ok")].set_index("sample_id")
    b = rb["res"][(rb["res"].strategy == lb) & (rb["res"].status == "ok")].set_index("sample_id")
    ids = sorted(set(a.index) & set(b.index) & (set(cases) if cases is not None else set(a.index)))
    pa = a.loc[ids].predicted_label.eq(RISKY).to_numpy(dtype=bool)
    pb = b.loc[ids].predicted_label.eq(RISKY).to_numpy(dtype=bool)
    y = a.loc[ids].reference_label.eq(RISKY).to_numpy(dtype=bool)
    fixed, broken, p = mcnemar(pa == y, pb == y)
    return {"n": len(ids), "same": float((pa == pb).mean()) if ids else math.nan, "flips": int((pa != pb).sum()),
            "kappa": kappa(pa, pb) if ids else math.nan, "acc_a": float((pa == y).mean()) if ids else math.nan,
            "acc_b": float((pb == y).mean()) if ids else math.nan, "p": p}


def labels(run: dict, level: str) -> pd.DataFrame:
    """Valid predictions of one level: sample_id -> (predicted RISKY, correct)."""
    r = run["res"]
    g = r[(r.strategy == level) & (r.status == "ok")].set_index("sample_id")
    return pd.DataFrame({"pred": g.predicted_label.eq(RISKY), "correct": g.predicted_label == g.reference_label})


def flips_vs_rerun(r1: dict, r2: dict, level: str) -> dict:
    """Does `level` change more S0 labels than an identical re-run of S0 does? Per case: x = label differs between
    S0 and `level` (run 1), z = label differs between S0 run 1 and S0 run 2; exact McNemar test on (x, z)."""
    a, b, c = labels(r1, "S0"), labels(r1, level), labels(r2, "S0")
    ids = sorted(set(a.index) & set(b.index) & set(c.index))
    x = (a.loc[ids].pred != b.loc[ids].pred).to_numpy()
    z = (a.loc[ids].pred != c.loc[ids].pred).to_numpy()
    only_ctx, only_rep, p = mcnemar(~x, ~z)  # "correct" = label unchanged; discordant pairs are x-only / z-only
    return {"n": len(ids), "ctx": int(x.sum()), "rep": int(z.sum()), "only_ctx": only_ctx, "only_rep": only_rep, "p": p}


def pooled(runs: dict, keys: list, level: str, rng_seed: int = SEED) -> dict:
    """Accuracy change of `level` against S0, averaged over models, on the cases valid for every model at both
    levels. Per case d_i = mean over models of (correct at level - correct at S0). 95% bootstrap CI over cases and a
    two-sided sign-flip permutation test of mean d = 0 (cases are the unit; models share cases)."""
    tabs = {k: (labels(runs[k], "S0"), labels(runs[k], level)) for k in keys}
    ids = sorted(set.intersection(*(set(a.index) & set(b.index) for a, b in tabs.values())))
    d = np.mean([(tabs[k][1].loc[ids].correct.to_numpy(dtype=float) - tabs[k][0].loc[ids].correct.to_numpy(dtype=float))
                 for k in keys], axis=0)
    rng = np.random.default_rng(rng_seed)
    boot = d[rng.integers(0, len(d), size=(BOOT, len(d)))].mean(1)
    signs = rng.choice([-1.0, 1.0], size=(BOOT, len(d)))
    perm = np.abs((signs * d).mean(1))
    p = (1 + int((perm >= abs(d.mean()) - 1e-12).sum())) / (BOOT + 1)
    return {"n": len(ids), "models": len(keys), "d": float(d.mean()),
            "ci": np.percentile(boot, [2.5, 97.5]).tolist(), "p": p}


def charged(run: dict) -> tuple[float, int]:
    att = run["attempts"]
    return sum(a["cost_usd"] for a in att if a.get("cost_usd") is not None), len(att)


# --------------------------------------------------------------------------------------
# figures (matplotlib; static print figures, light surface)
# --------------------------------------------------------------------------------------
def _axes_style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=INK2, labelsize=7.5, width=0.8, color=AXIS)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def fig_accuracy(tables: dict, la_acc: float, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(3.45, 2.2))
    fig.patch.set_facecolor(SURFACE)
    _axes_style(ax)
    xs = {s: i for i, s in enumerate(CONTEXT)}
    keys = list(tables)
    offs = {k: (i - (len(keys) - 1) / 2) * (0.5 / max(len(keys), 2)) for i, k in enumerate(keys)}
    for key, t in tables.items():
        lv = [s for s in t["levels"] if s in CONTEXT]
        x = np.array([xs[s] + offs[key] for s in lv])
        acc = np.array([t["rows"][s]["acc"] for s in lv])
        lo = np.array([t["rows"][s]["ci"]["acc"][0] for s in lv])
        hi = np.array([t["rows"][s]["ci"]["acc"][1] for s in lv])
        ax.errorbar(x, acc, yerr=[acc - lo, hi - acc], fmt="none", ecolor=SERIES[key], elinewidth=1.2, capsize=0,
                    zorder=2)
        ax.scatter(x, acc, s=26, marker=MARKER[key], color=SERIES[key], edgecolor=SURFACE, linewidth=1.2, zorder=3,
                   label=f"{RUNS[key][1]} (n = {t['n']})")
    ax.axhline(0.5, color=MUTED, linewidth=0.8, zorder=1)
    ax.axhline(la_acc, color=MUTED, linewidth=0.8, linestyle=(0, (3, 2)), zorder=1)
    edge = matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(1.01, 0.5, "chance", color=INK2, fontsize=6.5, va="center", ha="left", transform=edge)
    ax.text(1.01, la_acc, "lines-added\nrule", color=INK2, fontsize=6.5, va="center", ha="left",
            linespacing=0.95, transform=edge)
    ax.set_xticks(range(len(CONTEXT)), [LEVEL[s] for s in CONTEXT], fontsize=6.5)
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(0.3, 0.8)
    ax.set_ylabel("Accuracy (95% CI)", color=INK2, fontsize=7.5)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=6.5, labelcolor=INK,
              handletextpad=0.3, borderaxespad=0.2, ncol=2 if len(tables) > 2 else 1, columnspacing=0.8)
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def fig_cost(tables: dict, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(3.45, 2.05))
    fig.patch.set_facecolor(SURFACE)
    _axes_style(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    points = []  # (cost, acc, label): only the two ends of the cost range are named, the rest is in the table
    for key, t in tables.items():
        lv = [s for s in t["levels"] if s in CONTEXT]
        cost = np.array([1000 * t["rows"][s]["cost"] for s in lv])
        acc = np.array([t["rows"][s]["acc"] for s in lv])
        ax.scatter(cost, acc, s=26, marker=MARKER[key], color=SERIES[key], edgecolor=SURFACE, linewidth=1.2,
                   zorder=3, label=RUNS[key][1])
        points += [(c, a, LEVEL[s].lower() if s in ("S0", "S5") else "") for s, c, a in zip(lv, cost, acc)]
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"${v:g}"))
    ax.set_xlabel("List-price cost per 1,000 predictions (USD, log scale)", color=INK2, fontsize=7.5)
    ax.set_ylabel("Accuracy", color=INK2, fontsize=7.5)
    accs = [t["rows"][s]["acc"] for t in tables.values() for s in t["levels"] if s in CONTEXT]
    ax.set_ylim(min(0.45, min(accs) - 0.03), max(0.68, max(accs) + 0.06))
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=6.5, labelcolor=INK,
              handletextpad=0.3, borderaxespad=0.2, ncol=2 if len(tables) > 2 else 1, columnspacing=0.8)
    _place_labels(fig, ax, points)
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def fig_flips(rows: list, path: Path):
    """Share of labels that differ between two conditions, one row per comparison, one marker per model."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(3.0, 0.23 * len(rows) + 0.55))  # the row labels add about 0.5 in on the left
    fig.patch.set_facecolor(SURFACE)
    _axes_style(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ys = np.arange(len(rows))[::-1]
    present = [k for k in ("gv", "h1", "s1", "q1") if any(k in v for _, v in rows)]
    for i, key in enumerate(present):
        name = RUNS[key][1]
        # a small vertical offset per model, so equal values (e.g. both 8.6%) never hide each other
        dy = 0.3 * ((len(present) - 1) / 2 - i) / max(len(present) - 1, 1)
        pts = [(100 * vals[key], y + (dy if len(vals) > 1 else 0)) for (label, vals), y in zip(rows, ys) if key in vals]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=26, marker=MARKER[key], color=SERIES[key],
                   edgecolor=SURFACE, linewidth=1.2, zorder=3, label=name)
    ax.set_yticks(ys, [r[0] for r in rows], fontsize=6.5)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-1.5, 50)
    ax.set_xticks(range(0, 51, 10))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    ax.set_xlabel("Predictions that differ between the two requests", color=INK2, fontsize=7.5)
    ax.legend(loc="upper right", frameon=False, fontsize=6.5, labelcolor=INK, handletextpad=0.3, borderaxespad=0.2)
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def _place_labels(fig, ax, points):
    """Direct labels beside markers: for each point, the candidate offset with the least overlap with markers,
    labels already placed and the legend (greedy, deterministic)."""
    import matplotlib
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    axbox = ax.get_window_extent(rend)
    blocked = [ax.get_legend().get_window_extent(rend)] if ax.get_legend() else []
    first_marker = len(blocked)
    for c, a, _ in points:
        x, y = ax.transData.transform((c, a))
        blocked.append(matplotlib.transforms.Bbox.from_extents(x - 5, y - 5, x + 5, y + 5))
    dirs = [(0, 1, "center", "bottom"), (0, -1, "center", "top"), (1, 0, "left", "center"), (-1, 0, "right", "center"),
            (.8, .8, "left", "bottom"), (.8, -.8, "left", "top"), (-.8, .8, "right", "bottom"),
            (-.8, -.8, "right", "top")]

    def overlap(p, q):
        return max(0, min(p.x1, q.x1) - max(p.x0, q.x0)) * max(0, min(p.y1, q.y1) - max(p.y0, q.y0))

    for i, (c, a, text) in enumerate(points):
        if not text:  # unnamed point: its marker still blocks the labels of the others
            continue
        best = None
        for rad in (5, 9):
            for dx, dy, ha, va in dirs:
                kw = dict(xytext=(dx * rad, dy * rad), textcoords="offset points", ha=ha, va=va, fontsize=6.5,
                          color=INK)
                ann = ax.annotate(text, (c, a), **kw)
                bb = ann.get_window_extent(rend)
                ann.remove()
                inside = axbox.x0 <= bb.x0 and bb.x1 <= axbox.x1 and axbox.y0 <= bb.y0 and bb.y1 <= axbox.y1
                cost = sum(overlap(bb, o) for j, o in enumerate(blocked) if j != first_marker + i) \
                    + (0 if inside else 1e6)
                if best is None or cost < best[0]:
                    best = (cost, kw, bb)
            if best[0] == 0:
                break
        ax.annotate(text, (c, a), **best[1])
        blocked.append(best[2])


# --------------------------------------------------------------------------------------
# LaTeX tables
# --------------------------------------------------------------------------------------
GROUPS = ("blamed", "inherited", "nonrisky")  # audit groups of the sampled files (by the dataset's links + blame)
SHORT = {"gv": ("Gemini 2.5", "Flash-Lite", "Vertex"), "ga1": ("Gemini 2.5", "Flash-Lite", "AI Studio"),
         "h1": ("Claude", "Haiku 4.5", "Anthropic"), "s1": ("Claude", "Sonnet 4.6", "Anthropic"),
         "q1": ("Qwen3.8", "Flash", "Alibaba")}


def tex_main_table(tables: dict) -> str:
    """Two columns wide. Per model: one row per context, then the lines-added rule, which uses no model."""
    L = ["% generated by analysis.py - do not edit",
         "\\begin{tabular}{@{}l l r r l r r r r@{}}", "\\toprule",
         "Model & Context & Input tokens & Cost (\\$) & Accuracy [95\\% CI] & MCC & F1 & Predicted risky & $p$ \\\\",
         "\\midrule"]
    for j, (key, t) in enumerate(tables.items()):
        if j:
            L.append("\\midrule")
        lv = [s for s in t["levels"] if s in CONTEXT]
        a, b, _ = SHORT[key]
        for i, s in enumerate(lv):
            r = t["rows"][s]
            head = (f"\\multirow{{{len(lv) + 1}}}{{*}}{{\\shortstack[l]{{{a}\\\\{b}\\\\$n={t['n']}$}}}}" if i == 0 else "")
            acc = f"\\textbf{{{f2(r['acc'])}}}" if r["acc"] == max(t["rows"][x]["acc"] for x in lv) else f2(r["acc"])
            L.append(f"{head} & {LEVEL[s]} & {r['tokens']:,.0f} & {usd_k(r['cost'])} & {acc} {ci(r['ci']['acc'])} & "
                     f"{f2(r['mcc'])} & {f2(r['f1'])} & {pct(r['pos_rate'])} & "
                     f"{fp(r['p_holm']) if s != 'S0' else '--'} \\\\")
        for name, bl in (("Lines-added rule", t["baselines"]["la"]),):
            L.append(f" & \\textit{{{name}}} & -- & 0 & {f2(bl['acc'])} & {f2(bl['mcc'])} & {f2(bl['f1'])} & "
                     f"{pct(bl['pos_rate'])} & -- \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


MODEL_SHORT = {"gv": "Gemini", "ga1": "Gemini", "h1": "Haiku", "s1": "Sonnet", "q1": "Qwen"}


def tex_control_table(ctrl: dict) -> str:
    """One column wide: the model is a group row, not a column."""
    L = ["% generated by analysis.py - do not edit",
         "\\begin{tabular}{@{}l l r r r@{}}", "\\toprule",
         "Prompt & Accuracy [95\\% CI] & \\shortstack[r]{Predicted\\\\risky} & Changed & $p$ \\\\", "\\midrule"]
    names = {"S0": "Diff alone", "S2": "+ file", "N2": "+ unrelated code"}
    for j, (key, c) in enumerate(ctrl.items()):
        L.append(("\\addlinespace[3pt]" if j else "") +
                 f"\\multicolumn{{5}}{{@{{}}l}}{{\\textit{{{MODEL_SHORT[key]} ($n={c['n']}$)}}}} \\\\")
        for s in ("S0", "S2", "N2"):
            r = c["rows"][s]
            same = "--" if s == "S0" else f"{pct1(1 - c['same_as_s0'][s])}\\%"
            L.append(f"{names[s]} & {f2(r['acc'])} {ci(r['ci']['acc'])} & {pct(r['pos_rate'])} & "
                     f"{same} & {'--' if s == 'S0' else fp(r['p'])} \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def tex_message_table(msg: dict, base: dict) -> str:
    """Diff with and without the commit message, per model (one column wide); the message-length rule as last row."""
    L = ["% generated by analysis.py - do not edit",
         "\\begin{tabular}{@{}l r r l r r@{}}", "\\toprule",
         "Model & $n$ & Diff & With message & Changed & $p$ \\\\", "\\midrule"]
    for key, c in msg.items():
        L.append(f"{MODEL_SHORT[key]} & {c['n']} & {f2(c['rows']['S0']['acc'])} & {f2(c['rows']['M0']['acc'])} "
                 f"{ci(c['rows']['M0']['ci']['acc'])} & {pct1(1 - c['same'])}\\% & {fp(c['p_holm'])} \\\\")
    L.append("\\midrule")
    L.append(f"\\multicolumn{{3}}{{@{{}}l}}{{\\textit{{Message-length rule ($n={base['n']}$)}}}} & "
             f"{f2(base['acc'])} & -- & -- \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def tex_commit_table(com: dict, pooled_rows: dict | None = None) -> str:
    """One column wide: accuracy with the diff alone, the diff with the rest of the commit, and the whole commit;
    one row per model, corrected p of the difference to the diff alone in parentheses."""
    L = ["% generated by analysis.py - do not edit",
         "\\begin{tabular}{@{}l r l l l@{}}", "\\toprule",
         "Model & $n$ & Diff alone & \\shortstack[l]{Diff + rest\\\\of commit} & Whole commit \\\\", "\\midrule"]
    for key, c in com.items():
        r = c["rows"]
        cell = lambda lv: f"{f2(r[lv]['acc'])} ({fp(r[lv]['p_holm'])})"
        L.append(f"{MODEL_SHORT[key]} & {c['n']} & {f2(r['S0']['acc'])} & {cell('C0')} & {cell('J0')} \\\\")
    if pooled_rows:
        v = pooled_rows
        cell = lambda lv: f"${v[lv]['d']:+.3f}$ ({fp(v[lv]['p_holm'])})"
        L += ["\\midrule", f"Mean change & & -- & {cell('C0')} & {cell('J0')} \\\\"]
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def tex_groups_table(groups: dict, sizes: dict, keys: list) -> str:
    """One column wide: share of files called risky per audit group, for each prompt (diff alone, diff with the
    rest of the commit, whole commit): the four models and their mean."""
    names = {"blamed": "Blamed", "inherited": "Inherited", "nonrisky": "Non-risky"}
    lvs = [lv for lv in ("S0", "C0", "J0") if lv in groups]
    title = {"S0": "Diff alone", "C0": "Diff + rest of commit", "J0": "Whole commit"}
    w = len(keys) + 3
    L = ["% generated by analysis.py - do not edit",
         "\\begin{tabular}{@{}l r " + "r" * (len(keys) + 1) + "@{}}", "\\toprule",
         "Files & $n$ & " + " & ".join([MODEL_SHORT[k] for k in keys] + ["Mean"]) + " \\\\", "\\midrule"]
    for j, lv in enumerate(lvs):
        L.append(("\\addlinespace[3pt]" if j else "") + f"\\multicolumn{{{w}}}{{@{{}}l}}{{\\textit{{{title[lv]}}}}} \\\\")
        for g in GROUPS:
            cells = [f"{pct1(groups[lv]['cells'][f'{k}|{g}']['rate'])}\\%" for k in keys]
            cells.append(f"\\textbf{{{pct1(groups[lv]['mean'][g])}\\%}}")
            L.append(f"\\quad {names[g]} & {sizes[g]} & " + " & ".join(cells) + " \\\\")
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


def tex_stability_table(rows: list) -> str:
    """Two columns wide: one row per comparison, one column per model; cells are changed labels (count/n)."""
    models = ["Gemini", "Haiku", "Sonnet", "Qwen"]
    order, cells = [], {}
    for g, model, level, a in rows:
        if model not in models:  # cross-model agreement is reported in the text
            continue
        if (g, level) not in cells:
            order.append((g, level))
            cells[(g, level)] = {}
        cells[(g, level)][model] = a
    L = ["% generated by analysis.py - do not edit",
         "\\begin{tabular}{@{}l l " + "r " * len(models) + "@{}}", "\\toprule",
         "What differs between the two requests & Prompt or added text & " + " & ".join(models) + " \\\\",
         "\\midrule"]
    group = None
    for g, level in order:
        c = cells[(g, level)]
        vals = [f"{pct1(1 - c[m]['same'])}\\% ({c[m]['flips']}/{c[m]['n']})" if m in c else "--" for m in models]
        L.append(f"{g if g != group else ''} & {level} & " + " & ".join(vals) + " \\\\")
        group = g
    L += ["\\bottomrule", "\\end{tabular}", ""]
    return "\n".join(L)


# --------------------------------------------------------------------------------------
def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    runs = {k: r for k in RUNS if (r := load_run(k))}
    man = pd.read_csv(PREP / "manifest.csv")
    prep = json.loads((PREP / "prepare_summary.json").read_text())
    ctxs = pd.DataFrame(json.loads((PREP / "context_summary.json").read_text())["cases"])
    N, stats = Numbers(), {"runs": {k: RUNS[k] for k in runs}}

    # sample
    man["la"] = [lines_added(s) for s in man.sample_id]
    la_thr = float(man.la.median())
    sel = prep["selection"]
    N["nCases"], N["nRisky"], N["nNonRisky"] = len(man), int((man.label == RISKY).sum()), int((man.label != RISKY).sum())
    N["nRepos"] = man.github_repo.nunique()
    N["nExamined"], N["nExcluded"] = f"{sel['examined']:,}", f"{sel['excluded']:,}"
    lab = prep["labels"]["counts"]
    N["splitRows"] = f"{prep['dataset']['rows']:,}"
    N["splitRisky"], N["splitRiskyPct"] = f"{lab['RISKY']:,}", f"{100 * lab['RISKY'] / prep['dataset']['rows']:.1f}"
    dates = pd.to_datetime(man.commit_datetime, utc=True)
    N["dateFrom"], N["dateTo"] = dates.min().strftime("%B %Y"), dates.max().strftime("%B %Y")
    N["medDiffChars"], N["medFileChars"] = f"{man.diff_chars.median():,.0f}", f"{man.after_chars.median():,.0f}"
    N["medLA"], N["laThr"] = f"{man.la.median():g}", f"{la_thr:g}"
    N["medLARisky"] = f"{man[man.label == RISKY].la.median():g}"
    N["medLANonRisky"] = f"{man[man.label != RISKY].la.median():g}"
    N["callersFound"], N["calleesFound"] = int((ctxs.callers_found > 0).sum()), int((ctxs.callees_found > 0).sum())
    N["repoFilesMin"], N["repoFilesMax"] = f"{ctxs.py_files.min():,}", f"{ctxs.py_files.max():,}"
    excl = sel["exclusion_reasons_by_label"]
    top = sorted(((sum(v.values()), k) for k, v in excl.items()), reverse=True)
    for i, (cnt, k) in enumerate(top[:3]):
        N[f"exclTop{i + 1}"], N[f"exclTop{i + 1}N"] = k, f"{cnt:,}"
    gaps = [json.loads((PREP / "cases" / s / "noise.json").read_text()) for s in man.sample_id]
    N["nTwoGap"] = f"{np.mean([g['target_chars'] - g['chars'] for g in gaps]):.0f}"
    N["nTwoGapMax"] = max(g["target_chars"] - g["chars"] for g in gaps)
    auc = np.mean([(a > b) + 0.5 * (a == b) for a in man[man.label == RISKY].la for b in man[man.label != RISKY].la])
    N["laAUC"] = f2(auc)
    full = metrics(man.label.eq(RISKY).to_numpy(dtype=bool), (man.la > la_thr).to_numpy(dtype=bool))
    N["laAccAll"], N["laMccAll"] = f2(full["acc"]), f2(full["mcc"])

    # What a RISKY label refers to. Defectors assigns it per commit: every file of a blamed commit that adds
    # lines is marked (its paper, Sec. III-F: "the list of added (i.e., defective) line numbers if the commit is
    # defective"). Checked here on the whole split, then counted for the sample.
    if RAW.exists():
        raw = pd.read_parquet(RAW).reset_index(drop=True)
        raw["risky"] = raw["lines"].apply(lambda v: len(v) > 0)
        raw["adds"] = raw["content"].apply(lambda c: any(ln.startswith("+") and not ln.startswith("+++")
                                                         for ln in c.replace("\r\n", "\n").split("\n")))
        per = raw.groupby(["repo", "commit"]).risky.agg(["size", "sum"])
        multi = per[(per["size"] > 1) & (per["sum"] > 0)]  # commits with several files and a risky label
        inside = raw.set_index(["repo", "commit"]).loc[multi.index]
        exceptions = int((inside.adds & ~inside.risky).sum())  # files that add lines but are not marked

        def added_numbers(content: str) -> list[int]:
            out, n = [], None
            for ln in content.replace("\r\n", "\n").split("\n"):
                h = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", ln)
                if h:
                    n = int(h.group(1))
                elif n is None or ln.startswith(("+++", "---", "\\")) or ln.startswith("-"):
                    continue
                elif ln.startswith("+"):
                    out.append(n)
                    n += 1
                else:
                    n += 1
            return out

        rr = raw[raw.risky]
        same = sum(sorted(int(x) for x in v) == added_numbers(c) for v, c in zip(rr["lines"], rr["content"]))
        N["lab.riskyRows"], N["lab.linesAllAdded"] = f"{len(rr):,}", f"{same:,}"
        if same != len(rr):
            print(f"WARNING: the line column equals all added lines for only {same} of {len(rr)} risky rows")
        N["lab.multiRiskyCommits"], N["lab.exceptions"] = f"{len(multi):,}", exceptions
        sample_rows = raw.iloc[man[man.label == RISKY].dataset_row.astype(int)]
        N["nRiskyMultiFile"] = int(sum(per["size"][(r.repo, r.commit)] > 1 for r in sample_rows.itertuples()))
        stats["label_granularity"] = {"multi_file_risky_commits": len(multi), "unmarked_files_that_add_lines": exceptions,
                                      "sample_risky_from_multi_file_commits": int(N.d["nRiskyMultiFile"])}
        if exceptions:
            print(f"WARNING: {exceptions} files of risky commits add lines but are not marked; the paper says none")

    # the commits behind the sample: how many also change other files (commit.json, from the GitHub API)
    commit_json = {sid: json.loads((PREP / "cases" / sid / "commit.json").read_text()) for sid in man.sample_id
          if (PREP / "cases" / sid / "commit.json").exists()}
    n_other_files = None
    if len(commit_json) == len(man):
        n_other_files = man.sample_id.map(lambda sid: len(commit_json[sid]["other_files"]))
        N["nNoOtherFiles"] = int((n_other_files == 0).sum())
        N["nRiskyOtherFiles"] = int(((n_other_files > 0) & (man.label == RISKY)).sum())
        N["otherFilesMedian"] = f"{n_other_files.median():g}"
        N["otherFilesMax"] = int(n_other_files.max())
        N["otherFilesNoPatch"] = int(sum(c["without_patch"] for c in commit_json.values()))

    # RQ1 / RQ2: quality and cost by context level
    tables = {}
    if "gv" in runs:
        tables["gv"] = level_table(runs["gv"], CONTEXT, la_thr)
        r5 = runs["gv"]["res"][runs["gv"]["res"].strategy == "S5"]
        N["sFiveComplete"] = int(r5.repo_complete.fillna(False).astype(bool).sum())
        N["sFiveShare"] = f"{100 * (r5.repo_files_included / r5.repo_files_total).median():.0f}"
        N["sFiveTokens"] = f"{r5.prompt_tokens.mean():,.0f}"
        N["sFiveWindow"] = f"{100 * r5.prompt_tokens.mean() / 1_048_576:.0f}"
        N["sFiveInvalid"] = int((r5.status == "invalid_output").sum())
    for key in ("h1", "s1", "q1"):
        if key in runs:
            tables[key] = level_table(runs[key], tuple(s for s in CONTEXT if s in runs[key]["levels"]), la_thr)
    for key, t in tables.items():
        p = PREFIX[key]
        N[f"{p}.n"], N[f"{p}.nRisky"] = t["n"], t["n_risky"]
        N[f"{p}.Q"], N[f"{p}.Qdf"], N[f"{p}.Qp"] = f"{t['q']:.2f}", t["q_df"], fp(t["q_p"])
        for s, r in t["rows"].items():
            for m in ("acc", "mcc", "f1", "precision", "recall"):
                N[f"{p}.{s}.{m}"] = f2(r[m])
            N[f"{p}.{s}.pos"] = pct(r["pos_rate"]).replace("\\%", "")
            N[f"{p}.{s}.tok"] = f"{r['tokens']:,.0f}"
            N[f"{p}.{s}.costk"] = usd_k(r["cost"])
            N[f"{p}.{s}.xcost"] = f"{r['x_cost']:,.0f}" if r["x_cost"] >= 10 else f"{r['x_cost']:.1f}"
            N[f"{p}.{s}.accci"] = ci(r["ci"]["acc"])
            N[f"{p}.{s}.correct"] = r["tp"] + r["tn"]
            if s != "S0":
                N[f"{p}.{s}.p"], N[f"{p}.{s}.pholm"] = fp(r["p"]), fp(r["p_holm"])
                N[f"{p}.{s}.fixed"], N[f"{p}.{s}.broken"] = r["fixed"], r["broken"]
                N[f"{p}.{s}.daccci"] = ci(r["ci"]["d_acc"], signed=True)
                N[f"{p}.{s}.dacc"] = f"${r['acc'] - t['rows']['S0']['acc']:+.2f}$"
        for b in ("always", "la"):
            for m in ("acc", "mcc", "f1"):
                N[f"{p}.{b}.{m}"] = f2(t["baselines"][b][m])
        N[f"{p}.pareto"] = ", ".join(s for s, r in t["rows"].items() if r["pareto"])
        others = [r for s, r in t["rows"].items() if s != "S0"]
        N[f"{p}.minpholm"] = fp(min(r["p_holm"] for r in others))
        N[f"{p}.accmin"] = f2(min(r["acc"] for r in others))
        N[f"{p}.accmax"] = f2(max(r["acc"] for r in others))
        N[f"{p}.mccmax"] = f2(max(r["mcc"] for r in others))
        N[f"{p}.dAccHi"] = f"${max(r['ci']['d_acc'][1] for r in others):+.2f}$"
        for s, r in t["rows"].items():
            N[f"{p}.{s}.lat"] = f"{r['latency']:.1f}"
        stats[f"levels_{key}"] = {k: v for k, v in t.items() if k != "ids"}
    if "gv" in tables and "h1" in tables:  # ranges over all models, for the abstract
        N["costRatioHG"] = f"{tables['h1']['rows']['S0']['cost'] / tables['gv']['rows']['S0']['cost']:.0f}"
        if "s1" in tables:
            N["costRatioSH"] = f"{tables['s1']['rows']['S0']['cost'] / tables['h1']['rows']['S0']['cost']:.1f}"
            N["costRatioSG"] = f"{tables['s1']['rows']['S0']['cost'] / tables['gv']['rows']['S0']['cost']:.0f}"
        N["nModels"] = len(tables)
        for s in ("S1", "S2", "S3", "S4"):  # cost multiple of a level over models (tokenizers differ)
            xs = [t["rows"][s]["x_cost"] for t in tables.values() if s in t["rows"]]
            N[f"xcost.{s}.min"], N[f"xcost.{s}.max"] = f"{min(xs):.1f}", f"{max(xs):.1f}"
        both = [r for t in tables.values() for s, r in t["rows"].items() if s != "S0"]
        N["allAccMin"], N["allAccMax"] = f2(min(r["acc"] for r in both)), f2(max(r["acc"] for r in both))
        N["xcostMin"], N["xcostMax"] = f"{min(r['x_cost'] for r in both):.1f}", f"{max(r['x_cost'] for r in both):,.0f}"
        N["QpMin"], N["pHolmMin"] = fp(min(t["q_p"] for t in tables.values())), fp(min(r["p_holm"] for r in both))
        las = [t["baselines"]["la"]["acc"] for t in tables.values()]
        N["laAccMin"], N["laAccMax"] = f2(min(las)), f2(max(las))
        s0 = [t["rows"]["S0"]["acc"] for t in tables.values()]
        N["sZeroAccMin"], N["sZeroAccMax"] = f2(min(s0)), f2(max(s0))
        hi = [r["ci"]["d_acc"][1] for r in both]
        N["dAccHiMax"], N["dAccHiMin"] = f"${max(hi):+.2f}$", f"${min(hi):+.2f}$"
        every = [r for t in tables.values() for r in t["rows"].values()]  # all model rows, the diff included
        N["mccMax"], N["fOneMax"] = f2(max(r["mcc"] for r in every)), f2(max(r["f1"] for r in every))
        always = [t["baselines"]["always"]["f1"] for t in tables.values()]
        N["alwaysFOneMin"], N["alwaysFOneMax"] = f2(min(always)), f2(max(always))
    if "ga1" in runs:  # replicate of RQ1 for Gemini on AI Studio, S0-S4 (seven weeks after the Vertex run)
        rt = level_table(runs["ga1"], ("S0", "S1", "S2", "S3", "S4"), la_thr)
        others = {s: r for s, r in rt["rows"].items() if s != "S0"}
        lo = min(others, key=lambda s: others[s]["p"])
        N["ga.rq1.n"], N["ga.rq1.S0.acc"] = rt["n"], f2(rt["rows"]["S0"]["acc"])
        N["ga.rq1.accmin"] = f2(min(r["acc"] for r in others.values()))
        N["ga.rq1.accmax"] = f2(max(r["acc"] for r in others.values()))
        N["ga.rq1.Q"], N["ga.rq1.Qp"] = f"{rt['q']:.2f}", fp(rt["q_p"])
        N["ga.rq1.minp.level"], N["ga.rq1.minp"], N["ga.rq1.minp.holm"] = lo, fp(others[lo]["p"]), fp(others[lo]["p_holm"])
        stats["levels_ga1"] = {k: v for k, v in rt.items() if k != "ids"}
    if "h1" in runs:  # what S5 would have cost for Haiku: its prompt budget at Haiku's measured chars/token (S2)
        g = runs["h1"]["res"][(runs["h1"]["res"].strategy == "S2") & runs["h1"]["res"].prompt_tokens.notna()]
        cpt, pr = g.prompt_chars.sum() / g.prompt_tokens.sum(), runs["h1"]["pricing"]
        est = len(man) * (420_000 / cpt * pr["price_prompt_per_token"]
                          + g.completion_tokens.mean() * pr["price_completion_per_token"])
        N["haikuSFiveEst"] = f"{est:.0f}"

    # RQ3: length control (S0 vs S2 vs N2 within the same run)
    ctrl = {}
    for key in ("ga1", "h1", "s1", "q1"):
        if key in runs and "N2" in runs[key]["levels"]:
            ids, y, preds, sub = paired(runs[key], ("S0", "S2", "N2"))
            boot = bootstrap(y, preds)
            rows = {}
            for s in ("S0", "S2", "N2"):
                g = sub[sub.strategy == s]
                rows[s] = {**metrics(y, preds[s]), "tokens": float(g.prompt_tokens.mean()),
                           "chars": float(g.prompt_chars.mean()), "ci": boot[s]}
            for s in ("S2", "N2"):
                rows[s]["fixed"], rows[s]["broken"], rows[s]["p"] = mcnemar(preds["S0"] == y, preds[s] == y)
            n2v2 = mcnemar(preds["S2"] == y, preds["N2"] == y)
            ctrl[key] = {"n": len(ids), "ids": ids, "rows": rows, "n2_vs_s2": n2v2,
                         "same_as_s0": {s: float((preds[s] == preds["S0"]).mean()) for s in ("S2", "N2")}}
            p = PREFIX[key]
            N[f"{p}.ctl.n"] = len(ids)
            for s in ("S0", "S2", "N2"):
                r = rows[s]
                N[f"{p}.ctl.{s}.acc"], N[f"{p}.ctl.{s}.mcc"] = f2(r["acc"]), f2(r["mcc"])
                N[f"{p}.ctl.{s}.pos"] = pct(r["pos_rate"]).replace("\\%", "")
                N[f"{p}.ctl.{s}.tok"] = f"{r['tokens']:,.0f}"
                N[f"{p}.ctl.{s}.accci"] = ci(r["ci"]["acc"])
                if s != "S0":
                    N[f"{p}.ctl.{s}.p"] = fp(r["p"])
                    N[f"{p}.ctl.{s}.same"] = pct(ctrl[key]["same_as_s0"][s]).replace("\\%", "")
                    N[f"{p}.ctl.{s}.daccci"] = ci(r["ci"]["d_acc"], signed=True)
            N[f"{p}.ctl.NvsS.p"] = fp(n2v2[2])
            N[f"{p}.ctl.tokgap"] = f"{100 * abs(rows['N2']['tokens'] / rows['S2']['tokens'] - 1):.1f}"
    if ctrl:  # smallest p over the models for file vs. unrelated code
        N["ctl.NvsS.pMin"] = fp(min(c["n2_vs_s2"][2] for c in ctrl.values()))
    stats["control"] = ctrl

    # label changes (RQ3/RQ4): identical re-runs, provider change, an uninformative edit, unrelated code of S2's
    # length, real context. Within-run Gemini comparisons use AI Studio run 1 (where N2 exists), S5 the Vertex run.
    no_callers = set(ctxs[ctxs.callers_found == 0].sample_id)
    no_callees = set(ctxs[ctxs.callees_found == 0].sample_id)
    gem = "ga1" if "ga1" in runs else "gv"
    ctl_ids = {k: set(c["ids"]) for k, c in ctrl.items()}  # N2/S2 rows on the RQ3 paired set of the same run
    W = [("Gemini", gem, gem), ("Haiku", "h1", "h1"), ("Sonnet", "s1", "s1"), ("Qwen", "q1", "q1")]  # within run
    G, H = W[0], W[1]
    REP = [("Gemini", "ga1", "ga2"), ("Haiku", "h1", "h2"), ("Sonnet", "s1", "s2"), ("Qwen", "q1", "q2")]
    RERUN, PROV = "Nothing: the same request sent twice", "The provider"
    EMPTY, ADDED = "An empty block added to the functions", "Text added to the diff"
    specs = [  # (tag, table group, table detail, figure label, [(model, run a, run b)], level a, level b, cases)
        ("rep0", RERUN, "Diff", "Same request twice (diff)", REP, "S0", "S0", None),
        ("rep2", RERUN, "Diff + file", "Same request twice (file)", REP, "S2", "S2", None),
        ("prov0", PROV, "Diff", "Other provider (diff)", [("Gemini", "gv", "ga1")], "S0", "S0", None),
        ("prov2", PROV, "Diff + file", "Other provider (file)", [("Gemini", "gv", "ga1")], "S2", "S2", None),
        ("null", EMPTY, "No callers found", "Empty callers block", W, "S1", "S3", no_callers),
        ("nullfour", EMPTY, "No callees found", "Empty callees block", W, "S1", "S4", no_callees),
        ("noise", ADDED, "Unrelated code", "Unrelated code", W, "S0", "N2", ctl_ids),
        ("msg", ADDED, "Commit message", "Commit message", [("Gemini", "ga1", "ga1")] + W[1:], "S0", "M0", None),
        ("func", ADDED, "Function", "Function", W, "S0", "S1", None),
        ("file", ADDED, "File", "File", W, "S0", "S2", ctl_ids),
        ("callers", ADDED, "Callers", "Callers", W, "S0", "S3", None),
        ("callees", ADDED, "Callees", "Callees", W, "S0", "S4", None),
        ("repo", ADDED, "Repository", "Repository", [("Gemini", "gv", "gv")], "S0", "S5", None),
        ("xmodel", "Other model", "Diff", None, [("G.\\ vs.\\ H.", gem, "h1")], "S0", "S0", None),
        ("xmodelhs", "Other model", "Diff", None, [("H.\\ vs.\\ S.", "h1", "s1")], "S0", "S0", None),
    ]
    stab, flip_rows, by_tag = [], [], {}
    for tag, label, level, fig_label, pairs, la_, lb_, cases in specs:
        vals = {}
        for model, ka, kb in pairs:
            if ka in runs and kb in runs and la_ in runs[ka]["levels"] and lb_ in runs[kb]["levels"]:
                subset = cases.get(ka) if isinstance(cases, dict) else cases
                if isinstance(cases, dict) and subset is None:
                    continue
                a = agreement(runs[ka], runs[kb], la_, lb_, subset)
                stab.append((label, model, level, a))
                by_tag.setdefault(tag, []).append(1 - a["same"])
                m = model.split(".")[0][:1]  # G / H / S / Q
                N[f"chg.{tag}.{m}"], N[f"chg.{tag}.{m}.n"] = pct1(1 - a["same"]), a["n"]
                N[f"chg.{tag}.{m}.flips"], N[f"chg.{tag}.{m}.kappa"] = a["flips"], f2(a["kappa"])
                N[f"chg.{tag}.{m}.acca"], N[f"chg.{tag}.{m}.accb"] = f2(a["acc_a"]), f2(a["acc_b"])
                N[f"chg.{tag}.{m}.p"] = fp(a["p"])
                if fig_label:
                    vals[MODEL_KEY[model]] = 1 - a["same"]
        if vals:
            flip_rows.append((fig_label, vals))
    for tag, v in by_tag.items():  # range over models for each comparison
        N[f"chg.{tag}.min"], N[f"chg.{tag}.max"] = pct1(min(v)), pct1(max(v))
    for name, tags in (("ctx", ("func", "file", "callers", "callees", "repo")), ("null", ("null", "nullfour")),
                       ("noise", ("noise",)), ("extra", ("func", "file", "callers", "callees", "repo", "noise", "msg"))):
        v = [x for t in tags for x in by_tag.get(t, [])]
        if v:
            N[f"chg.{name}.min"], N[f"chg.{name}.max"] = pct1(min(v)), pct1(max(v))
    if "h1" in runs and "h2" in runs:  # repeats of Haiku cases whose first run is the reused October pilot
        res1 = runs["h1"]["res"]
        reused = {lv: set(res1[(res1.strategy == lv) & res1.reused_from.notna()].sample_id) for lv in ("S0", "S2")}
        ra = [agreement(runs["h1"], runs["h2"], lv, lv, reused[lv]) for lv in ("S0", "S2")]
        N["chg.rep.H.reusedn"], N["chg.rep.H.reusedflips"] = sum(a["n"] for a in ra), sum(a["flips"] for a in ra)
    stats["stability"] = [{"group": g, "model": m, "level": lv, **a} for g, m, lv, a in stab]
    if "gv" in runs and "ga1" in runs:  # provider change over all five shared levels
        allv = [agreement(runs["gv"], runs["ga1"], s, s) for s in ("S0", "S1", "S2", "S3", "S4")]
        N["chg.prov.min"] = pct1(1 - max(a["same"] for a in allv))
        N["chg.prov.max"] = pct1(1 - min(a["same"] for a in allv))
        N["chg.prov.dacc"] = f2(max(abs(a["acc_b"] - a["acc_a"]) for a in allv))
        N["chg.prov.pmin"] = fp(min(a["p"] for a in allv))
    if "gv" in runs:  # the same uninformative edit in the Vertex run (no repeat exists for that endpoint)
        a = agreement(runs["gv"], runs["gv"], "S1", "S3", no_callers)
        N["chg.nullvertex"], N["chg.nullvertex.flips"], N["chg.nullvertex.n"] = pct1(1 - a["same"]), a["flips"], a["n"]
    reps = [(m, a) for g, m, lv, a in stab if g == RERUN]
    if reps:
        N["chg.rep.max"] = pct1(max(1 - a["same"] for m, a in reps))
        for model in ("Gemini", "Haiku", "Sonnet", "Qwen"):
            mine = [a for m, a in reps if m == model]
            if mine:
                N[f"chg.rep.{model[0]}.flips"] = sum(a["flips"] for a in mine)
                N[f"chg.rep.{model[0]}.n"] = sum(a["n"] for a in mine)
    if tables:  # typical half-width of the accuracy CIs (for the conclusion-validity discussion)
        halves = [(r["ci"]["acc"][1] - r["ci"]["acc"][0]) / 2 for t in tables.values() for r in t["rows"].values()]
        N["ciHalf"] = f2(float(np.mean(halves)))

    # Do extra text and context change more labels than an identical re-run? (per model, Holm within model)
    fr, fr_ps = {}, {}
    for model, k1, k2 in (("Gemini", "ga1", "ga2"), ("Haiku", "h1", "h2"), ("Sonnet", "s1", "s2"), ("Qwen", "q1", "q2")):
        if k1 in runs and k2 in runs:
            for lv in ("S1", "S2", "S3", "S4", "N2", "M0"):
                if lv in runs[k1]["levels"]:
                    fr[(model, lv)] = flips_vs_rerun(runs[k1], runs[k2], lv)
            for lv, p_ in holm({lv: fr[(m, lv)]["p"] for m, lv in fr if m == model}).items():
                fr[(model, lv)]["p_holm"] = p_
    if fr:
        N["fr.pHolmMax"] = fp(max(v["p_holm"] for v in fr.values()))
        for m in ("Gemini", "Haiku", "Sonnet", "Qwen"):
            mine = [v for (mm, lv), v in fr.items() if mm == m]
            if mine:
                N[f"fr.{m[0]}.pHolmMax"] = fp(max(v["p_holm"] for v in mine))
                N[f"fr.{m[0]}.nSig"] = sum(v["p_holm"] < 0.05 for v in mine)
                N[f"fr.{m[0]}.nTests"] = len(mine)
        det = [v for (m, lv), v in fr.items() if m != "Qwen"]  # the three near-deterministic models
        if det:
            N["fr.det.pHolmMax"] = fp(max(v["p_holm"] for v in det))
            N["fr.det.nTests"] = len(det)
        N["fr.nSig"] = sum(v["p_holm"] < 0.05 for v in fr.values())
        N["fr.nTests"] = len(fr)
        for (m, lv), v in fr.items():
            N[f"fr.{m[0]}.{lv}.p"] = fp(v["p_holm"])
    stats["flips_vs_rerun"] = [{"model": m, "level": lv, **v} for (m, lv), v in fr.items()]

    # Pooled over the four models (same period: Gemini via AI Studio): accuracy change against S0 per level
    pool_keys = [k for k in ("ga1", "h1", "s1", "q1") if k in runs]
    pool = {}
    if len(pool_keys) == 4:
        for lv in ("S1", "S2", "S3", "S4", "N2", "M0"):
            if all(lv in runs[k]["levels"] for k in pool_keys):
                pool[lv] = pooled(runs, pool_keys, lv)
        for lv, p_ in holm({lv: v["p"] for lv, v in pool.items()}).items():
            pool[lv]["p_holm"] = p_
        for lv, v in pool.items():
            N[f"pool.{lv}.d"], N[f"pool.{lv}.ci"] = f"${v['d']:+.3f}$", ci(v["ci"], signed=True)
            N[f"pool.{lv}.p"], N[f"pool.{lv}.n"] = fp(v["p_holm"]), v["n"]
        ctxl = [v for lv, v in pool.items() if lv in CONTEXT]
        N["pool.ciLo"] = f"${min(v['ci'][0] for v in ctxl):+.2f}$"
        N["pool.ciHi"] = f"${max(v['ci'][1] for v in ctxl):+.2f}$"
        N["pool.dLo"], N["pool.dHi"] = f"${min(v['d'] for v in ctxl):+.3f}$", f"${max(v['d'] for v in ctxl):+.3f}$"
        N["pool.pMin"] = fp(min(v["p_holm"] for v in pool.values()))
        N["pool.nMin"] = min(v["n"] for v in pool.values())
        N["pool.nMax"] = max(v["n"] for v in pool.values())
    stats["pooled"] = pool

    # E4: commit message (S0 vs M0 within the same run; Gemini via AI Studio, where M0 was run)
    msgs = {s: json.loads((PREP / "cases" / s / "message.json").read_text())["text"]
            for s in man.sample_id if (PREP / "cases" / s / "message.json").exists()}
    msg, msg_p = {}, {}
    for key, src in (("ga1", "ga1"), ("h1", "h1"), ("s1", "s1"), ("q1", "q1")):
        if src in runs and "M0" in runs[src]["levels"]:
            ids, y, preds, sub = paired(runs[src], ("S0", "M0"))
            boot = bootstrap(y, preds)
            rows = {s: {**metrics(y, preds[s]), "ci": boot[s],
                        "cost": float(sub[sub.strategy == s].list_cost.mean()),
                        "tokens": float(sub[sub.strategy == s].prompt_tokens.mean())} for s in ("S0", "M0")}
            fixed, broken, p_ = mcnemar(preds["S0"] == y, preds["M0"] == y)
            msg[key] = {"n": len(ids), "rows": rows, "fixed": fixed, "broken": broken, "p": p_,
                        "same": float((preds["S0"] == preds["M0"]).mean())}
            msg_p[key] = p_
    for key, p_ in holm(msg_p).items():
        msg[key]["p_holm"] = p_
    for key, c in msg.items():
        p = PREFIX[key]
        for s in ("S0", "M0"):
            N[f"msg.{p}.{s}.acc"], N[f"msg.{p}.{s}.mcc"] = f2(c["rows"][s]["acc"]), f2(c["rows"][s]["mcc"])
            N[f"msg.{p}.{s}.pos"] = pct(c["rows"][s]["pos_rate"]).replace("\\%", "")
        N[f"msg.{p}.n"], N[f"msg.{p}.p"], N[f"msg.{p}.pholm"] = c["n"], fp(c["p"]), fp(c["p_holm"])
        N[f"msg.{p}.fixed"], N[f"msg.{p}.broken"] = c["fixed"], c["broken"]
        N[f"msg.{p}.daccci"] = ci(c["rows"]["M0"]["ci"]["d_acc"], signed=True)
        N[f"msg.{p}.dacc"] = f"${c['rows']['M0']['acc'] - c['rows']['S0']['acc']:+.2f}$"
        N[f"msg.{p}.chg"] = pct1(1 - c["same"])
        N[f"msg.{p}.xcost"] = f"{c['rows']['M0']['cost'] / c['rows']['S0']['cost']:.1f}"
    if msg:
        d = [c["rows"]["M0"]["acc"] - c["rows"]["S0"]["acc"] for c in msg.values()]
        N["msg.daccMin"], N["msg.daccMax"] = f"${min(d):+.2f}$", f"${max(d):+.2f}$"
        N["msg.pHolmMin"] = fp(min(c["p_holm"] for c in msg.values()))
        N["msg.chgMin"] = pct1(min(1 - c["same"] for c in msg.values()))
        N["msg.chgMax"] = pct1(max(1 - c["same"] for c in msg.values()))
    msg_base = {}
    if len(msgs) == len(man):  # label-free message heuristics on all cases
        y_all = man.label.eq(RISKY).to_numpy(dtype=bool)
        mlen = np.array([len(msgs[s]) for s in man.sample_id])
        subj = [msgs[s].split("\n")[0] for s in man.sample_id]
        fixkw = np.array([bool(re.search(r"\b(fix|bug)", t, re.I)) for t in subj])
        mlen_pred = mlen > np.median(mlen)
        msg_base = {**metrics(y_all, mlen_pred), "fix": metrics(y_all, fixkw)}
        N["msgChars"] = f"{np.median(mlen):,.0f}"
        N["msgCharsRisky"] = f"{np.median(mlen[y_all]):,.0f}"
        N["msgCharsNonRisky"] = f"{np.median(mlen[~y_all]):,.0f}"
        N["msgLen.acc"], N["msgLen.mcc"] = f2(msg_base["acc"]), f2(msg_base["mcc"])
        N["msgFix.acc"], N["msgFix.n"] = f2(msg_base["fix"]["acc"]), int(fixkw.sum())
        N["msgLenLaAgree"] = pct1(float((mlen_pred == (man.la > la_thr).to_numpy()).mean()))
    stats["message"] = {"models": msg, "baselines": msg_base}

    # Label audit of the RISKY cases against the dataset's own fix -> bug-inducing links (audit_szz.py). Only the
    # part that needs no judgement enters the paper: for each case, do the fix commits that the dataset links to its
    # commit remove lines of the commit in the sampled file (blamed), or only in other files (inherited)?
    # LLM-judged verdicts exist in data/audit/ (two rounds, Nov 24, 2026) but are deliberately not used.
    audit_dir = ROOT / "data" / "audit"
    audit = {}
    if (audit_dir / "szz_links.json").exists():
        links = json.loads((audit_dir / "szz_links.json").read_text())
        A = pd.DataFrame([{"sample_id": sid, "group": "blamed" if v["where"] == "sampled_file" else "inherited",
                           "touched": v["fix_changes_sampled_file"]} for sid, v in links.items()])
        unresolved = [sid for sid, v in links.items() if v["where"] not in ("sampled_file", "other_file")]
        cnt = A.group.value_counts().to_dict()
        N["audit.n"] = len(A)
        N["audit.links"] = sum(len(v["fixes"]) for v in links.values())
        N["audit.fixCommits"] = len({f["sha"] for v in links.values() for f in v["fixes"]})
        for g in ("blamed", "inherited"):
            N[f"audit.{g}"], N[f"audit.{g}.pct"] = int(cnt.get(g, 0)), pct1(cnt.get(g, 0) / len(A))
        # of the inherited files: not changed by any linked fix at all / changed without removing the commit's lines
        N["audit.notTouched"] = int(((A.group == "inherited") & ~A.touched).sum())
        N["audit.touchedNotBlamed"] = int(((A.group == "inherited") & A.touched).sum())
        audit = {"counts": cnt, "inherited_not_changed_by_any_fix": int(N.d["audit.notTouched"]),
                 "unresolved": unresolved}
        if unresolved:
            print(f"WARNING: no removed line found for {unresolved}; they are counted as inherited")
    stats["audit"] = audit

    # Whole commit (third round): C0 = diff + the diffs of the commit's other files, same question about the file;
    # J0 = the whole commit with the question asked about the commit. Both against the diff alone, within a run.
    com = {}
    for key in ("ga1", "h1", "s1", "q1"):
        if key in runs and {"C0", "J0"} <= set(runs[key]["levels"]):
            ids, y, preds, sub = paired(runs[key], ("S0", "C0", "J0"))
            boot = bootstrap(y, preds)
            rows = {lv: {**metrics(y, preds[lv]), "ci": boot[lv],
                         "cost": float(sub[sub.strategy == lv].list_cost.mean()),
                         "tokens": float(sub[sub.strategy == lv].prompt_tokens.mean())} for lv in ("S0", "C0", "J0")}
            raw_p = {}
            for lv in ("C0", "J0"):
                rows[lv]["fixed"], rows[lv]["broken"], raw_p[lv] = mcnemar(preds["S0"] == y, preds[lv] == y)
            for lv, ph in holm(raw_p).items():
                rows[lv].update(p=raw_p[lv], p_holm=ph)
            com[key] = {"n": len(ids), "rows": rows, "j0_vs_c0": mcnemar(preds["C0"] == y, preds["J0"] == y),
                        "same_as_s0": {lv: float((preds[lv] == preds["S0"]).mean()) for lv in ("C0", "J0")}}
            pfx = PREFIX[key]
            N[f"com.{pfx}.n"] = len(ids)
            for lv in ("S0", "C0", "J0"):
                r = rows[lv]
                N[f"com.{pfx}.{lv}.acc"], N[f"com.{pfx}.{lv}.mcc"] = f2(r["acc"]), f2(r["mcc"])
                N[f"com.{pfx}.{lv}.pos"] = pct(r["pos_rate"]).replace("\\%", "")
                N[f"com.{pfx}.{lv}.recall"] = f2(r["recall"])
                N[f"com.{pfx}.{lv}.tok"] = f"{r['tokens']:,.0f}"
                if lv != "S0":
                    N[f"com.{pfx}.{lv}.p"], N[f"com.{pfx}.{lv}.pholm"] = fp(r["p"]), fp(r["p_holm"])
                    N[f"com.{pfx}.{lv}.dacc"] = f"${r['acc'] - rows['S0']['acc']:+.2f}$"
                    N[f"com.{pfx}.{lv}.daccci"] = ci(r["ci"]["d_acc"], signed=True)
                    N[f"com.{pfx}.{lv}.chg"] = pct1(1 - com[key]["same_as_s0"][lv])
                    N[f"com.{pfx}.{lv}.xcost"] = f"{r['cost'] / rows['S0']['cost']:.1f}"
    if com:
        both = [(c["rows"][lv], c["rows"]["S0"]) for c in com.values() for lv in ("C0", "J0")]
        N["com.pHolmMin"] = fp(min(r["p_holm"] for r, _ in both))
        N["com.daccMin"] = f"${min(r['acc'] - b['acc'] for r, b in both):+.2f}$"
        N["com.daccMax"] = f"${max(r['acc'] - b['acc'] for r, b in both):+.2f}$"
        N["com.accMin"], N["com.accMax"] = f2(min(r["acc"] for r, _ in both)), f2(max(r["acc"] for r, _ in both))
        for lv in ("S0", "C0", "J0"):
            accs = [c["rows"][lv]["acc"] for c in com.values()]
            N[f"com.{lv}.accMin"], N[f"com.{lv}.accMax"] = f2(min(accs)), f2(max(accs))
            poss = [c["rows"][lv]["pos_rate"] for c in com.values()]
            N[f"com.{lv}.posMin"], N[f"com.{lv}.posMax"] = pct1(min(poss)), pct1(max(poss))
        for lv in ("C0", "J0"):
            xs = [c["rows"][lv]["cost"] / c["rows"]["S0"]["cost"] for c in com.values()]
            N[f"com.{lv}.xcostMin"], N[f"com.{lv}.xcostMax"] = f"{min(xs):.0f}", f"{max(xs):.0f}"
            ch = [1 - c["same_as_s0"][lv] for c in com.values()]
            N[f"com.{lv}.chgMin"], N[f"com.{lv}.chgMax"] = pct1(min(ch)), pct1(max(ch))
        N["com.nSig"] = sum(r["p_holm"] < 0.05 for r, _ in both)
        ckeys = [k for k in ("ga1", "h1", "s1", "q1") if k in com]
        if len(ckeys) == 4:  # averaged over the four models, as for the code contexts
            cp = {lv: pooled(runs, ckeys, lv) for lv in ("C0", "J0")}
            for lv, ph in holm({lv: v["p"] for lv, v in cp.items()}).items():
                cp[lv]["p_holm"] = ph
            for lv, v in cp.items():
                N[f"com.pool.{lv}.d"], N[f"com.pool.{lv}.ci"] = f"${v['d']:+.3f}$", ci(v["ci"], signed=True)
                N[f"com.pool.{lv}.p"], N[f"com.pool.{lv}.n"] = fp(v["p_holm"]), v["n"]
            stats["commit_pooled"] = cp
    stats["commit"] = {k: {kk: vv for kk, vv in v.items()} for k, v in com.items()}

    # Do the models call the files that SZZ's blame points to risky more often? Share of files called risky per
    # audit group (blamed: a linked fix removes lines of the commit in the file; inherited: only in other files),
    # for the diff alone and the two commit conditions.
    groups = {}
    if audit:
        G = {r.sample_id: r.group for r in A.itertuples()}
        G.update({sid: "nonrisky" for sid in man[man.label != RISKY].sample_id})
        gkeys = [k for k in ("ga1", "h1", "s1", "q1") if k in runs]
        bacc_mean, shares = {}, {}
        for lv in ("S0", "S1", "S2", "S3", "S4", "N2", "M0", "C0", "J0"):
            if not gkeys or not all(lv in runs[k]["levels"] for k in gkeys):
                continue
            pr = {k: labels(runs[k], lv).pred.astype(float) for k in gkeys}
            cell = {}
            for k in gkeys:
                for g in GROUPS:
                    v = pr[k][[i for i in pr[k].index if G.get(i) == g]]
                    cell[(k, g)] = {"rate": float(v.mean()), "n": int(len(v))}
                    N[f"grp.{lv}.{PREFIX[k]}.{g}"] = pct1(cell[(k, g)]["rate"])
            mean = {g: float(np.mean([cell[(k, g)]["rate"] for k in gkeys])) for g in GROUPS}
            for g in GROUPS:
                N[f"grp.{lv}.mean.{g}"] = pct1(mean[g])
            # balanced accuracy (mean of the share of risky files called risky and the share of non-risky files
            # called non-risky), per model and averaged: with all risky files, and with the blamed files only
            bacc = {"all": [], "blamed": []}
            for k in gkeys:
                risky_ids = [i for i in pr[k].index if G.get(i) in ("blamed", "inherited")]
                spec = 1 - cell[(k, "nonrisky")]["rate"]
                bacc["all"].append((float(pr[k][risky_ids].mean()) + spec) / 2)
                bacc["blamed"].append((cell[(k, "blamed")]["rate"] + spec) / 2)
            for name, vals in bacc.items():
                N[f"grp.{lv}.bacc.{name}"] = f2(float(np.mean(vals)))
                N[f"grp.{lv}.bacc.{name}.min"], N[f"grp.{lv}.bacc.{name}.max"] = f2(min(vals)), f2(max(vals))
            bacc_mean[lv] = {name: float(np.mean(vals)) for name, vals in bacc.items()}
            share = pd.DataFrame(pr).dropna().mean(axis=1)  # per file: share of the models that call it risky
            sel = lambda *gs: share[[i for i in share.index if G.get(i) in gs]].to_numpy()
            tests = {"blInh": (sel("blamed"), sel("inherited")), "blNon": (sel("blamed"), sel("nonrisky")),
                     "inhNon": (sel("inherited"), sel("nonrisky")),
                     "riskyNon": (sel("blamed", "inherited"), sel("nonrisky"))}
            ps = {t: perm_groups(a, b) for t, (a, b) in tests.items()}
            for t, pv in ps.items():
                N[f"grp.{lv}.p.{t}"] = fp(pv)
            N[f"grp.{lv}.gap.blInh"] = f"{100 * (mean['blamed'] - mean['inherited']):.0f}"
            N[f"grp.{lv}.gap.inhNon"] = f"{100 * (mean['inherited'] - mean['nonrisky']):.0f}"
            N[f"grp.{lv}.gap.blNon"] = f"{100 * (mean['blamed'] - mean['nonrisky']):.0f}"
            groups[lv] = {"cells": {f"{k}|{g}": v for (k, g), v in cell.items()}, "mean": mean, "p": ps,
                          "balanced_accuracy": {n_: dict(zip(gkeys, v)) for n_, v in bacc.items()},
                          "n_valid_for_all_models": {t: [len(a), len(b)] for t, (a, b) in tests.items()}}
            if lv != "S0" and "S0" in groups:
                # per file: change of the share of models that call it risky, against the diff alone
                both = pd.DataFrame(pr).dropna().mean(axis=1).to_frame("lv").join(base_share.rename("s0"), how="inner")
                chg = both.lv - both.s0
                selc = lambda *gs: chg[[i for i in chg.index if G.get(i) in gs]].to_numpy()
                rise = {g: float(selc(g).mean()) for g in GROUPS}
                dd = {"inhNon": (selc("inherited"), selc("nonrisky")), "blNon": (selc("blamed"), selc("nonrisky")),
                      "riskyNon": (selc("blamed", "inherited"), selc("nonrisky"))}
                for g in GROUPS:
                    N[f"grp.{lv}.rise.{g}"] = f"{100 * rise[g]:+.0f}".replace("-", "$-$").replace("+", "$+$")
                for t, (a, b) in dd.items():
                    N[f"grp.{lv}.pdd.{t}"] = fp(perm_groups(a, b))
                groups[lv]["rise_vs_diff"] = rise
                groups[lv]["p_rise_differs"] = {t: perm_groups(a, b) for t, (a, b) in dd.items()}
            shares[lv] = share
            if lv == "S0":
                base_share = share
        for g in GROUPS:
            N[f"grp.n.{g}"] = sum(1 for v in G.values() if v == g)
        # The lines-added rule by audit group (no model): blamed files have larger diffs, so the rule alone separates
        # them from the non-risky files. And do the models' answers follow the number of added lines?
        la = man.set_index("sample_id").la
        la_flag = (la > la_thr).astype(float)
        by = lambda g: la_flag[[i for i in la_flag.index if G.get(i) == g]].to_numpy()
        for g in GROUPS:
            N[f"la.grp.{g}"] = pct1(float(by(g).mean()))
            N[f"la.med.{g}"] = f"{la[[i for i in la.index if G.get(i) == g]].median():g}"
        N["la.grp.p.blNon"], N["la.grp.p.inhNon"] = fp(perm_groups(by("blamed"), by("nonrisky"))), fp(perm_groups(by("inherited"), by("nonrisky")))
        if "S0" in shares:
            both_ = shares["S0"].to_frame("share").join(la.rename("la"), how="inner")
            N["grp.S0.rhoLA"] = f2(float(both_.share.rank().corr(both_.la.rank())))  # Spearman
        stats["lines_added_rule_by_group"] = {g: float(by(g).mean()) for g in GROUPS}
        # Blamed against non-risky files for every prompt that asks about the file (all prompts that the four models
        # ran, except the whole commit, where the question is about the commit): range of the difference in points.
        fileq = [lv for lv in ("S0", "S1", "S2", "S3", "S4", "N2", "M0", "C0") if lv in groups]
        if fileq:
            gap = {lv: groups[lv]["mean"]["blamed"] - groups[lv]["mean"]["nonrisky"] for lv in fileq}
            N["grp.fileq.n"] = len(fileq)
            N["grp.fileq.gap.blNon.min"] = f"{100 * min(gap.values()):.0f}"
            N["grp.fileq.gap.blNon.max"] = f"{100 * max(gap.values()):.0f}"
            N["grp.fileq.p.blNon.min"] = fp(min(groups[lv]["p"]["blNon"] for lv in fileq))
            N["grp.fileq.p.blNon.max"] = fp(max(groups[lv]["p"]["blNon"] for lv in fileq))
            N["grp.fileq.nSig"] = sum(groups[lv]["p"]["blNon"] < 0.05 for lv in fileq)
            stats["blamed_vs_nonrisky_by_prompt"] = {lv: {"gap": gap[lv], "p": groups[lv]["p"]["blNon"]} for lv in fileq}
            if max(gap, key=gap.get) != "N2":
                print("WARNING: the paper says the blamed/non-risky difference is largest with unrelated code; "
                      f"it is largest with {max(gap, key=gap.get)}")
        # The same diffs with the other question: whole commit (question about the commit) against the diff with the
        # rest of the commit (question about the file). Does the share called risky change differently per group?
        if "C0" in shares and "J0" in shares:
            pair = shares["J0"].to_frame("j").join(shares["C0"].rename("c"), how="inner")
            delta = pair.j - pair.c
            seld = lambda *gs: delta[[i for i in delta.index if G.get(i) in gs]].to_numpy()
            for t, (a_, b_) in {"blNon": (seld("blamed"), seld("nonrisky")),
                                "inhNon": (seld("inherited"), seld("nonrisky"))}.items():
                N[f"grp.J0.pddC0.{t}"] = fp(perm_groups(a_, b_))
            groups["J0"]["rise_vs_rest_of_commit"] = {g: float(seld(g).mean()) for g in GROUPS}
            groups["J0"]["p_rise_vs_rest_of_commit_differs"] = {"blNon": perm_groups(seld("blamed"), seld("nonrisky")),
                                                                "inhNon": perm_groups(seld("inherited"), seld("nonrisky"))}
        ctx_levels = [lv for lv in ("S1", "S2", "S3", "S4") if lv in bacc_mean]
        if ctx_levels:  # the four code contexts that every model ran, with only the blamed files counted as risky
            vals = [bacc_mean[lv]["blamed"] for lv in ctx_levels]
            N["grp.ctx.bacc.blamed.min"], N["grp.ctx.bacc.blamed.max"] = f2(min(vals)), f2(max(vals))
        # size of the rest of the commit per group (characters of the other files' diffs; commits with other files)
        if len(commit_json) == len(man):
            rest = pd.DataFrame({"group": pd.Series(G), "files": n_other_files.set_axis(man.sample_id.to_numpy()),
                                 "chars": pd.Series({sid: sum(len(f.get("patch") or "") for f in c["other_files"])
                                                     for sid, c in commit_json.items()})})
            for g in GROUPS:
                sub_g = rest[(rest.group == g) & (rest.files > 0)]
                N[f"rest.{g}.n"], N[f"rest.{g}.none"] = len(sub_g), int(((rest.group == g) & (rest.files == 0)).sum())
                N[f"rest.{g}.chars"] = f"{sub_g.chars.median():,.0f}"
                N[f"rest.{g}.files"] = f"{sub_g.files.median():g}"
            # a rule without a model, at the level of the commit: flag every commit whose diff (all files) is
            # longer than the median commit diff of the sample
            size = rest.chars + man.set_index("sample_id").diff_chars.reindex(rest.index)
            flagged = size > size.median()
            truth = man.set_index("sample_id").label.reindex(rest.index) == RISKY
            N["rule.commitSize.acc"] = f2(float((flagged == truth).mean()))
            N["rule.commitSize.median"] = f"{size.median():,.0f}"
            for g in GROUPS:
                N[f"rule.commitSize.{g}"] = pct1(float(flagged[rest.group == g].mean()))
            stats["commit_size_rule"] = {"accuracy": float((flagged == truth).mean()), "median_chars": float(size.median()),
                                         "flagged": {g: float(flagged[rest.group == g].mean()) for g in GROUPS}}
            stats["rest_of_commit"] = {g: {"commits_with_other_files": int(((rest.group == g) & (rest.files > 0)).sum()),
                                           "median_chars": float(rest[(rest.group == g) & (rest.files > 0)].chars.median()),
                                           "median_files": float(rest[(rest.group == g) & (rest.files > 0)].files.median())}
                                       for g in GROUPS}
        # a predictor that flags exactly the blamed files is counted wrong on every inherited file
        N["audit.ceilingAcc"] = f2(sum(1 for v in G.values() if v in ("blamed", "nonrisky")) / len(G))
    stats["audit_groups"] = groups

    # invalid outputs (excluded from the paired sets, never mapped to a label)
    invalid = {}
    for key, r in runs.items():
        res = r["res"][r["res"].status != "not_run"]
        inv = res[res.status == "invalid_output"]
        invalid[key] = {s: {"n": int((res.strategy == s).sum()), "invalid": int((inv.strategy == s).sum()),
                            "length": int(((inv.strategy == s) & (inv.finish_reason == "length")).sum())}
                        for s in r["levels"]}
        N[f"inv.{key}.total"], N[f"inv.{key}.n"] = len(inv), f"{len(res):,}"
        N[f"inv.{key}.length"] = int((inv.finish_reason == "length").sum())
        cache = MAIN / RUNS[key][0] / "cache"
        raw = [json.loads((cache / f"{k}.json").read_text()).get("raw_content") or "" for k in
               inv[inv.finish_reason != "length"].cache_key]
        N[f"inv.{key}.badjson"] = sum(bool(re.search(r'"label"\s*:\s*"(RISKY|NON-RISKY)"', t)) for t in raw)
        for s, v in invalid[key].items():
            N[f"inv.{key}.{s}"], N[f"inv.{key}.{s}.length"] = v["invalid"], v["length"]
    stats["invalid"] = invalid

    # spending
    tot = 0.0
    for key, r in runs.items():
        c, n_att = charged(r)
        tot += c
        N[f"cost.{key}"], N[f"att.{key}"] = f"{c:.2f}", f"{n_att:,}"
    pilot = sum(json.loads(line).get("cost_usd") or 0 for d in ("gemini-2.5-flash-lite", "claude-haiku-4.5")
                for line in (ROOT / "results" / d / "attempts.jsonl").read_text().splitlines() if line.strip())
    N["cost.pilot"], N["cost.total"] = f"{pilot:.2f}", f"{tot + pilot:.2f}"
    r2 = lambda a: a.get("ts", "") >= ROUND2
    N["cost.new"] = f"{sum(a.get('cost_usd') or 0 for k in ('ga1', 'ga2', 'h1', 'h2') if k in runs for a in runs[k]['attempts'] if not r2(a)):.2f}"  # first follow-ups
    N["cost.round2"] = f"{sum(a.get('cost_usd') or 0 for r in runs.values() for a in r['attempts'] if r2(a)):.2f}"
    n_pred = sum(int((r["res"].status != "not_run").sum()) for r in runs.values())
    N["nPredictions"] = f"{n_pred:,}"
    n_inv = sum(int((r["res"].status == "invalid_output").sum()) for r in runs.values())
    N["inv.all.total"], N["inv.all.pct"] = n_inv, pct1(n_inv / n_pred)

    # outputs
    N.write(OUT / "numbers.tex")
    if tables:
        (OUT / "tab_levels.tex").write_text(tex_main_table(tables), encoding="utf-8")
        fig_accuracy(tables, metrics(man.label.eq(RISKY).to_numpy(dtype=bool),
                                     (man.la > la_thr).to_numpy(dtype=bool))["acc"], FIGS / "accuracy_by_level.pdf")
        fig_cost(tables, FIGS / "cost_vs_accuracy.pdf")
    if ctrl:
        (OUT / "tab_control.tex").write_text(tex_control_table(ctrl), encoding="utf-8")
    if msg and msg_base:
        (OUT / "tab_message.tex").write_text(tex_message_table(msg, msg_base), encoding="utf-8")
    if groups.get("S0"):
        (OUT / "tab_groups.tex").write_text(tex_groups_table(groups, {g: N.d[f"grp.n.{g}"] for g in GROUPS}, gkeys),
                                            encoding="utf-8")
    if com:
        (OUT / "tab_commit.tex").write_text(tex_commit_table(com, stats.get("commit_pooled")), encoding="utf-8")
    if stab:
        (OUT / "tab_stability.tex").write_text(tex_stability_table(stab), encoding="utf-8")
        fig_flips(flip_rows, FIGS / "label_changes.pdf")
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2, default=float), encoding="utf-8")

    # console summary
    for key, t in tables.items():
        print(f"\n== {RUNS[key][1]} ({RUNS[key][2]}), paired n = {t['n']} ({t['n_risky']} RISKY); "
              f"Cochran Q = {t['q']:.2f}, df = {t['q_df']}, p = {t['q_p']:.3f}")
        for s, r in t["rows"].items():
            print(f"  {s:3s} acc {r['acc']:.3f} {ci(r['ci']['acc'])}  mcc {r['mcc']:+.3f}  f1 {r['f1']:.3f}  "
                  f"P {r['precision']:.2f} R {r['recall']:.2f}  predR {r['pos_rate']:.2f}  tok {r['tokens']:9,.0f}  "
                  f"$/1k {usd_k(r['cost']):>7s}  " + (f"fixed/broken {r['fixed']}/{r['broken']} p {r['p']:.3f} "
                                                      f"holm {r['p_holm']:.3f}" if s != "S0" else "") +
                  ("  pareto" if r["pareto"] else ""))
        for b, m in t["baselines"].items():
            print(f"  baseline {b:6s} acc {m['acc']:.3f} mcc {m['mcc']:+.3f} f1 {m['f1']:.3f}")
    for key, c in ctrl.items():
        print(f"\n== length control, {RUNS[key][1]} ({RUNS[key][2]}), n = {c['n']}; N2 vs S2 McNemar p = "
              f"{c['n2_vs_s2'][2]:.3f} (fixed/broken {c['n2_vs_s2'][0]}/{c['n2_vs_s2'][1]})")
        for s, r in c["rows"].items():
            print(f"  {s} acc {r['acc']:.3f} {ci(r['ci']['acc'])} mcc {r['mcc']:+.3f} predR {r['pos_rate']:.2f} "
                  f"tok {r['tokens']:,.0f} chars {r['chars']:,.0f}" +
                  (f"  same-as-S0 {c['same_as_s0'][s]:.2f}  p vs S0 {r['p']:.3f}" if s != "S0" else ""))
    if stab:
        print("\n== stability / agreement")
        for g, m, lv, a in stab:
            print(f"  {g:38s} {m:7s} {lv:6s} n {a['n']:3d} same {a['same']:.3f} flips {a['flips']:3d} "
                  f"kappa {a['kappa']:.2f} acc {a['acc_a']:.3f} vs {a['acc_b']:.3f} (McNemar p {a['p']:.2f})")
    if fr:
        print("\n== label changes: extra text vs identical re-run of S0 (Holm within model)")
        for (m, lv), v in fr.items():
            print(f"  {m:7s} {lv}  n {v['n']:3d}  changed by level {v['ctx']:3d}  by re-run {v['rep']:2d}  "
                  f"(only level {v['only_ctx']}, only re-run {v['only_rep']})  p {v['p']:.2g} holm {v['p_holm']:.2g}")
    if pool:
        print("\n== pooled over 4 models: accuracy change vs S0 (mean over models per case)")
        for lv, v in pool.items():
            print(f"  {lv}  n {v['n']}  d {v['d']:+.3f}  {ci(v['ci'], signed=True)}  p {v['p']:.3f} holm {v['p_holm']:.3f}")
    for key, c in msg.items():
        r0, r1 = c["rows"]["S0"], c["rows"]["M0"]
        print(f"\n== commit message, {RUNS[key][1]}: n {c['n']}  S0 acc {r0['acc']:.3f}  M0 acc {r1['acc']:.3f} "
              f"{ci(r1['ci']['acc'])}  d {ci(r1['ci']['d_acc'], signed=True)}  fixed/broken {c['fixed']}/{c['broken']} "
              f"p {c['p']:.3f} holm {c['p_holm']:.3f}  changed {1 - c['same']:.3f}  predR {r0['pos_rate']:.2f}->{r1['pos_rate']:.2f}")
    if msg_base:
        print(f"  message-length baseline acc {msg_base['acc']:.3f} mcc {msg_base['mcc']:+.3f}; "
              f"fix/bug keyword acc {msg_base['fix']['acc']:.3f}")
    if audit:
        print(f"\n== label audit against the dataset's fix links (RISKY cases): {audit['counts']}; inherited and not "
              f"changed by any linked fix: {audit['inherited_not_changed_by_any_fix']}")
    for lv, gdata in groups.items():
        print(f"   share called risky, {lv}: " + ", ".join(f"{g} {v:.2f}" for g, v in gdata["mean"].items())
              + f"; p {gdata['p']}")
    print("\n== invalid outputs per level (finish_reason=length in parentheses)")
    for key, inv in invalid.items():
        print(f"  {key:4s} " + "  ".join(f"{s} {v['invalid']}/{v['n']} ({v['length']})" for s, v in inv.items()))
    print(f"\nlines-added baseline (all {len(man)} cases): threshold {la_thr:g}, acc {full['acc']:.3f}, "
          f"mcc {full['mcc']:+.3f}, AUC {auc:.3f}")
    print(f"spending: " + ", ".join(f"{k} ${N.d['cost.' + k]}" for k in runs) +
          f", pilot ${N.d['cost.pilot']}; total ${N.d['cost.total']}")
    print(f"wrote {OUT.relative_to(ROOT)}/numbers.tex, tab_*.tex, stats.json and {FIGS.relative_to(ROOT)}/*.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
