"""Document model -> Word .docx (native styles, live hyperlinks, TOC field).

The DOCX is the editable twin of the PDF: same content, numbering, figures,
tables, callouts and links, laid out with Word-native constructs (named
styles, keep-with-next, repeating table headers) so editors can work on it.
"""
from __future__ import annotations

import copy
from io import BytesIO
from pathlib import Path

from docx import Document as DocxDocument
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.shared import Inches, Pt, RGBColor

from .parse import Document, parse_inline_text, plain


def _rgb(hexs: str) -> RGBColor:
    return RGBColor.from_string(hexs.lstrip("#").upper())


def _hex(hexs: str) -> str:
    return hexs.lstrip("#").upper()


# ---------------------------------------------------------------- xml helpers
def _shade(cell, fill_hex: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), _hex(fill_hex))
    tcPr.append(shd)


def _cell_borders(cell, **edges) -> None:
    """edges: top/left/bottom/right = (size_eighths_pt, hex) or None for nil."""
    tcPr = cell._tc.get_or_add_tcPr()
    borders = tcPr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcPr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        spec = edges.get(edge, "nil")
        el = OxmlElement(f"w:{edge}")
        if spec == "nil" or spec is None:
            el.set(qn("w:val"), "nil")
        else:
            sz, color = spec
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(sz))
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), _hex(color))
        borders.append(el)


def _cell_margins(cell, top=0, bottom=0, left=0, right=0) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{k}")
        el.set(qn("w:w"), str(int(v)))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcPr.append(mar)


def _table_no_borders(table) -> None:
    tblPr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        borders.append(el)
    tblPr.append(borders)


def _table_width(table, inches: float) -> None:
    tblPr = table._tbl.tblPr
    w = tblPr.find(qn("w:tblW"))
    if w is None:
        w = OxmlElement("w:tblW")
        tblPr.append(w)
    w.set(qn("w:w"), str(int(inches * 1440)))
    w.set(qn("w:type"), "dxa")
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)


def _table_indent(table, dxa: int) -> None:
    tblPr = table._tbl.tblPr
    ind = OxmlElement("w:tblInd")
    ind.set(qn("w:w"), str(dxa))
    ind.set(qn("w:type"), "dxa")
    tblPr.append(ind)


def _repeat_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def _cant_split(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def _para_border(paragraph, edge: str, size: int, color: str, space: int = 4) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    el = OxmlElement(f"w:{edge}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), str(space))
    el.set(qn("w:color"), _hex(color))
    pBdr.append(el)


def _para_shading(paragraph, fill: str) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), _hex(fill))
    pPr.append(shd)


def _field(paragraph, instr: str, placeholder: str = "1", run_font=None) -> None:
    def r(el):
        run = paragraph.add_run()
        if run_font:
            run_font(run)
        run._r.append(el)
        return run

    b = OxmlElement("w:fldChar")
    b.set(qn("w:fldCharType"), "begin")
    r(b)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = f" {instr} "
    r(it)
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    r(sep)
    run = paragraph.add_run(placeholder)
    if run_font:
        run_font(run)
    e = OxmlElement("w:fldChar")
    e.set(qn("w:fldCharType"), "end")
    r(e)


def _set_fonts(style_or_run_font, name: str) -> None:
    style_or_run_font.name = name
    rpr = style_or_run_font.element.rPr if hasattr(style_or_run_font, "element") else None
    if rpr is None:
        return
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(k), name)


def _run_font(run, name: str) -> None:
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for k in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(k), name)


