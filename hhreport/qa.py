"""Quality gate for built reports.

Checks the PDF (the canonical output) and the parsed source:
  * page count inside the house range
  * page fill - no half-empty pages mid-section, section tails measured
  * counts: numbered sections, figures, tables, words, hyperlinks
  * optional live link check (--check-links) so no URL is invented
  * contact-sheet preview PNG an agent can look at

Every finding comes with a concrete fix an agent can act on.
"""
from __future__ import annotations

import json
import re
import ssl
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

WORDS_PER_PAGE = 520  # body text at house settings


def _content_rows(page, top: float, bottom: float):
    """Vertical intervals [y0, y1] that carry ink inside the body area."""
    spans = []
    try:
        for kind, rect in page.get_bboxlog():
            x0, y0, x1, y1 = rect
            if y1 <= top or y0 >= bottom or (x1 - x0) < 0.5 and (y1 - y0) < 0.5:
                continue
            if kind.startswith("fill-path") and (x1 - x0) > page.rect.width * 0.95 and (y1 - y0) > page.rect.height * 0.9:
                continue  # page background
            spans.append((max(y0, top), min(y1, bottom)))
    except Exception:
        for b in page.get_text("blocks"):
            if b[3] > top and b[1] < bottom:
                spans.append((max(b[1], top), min(b[3], bottom)))
    spans.sort()
    merged = []
    for s in spans:
        if merged and s[0] <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], s[1]))
        else:
            merged.append(s)
    return merged


def analyse_pdf(pdf_path: Path, brand: dict) -> dict:
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    n = doc.page_count
    margin = brand["layout"]["margin_in"] * 72
    pages = []
    for i in range(n):
        p = doc[i]
        top, bottom = margin - 4, p.rect.height - margin + 4
        rows = _content_rows(p, top, bottom)
        body_h = bottom - top
        if rows:
            last = rows[-1][1]
            first = rows[0][0]
            fill = (last - top) / body_h
            gaps = [(rows[k + 1][0] - rows[k][1]) for k in range(len(rows) - 1)]
            gaps.append(first - top)
            max_gap = max(gaps) if gaps else 0
        else:
            fill, max_gap = 0.0, body_h
        links = [l for l in p.get_links() if l.get("kind") == pymupdf.LINK_URI]
        pages.append({"page": i + 1, "fill": round(fill, 3), "max_gap_in": round(max_gap / 72, 2),
                      "links": len(links), "words": len(p.get_text("words"))})
    toc = doc.get_toc()
    uri = sorted({l["uri"] for p in doc for l in p.get_links() if l.get("kind") == pymupdf.LINK_URI})
    return {"pages": pages, "page_count": n, "toc": toc, "pdf_links": uri}


def _section_map(toc, page_count):
    """level-1 headings -> (title, first page, last page). Excludes cover/contents/back."""
    l1 = [(t, p) for lvl, t, p in toc if lvl == 1]
    out = []
    for k, (title, start) in enumerate(l1):
        end = (l1[k + 1][1] - 1) if k + 1 < len(l1) else page_count - 1  # last page is back cover
        out.append({"title": title, "start": start, "end": end})
    return out


