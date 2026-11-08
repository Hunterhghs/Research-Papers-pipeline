"""Chart engine: YAML chart specs -> house-style SVG (PDF) + 300-dpi PNG (DOCX).

House rules (enforced here, not left to authors):
  * one y-axis only - no dual-axis charts
  * fixed categorical palette order from brand.yaml, never cycled
  * legend for >= 2 series, none for a single series
  * recessive hairline grid, no top/right spines, text in ink colors only
  * selective value labels (single-series bars by default, line end-points)
"""
from __future__ import annotations

import hashlib
import json
import math
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon  # noqa: E402
from matplotlib.ticker import FuncFormatter, MaxNLocator  # noqa: E402

from .parse import ReportError

CHART_TYPES = ("line", "area", "bar", "barh", "stacked_bar", "stacked_barh", "scatter",
               "donut", "waterfall", "heatmap", "dumbbell", "process", "matrix", "timeline")
ENGINE_VERSION = "7"
_FONTS_READY = False


def _setup_fonts(brand: dict, fonts_dir: Path) -> None:
    global _FONTS_READY
    if _FONTS_READY:
        return
    for f in sorted(fonts_dir.glob("*.ttf")):
        font_manager.fontManager.addfont(str(f))
    _FONTS_READY = True


def _style(brand: dict) -> dict:
    c = brand["colors"]
    sans = brand["fonts"]["sans"]
    return {
        "font.family": sans,
        "font.size": 8.5,
        "axes.edgecolor": c["rule"],
        "axes.linewidth": 0.8,
        "axes.labelcolor": c["ink_muted"],
        "axes.labelsize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "xtick.color": c["ink_muted"],
        "ytick.color": c["ink_muted"],
        "xtick.labelcolor": c["ink_muted"],
        "ytick.labelcolor": c["ink_muted"],
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.major.pad": 5,
        "ytick.major.pad": 5,
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "text.color": c["ink"],
        "svg.fonttype": "path",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }


# ---------------------------------------------------------------- helpers
class Fmt:
    def __init__(self, spec: dict, values=None):
        self.prefix = spec.get("prefix", "")
        self.suffix = spec.get("suffix", spec.get("unit", ""))
        fmt = spec.get("format")
        if not fmt:
            vals = [v for v in (values or []) if isinstance(v, (int, float))]
            fmt = "{:,.0f}" if vals and all(float(v).is_integer() for v in vals) else "{:,.1f}"
        self.fmt = fmt

    def __call__(self, v, _pos=None) -> str:
        try:
            s = self.fmt.format(v)
        except (ValueError, TypeError):
            s = str(v)
        if s.startswith("-"):
            return "−" + self.prefix + s[1:] + self.suffix
        return self.prefix + s + self.suffix

    def axis(self, v, _pos=None) -> str:
        # axis ticks: drop decimals when the tick is a whole number
        if isinstance(v, float) and v.is_integer() and "{:,.1f}" == self.fmt:
            return Fmt({"prefix": self.prefix, "suffix": self.suffix, "format": "{:,.0f}"})(v)
        return self(v)


def _series(spec: dict) -> list:
    s = spec.get("series")
    if s is None and "values" in spec:
        s = [{"name": spec.get("name", ""), "values": spec["values"]}]
    if not s:
        raise ReportError(f"Chart '{spec.get('type')}' (line {spec.get('_line')}) needs 'series' or 'values'")
    if len(s) > 6:
        raise ReportError(f"Chart at line {spec.get('_line')} has {len(s)} series; max is 6 "
                          "(fold extras into 'Other' or split into two charts)")
    return s


def _colors(brand: dict, n: int) -> list:
    pal = brand["colors"]["series"]
    return [pal[i] for i in range(n)]


def _grid(ax, brand, axis="y"):
    ax.grid(axis=axis, color=brand["colors"]["rule"], linewidth=0.6, linestyle="-")
    ax.set_axisbelow(True)


