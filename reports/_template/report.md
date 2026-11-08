---
title: "{{TITLE}}"
subtitle: "One sentence that states the report's argument, not just its topic"
short_title: "{{TITLE}}"          # running header; keep under ~45 characters
report_type: "Research Report"    # or "Industry Brief", "Technical Note", "Market Outlook"
report_id: "{{REPORT_ID}}"
date: "{{DATE}}"
authors:
  - name: "H Heuristics Research"
    role: "Research Team"
keywords: [keyword one, keyword two, keyword three]
toc_depth: 2
abstract: |
  120-180 words. What question does the report answer, why does it matter now, what evidence
  does it use, and what is the headline conclusion? Link one or two key sources inline, e.g.
  [the primary dataset](https://example.org/real-url-you-verified).

  Optional second paragraph: scope and method in two or three sentences.
---

<!--
  HOW TO USE THIS TEMPLATE
  - Executive Summary lives here; numbered sections live in sections/01-*.md ... 08-*.md,
    and References in sections/99-references.md. Files are joined in filename order.
  - Target: 30-50 PDF pages = roughly 9,000-13,000 words + 8-14 figures + 4-8 tables.
  - Full syntax: docs/AUTHORING_GUIDE.md.  Writing rules: docs/STYLE_GUIDE.md.
  - Build + check: ./hh make <slug>   (repeat until QA -> PASS with no fill warnings)
  - Delete these comments when done (they are ignored by the renderer anyway).
-->

# Executive Summary

<!-- 700-1,000 words. Lead with the answer. Then the key findings box, a stats row, and
     3-4 paragraphs on implications and recommendations. Must stand alone. -->

Opening paragraph: the single most important conclusion, stated plainly, with the evidence that supports it and a [link to the source](https://example.org).

::: keyfindings
1. **First finding in bold.** One or two sentences of explanation with the number that matters.
2. **Second finding.** ...
3. **Third finding.** ...
4. **Fourth finding.** ...
5. **Fifth finding.** ...
:::

::: stats
- 00% | short label for the first headline number
- $0.0bn | short label for the second headline number
- 0x | short label for the third headline number
:::

Implications paragraph(s).

Recommendations paragraph, then a sentence that maps the rest of the report: @sec:context sets out ..., @sec:findings examines ...
