"""Command line: python -m hhreport <command> ...

  new    <slug> --title "..."      scaffold reports/<slug>/report.md from the template
  lint   <slug>                    parse + validate the markdown only (fast)
  build  <slug> [--pdf|--docx]     render PDF and DOCX into output/<slug>/
  qa     <slug> [--check-links]    build, then run the quality gate
  make   <slug>                    build + QA + live link check (the full gate)
  batch  [slugs...] [--all]        build + QA many reports, print a summary table
  queue                            show queue/topics.csv status
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .build import BUILD_DIR, OUTPUT_DIR, REPO, REPORTS_DIR, build, load_brand, resolve_report
from .parse import ReportError, load

QUEUE = REPO / "queue" / "topics.csv"


def cmd_new(a) -> int:
    slug = re.sub(r"[^a-z0-9-]+", "-", a.slug.lower()).strip("-")
    dst = REPORTS_DIR / slug
    if dst.exists():
        print(f"reports/{slug} already exists")
        return 1
    shutil.copytree(REPORTS_DIR / "_template", dst)
    md = dst / "report.md"
    text = md.read_text(encoding="utf-8")
    today = dt.date.today()
    n = len([p for p in REPORTS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")])
    repl = {
        "{{TITLE}}": a.title or slug.replace("-", " ").title(),
        "{{DATE}}": today.strftime("%B %Y"),
        "{{REPORT_ID}}": f"HH-{today.year}-{n:03d}",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    md.write_text(text, encoding="utf-8")
    print(f"Created reports/{slug}/report.md")
    return 0


def cmd_lint(a) -> int:
    try:
        doc = load(resolve_report(a.slug))
    except ReportError as e:
        print(f"ERROR {e}")
        return 1
    s = doc.stats
    print(f"OK  sections {s['sections']} | figures {s['figures']} | tables {s['tables']} | "
          f"words {s['words']:,} | links {s['links']}")
    for w in doc.warnings:
        print(f"  warning {w}")
    return 0


def _docx_pdf(docx: Path) -> None:
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        print("  (skip) LibreOffice not installed; cannot render DOCX preview")
        return
    out = BUILD_DIR / docx.stem
    subprocess.run([exe, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(docx)],
                   capture_output=True)
    pdf = out / f"{docx.stem}.pdf"
    if pdf.exists():
        target = out / "docx-preview.pdf"
        pdf.replace(target)
        print(f"  DOCX preview (LibreOffice render) {target.relative_to(REPO)}")


def _build_and_qa(slug, a, do_qa=True, links=False):
    from . import qa

    try:
        res = build(slug, pdf=not getattr(a, "docx_only", False), docx=not getattr(a, "pdf_only", False))
    except ReportError as e:
        print(f"ERROR {e}")
        return None, None
    if getattr(a, "docx_preview", False) and "docx" in res["outputs"]:
        _docx_pdf(res["outputs"]["docx"])
    if not do_qa:
        return res, None
    r = qa.run(res, check_links_online=links, preview=not getattr(a, "no_preview", False),
               strict=getattr(a, "strict", False))
    qa.print_report(r)
    return res, r


def cmd_build(a) -> int:
    res, _ = _build_and_qa(a.slug, a, do_qa=False)
    return 0 if res else 1


def cmd_qa(a) -> int:
    res, r = _build_and_qa(a.slug, a, do_qa=True, links=a.check_links)
    return 0 if (r and r["pass"]) else 1


def cmd_make(a) -> int:
    a.check_links = True
    return cmd_qa(a)


def cmd_batch(a) -> int:
    slugs = a.slugs
    if a.all or not slugs:
        slugs = sorted(p.name for p in REPORTS_DIR.iterdir()
                       if p.is_dir() and not p.name.startswith("_") and (p / "report.md").exists())
    rows = []
    for slug in slugs:
        print(f"\n=== {slug}")
        res, r = _build_and_qa(slug, a, do_qa=True, links=a.check_links)
        if r is None:
            rows.append((slug, "ERROR", "-", "-", "-", "-"))
            continue
        s = r["stats"]
        rows.append((slug, "PASS" if r["pass"] else "FAIL", s["pages"], s["figures"], s["links"], len(r["errors"])))
    print("\nSUMMARY")
    print(f"  {'report':40} {'result':6} {'pages':>5} {'figs':>4} {'links':>5} {'errors':>6}")
    for row in rows:
        print(f"  {row[0]:40} {row[1]:6} {row[2]!s:>5} {row[3]!s:>4} {row[4]!s:>5} {row[5]!s:>6}")
    return 0 if all(r[1] == "PASS" for r in rows) else 1


def cmd_queue(a) -> int:
    if not QUEUE.exists():
        print("queue/topics.csv not found")
        return 1
    with QUEUE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        print(f"  [{r.get('status', ''):^8}] {r.get('slug', ''):38} {r.get('title', '')}")
    todo = [r for r in rows if r.get("status", "").strip().lower() == "todo"]
    print(f"\n{len(todo)} todo / {len(rows)} total")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="hhreport", description="H Heuristics research report pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("new", help="scaffold a new report")
    s.add_argument("slug")
    s.add_argument("--title")
    s.set_defaults(fn=cmd_new)

    s = sub.add_parser("lint", help="validate markdown only")
    s.add_argument("slug")
    s.set_defaults(fn=cmd_lint)

    def common(sp):
        sp.add_argument("--pdf-only", action="store_true")
        sp.add_argument("--docx-only", action="store_true")
        sp.add_argument("--docx-preview", action="store_true", help="also render the DOCX via LibreOffice")
        sp.add_argument("--no-preview", action="store_true", help="skip the contact-sheet PNG")
        sp.add_argument("--strict", action="store_true", help="treat warnings as errors")

    s = sub.add_parser("build", help="render PDF + DOCX")
    s.add_argument("slug")
    common(s)
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("qa", help="build + quality gate")
    s.add_argument("slug")
    s.add_argument("--check-links", action="store_true")
    common(s)
    s.set_defaults(fn=cmd_qa)

    s = sub.add_parser("make", help="build + QA + live link check")
    s.add_argument("slug")
    common(s)
    s.set_defaults(fn=cmd_make)

    s = sub.add_parser("batch", help="build + QA many reports")
    s.add_argument("slugs", nargs="*")
    s.add_argument("--all", action="store_true")
    s.add_argument("--check-links", action="store_true")
    common(s)
    s.set_defaults(fn=cmd_batch)

    s = sub.add_parser("queue", help="show the topic queue")
    s.set_defaults(fn=cmd_queue)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