def _legend(ax, handles_labels=None, ncol=None, brand=None):
    h, lab = handles_labels or ax.get_legend_handles_labels()
    if len(lab) < 2:
        return
    if ncol is None:
        # fit the legend inside the figure width: ~95 characters per row at 8.5pt on 6in
        ncol = len(lab)
        while ncol > 1 and sum(len(str(x)) + 6 for x in lab[:ncol]) > 95:
            ncol -= 1
    ax.legend(h, lab, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=ncol,
              handlelength=1.0, handleheight=0.8, columnspacing=1.4, borderaxespad=0.3,
              labelcolor=brand["colors"]["ink"] if brand else None)


def _labels(spec, axes_obj):
    if spec.get("x_label"):
        axes_obj.set_xlabel(spec["x_label"])
    if spec.get("y_label"):
        axes_obj.set_ylabel(spec["y_label"])


def _check_len(spec, cats, values, name):
    if len(values) != len(cats):
        raise ReportError(f"Chart at line {spec.get('_line')}: series '{name}' has {len(values)} values "
                          f"but there are {len(cats)} categories")


def _wrap(s, width):
    return "\n".join(textwrap.wrap(str(s), width, break_long_words=False, break_on_hyphens=False)) if s else ""


def _height_pt(fig, artist) -> float:
    """Rendered height of a text artist in points."""
    r = fig.canvas.get_renderer()
    return artist.get_window_extent(renderer=r).height * 72 / fig.dpi


# ---------------------------------------------------------------- chart types
def _line(ax, spec, brand, area=False):
    cats = [str(c) for c in spec.get("categories") or spec.get("x") or []]
    series = _series(spec)
    cols = _colors(brand, len(series))
    allv = [v for s in series for v in s["values"] if v is not None]
    f = Fmt(spec, allv)
    x = list(range(len(cats)))
    for s, col in zip(series, cols):
        _check_len(spec, cats, s["values"], s.get("name"))
        pts = [(xi, v) for xi, v in zip(x, s["values"]) if v is not None]
        xs, ys = zip(*pts)
        dashed = s.get("projected_from") is not None
        if dashed:
            k = cats.index(str(s["projected_from"]))
            solid = [(a, b) for a, b in pts if a <= k]
            proj = [(a, b) for a, b in pts if a >= k]
            ax.plot(*zip(*solid), color=col, linewidth=1.8, solid_capstyle="round", label=s.get("name"))
            ax.plot(*zip(*proj), color=col, linewidth=1.8, linestyle=(0, (3, 2)))
        else:
            ax.plot(xs, ys, color=col, linewidth=1.8, solid_capstyle="round", solid_joinstyle="round",
                    label=s.get("name"))
        if area:
            ax.fill_between(xs, ys, color=col, alpha=0.10, linewidth=0)
        ax.scatter([xs[-1]], [ys[-1]], s=28, color=col, edgecolor="white", linewidth=1.5, zorder=5)
        if spec.get("end_labels", True):
            ax.annotate(f(ys[-1]), (xs[-1], ys[-1]), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=8, color=brand["colors"]["ink"], fontweight="semibold")
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    if len(cats) > 12:
        step = math.ceil(len(cats) / 10)
        for i, lbl in enumerate(ax.get_xticklabels()):
            lbl.set_visible(i % step == 0 or i == len(cats) - 1)
    ax.yaxis.set_major_formatter(FuncFormatter(f.axis))
    ax.yaxis.set_major_locator(MaxNLocator(5))
    if area or spec.get("zero_base", True):
        lo = min(allv)
        if lo >= 0:
            ax.set_ylim(bottom=0)
    ax.set_xlim(-0.3, len(cats) - 1 + 0.6)
    _labels(spec, ax)
    _grid(ax, brand)
    ax.spines["left"].set_visible(False)
    _legend(ax, brand=brand)