# ---------------------------------------------------------------- renderer
class DocxRenderer:
    def __init__(self, doc: Document, brand: dict, figures: dict):
        self.doc = doc
        self.brand = brand
        self.c = brand["colors"]
        self.body_font = brand["fonts"]["docx_body"]
        self.head_font = brand["fonts"]["docx_heading"]
        self.figures = figures
        self.d = DocxDocument()
        self.text_width = 8.5 - 2 * brand["layout"]["margin_in"]
        if brand["layout"]["paper"] == "a4":
            self.text_width = 8.27 - 2 * brand["layout"]["margin_in"]
        self._abs_bullet = None
        self._abs_decimal = None
        self._setup_styles()
        self._setup_numbering()

    # ---------------- styles
    def _style(self, name, base="Normal", kind=WD_STYLE_TYPE.PARAGRAPH):
        styles = self.d.styles
        try:
            return styles[name]
        except KeyError:
            st = styles.add_style(name, kind)
            if base:
                st.base_style = styles[base]
            return st

    def _setup_styles(self):
        c = self.c
        size = self.brand["layout"]["body_size_pt"]
        st = self.d.styles
        normal = st["Normal"]
        _set_fonts(normal.font, self.body_font)
        normal.font.size = Pt(size)
        normal.font.color.rgb = _rgb(c["ink"])
        pf = normal.paragraph_format
        pf.space_after = Pt(6)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.15
        pf.widow_control = True

        body = self._style("HH Body")
        body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        def heading(name, size_pt, color, before, after, bold=True, font=None):
            h = st[name]
            _set_fonts(h.font, font or self.head_font)
            h.font.size = Pt(size_pt)
            h.font.bold = bold
            h.font.italic = False
            h.font.color.rgb = _rgb(color)
            h.paragraph_format.space_before = Pt(before)
            h.paragraph_format.space_after = Pt(after)
            h.paragraph_format.keep_with_next = True
            h.paragraph_format.line_spacing = 1.0
            return h

        h1 = heading("Heading 1", 24, c["navy"], 0, 16, bold=False, font=self.body_font)
        h1.paragraph_format.page_break_before = False
        heading("Heading 2", 13, c["navy"], 14, 6)
        heading("Heading 3", 11, c["navy"], 10, 4)

        kicker = self._style("HH Kicker")
        _set_fonts(kicker.font, self.head_font)
        kicker.font.size = Pt(8.5)
        kicker.font.bold = True
        kicker.font.color.rgb = _rgb(c["blue"])
        kicker.paragraph_format.keep_with_next = True
        kicker.paragraph_format.space_after = Pt(4)
        kicker.paragraph_format.page_break_before = True
        self._spacing(kicker, 40)

        cap = self._style("HH Caption")
        _set_fonts(cap.font, self.head_font)
        cap.font.size = Pt(10.5)
        cap.font.bold = True
        cap.font.color.rgb = _rgb(c["navy"])
        cap.paragraph_format.keep_with_next = True
        cap.paragraph_format.space_before = Pt(12)
        cap.paragraph_format.space_after = Pt(6)

        src = self._style("HH Source")
        _set_fonts(src.font, self.head_font)
        src.font.size = Pt(7.5)
        src.font.color.rgb = _rgb(c["ink_muted"])
        src.paragraph_format.space_before = Pt(3)
        src.paragraph_format.space_after = Pt(12)

        fig = self._style("HH Figure")
        fig.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fig.paragraph_format.keep_with_next = True
        fig.paragraph_format.space_after = Pt(0)

        cell = self._style("HH Table Text")
        _set_fonts(cell.font, self.head_font)
        cell.font.size = Pt(8.5)
        cell.paragraph_format.space_after = Pt(0)
        cell.paragraph_format.line_spacing = 1.0

        lst = self._style("HH List")
        lst.paragraph_format.space_after = Pt(3)
        lst.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

        quote = self._style("HH Quote")
        quote.font.size = Pt(12.5)
        quote.font.italic = True
        quote.font.color.rgb = _rgb(c["navy"])
        quote.paragraph_format.left_indent = Inches(0.25)
        quote.paragraph_format.space_before = Pt(10)
        quote.paragraph_format.space_after = Pt(4)

        code = self._style("HH Code")
        _set_fonts(code.font, "Consolas")
        code.font.size = Pt(8.5)
        code.paragraph_format.space_after = Pt(0)
        code.paragraph_format.line_spacing = 1.0

        label = self._style("HH Label")
        _set_fonts(label.font, self.head_font)
        label.font.size = Pt(8.5)
        label.font.bold = True
        label.font.color.rgb = _rgb(c["blue"])
        label.paragraph_format.space_after = Pt(4)
        label.paragraph_format.keep_with_next = True

        for lvl, (sz, bold, before, indent) in {1: (10.5, True, 6, 0), 2: (9.5, False, 0, 0.25)}.items():
            t = st[f"TOC {lvl}"] if f"TOC {lvl}" in [s.name for s in st] else self._style(f"TOC {lvl}")
            _set_fonts(t.font, self.head_font)
            t.font.size = Pt(sz)
            t.font.bold = bold
            t.font.color.rgb = _rgb(c["navy"] if bold else c["ink"])
            t.paragraph_format.space_before = Pt(before)
            t.paragraph_format.space_after = Pt(1)
            t.paragraph_format.left_indent = Inches(indent)
            t.paragraph_format.tab_stops.add_tab_stop(Inches(self.text_width), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

        # hyperlink character style
        try:
            hl = st["Hyperlink"]
        except KeyError:
            hl = st.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
        hl.font.color.rgb = _rgb(c["blue"])
        hl.font.underline = True

    @staticmethod
    def _spacing(style, tracking_twentieths: int):
        rpr = style.element.get_or_add_rPr()
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:val"), str(tracking_twentieths // 10))
        rpr.append(sp)

    # ---------------- numbering (lists that restart correctly)
    def _setup_numbering(self):
        numbering = self.d.part.numbering_part.element
        accent = _hex(self.c["accent"])
        blue = _hex(self.c["blue"])

        def abstract(abs_id, fmt):
            a = OxmlElement("w:abstractNum")
            a.set(qn("w:abstractNumId"), str(abs_id))
            mlt = OxmlElement("w:multiLevelType")
            mlt.set(qn("w:val"), "hybridMultilevel")
            a.append(mlt)
            for lvl in range(3):
                l_ = OxmlElement("w:lvl")
                l_.set(qn("w:ilvl"), str(lvl))
                start = OxmlElement("w:start")
                start.set(qn("w:val"), "1")
                l_.append(start)
                nf = OxmlElement("w:numFmt")
                text = OxmlElement("w:lvlText")
                if fmt == "bullet":
                    nf.set(qn("w:val"), "bullet")
                    text.set(qn("w:val"), ["■", "–", "•"][lvl])
                else:
                    nf.set(qn("w:val"), ["decimal", "lowerLetter", "lowerRoman"][lvl])
                    text.set(qn("w:val"), f"%{lvl + 1}.")
                l_.append(nf)
                l_.append(text)
                jc = OxmlElement("w:lvlJc")
                jc.set(qn("w:val"), "left")
                l_.append(jc)
                ppr = OxmlElement("w:pPr")
                ind = OxmlElement("w:ind")
                ind.set(qn("w:left"), str(380 + lvl * 340))
                ind.set(qn("w:hanging"), "340")
                ppr.append(ind)
                l_.append(ppr)
                rpr = OxmlElement("w:rPr")
                col = OxmlElement("w:color")
                col.set(qn("w:val"), accent if fmt == "bullet" else blue)
                rpr.append(col)
                if fmt == "bullet" and lvl == 0:
                    sz = OxmlElement("w:sz")
                    sz.set(qn("w:val"), "14")
                    rpr.append(sz)
                if fmt != "bullet":
                    b = OxmlElement("w:b")
                    rpr.append(b)
                    rf = OxmlElement("w:rFonts")
                    for k in ("w:ascii", "w:hAnsi"):
                        rf.set(qn(k), self.head_font)
                    rpr.insert(0, rf)
                l_.append(rpr)
                a.append(l_)
            return a

        existing = [int(x.get(qn("w:abstractNumId"))) for x in numbering.findall(qn("w:abstractNum"))]
        base = max(existing + [0]) + 10
        self._abs_bullet, self._abs_decimal = base, base + 1
        first_num = numbering.find(qn("w:num"))
        for el in (abstract(base, "bullet"), abstract(base + 1, "decimal")):
            if first_num is not None:
                first_num.addprevious(el)
            else:
                numbering.append(el)
        self._next_num = max([int(x.get(qn("w:numId"))) for x in numbering.findall(qn("w:num"))] + [0]) + 1

    def _new_num(self, ordered: bool, start: int = 1) -> int:
        numbering = self.d.part.numbering_part.element
        nid = self._next_num
        self._next_num += 1
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(nid))
        an = OxmlElement("w:abstractNumId")
        an.set(qn("w:val"), str(self._abs_decimal if ordered else self._abs_bullet))
        num.append(an)
        ov = OxmlElement("w:lvlOverride")
        ov.set(qn("w:ilvl"), "0")
        so = OxmlElement("w:startOverride")
        so.set(qn("w:val"), str(start))
        ov.append(so)
        num.append(ov)
        numbering.append(num)
        return nid

    @staticmethod
    def _apply_num(paragraph, num_id: int, level: int):
        pPr = paragraph._p.get_or_add_pPr()
        numPr = OxmlElement("w:numPr")
        ilvl = OxmlElement("w:ilvl")
        ilvl.set(qn("w:val"), str(level))
        nid = OxmlElement("w:numId")
        nid.set(qn("w:val"), str(num_id))
        numPr.append(ilvl)
        numPr.append(nid)
        pPr.append(numPr)

    # ---------------- inlines
    def add_inlines(self, p, items, bold=False, italic=False, color=None, size=None, font=None):
        for i in items:
            t = i["t"]
            if t == "text":
                r = p.add_run(i["v"])
                self._fmt(r, bold, italic, color, size, font)
            elif t == "strong":
                self.add_inlines(p, i["c"], True, italic, color, size, font)
            elif t == "em":
                self.add_inlines(p, i["c"], bold, True, color, size, font)
            elif t == "code":
                r = p.add_run(i["v"])
                self._fmt(r, bold, italic, color, (size or Pt(self.brand["layout"]["body_size_pt"])) * 0.92, "Consolas")
            elif t == "br":
                p.add_run().add_break()
            elif t == "link":
                self._hyperlink(p, i["href"], i["c"], bold, italic, size, font)

    @staticmethod
    def _fmt(r, bold, italic, color, size, font):
        if bold:
            r.bold = True
        if italic:
            r.italic = True
        if color:
            r.font.color.rgb = _rgb(color)
        if size:
            r.font.size = size
        if font:
            _run_font(r, font)

    def _hyperlink(self, p, url, items, bold, italic, size, font):
        r_id = p.part.relate_to(url, RT.HYPERLINK, is_external=True)
        h = OxmlElement("w:hyperlink")
        h.set(qn("r:id"), r_id)
        h.set(qn("w:history"), "1")
        # build runs in a scratch paragraph, then move them inside the hyperlink
        tmp = self.d.add_paragraph()
        self.add_inlines(tmp, items, bold, italic, None, size, font)
        for r in list(tmp._p.findall(qn("w:r"))):
            rpr = r.get_or_add_rPr()
            rs = OxmlElement("w:rStyle")
            rs.set(qn("w:val"), "Hyperlink")
            rpr.insert(0, rs)
            col = OxmlElement("w:color")
            col.set(qn("w:val"), _hex(self.c["blue"]))
            rpr.append(col)
            u = OxmlElement("w:u")
            u.set(qn("w:val"), "single")
            rpr.append(u)
            h.append(r)
        tmp._p.getparent().remove(tmp._p)
        p._p.append(h)

    # ---------------- blocks
    def blocks(self, target, blocks, list_level=0):
        for b in blocks:
            self.block(target, b, list_level)

    def _para(self, target, style="HH Body"):
        return target.add_paragraph(style=style)

    def block(self, target, b, list_level=0):
        t = b["t"]
        c = self.c
        if t == "heading":
            self.heading(target, b)
        elif t == "para":
            p = self._para(target)
            self.add_inlines(p, b["inlines"])
        elif t == "pagebreak":
            target.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        elif t == "list":
            nid = self._new_num(b["ordered"], b["start"])
            for item in b["items"]:
                first = True
                for sub in item:
                    if sub["t"] == "para":
                        p = self._para(target, "HH List")
                        if first:
                            self._apply_num(p, nid, list_level)
                        else:
                            p.paragraph_format.left_indent = Inches(0.264 + 0.236 * list_level)
                        self.add_inlines(p, sub["inlines"])
                        first = False
                    elif sub["t"] == "list":
                        self.block(target, sub, list_level + 1)
                    else:
                        self.block(target, sub, list_level)
        elif t == "code":
            for line in b["text"].split("\n"):
                p = self._para(target, "HH Code")
                _para_shading(p, c["tint"])
                p.add_run(line)
        elif t == "quote":
            for sub in b["blocks"]:
                if sub["t"] == "para":
                    p = self._para(target, "HH Quote")
                    _para_border(p, "left", 16, c["accent"], 10)
                    self.add_inlines(p, sub["inlines"])
            if b.get("attribution"):
                p = self._para(target, "HH Source")
                p.paragraph_format.left_indent = Inches(0.25)
                p.add_run("— ")
                self.add_inlines(p, b["attribution"])
        elif t == "callout":
            self.callout(target, b)
        elif t == "stats":
            self.stats(target, b)
        elif t == "figure":
            self.figure(target, b)
        elif t == "table":
            self.table(target, b)

    def heading(self, target, b):
        c = self.c
        if b["level"] == 1:
            k = self._para(target, "HH Kicker")
            kick = f"SECTION {int(b['number']):02d}" if b.get("number") else str(
                self.doc.meta.get("short_title") or self.doc.meta["title"]).upper()
            k.add_run(kick)
            p = target.add_paragraph(style="Heading 1")
            self.add_inlines(p, b["inlines"])
            _para_border(p, "bottom", 18, c["accent"], 8)
        else:
            p = target.add_paragraph(style=f"Heading {b['level']}")
            if b.get("number"):
                r = p.add_run(f"{b['number']}  ")
                r.font.color.rgb = _rgb(c["blue"])
            self.add_inlines(p, b["inlines"])

    def _caption(self, target, kind, num, caption):
        p = self._para(target, "HH Caption")
        r = p.add_run(f"{kind.upper()} {num}   ")
        r.font.color.rgb = _rgb(self.c["blue"])
        r.font.size = Pt(8)
        self.add_inlines(p, caption or [])
        return p

    def figure(self, target, b):
        f = self.figures[b["number"]]
        cap = self._caption(target, "Figure", b["number"], b["caption"])
        _para_border(cap, "bottom", 4, self.c["rule"], 4)
        p = self._para(target, "HH Figure")
        p.paragraph_format.space_before = Pt(6)
        p.add_run().add_picture(str(f["png"]), width=Inches(f["width_in"]))
        _para_border(p, "bottom", 4, self.c["rule"], 4)
        if b.get("source"):
            s = self._para(target, "HH Source")
            self.add_inlines(s, b["source"])
        else:
            p.paragraph_format.space_after = Pt(12)

    def table(self, target, b):
        c = self.c
        self._caption(target, "Table", b["number"], b["caption"])
        ncol = len(b["header"])
        lens = []
        for ci in range(ncol):
            cells = [b["header"][ci]] + [r[ci] for r in b["rows"] if ci < len(r)]
            longest = max(len(plain(x)) for x in cells)
            avg = sum(len(plain(x)) for x in cells) / max(len(cells), 1)
            lens.append(min(max(0.5 * longest + 0.5 * avg, 6), 48))
        total = sum(lens)
        widths = [self.text_width * w / total for w in lens]
        tbl = target.add_table(rows=1 + len(b["rows"]), cols=ncol)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        _table_no_borders(tbl)
        _table_width(tbl, self.text_width)
        aligns = {"left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT, "center": WD_ALIGN_PARAGRAPH.CENTER}
        for ri, row in enumerate(tbl.rows):
            data = b["header"] if ri == 0 else b["rows"][ri - 1]
            if ri == 0:
                _repeat_header(row)
            _cant_split(row)
            for ci, cell in enumerate(row.cells):
                cell.width = Inches(widths[ci])
                _cell_margins(cell, 70, 70, 100, 100)
                para = cell.paragraphs[0]
                para.style = self.d.styles["HH Table Text"]
                para.alignment = aligns.get(b["align"][ci] if ci < len(b["align"]) else "left")
                items = data[ci] if ci < len(data) else []
                if ri == 0:
                    _shade(cell, c["navy"])
                    self.add_inlines(para, items, bold=True, color="#FFFFFF")
                else:
                    if ri % 2 == 0:
                        _shade(cell, c["tint"])
                    self.add_inlines(para, items)
                    if ri == len(b["rows"]):
                        _cell_borders(cell, bottom=(8, c["navy"]))
        if b.get("source"):
            s = self._para(target, "HH Source")
            self.add_inlines(s, b["source"])
        else:
            target.add_paragraph().paragraph_format.space_after = Pt(4)

    def callout(self, target, b):
        c = self.c
        keyf = b["style"] == "keyfindings"
        tbl = target.add_table(rows=1, cols=1)
        _table_no_borders(tbl)
        _table_width(tbl, self.text_width)
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(self.text_width)
        _shade(cell, c["tint_accent"] if keyf else c["tint"])
        _cell_borders(cell, left=(24, c["accent"] if keyf else c["blue"]))
        _cell_margins(cell, 160, 160, 220, 220)
        first = cell.paragraphs[0]
        if b.get("title"):
            first.style = self.d.styles["Normal"]
            r = first.add_run(b["title"])
            r.bold = True
            r.font.size = Pt(10.5)
            r.font.color.rgb = _rgb(c["navy"])
            _run_font(r, self.head_font)
            first.paragraph_format.space_after = Pt(6)
        else:
            first._p.getparent().remove(first._p)
        self.blocks(cell, b["blocks"])
        # trim trailing space inside the box
        if cell.paragraphs:
            cell.paragraphs[-1].paragraph_format.space_after = Pt(0)
        sp = target.add_paragraph()
        sp.paragraph_format.space_after = Pt(4)

    def stats(self, target, b):
        c = self.c
        n = len(b["items"])
        tbl = target.add_table(rows=1, cols=n)
        _table_no_borders(tbl)
        _table_width(tbl, self.text_width)
        gap = 0.15
        for cell, it in zip(tbl.rows[0].cells, b["items"]):
            cell.width = Inches(self.text_width / n)
            _cell_borders(cell, top=(18, c["accent"]))
            _cell_margins(cell, 120, 60, 0, int(gap * 1440))
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(it["value"])
            r.font.size = Pt(22)
            r.font.color.rgb = _rgb(c["navy"])
            p2 = cell.add_paragraph()
            p2.paragraph_format.space_after = Pt(0)
            p2.paragraph_format.line_spacing = 1.0
            self.add_inlines(p2, it["label"], color=c["ink_muted"], size=Pt(8.5), font=self.head_font)
        sp = target.add_paragraph()
        sp.paragraph_format.space_after = Pt(6)

    # ---------------- page furniture
    def _sect_margins(self, section, m):
        section.top_margin = section.bottom_margin = Inches(m)
        section.left_margin = section.right_margin = Inches(m)

    def _page_size(self, section):
        if self.brand["layout"]["paper"] == "a4":
            section.page_width, section.page_height = Inches(8.27), Inches(11.69)
        else:
            section.page_width, section.page_height = Inches(8.5), Inches(11)

    # ---------------- covers: full-bleed background image anchored behind text
    def _background_png(self, page_w: float, page_h: float, arcs: bool) -> BytesIO:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Circle

        fig = plt.figure(figsize=(page_w, page_h), dpi=110)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, page_w * 72)
        ax.set_ylim(0, page_h * 72)
        ax.axis("off")
        fig.patch.set_facecolor(self.c["navy"])
        if arcs:  # same motif as the PDF cover, centred off the bottom-right corner
            for i in range(1, 9):
                r = 70 * i
                cx, cy = page_w * 72 + r * 0.55 - r, -r * 0.55 + r
                ax.add_patch(Circle((cx, cy), r, fill=False, edgecolor="white",
                                    alpha=max(0.04, 0.12 - i * 0.004), linewidth=0.6))
        buf = BytesIO()
        fig.savefig(buf, format="png", facecolor=self.c["navy"])
        plt.close(fig)
        buf.seek(0)
        return buf

    def _anchor_background(self, paragraph, section, arcs: bool):
        pw, ph = section.page_width.inches, section.page_height.inches
        run = paragraph.add_run()
        run.add_picture(self._background_png(pw, ph, arcs), width=Inches(pw), height=Inches(ph))
        inline = run._r.find(".//" + qn("wp:inline"))
        anchor = OxmlElement("wp:anchor")
        for k, v in {"distT": "0", "distB": "0", "distL": "0", "distR": "0", "simplePos": "0",
                     "relativeHeight": "0", "behindDoc": "1", "locked": "1", "layoutInCell": "1",
                     "allowOverlap": "1"}.items():
            anchor.set(k, v)
        sp = OxmlElement("wp:simplePos")
        sp.set("x", "0")
        sp.set("y", "0")
        anchor.append(sp)
        for tag in ("wp:positionH", "wp:positionV"):
            pos = OxmlElement(tag)
            pos.set("relativeFrom", "page")
            off = OxmlElement("wp:posOffset")
            off.text = "0"
            pos.append(off)
            anchor.append(pos)
        anchor.append(copy.deepcopy(inline.find(qn("wp:extent"))))
        eff = OxmlElement("wp:effectExtent")
        for k in ("l", "t", "r", "b"):
            eff.set(k, "0")
        anchor.append(eff)
        anchor.append(OxmlElement("wp:wrapNone"))
        anchor.append(copy.deepcopy(inline.find(qn("wp:docPr"))))
        anchor.append(OxmlElement("wp:cNvGraphicFramePr"))
        anchor.append(copy.deepcopy(inline.find(qn("a:graphic"))))
        inline.getparent().replace(inline, anchor)

    def _tiny(self, p):
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = Pt(1)
        r = p.runs[0] if p.runs else p.add_run("")
        r.font.size = Pt(1)

    def _two_zone(self, top_height_in: float):
        """Borderless 2-row layout table: a fixed-height top zone and a bottom zone."""
        tbl = self.d.add_table(rows=2, cols=1)
        _table_no_borders(tbl)
        _table_width(tbl, self.cover_width)
        top = tbl.rows[0]
        top.height = Inches(top_height_in)
        top.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        for row in tbl.rows:
            cell = row.cells[0]
            cell.width = Inches(self.cover_width)
            _cell_margins(cell, 0, 0, 0, 0)
        return tbl.rows[0].cells[0], tbl.rows[1].cells[0]

    def _cpara(self, cell, text="", size=10, color="#FFFFFF", bold=False, font=None, after=0, before=0,
               spacing=None, line=1.1):
        p = cell.paragraphs[0] if (len(cell.paragraphs) == 1 and not cell.paragraphs[0].runs
                                   and not getattr(cell, "_hh_used", False)) else cell.add_paragraph()
        cell._hh_used = True
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.line_spacing = line
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if text:
            r = p.add_run(text)
            r.font.size = Pt(size)
            r.font.color.rgb = _rgb(color)
            r.bold = bold
            _run_font(r, font or self.head_font)
            if spacing:
                rpr = r._r.get_or_add_rPr()
                sp = OxmlElement("w:spacing")
                sp.set(qn("w:val"), str(spacing))
                rpr.append(sp)
        return p

    def _wordmark(self, cell):
        p = self._cpara(cell, "■ ", 12, self.c["accent"])
        r = p.add_run(self.brand["org"]["wordmark"])
        r.font.size = Pt(10)
        r.bold = True
        r.font.color.rgb = _rgb("#FFFFFF")
        _run_font(r, self.head_font)
        rpr = r._r.get_or_add_rPr()
        sp = OxmlElement("w:spacing")
        sp.set(qn("w:val"), "50")
        rpr.append(sp)
        return p

    def cover(self):
        m = self.doc.meta
        c = self.c
        section = self.d.sections[0]
        self._page_size(section)
        self._sect_margins(section, 0.9)
        self.cover_width = section.page_width.inches - 1.8
        anchor_p = self.d.paragraphs[0] if self.d.paragraphs else self.d.add_paragraph()
        self._tiny(anchor_p)
        self._anchor_background(anchor_p, section, arcs=True)
        avail = section.page_height.inches - 1.8
        top, bottom = self._two_zone(avail - 1.3)
        self._wordmark(top)
        if m.get("sample"):
            self._cpara(top, "SAMPLE · ILLUSTRATIVE DATA", 8, c["accent"], True, before=6, spacing=25)
        self._cpara(top, str(m.get("report_type", "Research Report")).upper(), 10, c["accent"], True,
                    before=150, after=12, spacing=40)
        tp = self._cpara(top, after=16, line=1.0)
        self.add_inlines(tp, parse_inline_text(m["title"]), color="#FFFFFF", size=Pt(34), font=self.body_font)
        sp_ = self._cpara(top, after=20)
        self.add_inlines(sp_, parse_inline_text(m.get("subtitle", "")), color="#D5DCE6", size=Pt(15),
                         font=self.head_font)
        self._cpara(top, "▬▬", 14, c["accent"])
        for a in m.get("authors") or []:
            name = a if isinstance(a, str) else a.get("name", "")
            role = None if isinstance(a, str) else (a.get("role") or a.get("title"))
            p = self._cpara(bottom, name, 10, "#FFFFFF", True)
            if role:
                rr = p.add_run(f" · {role}")
                rr.font.size = Pt(10)
                rr.font.color.rgb = _rgb("#B8C2D0")
                _run_font(rr, self.head_font)
        line = str(m.get("date", "")) + (f"   |   {m['report_id']}" if m.get("report_id") else "")
        self._cpara(bottom, line, 9, "#B8C2D0", before=8, spacing=10)

        new = self.d.add_section(WD_SECTION.NEW_PAGE)
        self._tiny(self.d.paragraphs[-1])
        self._page_size(new)
        self._sect_margins(new, self.brand["layout"]["margin_in"])
        new.header_distance = new.footer_distance = Inches(0.5)
        self._header_footer(new)
        return new

    def _header_footer(self, section):
        c = self.c
        m = self.doc.meta
        section.header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False
        hp = section.header.paragraphs[0]
        hp.paragraph_format.tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CLEAR)
        hp.paragraph_format.tab_stops.add_tab_stop(Inches(self.text_width), WD_TAB_ALIGNMENT.RIGHT)
        r = hp.add_run(self.brand["org"]["wordmark"])
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = _rgb(c["navy"])
        _run_font(r, self.head_font)
        r = hp.add_run("\t" + str(m.get("short_title") or m["title"]))
        r.font.size = Pt(7.5)
        r.font.color.rgb = _rgb(c["ink_muted"])
        _run_font(r, self.head_font)
        _para_border(hp, "bottom", 4, c["rule"], 4)

        fp = section.footer.paragraphs[0]
        fp.paragraph_format.tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CLEAR)
        fp.paragraph_format.tab_stops.add_tab_stop(Inches(self.text_width), WD_TAB_ALIGNMENT.RIGHT)
        bits = [str(m.get("report_type", "Research Report"))]
        if m.get("report_id"):
            bits.append(str(m["report_id"]))
        bits.append(str(m.get("date", "")))
        r = fp.add_run(" · ".join(bits) + "\t")
        r.font.size = Pt(7.5)
        r.font.color.rgb = _rgb(c["ink_muted"])
        _run_font(r, self.head_font)

        def fnt(run):
            run.font.size = Pt(7.5)
            run.bold = True
            run.font.color.rgb = _rgb(c["navy"])
            _run_font(run, self.head_font)

        _field(fp, "PAGE", "2", fnt)

    def contents_page(self):
        m = self.doc.meta
        c = self.c
        p = self._para(self.d, "HH Label")
        p.add_run("ABOUT THIS REPORT")
        for para_text in [x.strip() for x in str(m.get("abstract", "")).split("\n\n") if x.strip()]:
            p = self._para(self.d)
            self.add_inlines(p, parse_inline_text(para_text))
        if m.get("keywords"):
            p = self._para(self.d, "HH Source")
            r = p.add_run("Keywords: ")
            r.bold = True
            p.add_run(" · ".join(str(k) for k in m["keywords"]))
            _para_border(p, "bottom", 4, c["rule"], 10)
        p = self._para(self.d, "HH Label")
        p.paragraph_format.space_before = Pt(14)
        p.add_run("CONTENTS")
        # TOC field, pre-filled with the heading list so it reads well before
        # Word refreshes it (settings.updateFields asks Word to refresh on open).
        depth = int(m.get("toc_depth", 2))
        entries = [b for b in self.doc.blocks if b["t"] == "heading" and b["level"] <= depth]
        first = self.d.add_paragraph(style="TOC 1")
        fb = OxmlElement("w:fldChar")
        fb.set(qn("w:fldCharType"), "begin")
        first.add_run()._r.append(fb)
        it = OxmlElement("w:instrText")
        it.set(qn("xml:space"), "preserve")
        it.text = f' TOC \\o "1-{depth}" \\h \\z \\u '
        first.add_run()._r.append(it)
        fs = OxmlElement("w:fldChar")
        fs.set(qn("w:fldCharType"), "separate")
        first.add_run()._r.append(fs)
        para = first
        for i, e in enumerate(entries):
            if i > 0:
                para = self.d.add_paragraph(style=f"TOC {e['level']}")
            elif e["level"] != 1:
                para.style = self.d.styles[f"TOC {e['level']}"]
            label = (f"{e['number']}  " if e.get("number") else "") + e["title"]
            para.add_run(label)
        fe = OxmlElement("w:fldChar")
        fe.set(qn("w:fldCharType"), "end")
        para.add_run()._r.append(fe)

    def back_cover(self):
        c = self.c
        org = self.brand["org"]
        m = self.doc.meta
        sect = self.d.add_section(WD_SECTION.NEW_PAGE)
        self._page_size(sect)
        self._sect_margins(sect, 0.9)
        sect.header.is_linked_to_previous = False
        sect.footer.is_linked_to_previous = False
        for hf in (sect.header, sect.footer):
            for p in hf.paragraphs:
                self._tiny(p)
        anchor_p = self.d.add_paragraph()
        self._tiny(anchor_p)
        self._anchor_background(anchor_p, sect, arcs=False)
        avail = sect.page_height.inches - 1.8
        top, bottom = self._two_zone(avail - 1.6)
        self._wordmark(top)
        self._cpara(top, "ABOUT", 9, c["accent"], True, before=30, after=4, spacing=30)
        self._cpara(top, org["about"], 13, "#FFFFFF", after=16, line=1.2)
        self._cpara(top, "HOW TO CITE", 9, c["accent"], True, before=8, after=4, spacing=30)
        names = ", ".join(a if isinstance(a, str) else a.get("name", "") for a in m.get("authors") or [])
        date = str(m.get("date"))
        year = date[-4:] if date[-4:].isdigit() else date[:4]
        cite = (f"{names} ({year}). {m['title']}. {org['name']} {m.get('report_type', 'Research Report')}"
                + (f" {m['report_id']}" if m.get("report_id") else "") + ".")
        self._cpara(top, cite, 9.5, "#E3E8EF", line=1.2)
        contact = " · ".join(x for x in (org.get("email"), org.get("website")) if x)
        if contact:
            self._cpara(top, "CONTACT", 9, c["accent"], True, before=16, after=4, spacing=30)
            self._cpara(top, contact, 9.5, "#E3E8EF")
        self._cpara(bottom, "DISCLAIMER", 7.5, "#B8C2D0", True, after=3, spacing=20)
        self._cpara(bottom, org["disclaimer"], 7.5, "#B8C2D0", after=6, line=1.15)
        self._cpara(bottom, f"© {year} {org['name']}. {date}" + (f" · {m['report_id']}" if m.get("report_id") else ""),
                    7.5, "#B8C2D0")
        self._tiny(self.d.add_paragraph())

    def settings(self):
        st = self.d.settings.element
        uf = OxmlElement("w:updateFields")
        uf.set(qn("w:val"), "true")
        st.append(uf)
        ah = OxmlElement("w:autoHyphenation")
        ah.set(qn("w:val"), "true")
        st.append(ah)
        m = self.doc.meta
        cp = self.d.core_properties
        cp.title = str(m["title"])
        cp.subject = str(m.get("subtitle", ""))
        cp.author = ", ".join(a if isinstance(a, str) else a.get("name", "") for a in m.get("authors") or [])
        cp.keywords = ", ".join(str(k) for k in m.get("keywords") or [])
        cp.comments = f"{self.brand['org']['name']} {m.get('report_type', 'Research Report')}"

    def render(self, path: Path):
        self.cover()
        self.contents_page()
        self.blocks(self.d, self.doc.blocks)
        self.back_cover()
        self.settings()
        self.d.save(str(path))


def render_docx(doc: Document, brand: dict, figures: dict, path: Path) -> None:
    DocxRenderer(doc, brand, figures).render(path)