def check_links(urls, timeout=12, workers=12) -> dict:
    ctx = ssl.create_default_context()
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 hhreport-linkcheck",
               "Accept": "text/html,application/xhtml+xml,application/pdf,*/*"}

    def one(url):
        if url.startswith("mailto:"):
            return url, "ok", None
        m = re.match(r"^https?://(dx\.)?doi\.org/(10\..+)$", url)
        if m:
            # Publishers block bots, so verify the DOI against the DOI registry itself.
            try:
                api = "https://doi.org/api/handles/" + urllib.parse.quote(m.group(2), safe="/")
                with urllib.request.urlopen(urllib.request.Request(api, headers=headers), timeout=timeout,
                                            context=ctx) as r:
                    code = json.loads(r.read().decode()).get("responseCode")
                return url, ("ok" if code == 1 else "broken"), f"doi:{code}"
            except urllib.error.HTTPError as e:
                return url, "broken", f"doi:{e.code}"
            except Exception as e:
                return url, "blocked", type(e).__name__
        for method in ("HEAD", "GET"):
            try:
                req = urllib.request.Request(url, method=method, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                    return url, "ok", r.status
            except urllib.error.HTTPError as e:
                if method == "HEAD" and e.code in (403, 404, 405, 429, 500, 501, 503):
                    continue
                # 401/403/429 usually mean "exists but blocks bots"
                status = "blocked" if e.code in (401, 403, 429, 999) else "broken"
                return url, status, e.code
            except Exception as e:  # DNS, TLS, timeout
                if method == "HEAD":
                    continue
                return url, "broken", type(e).__name__
        return url, "broken", None

    with ThreadPoolExecutor(workers) as ex:
        res = list(ex.map(one, urls))
    return {u: {"status": s, "code": c} for u, s, c in res}


def contact_sheet(pdf_path: Path, out_png: Path, cols: int = 6, dpi: int = 40) -> Path:
    import pymupdf
    from PIL import Image, ImageDraw

    doc = pymupdf.open(str(pdf_path))
    ims = []
    for pg in doc:
        pix = pg.get_pixmap(dpi=dpi)
        ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    pad = 10
    sheet = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + pad + 14) + pad), "#7d8590")
    draw = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x = pad + (k % cols) * (w + pad)
        y = pad + (k // cols) * (h + pad + 14)
        sheet.paste(im, (x, y + 14))
        draw.text((x, y), f"p{k + 1}", fill="white")
    sheet.save(out_png)
    return out_png


def run(result: dict, check_links_online: bool = False, preview: bool = True, strict: bool = False) -> dict:
    doc = result["doc"]
    brand = result["brand"]
    q = brand["qa"]
    meta_q = doc.meta.get("qa") or {}
    q = {**q, **meta_q}  # per-report overrides (use sparingly)
    pdf = result["outputs"].get("pdf")
    errors, warnings, fixes = [], [], []
    stats = dict(doc.stats)

    if pdf is None:
        raise RuntimeError("QA needs the PDF; build with --pdf")
    a = analyse_pdf(pdf, brand)
    n = a["page_count"]
    stats["pages"] = n

    # ---- page count
    if n < q["min_pages"]:
        short = q["min_pages"] - n
        errors.append(f"Report is {n} pages; minimum is {q['min_pages']}.")
        fixes.append(f"Add roughly {short * WORDS_PER_PAGE:,} words of substantive analysis (or ~{short} pages of "
                     "text, figures and tables). Deepen thin sections, add a case study, a data table or a figure.")
    elif n > q["max_pages"]:
        over = n - q["max_pages"]
        errors.append(f"Report is {n} pages; maximum is {q['max_pages']}.")
        fixes.append(f"Cut roughly {over * WORDS_PER_PAGE:,} words, or move detail into tighter tables.")

    # ---- counts
    for key, label in (("sections", "numbered sections"), ("figures", "figures"), ("tables", "tables")):
        if stats.get(key, 0) < q[f"min_{key}"]:
            errors.append(f"Only {stats.get(key, 0)} {label}; minimum is {q[f'min_{key}']}.")
    if stats["words"] < q["min_words"]:
        warnings.append(f"Word count {stats['words']:,} is below the {q['min_words']:,} target.")
    if stats["links"] < q["min_links"]:
        errors.append(f"Only {stats['links']} in-text hyperlinks; minimum is {q['min_links']}.")
        fixes.append("Link claims to their primary sources inline: [descriptive anchor text](https://...).")

    # ---- page fill
    sections = _section_map(a["toc"], n)
    tail_pages = {s["end"] for s in sections}
    start_pages = {s["start"] for s in sections}
    body_pages = set(range(sections[0]["start"], n)) if sections else set()
    page_notes = []
    for s in sections:
        tail = a["pages"][s["end"] - 1]
        if s is not sections[-1] and tail["fill"] < q["tail_warn"]:
            need = int((0.92 - tail["fill"]) * WORDS_PER_PAGE)
            warnings.append(f"Section '{s['title']}' ends on p{s['end']} at {tail['fill']:.0%} page fill.")
            fixes.append(f"In '{s['title']}': add ~{need} words (or a table/figure), or trim "
                         f"~{int(tail['fill'] * WORDS_PER_PAGE)} words so it ends on the previous page.")
        stats.setdefault("section_pages", []).append(
            {"title": s["title"], "pages": f"{s['start']}-{s['end']}", "tail_fill": tail["fill"]})
    for pg in a["pages"]:
        i = pg["page"]
        if i not in body_pages or i == n:
            continue
        if i not in tail_pages and pg["fill"] < q["fill_warn"]:
            warnings.append(f"p{i} is only {pg['fill']:.0%} full but is not the end of a section.")
            page_notes.append(i)
        if pg["max_gap_in"] > q["max_gap_in"] and i not in tail_pages:
            warnings.append(f"p{i} has a {pg['max_gap_in']:.1f}in blank gap inside the page.")
            page_notes.append(i)
    if page_notes:
        fixes.append("Mid-section gaps usually come from a large table or several figures in a row. Spread "
                     "figures out (at least 2-3 paragraphs between them), split long tables, or set "
                     "'placement: top' on a figure that should lead its page.")

    # ---- links in PDF
    stats["pdf_links"] = len(a["pdf_links"])
    link_report = None
    if check_links_online:
        link_report = check_links(doc.stats["link_urls"])
        broken = [u for u, r in link_report.items() if r["status"] == "broken"]
        blocked = [u for u, r in link_report.items() if r["status"] == "blocked"]
        for u in broken:
            errors.append(f"Broken link: {u} ({link_report[u]['code']})")
        if broken:
            fixes.append("Replace every broken URL with a working primary source (search for the exact "
                         "document; never guess a URL).")
        for u in blocked:
            warnings.append(f"Link could not be verified (site blocks bots): {u}")

    # ---- leftovers from the template
    if not doc.meta.get("sample"):
        placeholders = [u for u in doc.stats.get("link_urls", [])
                        if re.match(r"^https?://(www\.)?example\.(com|org|net)\b", u)]
        for u in placeholders:
            errors.append(f"Placeholder link left in the report: {u}")
        if placeholders:
            fixes.append("Replace every example.com/example.org link with the real, verified source URL.")
    raw = "\n".join(f.read_text(encoding="utf-8") for f in [doc.source_dir / "report.md",
                    *sorted((doc.source_dir / "sections").glob("*.md"))] if f.exists())
    tokens = sorted(set(re.findall(r"\{\{[A-Z_ ]+\}\}", raw)))
    if tokens:
        errors.append(f"Template placeholders still present: {', '.join(tokens)}")

    for w in doc.warnings:
        warnings.append(w)

    if strict and warnings:
        errors.append(f"{len(warnings)} warning(s) with --strict")

    report = {
        "slug": result["slug"],
        "pass": not errors,
        "errors": errors,
        "warnings": warnings,
        "fixes": fixes,
        "stats": {k: v for k, v in stats.items() if k != "link_urls"},
        "pages": a["pages"],
        "links": link_report,
    }
    build_dir = result["build_dir"]
    (build_dir / "qa.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if preview:
        report["preview"] = str(contact_sheet(pdf, build_dir / "preview.png"))
    return report


def print_report(r: dict) -> None:
    s = r["stats"]
    print(f"\nQA  {r['slug']}  ->  {'PASS' if r['pass'] else 'FAIL'}")
    print(f"  pages {s.get('pages')} | sections {s.get('sections')} | figures {s.get('figures')} | "
          f"tables {s.get('tables')} | words {s.get('words'):,} | links {s.get('links')} "
          f"({s.get('unique_links')} unique)")
    for sp in s.get("section_pages", []):
        print(f"    {sp['pages']:>7}  tail {sp['tail_fill']:>4.0%}  {sp['title']}")
    for e in r["errors"]:
        print(f"  ERROR   {e}")
    for w in r["warnings"]:
        print(f"  warning {w}")
    if r["fixes"]:
        print("  How to fix:")
        for f in r["fixes"]:
            print(f"   - {f}")
    if r.get("preview"):
        print(f"  preview {r['preview']}")