def _bar(ax, spec, brand, horizontal=False, stacked=False):
    cats = [str(c) for c in spec.get("categories") or spec.get("x") or []]
    series = _series(spec)
    cols = _colors(brand, len(series))
    neutral = brand["colors"]["neutral"]
    allv = [v for s in series for v in s["values"]]
    f = Fmt(spec, allv)
    n = len(series)
    idx = list(range(len(cats)))
    if horizontal:
        idx = idx[::-1]  # first category on top
    slot = 0.72
    width = slot if (stacked or n == 1) else slot / n
    bottoms = [0.0] * len(cats)
    highlight = {str(h) for h in (spec.get("highlight") or [])}
    show_labels = spec.get("labels", n == 1 or stacked is False and n <= 2 and len(cats) <= 6)
    for si, (s, col) in enumerate(zip(series, cols)):
        _check_len(spec, cats, s["values"], s.get("name"))
        offs = 0 if (stacked or n == 1) else (si - (n - 1) / 2) * width
        pos = [i + offs for i in idx]
        colors = [col if (not highlight or c in highlight) else neutral for c in cats] if n == 1 else col
        kw = dict(color=colors, edgecolor="white", linewidth=1.0 if (stacked or n > 1) else 0, label=s.get("name"))
        if horizontal:
            bars = ax.barh(pos, s["values"], height=width * (0.86 if n > 1 and not stacked else 1),
                           left=bottoms if stacked else None, **kw)
        else:
            bars = ax.bar(pos, s["values"], width=width * (0.86 if n > 1 and not stacked else 1),
                          bottom=bottoms if stacked else None, **kw)
        if show_labels and not stacked:
            for b, v in zip(bars, s["values"]):
                if horizontal:
                    ax.annotate(f(v), (b.get_x() + b.get_width(), b.get_y() + b.get_height() / 2),
                                xytext=(4 if v >= 0 else -4, 0), textcoords="offset points",
                                ha="left" if v >= 0 else "right", va="center", fontsize=8,
                                color=brand["colors"]["ink"])
                else:
                    ax.annotate(f(v), (b.get_x() + b.get_width() / 2, b.get_y() + b.get_height()),
                                xytext=(0, 3 if v >= 0 else -10), textcoords="offset points",
                                ha="center", fontsize=8, color=brand["colors"]["ink"])
        if stacked:
            bottoms = [a + b for a, b in zip(bottoms, s["values"])]
    if stacked and spec.get("totals", True):
        for i, tot in zip(idx, bottoms):
            if horizontal:
                ax.annotate(f(tot), (tot, i), xytext=(4, 0), textcoords="offset points", va="center",
                            fontsize=8, color=brand["colors"]["ink"], fontweight="semibold")
            else:
                ax.annotate(f(tot), (i, tot), xytext=(0, 3), textcoords="offset points", ha="center",
                            fontsize=8, color=brand["colors"]["ink"], fontweight="semibold")
    if horizontal:
        ax.set_yticks(idx)
        ax.set_yticklabels([_wrap(c, 28) for c in cats])
        ax.xaxis.set_major_formatter(FuncFormatter(f.axis))
        ax.xaxis.set_major_locator(MaxNLocator(5))
        _grid(ax, brand, "x")
        ax.spines["bottom"].set_visible(False)
        ax.margins(x=0.08)
    else:
        ax.set_xticks(idx)
        wrap = 14 if len(cats) <= 6 else 9
        ax.set_xticklabels([_wrap(c, wrap) for c in cats])
        ax.yaxis.set_major_formatter(FuncFormatter(f.axis))
        ax.yaxis.set_major_locator(MaxNLocator(5))
        _grid(ax, brand)
        ax.spines["left"].set_visible(False)
        ax.margins(y=0.08)
    _labels(spec, ax)
    _legend(ax, brand=brand)


