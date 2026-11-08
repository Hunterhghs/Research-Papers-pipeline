"""Markdown -> report document model.

The same model feeds every renderer (Typst/PDF and DOCX), so numbering,
captions and cross-references are identical in both outputs.

Block nodes are plain dicts with a "t" key:
  heading   level, inlines, numbered, number, id
  para      inlines
  list      ordered, start, items: [[block, ...], ...]
  table     header: [inlines], rows: [[inlines]], align, caption, source, number, id
  figure    kind ("chart"|"image"), spec|path, caption, source, width, number, id
  callout   style ("callout"|"keyfindings"), title, blocks
  stats     items: [{value, label: inlines}]
  quote     blocks, attribution (inlines|None)
  code      text
Inline nodes:
  text v | strong c | em c | code v | link href c | br
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.container import container_plugin
from mdit_py_plugins.front_matter import front_matter_plugin

CONTAINERS = ("callout", "keyfindings", "stats")
AUTO_UNNUMBERED = {
    "executive summary", "summary", "references", "sources", "bibliography",
    "notes", "endnotes", "glossary", "acknowledgements", "acknowledgments",
    "about the authors", "about this report",
}
REF_RE = re.compile(r"@(fig|tbl|sec):([A-Za-z0-9_-]+)")
HEADING_ATTR_RE = re.compile(r"\s*\{([^}]*)\}\s*$")


class ReportError(Exception):
    """Authoring error with a message an agent can act on."""


@dataclass
class Document:
    meta: dict
    blocks: list
    source_dir: Path
    warnings: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def _md() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"typographer": True, "html": True})  # html on so <!-- comments --> are dropped
    md.enable(["table", "strikethrough", "replacements", "smartquotes"])
    md.use(front_matter_plugin)
    md.use(attrs_plugin)
    for name in CONTAINERS:
        md.use(container_plugin, name=name)
    return md


MD = _md()


# ---------------------------------------------------------------- inlines
def parse_inline_text(text: str) -> list:
    """Parse a one-line markdown string (captions, sources, front matter)."""
    if not text:
        return []
    tokens = MD.parseInline(str(text).strip())
    root = SyntaxTreeNode(tokens)
    out = []
    for child in root.children:
        if child.type == "inline":
            out.extend(_inlines(child.children))
    return out


def _inlines(nodes) -> list:
    out: list = []
    for n in nodes:
        t = n.type
        if t == "text":
            out.append({"t": "text", "v": n.content})
        elif t == "softbreak":
            out.append({"t": "text", "v": " "})
        elif t == "hardbreak":
            out.append({"t": "br"})
        elif t == "strong":
            out.append({"t": "strong", "c": _inlines(n.children)})
        elif t == "em":
            out.append({"t": "em", "c": _inlines(n.children)})
        elif t == "s":
            out.extend(_inlines(n.children))
        elif t == "code_inline":
            out.append({"t": "code", "v": n.content})
        elif t == "link":
            out.append({"t": "link", "href": n.attrs.get("href", ""), "c": _inlines(n.children)})
        elif t == "image":
            # inline images are not supported; keep the alt text
            out.append({"t": "text", "v": n.content or ""})
        elif t == "html_inline":
            continue
        else:
            out.extend(_inlines(n.children) if n.children else [{"t": "text", "v": n.content or ""}])
    return _merge_text(out)


def _merge_text(items: list) -> list:
    merged: list = []
    for it in items:
        if it["t"] == "text" and merged and merged[-1]["t"] == "text":
            merged[-1] = {"t": "text", "v": merged[-1]["v"] + it["v"]}
        else:
            merged.append(it)
    return merged


def plain(inlines: list) -> str:
    parts = []
    for i in inlines:
        if i["t"] in ("text", "code"):
            parts.append(i["v"])
        elif i["t"] == "br":
            parts.append(" ")
        else:
            parts.append(plain(i.get("c", [])))
    return "".join(parts)


def _starts_with(inlines: list, prefixes: tuple) -> bool:
    return bool(inlines) and inlines[0]["t"] == "text" and inlines[0]["v"].lstrip().startswith(prefixes)


def _strip_prefix(inlines: list, prefix_re: str) -> list:
    if not inlines or inlines[0]["t"] != "text":
        return inlines
    first = re.sub(prefix_re, "", inlines[0]["v"], count=1)
    rest = inlines[1:]
    return ([{"t": "text", "v": first}] if first else []) + rest


def _no_widow(s: str, max_last: int = 12) -> str:
    """Bind the last two words with a no-break space so a title never ends on a lone word."""
    head, sep, last = s.rstrip().rpartition(" ")
    if sep and head and len(last) <= max_last:
        return head + "\u00a0" + last
    return s


def slugify(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_]+", "-", s)[:60] or "section"


# ---------------------------------------------------------------- blocks
def load(report_path: Path) -> Document:
    report_path = Path(report_path)
    if report_path.is_dir():
        report_path = report_path / "report.md"
    if not report_path.exists():
        raise ReportError(f"Report file not found: {report_path}")
    text = report_path.read_text(encoding="utf-8")
    # Long reports may be split: reports/<slug>/sections/*.md are appended to
    # report.md in filename order (01-intro.md, 02-market.md, ...).
    sec_dir = report_path.parent / "sections"
    if sec_dir.is_dir():
        for f in sorted(sec_dir.glob("*.md")):
            text = text.rstrip("\n") + "\n\n" + f.read_text(encoding="utf-8").strip("\n") + "\n"
    tokens = MD.parse(text)
    root = SyntaxTreeNode(tokens)
    lines = text.splitlines()

    meta: dict = {}
    body_nodes = []
    for node in root.children:
        if node.type == "front_matter":
            try:
                meta = yaml.safe_load(node.content) or {}
            except yaml.YAMLError as e:
                raise ReportError(f"Front matter is not valid YAML: {e}") from e
        else:
            body_nodes.append(node)

    for key in ("title", "subtitle"):
        if isinstance(meta.get(key), str):
            meta[key] = _no_widow(meta[key])
    doc = Document(meta=meta, blocks=[], source_dir=report_path.parent)
    doc.blocks = _blocks(body_nodes, doc, lines)
    _attach_captions(doc)
    _number(doc)
    _resolve_refs(doc)
    _validate(doc)
    return doc


def _blocks(nodes, doc: Document, lines: list) -> list:
    out = []
    for n in nodes:
        b = _block(n, doc, lines)
        if b is None:
            continue
        if isinstance(b, list):
            out.extend(b)
        else:
            out.append(b)
    return out


def _parse_attr_string(s: str) -> dict:
    attrs: dict = {}
    for part in s.split():
        if part == "-" or part == ".unnumbered":
            attrs["unnumbered"] = True
        elif part.startswith("#"):
            attrs["id"] = part[1:]
        elif "=" in part:
            k, v = part.split("=", 1)
            attrs[k] = v.strip('"')
    return attrs


def _block(n, doc: Document, lines: list):
    t = n.type
    if t == "heading":
        level = int(n.tag[1])
        inl = _inlines(n.children[0].children) if n.children else []
        attrs: dict = {}
        if inl and inl[-1]["t"] == "text":
            m = HEADING_ATTR_RE.search(inl[-1]["v"])
            if m:
                attrs = _parse_attr_string(m.group(1))
                inl[-1] = {"t": "text", "v": inl[-1]["v"][: m.start()]}
        title = plain(inl).strip()
        if level <= 2 and inl and inl[-1]["t"] == "text":
            inl[-1] = {"t": "text", "v": _no_widow(inl[-1]["v"])}
        numbered = not attrs.get("unnumbered") and not (level == 1 and title.lower() in AUTO_UNNUMBERED)
        if level > 3:
            level = 3
        return {"t": "heading", "level": level, "inlines": inl, "numbered": numbered,
                "id": attrs.get("id") or slugify(title), "title": title}

    if t == "paragraph":
        inline_node = n.children[0] if n.children else None
        kids = inline_node.children if inline_node else []
        real = [k for k in kids if not (k.type == "text" and not k.content.strip())]
        trailing = {}
        if (len(real) == 2 and real[0].type == "image" and real[1].type == "text"
                and re.fullmatch(r"\s*\{[^}]*\}\s*", real[1].content)):
            # attrs the plugin could not parse, e.g. {width=5.5in}
            trailing = _parse_attr_string(real[1].content.strip()[1:-1])
            real = real[:1]
        if len(real) == 1 and real[0].type == "image":
            img = real[0]
            attrs = {**dict(img.attrs), **trailing}
            return {"t": "figure", "kind": "image", "path": attrs.get("src", ""),
                    "caption": parse_inline_text(img.content), "source": None,
                    "width": attrs.get("width"), "id": attrs.get("id"),
                    "placement": attrs.get("placement")}
        inl = _inlines(kids)
        if plain(inl).strip() in ("\\newpage", "<!-- pagebreak -->"):
            return {"t": "pagebreak"}
        return {"t": "para", "inlines": inl}

    if t in ("bullet_list", "ordered_list"):
        items = []
        for li in n.children:
            items.append(_blocks(li.children, doc, lines))
        start = 1
        if t == "ordered_list":
            try:
                start = int(n.attrs.get("start", 1))
            except (TypeError, ValueError):
                start = 1
        return {"t": "list", "ordered": t == "ordered_list", "start": start, "items": items}

    if t == "table":
        header, rows, align = [], [], []
        for section in n.children:
            for tr in section.children:
                cells = []
                for cell in tr.children:
                    inl = _inlines(cell.children[0].children) if cell.children else []
                    cells.append(inl)
                    if section.type == "thead":
                        style = cell.attrs.get("style", "") if cell.attrs else ""
                        a = "left"
                        if "right" in style:
                            a = "right"
                        elif "center" in style:
                            a = "center"
                        align.append(a)
                if section.type == "thead":
                    header = cells
                else:
                    rows.append(cells)
        return {"t": "table", "header": header, "rows": rows, "align": align,
                "caption": None, "source": None, "id": None}

    if t == "fence":
        info = (n.info or "").strip().split()
        lang = info[0] if info else ""
        if lang == "chart":
            try:
                spec = yaml.safe_load(n.content) or {}
            except yaml.YAMLError as e:
                line = (n.map[0] + 1) if n.map else "?"
                raise ReportError(f"Chart block at line {line} is not valid YAML: {e}") from e
            if not isinstance(spec, dict) or "type" not in spec:
                line = (n.map[0] + 1) if n.map else "?"
                raise ReportError(f"Chart block at line {line} needs a 'type:' field")
            spec["_line"] = (n.map[0] + 1) if n.map else None
            return {"t": "figure", "kind": "chart", "spec": spec,
                    "caption": parse_inline_text(spec.get("caption", "")),
                    "source": parse_inline_text(spec.get("source", "")) or None,
                    "width": spec.get("width"), "id": spec.get("id"),
                    "placement": spec.get("placement")}
        return {"t": "code", "text": n.content.rstrip("\n")}

    if t == "code_block":
        return {"t": "code", "text": n.content.rstrip("\n")}

    if t == "blockquote":
        inner = _blocks(n.children, doc, lines)
        attribution = None
        if inner and inner[-1]["t"] == "para" and _starts_with(inner[-1]["inlines"], ("—", "--", "–")):
            attribution = _strip_prefix(inner.pop()["inlines"], r"^\s*(—|--|–)\s*")
        return {"t": "quote", "blocks": inner, "attribution": attribution}

    if t.startswith("container_"):
        name = t[len("container_"):]
        info = (n.info or "").strip()
        title = info[len(name):].strip().strip('"').strip("'") if info.startswith(name) else ""
        if name == "stats":
            return _stats_block(n, lines)
        style = name
        if name == "keyfindings" and not title:
            title = "Key findings"
        return {"t": "callout", "style": style, "title": title,
                "blocks": _blocks(n.children, doc, lines)}

    if t in ("hr", "html_block"):
        return None
    doc.warnings.append(f"Unsupported markdown element '{t}' ignored")
    return None


def _stats_block(n, lines: list) -> dict:
    start, end = n.map if n.map else (0, 0)
    items = []
    for raw in lines[start + 1:end]:
        s = raw.strip()
        if not s.startswith(("- ", "* ")):
            continue
        s = s[2:]
        if "|" not in s:
            raise ReportError(f"Stats item must be 'VALUE | label' (line {start + 1}): {raw.strip()}")
        value, label = s.split("|", 1)
        items.append({"value": value.strip().strip("*"), "label": parse_inline_text(label.strip())})
    if not 2 <= len(items) <= 4:
        raise ReportError(f"::: stats block near line {start + 1} needs 2-4 items, found {len(items)}")
    return {"t": "stats", "items": items}


# ---------------------------------------------------------------- passes
def _attach_captions(doc: Document) -> None:
    """'Table: ...' paragraph before a table -> caption; 'Source: ...' after a
    table or figure -> source note."""
    out = []
    blocks = doc.blocks
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b["t"] == "para" and _starts_with(b["inlines"], ("Table:",)) and i + 1 < len(blocks) and blocks[i + 1]["t"] == "table":
            cap = _strip_prefix(b["inlines"], r"^\s*Table:\s*")
            tbl = blocks[i + 1]
            if cap and cap[-1]["t"] == "text":
                m = HEADING_ATTR_RE.search(cap[-1]["v"])
                if m:
                    ta = _parse_attr_string(m.group(1))
                    tbl["id"] = ta.get("id")
                    tbl["placement"] = ta.get("placement")
                    cap[-1] = {"t": "text", "v": cap[-1]["v"][: m.start()]}
            tbl["caption"] = cap
            out.append(tbl)
            i += 2
            continue
        if b["t"] == "para" and _starts_with(b["inlines"], ("Source:", "Sources:", "Note:", "Notes:")) and out and out[-1]["t"] in ("table", "figure"):
            prev = out[-1]
            prev["source"] = (prev["source"] or []) + ([{"t": "text", "v": " "}] if prev["source"] else []) + b["inlines"]
            i += 1
            continue
        out.append(b)
        i += 1
    doc.blocks = out


def _walk(blocks):
    for b in blocks:
        yield b
        if b["t"] == "list":
            for item in b["items"]:
                yield from _walk(item)
        elif b["t"] in ("callout", "quote"):
            yield from _walk(b["blocks"])


def _number(doc: Document) -> None:
    sec = sub = 0
    fig = tbl = 0
    in_numbered = True
    refs: dict = {}
    for b in _walk(doc.blocks):
        if b["t"] == "heading":
            if b["level"] == 1:
                in_numbered = b["numbered"]
                if b["numbered"]:
                    sec += 1
                    sub = 0
                    b["number"] = str(sec)
                else:
                    b["number"] = None
                refs[("sec", b["id"])] = f"Section {sec}" if b["numbered"] else b["title"]
            elif b["level"] == 2:
                if in_numbered and b["numbered"]:
                    sub += 1
                    b["number"] = f"{sec}.{sub}"
                else:
                    b["number"] = None
                    b["numbered"] = False
                refs[("sec", b["id"])] = f"Section {b['number']}" if b["number"] else b["title"]
            else:
                b["number"] = None
        elif b["t"] == "figure":
            fig += 1
            b["number"] = fig
            if b.get("id"):
                refs[("fig", str(b["id"]))] = f"Figure {fig}"
        elif b["t"] == "table":
            tbl += 1
            b["number"] = tbl
            if b.get("id"):
                refs[("tbl", str(b["id"]))] = f"Table {tbl}"
    doc.stats.update({"sections": sec, "figures": fig, "tables": tbl})
    doc._refs = refs  # type: ignore[attr-defined]


def _resolve_inlines(inlines, refs, missing):
    out = []
    for i in inlines:
        if i["t"] == "text" and "@" in i["v"]:
            def repl(m):
                key = (m.group(1), m.group(2))
                if key in refs:
                    return refs[key]
                missing.add(m.group(0))
                return m.group(0)
            out.append({"t": "text", "v": REF_RE.sub(repl, i["v"])})
        elif "c" in i:
            out.append({**i, "c": _resolve_inlines(i["c"], refs, missing)})
        else:
            out.append(i)
    return out


def _resolve_refs(doc: Document) -> None:
    refs = doc._refs  # type: ignore[attr-defined]
    missing: set = set()
    for b in _walk(doc.blocks):
        for key in ("inlines", "caption", "source", "attribution"):
            if b.get(key):
                b[key] = _resolve_inlines(b[key], refs, missing)
        if b["t"] == "table":
            b["header"] = [_resolve_inlines(c, refs, missing) for c in b["header"]]
            b["rows"] = [[_resolve_inlines(c, refs, missing) for c in r] for r in b["rows"]]
        if b["t"] == "stats":
            for it in b["items"]:
                it["label"] = _resolve_inlines(it["label"], refs, missing)
    for m in sorted(missing):
        doc.warnings.append(f"Unresolved cross-reference {m} (no figure/table/section with that id)")


def _count_words(blocks) -> int:
    n = 0
    for b in _walk(blocks):
        for key in ("inlines", "caption", "source"):
            if b.get(key):
                n += len(plain(b[key]).split())
        if b["t"] == "table":
            for r in b["rows"]:
                for c in r:
                    n += len(plain(c).split())
    return n


def _count_links(blocks) -> list:
    links = []

    def scan(inl):
        for i in inl:
            if i["t"] == "link":
                links.append(i["href"])
            if "c" in i:
                scan(i["c"])

    for b in _walk(blocks):
        for key in ("inlines", "caption", "source", "attribution"):
            if b.get(key):
                scan(b[key])
        if b["t"] == "table":
            for r in [b["header"], *b["rows"]]:
                for c in r:
                    scan(c)
        if b["t"] == "stats":
            for it in b["items"]:
                scan(it["label"])
    return links


REQUIRED_META = ("title", "subtitle", "date", "authors", "abstract")


def _validate(doc: Document) -> None:
    missing = [k for k in REQUIRED_META if not doc.meta.get(k)]
    if missing:
        raise ReportError(f"Front matter is missing required field(s): {', '.join(missing)}")
    if not any(b["t"] == "heading" and b["level"] == 1 for b in doc.blocks):
        raise ReportError("Report has no '# ' sections")
    if doc.blocks and not (doc.blocks[0]["t"] == "heading" and doc.blocks[0]["level"] == 1):
        doc.warnings.append("Content appears before the first '# ' section; it will sit on the contents page")
    for b in _walk(doc.blocks):
        if b["t"] == "figure":
            if not b["caption"]:
                doc.warnings.append(f"Figure {b['number']} has no caption")
            if not b["source"]:
                doc.warnings.append(f"Figure {b['number']} has no source note (add 'source:' or a 'Source:' line)")
            if b["kind"] == "image":
                p = (doc.source_dir / b["path"]) if b["path"] else None
                if not p or not p.exists():
                    raise ReportError(f"Figure {b['number']}: image not found: {b['path']}")
        if b["t"] == "table":
            if not b["caption"]:
                doc.warnings.append(f"Table {b['number']} has no 'Table:' caption line")
        if b["t"] == "link" or b["t"] == "para":
            pass
    links = _count_links(doc.blocks)
    bad = [h for h in links if not re.match(r"^(https?://|mailto:)", h)]
    for h in bad:
        doc.warnings.append(f"Link is not an absolute http(s) URL: {h}")
    doc.stats.update({"words": _count_words(doc.blocks), "links": len(links),
                      "unique_links": len(set(links)), "link_urls": sorted(set(links))})


def figure_width(b: dict, layout: dict, warnings: list) -> float:
    """Resolve a figure width in inches, clamped to the house range."""
    w = b.get("width")
    lo, hi = float(layout["figure_min_in"]), float(layout["figure_max_in"])
    if w is None or w == "":
        return float(layout["figure_width_in"])
    s = str(w).strip().lower()
    try:
        if s.endswith("in"):
            v = float(s[:-2])
        elif s.endswith("%"):
            v = 6.5 * float(s[:-1]) / 100
        else:
            v = float(s)
    except ValueError:
        warnings.append(f"Figure {b['number']}: width '{w}' not understood; using default")
        return float(layout["figure_width_in"])
    if not lo <= v <= hi:
        warnings.append(f"Figure {b['number']}: width {v:.2f}in clamped to {lo}-{hi}in house range")
        v = min(max(v, lo), hi)
    return v
