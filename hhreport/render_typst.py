"""Document model -> Typst source -> PDF."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .parse import Document, ReportError, plain

TEMPLATE = Path(__file__).parent / "templates" / "hh-report.typ"
FLOAT_TABLE_MAX_ROWS = 14  # tables up to this many body rows float; longer ones flow and break


# ---------------------------------------------------------------- literals
def s(text) -> str:
    """Typst string literal."""
    t = str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")
    return f'"{t}"'


def lit(v) -> str:
    """Python value -> Typst literal (dict, list, str, number, bool, None)."""
    if v is None:
        return "none"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, dict):
        if not v:
            return "(:)"
        return "(" + ", ".join(f"{k}: {lit(x)}" for k, x in v.items()) + ")"
    if isinstance(v, (list, tuple)):
        if not v:
            return "()"
        return "(" + ", ".join(lit(x) for x in v) + ",)"
    if isinstance(v, Content):
        return v.code
    return s(v)


class Content:
    def __init__(self, code: str):
        self.code = code


# ---------------------------------------------------------------- inlines
def inl(items: list) -> str:
    out = []
    for i in items:
        t = i["t"]
        if t == "text":
            if i["v"]:
                out.append("#" + s(i["v"]))
        elif t == "strong":
            out.append("#strong[" + inl(i["c"]) + "]")
        elif t == "em":
            out.append("#emph[" + inl(i["c"]) + "]")
        elif t == "code":
            out.append("#raw(" + s(i["v"]) + ")")
        elif t == "link":
            out.append("#link(" + s(i["href"]) + ")[" + inl(i["c"]) + "]")
        elif t == "br":
            out.append("#linebreak()")
    return "".join(out)


def content(items) -> str:
    return "[" + inl(items or []) + "]"


# ---------------------------------------------------------------- blocks
class TypstRenderer:
    def __init__(self, doc: Document, brand: dict, figures: dict):
        self.doc = doc
        self.brand = brand
        self.figures = figures  # figure number -> {"svg", "png", "width_in", "rel"}

    def blocks(self, blocks: list) -> str:
        # A figure that closes a section stays in the flow: as a float it could
        # be flushed onto a page of its own before the next section opener.
        default = str(self.doc.meta.get("figure_placement") or "bottom")
        for i, b in enumerate(blocks):
            if b["t"] == "figure" and not b.get("placement"):
                b["placement"] = default
            if b["t"] == "table" and not b.get("placement"):
                b["placement"] = "bottom" if len(b["rows"]) <= FLOAT_TABLE_MAX_ROWS else "here"
            if b["t"] in ("figure", "table") and b.get("placement") == "bottom":
                nxt = next((x for x in blocks[i + 1:] if x["t"] not in ("figure", "table")), None)
                if nxt is None or (nxt["t"] == "heading" and nxt["level"] == 1):
                    b["placement"] = "here"
        return "\n\n".join(filter(None, (self.block(b) for b in blocks)))

    def block(self, b: dict) -> str:
        t = b["t"]
        if t == "heading":
            num = b.get("number")
            kicker = f"{int(num):02d}" if (b["level"] == 1 and num) else None
            brk = "#hh-section-break()\n" if b["level"] == 1 else ""
            return (brk + f"#hh-heading(level: {b['level']}, num: {lit(num)}, kicker: {lit(kicker)})"
                    f"{content(b['inlines'])}")
        if t == "para":
            return inl(b["inlines"]) or None
        if t == "pagebreak":
            return "#pagebreak(weak: true)"
        if t == "list":
            items = ", ".join("[" + self.blocks(item) + "]" for item in b["items"])
            if b["ordered"]:
                return f"#enum(start: {b['start']}, {items})"
            return f"#list({items})"
        if t == "code":
            code = b["text"].replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
            return f'#raw(block: true, "{code}")'
        if t == "quote":
            attr = content(b["attribution"]) if b.get("attribution") else "none"
            return f"#hh-quote(attribution: {attr}, brand: BRAND)[{self.blocks(b['blocks'])}]"
        if t == "callout":
            return (f"#hh-callout(title: {s(b['title'])}, style: {s(b['style'])}, brand: BRAND)"
                    f"[{self.blocks(b['blocks'])}]")
        if t == "stats":
            items = ", ".join(f"({s(it['value'])}, {content(it['label'])})" for it in b["items"])
            return f"#hh-stats(({items},), brand: BRAND)"
        if t == "figure":
            f = self.figures[b["number"]]
            src = content(b["source"]) if b.get("source") else "none"
            return (f"#hh-figure({s(f['rel'])}, width: {f['width_in']:.2f}in, num: {b['number']}, "
                    f"caption: {content(b['caption'])}, source: {src}, placement: {s(b.get('placement') or 'bottom')}, brand: BRAND)")
        if t == "table":
            return self.table(b)
        return None

    def table(self, b: dict) -> str:
        ncol = len(b["header"])
        # column widths proportional to content length, clamped
        lens = []
        for ci in range(ncol):
            cells = [b["header"][ci]] + [r[ci] for r in b["rows"] if ci < len(r)]
            longest = max(len(plain(c)) for c in cells)
            avg = sum(len(plain(c)) for c in cells) / max(len(cells), 1)
            lens.append(min(max(0.5 * longest + 0.5 * avg, 6), 48))
        cols = "(" + ", ".join(f"{w:.1f}fr" for w in lens) + ",)"
        aligns = "(" + ", ".join(b["align"][i] if i < len(b["align"]) else "left" for i in range(ncol)) + ",)"
        header = "(" + ", ".join(content(h) for h in b["header"]) + ",)"
        rows = []
        for r in b["rows"]:
            cells = list(r) + [[] for _ in range(ncol - len(r))]
            rows.append("(" + ", ".join(content(c) for c in cells[:ncol]) + ",)")
        rows_s = "(" + ", ".join(rows) + ",)"
        cap = content(b["caption"]) if b.get("caption") else "none"
        src = content(b["source"]) if b.get("source") else "none"
        return (f"#hh-table(num: {b['number']}, caption: {cap}, source: {src}, columns: {cols}, "
                f"aligns: {aligns}, header: {header}, rows: {rows_s}, placement: {s(b.get('placement') or 'here')}, brand: BRAND)")


def _meta(doc: Document, brand: dict) -> dict:
    m = doc.meta
    from .parse import parse_inline_text

    authors = []
    for a in m.get("authors") or []:
        if isinstance(a, str):
            authors.append({"name": a, "role": None})
        else:
            authors.append({"name": a.get("name", ""), "role": a.get("role") or a.get("title")})
    date = str(m.get("date"))
    year = date[-4:] if date[-4:].isdigit() else date[:4]
    org = brand["org"]
    names = ", ".join(a["name"] for a in authors)
    citation = (f"{names} ({year}). *{m['title']}*. {org['name']} {m.get('report_type', 'Research Report')}"
                + (f" {m['report_id']}" if m.get("report_id") else "") + ".")
    contact_bits = [x for x in (org.get("email"), org.get("website")) if x]
    abstract_paras = [p.strip() for p in str(m.get("abstract", "")).split("\n\n") if p.strip()]
    abstract_code = "[" + " #parbreak() ".join(inl(parse_inline_text(p)) for p in abstract_paras) + "]"
    return {
        "title": Content(content(parse_inline_text(m["title"]))),
        "title_plain": str(m["title"]),
        "short_title": str(m.get("short_title") or m["title"]),
        "subtitle": Content(content(parse_inline_text(m.get("subtitle", "")))),
        "report_type": str(m.get("report_type", "Research Report")),
        "report_id": m.get("report_id"),
        "date": date,
        "year": year,
        "authors": authors,
        "author_names": [a["name"] for a in authors],
        "keywords": [str(k) for k in (m.get("keywords") or [])],
        "abstract": Content(abstract_code),
        "citation": Content(content(parse_inline_text(citation))),
        "contact": Content(content(parse_inline_text(" · ".join(contact_bits)))) if contact_bits else None,
        "toc_depth": int(m.get("toc_depth", 2)),
        "sample": bool(m.get("sample", False)),
    }


def to_typst(doc: Document, brand: dict, figures: dict) -> str:
    r = TypstRenderer(doc, brand, figures)
    brand_lit = {
        "org": {k: (v or "") for k, v in brand["org"].items()},
        "colors": {k: v for k, v in brand["colors"].items() if isinstance(v, str)},
        "fonts": brand["fonts"],
        "layout": brand["layout"],
    }
    return "\n".join([
        "// GENERATED by hhreport - edit report.md, not this file.",
        '#import "hh-report.typ": *',
        f"#let BRAND = {lit(brand_lit)}",
        f"#show: report.with(meta: {lit(_meta(doc, brand))}, brand: BRAND)",
        "",
        r.blocks(doc.blocks),
        "",
    ])


def compile_pdf(typ_path: Path, pdf_path: Path, fonts_dir: Path) -> None:
    """Compile with the `typst` Python package (pinned) or fall back to the CLI."""
    root = typ_path.parent
    try:
        import typst  # type: ignore

        try:
            typst.compile(str(typ_path), output=str(pdf_path), root=str(root), font_paths=[str(fonts_dir)])
            return
        except Exception as e:  # typst.TypstError carries the diagnostics
            raise ReportError(f"Typst compile failed:\n{e}") from e
    except ImportError:
        pass
    exe = shutil.which("typst")
    if not exe:
        raise ReportError("Neither the 'typst' Python package nor the typst CLI is installed. Run: pip install -r requirements.txt")
    proc = subprocess.run([exe, "compile", "--root", str(root), "--font-path", str(fonts_dir),
                           str(typ_path), str(pdf_path)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise ReportError(f"Typst compile failed:\n{proc.stderr}")