def _scatter(ax, spec, brand):
    pts = spec.get("points") or []
    if not pts:
        raise ReportError(f"Scatter chart at line {spec.get('_line')} needs 'points: [{{label, x, y}}]'")
    groups = []
    for p in pts:
        g = p.get("group", "")
        if g not in groups:
            groups.append(g)
    cols = dict(zip(groups, _colors(brand, len(groups))))
    fx = Fmt({k[2:]: v for k, v in spec.items() if k.startswith("x_")}, [p["x"] for p in pts])
    fy = Fmt({k[2:]: v for k, v in spec.items() if k.startswith("y_")}, [p["y"] for p in pts])
    for g in groups:
        gp = [p for p in pts if p.get("group", "") == g]
        sizes = [max(30, float(p.get("size", 1)) * 40) for p in gp]
        ax.scatter([p["x"] for p in gp], [p["y"] for p in gp], s=sizes, color=cols[g], alpha=0.9,
                   edgecolor="white", linewidth=1.2, label=g or None, zorder=3)
    for p in pts:
        if p.get("label"):
            ax.annotate(p["label"], (p["x"], p["y"]), xytext=(6, 4), textcoords="offset points",
                        fontsize=7.5, color=brand["colors"]["ink"])
    ax.xaxis.set_major_formatter(FuncFormatter(fx.axis))
    ax.yaxis.set_major_formatter(FuncFormatter(fy.axis))
    _grid(ax, brand, "both")
    if spec.get("trend"):
        import numpy as np
        xs = np.array([p["x"] for p in pts], float)
        ys = np.array([p["y"] for p in pts], float)
        k, b0 = np.polyfit(xs, ys, 1)
        xx = np.linspace(xs.min(), xs.max(), 20)
        ax.plot(xx, k * xx + b0, color=brand["colors"]["neutral"], linewidth=1, linestyle=(0, (4, 3)), zorder=2)
    _labels(spec, ax)
    if len(groups) > 1:
        _legend(ax, brand=brand)


def _donut(fig, spec, brand):
    cats = spec.get("categories") or []
    vals = spec.get("values") or []
    if not cats or len(cats) != len(vals):
        raise ReportError(f"Donut chart at line {spec.get('_line')} needs equal-length 'categories' and 'values'")
    if len(cats) > 6:
        raise ReportError(f"Donut chart at line {spec.get('_line')}: max 6 slices (fold extras into 'Other')")
    f = Fmt(spec, vals)
    ax = fig.add_axes([0.02, 0.04, 0.45, 0.92])
    cols = _colors(brand, len(cats))
    ax.pie(vals, colors=cols, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.32, edgecolor="white", linewidth=2))
    ax.set_aspect("equal")
    total = sum(vals)
    if spec.get("center_text"):
        ax.text(0, 0.08, spec["center_text"], ha="center", va="center", fontsize=15,
                fontweight="semibold", color=brand["colors"]["navy"])
        if spec.get("center_label"):
            ax.text(0, -0.2, _wrap(spec["center_label"], 16), ha="center", va="center", fontsize=8,
                    color=brand["colors"]["ink_muted"])
    lx = fig.add_axes([0.52, 0.04, 0.46, 0.92])
    lx.axis("off")
    n = len(cats)
    for i, (c, v, col) in enumerate(zip(cats, vals, cols)):
        y = 1 - (i + 0.5) / max(n, 4)
        lx.add_patch(FancyBboxPatch((0, y - 0.025), 0.035, 0.05, boxstyle="round,pad=0,rounding_size=0.008",
                                    color=col, transform=lx.transAxes, clip_on=False))
        pct = 100 * v / total if total else 0
        lx.text(0.07, y, _wrap(c, 34), va="center", fontsize=9, color=brand["colors"]["ink"], transform=lx.transAxes)
        lx.text(1.0, y, f(v) if spec.get("show_values") else f"{pct:.0f}%", va="center", ha="right", fontsize=9,
                fontweight="semibold", color=brand["colors"]["ink"], transform=lx.transAxes)


def _waterfall(ax, spec, brand):
    cats = [str(c) for c in spec.get("categories") or []]
    vals = spec.get("values") or []
    if len(cats) != len(vals):
        raise ReportError(f"Waterfall at line {spec.get('_line')}: categories and values differ in length")
    f = Fmt(spec, vals)
    c = brand["colors"]
    totals = set(spec.get("totals_at", [0, len(vals) - 1] if spec.get("total", True) else []))
    run = 0.0
    prev_top = None
    for i, (cat, v) in enumerate(zip(cats, vals)):
        if i in totals:
            bottom, height, col = 0, v, c["navy"]
            run = v
        else:
            bottom = run if v >= 0 else run + v
            height = abs(v)
            col = c["positive"] if v >= 0 else c["negative"]
            run += v
        ax.bar(i, height, bottom=bottom, width=0.6, color=col, linewidth=0)
        top = bottom + height
        label = f(v) if i in totals else ("+" + f(v) if v >= 0 else f(v))
        ax.annotate(label, (i, top), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8,
                    color=c["ink"], fontweight="semibold" if i in totals else "normal")
        if prev_top is not None:
            ax.plot([i - 1 + 0.3, i - 0.3], [prev_top, prev_top], color=c["neutral"], linewidth=0.7)
        prev_top = run
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels([_wrap(x, 11) for x in cats])
    ax.yaxis.set_major_formatter(FuncFormatter(f.axis))
    ax.yaxis.set_major_locator(MaxNLocator(5))
    _grid(ax, brand)
    ax.spines["left"].set_visible(False)
    ax.margins(y=0.1)
    _labels(spec, ax)


