"""Build orchestration: report.md -> figures -> PDF (Typst) + DOCX."""
from __future__ import annotations

import shutil
import time
from pathlib import Path

import yaml

from . import charts
from .parse import Document, ReportError, figure_width, load

REPO = Path(__file__).resolve().parents[1]
BRAND_DIR = REPO / "brand"
FONTS_DIR = BRAND_DIR / "fonts"
REPORTS_DIR = REPO / "reports"
BUILD_DIR = REPO / "build"
OUTPUT_DIR = REPO / "output"


def load_brand() -> dict:
    return yaml.safe_load((BRAND_DIR / "brand.yaml").read_text(encoding="utf-8"))


def resolve_report(name: str) -> Path:
    """Accept a slug, a report directory or a path to report.md."""
    p = Path(name)
    if p.is_file():
        return p.resolve()
    if p.is_dir() and (p / "report.md").exists():
        return (p / "report.md").resolve()
    cand = REPORTS_DIR / name / "report.md"
    if cand.exists():
        return cand
    raise ReportError(f"No report found for '{name}'. Expected reports/{name}/report.md")


def slug_of(report_md: Path) -> str:
    return report_md.parent.name


def prepare_figures(doc: Document, brand: dict, build: Path) -> dict:
    figdir = build / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    out: dict = {}
    from .parse import _walk

    for b in _walk(doc.blocks):
        if b["t"] != "figure":
            continue
        w = figure_width(b, brand["layout"], doc.warnings)
        name = f"fig{b['number']:02d}"
        if b["kind"] == "chart":
            r = charts.render(b["spec"], brand, FONTS_DIR, figdir, w, name)
            out[b["number"]] = {"svg": r["svg"], "png": r["png"], "width_in": w,
                                "rel": f"figures/{r['svg'].name}"}
        else:
            src = (doc.source_dir / b["path"]).resolve()
            dst = figdir / f"{name}{src.suffix.lower()}"
            shutil.copyfile(src, dst)
            png = dst
            if src.suffix.lower() == ".svg":
                import pymupdf as fitz

                svgdoc = fitz.open(str(dst))
                pix = svgdoc[0].get_pixmap(dpi=300)
                png = figdir / f"{name}.png"
                pix.save(str(png))
            out[b["number"]] = {"svg": dst, "png": png, "width_in": w, "rel": f"figures/{dst.name}"}
    return out


def build(name: str, pdf: bool = True, docx: bool = True, quiet: bool = False) -> dict:
    t0 = time.time()
    report_md = resolve_report(name)
    slug = slug_of(report_md)
    brand = load_brand()
    doc = load(report_md)
    build_dir = BUILD_DIR / slug
    build_dir.mkdir(parents=True, exist_ok=True)
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    figures = prepare_figures(doc, brand, build_dir)
    result = {"slug": slug, "doc": doc, "brand": brand, "build_dir": build_dir, "outputs": {}}

    if pdf:
        from .render_typst import TEMPLATE, compile_pdf, to_typst

        shutil.copyfile(TEMPLATE, build_dir / TEMPLATE.name)
        typ = build_dir / "report.typ"
        typ.write_text(to_typst(doc, brand, figures), encoding="utf-8")
        pdf_path = out_dir / f"{slug}.pdf"
        compile_pdf(typ, pdf_path, FONTS_DIR)
        result["outputs"]["pdf"] = pdf_path
    if docx:
        from .render_docx import render_docx

        docx_path = out_dir / f"{slug}.docx"
        render_docx(doc, brand, figures, docx_path)
        result["outputs"]["docx"] = docx_path

    result["seconds"] = round(time.time() - t0, 1)
    if not quiet:
        for w in doc.warnings:
            print(f"  warning: {w}")
        for k, v in result["outputs"].items():
            print(f"  {k.upper():5} {v.relative_to(REPO)}")
        print(f"  built in {result['seconds']}s")
    return result
