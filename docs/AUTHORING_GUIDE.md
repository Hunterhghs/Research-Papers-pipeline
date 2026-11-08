# Authoring Guide

Everything a writer (human or AI) needs to produce a report the pipeline renders correctly.
The visual reference for every element is `reports/_features/report.md`; build it with
`./hh qa _features` and open `output/_features/_features.pdf`.

## 1. Files and layout

```
reports/<slug>/
  report.md               front matter + Executive Summary
  sections/01-*.md        one file per numbered section (joined in filename order)
  sections/99-references.md
  figures/                optional: your own PNG/JPG/SVG images
```

You may also write everything in `report.md`; the `sections/` folder is optional but strongly
recommended for long reports because each file can be drafted, checked and revised on its own.

## 2. Front matter (YAML, top of report.md)

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Cover title. Markdown emphasis allowed. |
| `subtitle` | yes | One sentence stating the argument. |
| `date` | yes | e.g. `"November 2026"`. |
| `authors` | yes | List of `{name, role}` or plain strings. |
| `abstract` | yes | 120–180 words; links allowed; blank line = new paragraph. |
| `short_title` | no | Running header (keep under ~45 characters). Defaults to title. |
| `report_type` | no | Cover kicker, default `Research Report`. |
| `report_id` | no | e.g. `HH-2026-014`. `./hh new` assigns one. |
| `keywords` | no | List; shown on contents page and in PDF metadata. |
| `toc_depth` | no | `1` or `2` (default 2). |
| `sample` | no | `true` adds a "SAMPLE · ILLUSTRATIVE DATA" badge to the cover. |
| `figure_placement` | no | Default for all figures: `bottom` (default), `top`, `auto`, `here`. |

## 3. Structure rules

- `# Heading` = **section**. Every section starts on a new page. Numbered automatically
  (Section 01, 02 …) except *Executive Summary*, *References*, *Sources*, *Notes*, *Glossary*,
  *Acknowledgements*, *About this report*, or any heading ending in `{-}`.
- `## Heading` = **subsection** (1.1, 1.2 …). Never starts a new page.
- `### Heading` = minor heading (unnumbered, run in the flow).
- Give a section or subsection an id for cross-references: `# Market Landscape {#landscape}`.
- Do not insert manual page breaks. Pagination is automatic.

## 4. Text

Standard Markdown: `**bold**`, `*italic*`, `` `code` ``, bullet lists (`-`), numbered lists
(`1.`), nested lists (indent 3 spaces), block quotes (`>`). Straight quotes and `--`/`---` are
converted to typographic quotes and dashes automatically.

**Hyperlinks** are written inline and render as live links in both PDF and Word:

```markdown
Adoption doubled in two years, according to the [OECD Digital Economy Outlook](https://www.oecd.org/...).
```

Use descriptive anchor text (the name of the source), never "click here" or a bare URL in
body text. Every link must be an absolute `https://` URL that you have opened and verified.

**Pull quote** – a block quote whose last paragraph starts with an em dash becomes an attributed
pull quote:

```markdown
> The constraint on modern decision-making is attention, not data.
>
> — Name Surname, Title, Organization
```

## 5. Cross-references

Write `@fig:id`, `@tbl:id` or `@sec:id` in text; they become "Figure 3", "Table 2",
"Section 4" (numbers are assigned automatically, identically in PDF and Word). Unresolved
references are reported by `./hh lint` and QA.

## 6. Callouts, key findings and stat rows

```markdown
::: callout Optional title
Shaded box with a blue rule. Paragraphs and lists allowed.
:::

::: keyfindings
1. **Finding.** Explanation.
2. **Finding.** Explanation.
:::

::: keyfindings What success looks like
- Title after the keyword overrides the default "Key findings".
:::

::: stats
- 42% | label text (may contain *emphasis* and [links](https://…))
- $3.1T | second stat
- 7x | third stat
:::
```

`stats` takes 2–4 items in `VALUE | label` form. Use real, sourced numbers.

## 7. Tables

```markdown
Table: Caption text that states the takeaway {#costs}

| Item | 2024 | 2025 | Change |
|:-----|-----:|-----:|-------:|
| Compute | 10.2 | 12.5 | +22% |

Source: Organization, [Dataset name](https://…); H Heuristics analysis.
```