def _heatmap(ax, spec, brand):
    rows = spec.get("rows") or []
    cols_ = spec.get("columns") or []
    vals = spec.get("values") or []
    if len(vals) != len(rows) or any(len(r) != len(cols_) for r in vals):
        raise ReportError(f"Heatmap at line {spec.get('_line')}: 'values' must be rows x columns")
    cmap = LinearSegmentedColormap.from_list("hh", brand["colors"]["sequential"])
    flat = [v for r in vals for v in r]
    f = Fmt(spec, flat)
    vmin, vmax = spec.get("min", min(flat)), spec.get("max", max(flat))
    ax.imshow(vals, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    for i, r in enumerate(vals):
        for j, v in enumerate(r):
            frac = (v - vmin) / (vmax - vmin) if vmax > vmin else 0
            ax.text(j, i, f(v), ha="center", va="center", fontsize=8,
                    color="white" if frac > 0.55 else brand["colors"]["ink"])
    ax.set_xticks(range(len(cols_)))
    ax.set_xticklabels([_wrap(c, 12) for c in cols_])
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(rows)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([x - 0.5 for x in range(1, len(cols_))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(rows))], minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", length=0)


def _dumbbell(ax, spec, brand):
    cats = [str(c) for c in spec.get("categories") or []]
    series = _series(spec)
    if len(series) != 2:
        raise ReportError(f"Dumbbell chart at line {spec.get('_line')} needs exactly 2 series (e.g. before/after)")
    a, b = series
    _check_len(spec, cats, a["values"], a.get("name"))
    _check_len(spec, cats, b["values"], b.get("name"))
    ca, cb = _colors(brand, 2)
    f = Fmt(spec, a["values"] + b["values"])
    ys = list(range(len(cats)))[::-1]
    for y, va, vb in zip(ys, a["values"], b["values"]):
        ax.plot([va, vb], [y, y], color=brand["colors"]["rule"], linewidth=2.2, zorder=1)
        ax.annotate(f(vb), (vb, y), xytext=(8 if vb >= va else -8, 0), textcoords="offset points",
                    ha="left" if vb >= va else "right", va="center", fontsize=8, color=brand["colors"]["ink"])
    ax.scatter(a["values"], ys, s=46, color=ca, edgecolor="white", linewidth=1.5, zorder=3, label=a.get("name"))
    ax.scatter(b["values"], ys, s=46, color=cb, edgecolor="white", linewidth=1.5, zorder=3, label=b.get("name"))
    ax.set_yticks(ys)
    ax.set_yticklabels([_wrap(c, 30) for c in cats])
    ax.xaxis.set_major_formatter(FuncFormatter(f.axis))
    _grid(ax, brand, "x")
    ax.spines["left"].set_visible(False)
    ax.margins(x=0.1, y=0.08)
    _labels(spec, ax)
    _legend(ax, brand=brand)


def _process_lines(spec, width_in):
    """Wrap widths and the tallest card's content height (points) for a process diagram."""
    steps = spec.get("steps") or []
    n = max(len(steps), 1)
    card_in = (width_in - 0.14 * (n - 1)) / n
    chars = max(10, int((card_in - 0.2) * 72 / (8 * 0.47)))
    tchars = max(8, int((card_in - 0.2) * 72 / (9 * 0.52)))
    tallest = 0.0
    for s in steps:
        tl = len(_wrap(s.get("title", ""), tchars).split("\n")) if s.get("title") else 0
        bl = len(_wrap(s.get("text", ""), chars).split("\n")) if s.get("text") else 0
        tallest = max(tallest, tl * 9 * 1.45 + 6 + bl * 8 * 1.78)
    return chars, tchars, tallest


def _process(fig, spec, brand):
    width_in, height_in = fig.get_figwidth(), fig.get_figheight()
    steps = spec.get("steps") or []
    if not 2 <= len(steps) <= 6:
        raise ReportError(f"Process diagram at line {spec.get('_line')} needs 2-6 'steps'")
    c = brand["colors"]
    ax = fig.add_axes([0, 0, 1, 1])
    W, H = width_in * 72, height_in * 72
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)  # work in points
    ax.axis("off")
    n = len(steps)
    gap = 0.14 * 72
    tipw = 8
    w = (W - tipw - gap * (n - 1)) / n
    chars, tchars, _ = _process_lines(spec, width_in)
    head_h = 22
    for i, st in enumerate(steps):
        x0 = i * (w + gap)
        tip = tipw if i < n - 1 else 0
        notch = tipw if i > 0 else 0
        y1, y0 = H - 1, H - 1 - head_h
        head = [(x0, y1), (x0 + w, y1), (x0 + w + tip, (y0 + y1) / 2), (x0 + w, y0), (x0, y0), (x0 + notch, (y0 + y1) / 2)]
        ax.add_patch(Polygon(head, closed=True, color=c["navy"] if i % 2 == 0 else c["blue"], linewidth=0))
        ax.text(x0 + notch + 7, (y0 + y1) / 2, f"STEP {i + 1:02d}", color="white", fontsize=7.5,
                fontweight="bold", va="center")
        card_top = y0 - 5
        ax.add_patch(FancyBboxPatch((x0, 1), w, card_top - 1, boxstyle="round,pad=0,rounding_size=3",
                                    color=c["tint"], linewidth=0))
        y = card_top - 8
        if st.get("title"):
            tt = ax.text(x0 + 8, y, _wrap(st["title"], tchars), fontsize=9, fontweight="semibold",
                         color=c["navy"], va="top", linespacing=1.15)
            y -= _height_pt(fig, tt) + 4
        ax.text(x0 + 8, y, _wrap(st.get("text", ""), chars), fontsize=8, color=c["ink"], va="top",
                linespacing=1.35)


def _matrix(fig, spec, brand):
    q = spec.get("quadrants") or []
    if len(q) != 4:
        raise ReportError(f"Matrix at line {spec.get('_line')} needs 4 'quadrants' (top-left, top-right, bottom-left, bottom-right)")
    c = brand["colors"]
    ax = fig.add_axes([0.07, 0.1, 0.92, 0.88])
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    pos = [(0, 1), (1, 1), (0, 0), (1, 0)]
    fills = [c["tint"], c["tint_accent"], "#FFFFFF", c["tint"]]
    for (x, y), quad, fill in zip(pos, q, fills):
        ax.add_patch(FancyBboxPatch((x + 0.015, y + 0.015), 0.97, 0.97, boxstyle="round,pad=0,rounding_size=0.03",
                                    facecolor=fill, edgecolor=c["rule"], linewidth=0.8))
        ax.text(x + 0.06, y + 0.9, quad.get("title", ""), fontsize=10, fontweight="semibold", color=c["navy"], va="top")
        ax.text(x + 0.06, y + 0.76, _wrap(quad.get("text", ""), 48), fontsize=8, color=c["ink"], va="top",
                linespacing=1.35)
    for p in spec.get("points") or []:
        ax.scatter([p["x"] * 2], [p["y"] * 2], s=40, color=c["accent"], edgecolor="white", linewidth=1.4, zorder=4)
        ax.annotate(p.get("label", ""), (p["x"] * 2, p["y"] * 2), xytext=(6, -3), textcoords="offset points",
                    fontsize=7.5, color=c["ink"], zorder=5)
    ax.annotate("", xy=(2.0, -0.06), xytext=(0, -0.06), xycoords="data",
                arrowprops=dict(arrowstyle="-|>", color=c["ink_muted"], linewidth=0.8), annotation_clip=False)
    ax.annotate("", xy=(-0.04, 2.0), xytext=(-0.04, 0), xycoords="data",
                arrowprops=dict(arrowstyle="-|>", color=c["ink_muted"], linewidth=0.8), annotation_clip=False)
    ax.text(1, -0.13, spec.get("x_label", ""), ha="center", va="top", fontsize=8.5, color=c["ink_muted"])
    ax.text(-0.08, 1, spec.get("y_label", ""), ha="right", va="center", rotation=90, fontsize=8.5, color=c["ink_muted"])