- The `Table:` line immediately **before** the table is the caption; `{#id}` is optional.
- A `Source:` (or `Note:`) paragraph immediately **after** becomes the source note.
- Alignment comes from the separator row (`:--` left, `--:` right, `:-:` centre). Right-align numbers.
- Tables of up to 14 rows float (kept whole, placed to avoid page gaps). Longer tables flow and
  break across pages with a repeated header. Override with `{#id placement=here}`.
- Keep tables to 2–6 columns and short cell text; long prose belongs in paragraphs.

## 8. Charts (fenced `chart` blocks, YAML inside)

Every chart is drawn in the house style (fonts, palette, gridlines, legend rules) at 6 in wide.
Common keys for all types:

| Key | Meaning |
|---|---|
| `type` | one of the types below (required) |
| `caption` | figure title shown above the chart — state the insight, not the topic (required) |
| `source` | source note under the chart; Markdown links allowed (required) |
| `id` | for `@fig:id` references |
| `width` | 5.0–6.0 (inches), default 6.0 |
| `height` | inches, default 3.3 (diagrams size themselves) |
| `placement` | `bottom` (default), `top`, `auto`, `here` |
| `prefix` / `suffix` | value formatting, e.g. `prefix: "$"`, `suffix: "%"` |
| `format` | Python format for values, e.g. `"{:,.1f}"` |
| `x_label` / `y_label` | axis titles |
| `annotations` | `[{x: <category or value>, y: <value>, text: "…", dx: 10, dy: 18}]` |

House rules enforced by the engine: max 6 series, no dual axes, legend only when there are
2+ series, one fixed colour order.

### Data charts

```chart
type: line            # also: area (single or multi series, filled)
caption: "Adoption is accelerating in large firms"
source: "Source: [Survey name](https://…), 2026."
categories: [2020, 2021, 2022, 2023, 2024, 2025]
suffix: "%"
series:
  - name: Large firms
    values: [5, 9, 14, 21, 29, 38]
  - name: SMEs
    values: [2, 3, 5, 8, 12, 16]
    projected_from: 2024    # optional: dashed after this category
```

| Type | Data keys | Use for |
|---|---|---|
| `line`, `area` | `categories`, `series` (or `values`) | change over time |
| `bar` | `categories`, `series` or `values`; `highlight: [cat]` | comparing categories (columns) |
| `barh` | same as `bar` | rankings, long category names |
| `stacked_bar`, `stacked_barh` | `categories`, `series`; `totals: false` to hide totals | composition across categories |
| `dumbbell` | `categories`, exactly 2 `series` | before/after, gap between two groups |
| `scatter` | `points: [{label, x, y, group, size}]`, `trend: true`, `x_suffix`, `y_suffix` | relationships |
| `donut` | `categories`, `values` (≤6), `center_text`, `center_label` | share of a whole (use sparingly) |
| `waterfall` | `categories`, `values` (first & last are totals) | bridges: how A became B |
| `heatmap` | `rows`, `columns`, `values` (rows × columns) | two-way comparison grids |

### Diagrams

| Type | Keys | Use for |
|---|---|---|
| `process` | `steps: [{title, text}]` (2–6) | methods, sequences, frameworks |
| `matrix` | `x_label`, `y_label`, `quadrants: [TL, TR, BL, BR]` each `{title, text}`, optional `points: [{label, x, y}]` in 0–1 | 2×2 frameworks |
| `timeline` | `events: [{date, title, text, highlight}]` (3–9) | history, roadmaps |

## 9. Images

```markdown
![Caption text for the image](figures/my-diagram.png){width=5.5in}

Source: Organization, [link](https://…).
```

A paragraph containing only an image becomes a numbered figure. PNG, JPG and SVG are supported;
use at least 1800 px wide for raster images. Width is clamped to 5.0–6.0 in. Only use images
you have rights to publish.

## 10. What the pipeline handles for you

Cover, inside-cover abstract, two-column contents with page numbers, running headers and
footers, section openers, figure/table numbering, PDF bookmarks, document metadata, back cover
with About/How to cite/Disclaimer (from `brand/brand.yaml`), Word styles and a Word TOC field
that refreshes on open. Do not try to reproduce any of these in Markdown.