def _timeline(fig, spec, brand):
    ev = spec.get("events") or []
    if not 3 <= len(ev) <= 9:
        raise ReportError(f"Timeline at line {spec.get('_line')} needs 3-9 'events'")
    c = brand["colors"]
    n = len(ev)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-1, 1)
    ax.axis("off")
    ax.plot([-0.45, n - 0.55], [0, 0], color=c["navy"], linewidth=1.6)
    # labels alternate above/below the line, so each may use ~1.7 slots of width
    slot_in = fig.get_figwidth() / n * 1.7
    chars = max(14, int((slot_in - 0.2) * 72 / (7.5 * 0.47)))
    tchars = max(12, int((slot_in - 0.2) * 72 / (8.5 * 0.52)))
    for i, e in enumerate(ev):
        up = i % 2 == 0
        sgn = 1 if up else -1
        # first/last labels hug the inside edge so they never leave the canvas
        ha = "left" if i == 0 else ("right" if i == n - 1 else "center")
        dx = -10 if i == 0 else (10 if i == n - 1 else 0)
        ax.scatter([i], [0], s=60, color=c["accent"] if e.get("highlight") else c["blue"], edgecolor="white",
                   linewidth=1.8, zorder=4)
        ax.annotate("", (i, 0), xytext=(0, sgn * 14), textcoords="offset points",
                    arrowprops=dict(arrowstyle="-", color=c["rule"], linewidth=0.8))
        ax.annotate(str(e.get("date", "")), (i, 0), xytext=(0, -sgn * 7), textcoords="offset points",
                    ha="center", va="top" if up else "bottom", fontsize=8, fontweight="bold", color=c["blue"])
        title = _wrap(e.get("title", ""), tchars)
        body = _wrap(e.get("text", ""), chars)
        if up:
            b = ax.annotate(body, (i, 0), xytext=(dx, 18), textcoords="offset points", ha=ha, va="bottom",
                            fontsize=7.5, color=c["ink"], linespacing=1.3, multialignment=ha if ha != "center" else "center")
            off = 18 + (_height_pt(fig, b) if body else 0) + 3
            ax.annotate(title, (i, 0), xytext=(dx, off), textcoords="offset points", ha=ha, va="bottom",
                        fontsize=8.5, fontweight="semibold", color=c["navy"], linespacing=1.15)
        else:
            tt = ax.annotate(title, (i, 0), xytext=(dx, -18), textcoords="offset points", ha=ha, va="top",
                             fontsize=8.5, fontweight="semibold", color=c["navy"], linespacing=1.15)
            off = -18 - (_height_pt(fig, tt) if title else 0) - 3
            ax.annotate(body, (i, 0), xytext=(dx, off), textcoords="offset points", ha=ha, va="top",
                        fontsize=7.5, color=c["ink"], linespacing=1.3, multialignment=ha if ha != "center" else "center")


def _content_bbox(fig, pad_in: float = 0.06):
    """Full-width bbox (inches) trimmed vertically to what is actually drawn."""
    from matplotlib.transforms import Bbox

    r = fig.canvas.get_renderer()
    ys = []
    for ax in fig.axes:
        for a in list(ax.texts) + list(ax.collections) + list(ax.lines) + list(ax.patches):
            try:
                e = a.get_window_extent(r)
            except Exception:
                continue
            if e.height > 0 or e.width > 0:
                ys += [e.y0, e.y1]
    if not ys:
        return None
    y0 = max(min(ys) / fig.dpi - pad_in, 0)
    y1 = min(max(ys) / fig.dpi + pad_in, fig.get_figheight())
    return Bbox([[0, y0], [fig.get_figwidth(), y1]])


# ---------------------------------------------------------------- entry point
def render(spec: dict, brand: dict, fonts_dir: Path, out_dir: Path, width_in: float, name: str) -> dict:
    """Render a chart spec. Returns {"svg": Path, "png": Path, "height_in": float}."""
    _setup_fonts(brand, fonts_dir)
    ctype = spec.get("type")
    if ctype not in CHART_TYPES:
        raise ReportError(f"Unknown chart type '{ctype}' at line {spec.get('_line')}. "
                          f"Use one of: {', '.join(CHART_TYPES)}")
    if spec.get("secondary_axis") or spec.get("y2"):
        raise ReportError(f"Chart at line {spec.get('_line')}: dual-axis charts are not allowed by house style. "
                          "Use two charts or index both series to a common base.")
    default_h = {"process": 2.0, "timeline": 2.9, "matrix": 4.0, "donut": 2.8}.get(ctype, brand["layout"]["figure_height_in"])
    if ctype == "process" and "height" not in spec:
        _, _, nlines = _process_lines(spec, width_in)
        default_h = (22 + 5 + 8 + nlines + 14) / 72
    height = float(spec.get("height", default_h))
    height = min(max(height, 1.8), 5.0)

    clean = {k: v for k, v in spec.items() if not k.startswith("_") and k not in ("caption", "source", "id")}
    key = hashlib.sha1(json.dumps([clean, brand["colors"], brand["fonts"], width_in, height, ENGINE_VERSION],
                                  sort_keys=True, default=str).encode()).hexdigest()[:10]
    out_dir.mkdir(parents=True, exist_ok=True)
    svg = out_dir / f"{name}-{key}.svg"
    png = out_dir / f"{name}-{key}.png"
    if svg.exists() and png.exists():
        return {"svg": svg, "png": png, "height_in": height}

    with plt.rc_context(_style(brand)):
        fig = plt.figure(figsize=(width_in, height))
        if ctype in ("donut", "process", "matrix", "timeline"):
            {"donut": _donut, "process": _process, "matrix": _matrix, "timeline": _timeline}[ctype](fig, spec, brand)
            bbox = _content_bbox(fig) if ctype == "timeline" else None
        else:
            ax = fig.add_subplot(111)
            if ctype in ("line", "area"):
                _line(ax, spec, brand, area=ctype == "area")
            elif ctype in ("bar", "barh", "stacked_bar", "stacked_barh"):
                _bar(ax, spec, brand, horizontal=ctype.endswith("barh"), stacked=ctype.startswith("stacked"))
            elif ctype == "scatter":
                _scatter(ax, spec, brand)
            elif ctype == "waterfall":
                _waterfall(ax, spec, brand)
            elif ctype == "heatmap":
                _heatmap(ax, spec, brand)
            elif ctype == "dumbbell":
                _dumbbell(ax, spec, brand)
            cats = [str(c) for c in spec.get("categories") or spec.get("x") or []]
            for note in spec.get("annotations") or []:
                nx = note["x"]
                if str(nx) in cats:
                    nx = cats.index(str(nx))
                    if ctype.endswith("barh"):
                        nx, ny = note["y"], len(cats) - 1 - nx
                    else:
                        ny = note["y"]
                else:
                    ny = note["y"]
                ax.annotate(_wrap(note.get("text", ""), 26), (nx, ny),
                            xytext=(note.get("dx", 10), note.get("dy", 18)), textcoords="offset points",
                            fontsize=7.5, color=brand["colors"]["ink"],
                            arrowprops=dict(arrowstyle="-", color=brand["colors"]["ink_muted"], linewidth=0.6))
            fig.tight_layout(pad=0.4)
            bbox = None
        fig.savefig(svg, format="svg", bbox_inches=bbox, pad_inches=0.08)
        fig.savefig(png, format="png", dpi=300, bbox_inches=bbox, pad_inches=0.08)
        plt.close(fig)
    return {"svg": svg, "png": png, "height_in": height}
