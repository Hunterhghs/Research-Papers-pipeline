// H Heuristics research report template (Typst).
// Generated report sources import this file; do not hand-edit generated files.
// All colours, fonts and sizes arrive from brand/brand.yaml via `brand`.

#let _c(brand, key) = rgb(brand.colors.at(key))

// ------------------------------------------------------------ headings
#let hh-heading(level: 1, num: none, kicker: none, body) = heading(
  level: level,
  numbering: if num == none { none } else { (..n) => num },
  supplement: if kicker == none { [] } else { [#kicker] },
  outlined: true,
  body,
)

#let hh-section-break() = {
  place.flush()
  pagebreak(weak: true)
}

// ------------------------------------------------------------ cover
#let _cover(meta, brand) = {
  let navy = _c(brand, "navy")
  let accent = _c(brand, "accent")
  page(margin: 0pt, fill: navy, header: none, footer: none, numbering: none)[
    #set text(hyphenate: false)
    // decorative arcs, bottom-right
    #for i in range(1, 9) {
      let r = 70pt * i
      place(bottom + right, dx: r * 0.55, dy: r * 0.55,
        circle(radius: r, stroke: 0.6pt + white.transparentize(88% - i * 0.4%)))
    }
    #place(top + left, dx: 0.9in, dy: 0.85in)[
      #box(width: 16pt, height: 16pt, fill: accent, radius: 1pt,
        align(center + horizon, text(font: brand.fonts.sans, weight: "bold", size: 10pt, fill: navy)[H]))
      #h(8pt)
      #box(baseline: -3pt, text(font: brand.fonts.sans, weight: "semibold", size: 10pt, tracking: 2.6pt, fill: white)[#brand.org.wordmark])
    ]
    #place(top + left, dx: 0.9in, dy: 3.1in, block(width: 6.4in)[
      #text(font: brand.fonts.sans, size: 10pt, weight: "bold", tracking: 2pt, fill: accent)[#upper(meta.report_type)]
      #v(14pt)
      #set par(leading: 0.32em, justify: false)
      #text(font: brand.fonts.serif_display, size: 36pt, weight: "semibold", fill: white)[#meta.title]
      #v(18pt)
      #set par(leading: 0.5em)
      #text(font: brand.fonts.sans, size: 15pt, weight: "regular", fill: white.transparentize(18%))[#meta.subtitle]
      #v(24pt)
      #box(width: 64pt, height: 3pt, fill: accent)
    ])
    #if meta.sample {
      place(top + right, dx: -0.9in, dy: 0.8in,
        box(stroke: 0.8pt + accent, inset: (x: 8pt, y: 5pt), radius: 2pt,
          text(font: brand.fonts.sans, size: 8pt, weight: "bold", tracking: 1.4pt, fill: accent)[SAMPLE · ILLUSTRATIVE DATA]))
    }
    #place(bottom + left, dx: 0.9in, dy: -0.85in, block(width: 4.6in)[
      #set par(leading: 0.55em, justify: false)
      #text(font: brand.fonts.sans, size: 10pt, fill: white)[
        #for a in meta.authors [
          #text(weight: "semibold")[#a.name]#if a.at("role", default: none) != none [ · #text(fill: white.transparentize(30%))[#a.role]] \
        ]
      ]
      #v(10pt)
      #text(font: brand.fonts.sans, size: 9pt, tracking: 0.6pt, fill: white.transparentize(30%))[
        #meta.date#if meta.report_id != none [ #h(6pt)|#h(6pt) #meta.report_id]
      ]
    ])
  ]
}

// ------------------------------------------------------------ back cover
#let _back(meta, brand) = {
  let navy = _c(brand, "navy")
  let accent = _c(brand, "accent")
  page(margin: (x: 0.9in, top: 1in, bottom: 0.9in), fill: navy, header: none, footer: none)[
    #set text(font: brand.fonts.sans, fill: white.transparentize(12%), size: 9.5pt)
    #set par(justify: false, leading: 0.62em, spacing: 1em)
    #box(width: 16pt, height: 16pt, fill: accent, radius: 1pt,
      align(center + horizon, text(weight: "bold", size: 10pt, fill: navy)[H]))
    #h(8pt)
    #box(baseline: -3pt, text(weight: "semibold", size: 10pt, tracking: 2.6pt, fill: white)[#brand.org.wordmark])
    #v(36pt)
    #text(size: 9pt, weight: "bold", tracking: 1.8pt, fill: accent)[ABOUT]
    #v(2pt)
    #text(size: 13pt, fill: white)[#brand.org.about]
    #v(22pt)
    #text(size: 9pt, weight: "bold", tracking: 1.8pt, fill: accent)[HOW TO CITE]
    #v(2pt)
    #meta.citation
    #if meta.contact != none [
      #v(22pt)
      #text(size: 9pt, weight: "bold", tracking: 1.8pt, fill: accent)[CONTACT]
      #v(2pt)
      #meta.contact
    ]
    #v(1fr)
    #line(length: 100%, stroke: 0.5pt + white.transparentize(70%))
    #v(4pt)
    #text(size: 7.5pt, fill: white.transparentize(35%))[
      #text(weight: "bold", tracking: 1.2pt)[DISCLAIMER] \
      #brand.org.disclaimer
    ]
    #v(8pt)
    #text(size: 7.5pt, fill: white.transparentize(35%))[© #meta.year #brand.org.name. #meta.date#if meta.report_id != none [ · #meta.report_id]]
  ]
}

// ------------------------------------------------------------ blocks
#let hh-figure(path, width: 6in, num: 1, caption: none, source: none, placement: "bottom", brand: none) = {
  let fig = block(width: 100%, breakable: false, above: 18pt, below: 18pt)[
    #set align(left)
    #set par(justify: false, leading: 0.45em, spacing: 0pt)
    #text(font: brand.fonts.sans, size: 8pt, weight: "bold", tracking: 1.2pt, fill: _c(brand, "blue"))[FIGURE #num]
    #v(3pt)
    #text(font: brand.fonts.sans, size: 10.5pt, weight: "semibold", fill: _c(brand, "navy"))[#caption]
    #v(5pt)
    #line(length: 100%, stroke: 0.5pt + _c(brand, "rule"))
    #v(6pt)
    #align(center, image(path, width: width))
    #v(4pt)
    #line(length: 100%, stroke: 0.5pt + _c(brand, "rule"))
    #if source != none {
      v(4pt)
      text(font: brand.fonts.sans, size: 7.5pt, fill: _c(brand, "ink_muted"))[#source]
    }
  ]
  // Floats fill pages without leaving gaps. "bottom" (default) never lands above
  // a section heading; "top"/"auto" are allowed; "here" keeps it in the flow.
  if placement == "here" { fig } else {
    let where = if placement == "top" { top } else if placement == "auto" { auto } else { bottom }
    place(where, float: true, clearance: 18pt, fig)
  }
}

#let hh-table(num: 1, caption: none, source: none, columns: (), aligns: (), header: (), rows: (), placement: "here", brand: none) = {
  let navy = _c(brand, "navy")
  let floating = placement != "here"
  let tbl = block(width: 100%, above: 16pt, below: 16pt, breakable: not floating)[
    #set align(left)
    #set par(justify: false, leading: 0.45em, spacing: 0pt)
    #block(sticky: true, below: 6pt)[
      #text(font: brand.fonts.sans, size: 8pt, weight: "bold", tracking: 1.2pt, fill: _c(brand, "blue"))[TABLE #num]
      #v(3pt)
      #text(font: brand.fonts.sans, size: 10.5pt, weight: "semibold", fill: navy)[#caption]
    ]
    #set text(font: brand.fonts.sans, size: 8.5pt, hyphenate: false)
    #table(
      columns: columns,
      stroke: none,
      inset: (x: 6pt, y: 5pt),
      align: (x, y) => aligns.at(x, default: left) + horizon,
      fill: (x, y) => if y == 0 { navy } else if calc.even(y) { _c(brand, "tint") } else { none },
      table.header(..header.map(h => text(fill: white, weight: "semibold")[#h])),
      ..rows.flatten(),
      table.hline(stroke: 0.8pt + navy),
    )
    #if source != none {
      v(5pt)
      text(font: brand.fonts.sans, size: 7.5pt, fill: _c(brand, "ink_muted"))[#source]
    }
  ]
  // Short tables float (kept whole, no page gaps); long tables break across
  // pages with a repeating header.
  if floating {
    let where = if placement == "top" { top } else if placement == "auto" { auto } else { bottom }
    place(where, float: true, clearance: 18pt, tbl)
  } else { tbl }
}

#let hh-callout(title: none, style: "callout", brand: none, body) = {
  let keyf = style == "keyfindings"
  block(
    width: 100%, breakable: true, above: 14pt, below: 14pt,
    fill: if keyf { _c(brand, "tint_accent") } else { _c(brand, "tint") },
    stroke: (left: 3pt + if keyf { _c(brand, "accent") } else { _c(brand, "blue") }),
    inset: (left: 14pt, right: 14pt, top: 11pt, bottom: 12pt),
  )[
    #set par(justify: false)
    #set text(size: 0.95em)
    #if title != none and title != "" {
      block(sticky: true, below: 8pt, text(font: brand.fonts.sans, size: 10.5pt, weight: "bold", fill: _c(brand, "navy"))[#title])
    }
    #body
  ]
}

#let hh-stats(items, brand: none) = block(width: 100%, above: 16pt, below: 16pt, breakable: false)[
  #grid(
    columns: (1fr,) * items.len(),
    column-gutter: 14pt,
    ..items.map(it => block(width: 100%, stroke: (top: 2pt + _c(brand, "accent")), inset: (top: 8pt))[
      #set par(justify: false, leading: 0.4em, spacing: 0pt)
      #text(font: brand.fonts.serif_display, size: 24pt, weight: "semibold", fill: _c(brand, "navy"))[#it.at(0)]
      #v(6pt)
      #set par(leading: 0.5em)
      #text(font: brand.fonts.sans, size: 8.5pt, fill: _c(brand, "ink_muted"))[#it.at(1)]
    ]),
  )
]

#let hh-quote(attribution: none, brand: none, body) = block(
  width: 100%, above: 16pt, below: 16pt, inset: (left: 18pt, y: 4pt),
  stroke: (left: 2pt + _c(brand, "accent")),
)[
  #set par(justify: false, leading: 0.55em)
  #text(font: brand.fonts.serif, style: "italic", size: 13pt, fill: _c(brand, "navy"))[#body]
  #if attribution != none {
    v(4pt)
    text(font: brand.fonts.sans, size: 8.5pt, fill: _c(brand, "ink_muted"))[— #attribution]
  }
]

// ------------------------------------------------------------ main
#let report(meta: (:), brand: (:), body) = {
  let ink = _c(brand, "ink")
  let navy = _c(brand, "navy")
  let blue = _c(brand, "blue")
  let accent = _c(brand, "accent")
  let muted = _c(brand, "ink_muted")
  let rule = _c(brand, "rule")
  let sans = brand.fonts.sans

  set document(title: meta.title_plain, author: meta.author_names, keywords: meta.keywords)
  set text(font: brand.fonts.serif, size: brand.layout.body_size_pt * 1pt, fill: ink, lang: "en",
    hyphenate: true, number-type: "lining")
  set par(justify: true, leading: brand.layout.leading_em * 1em, spacing: 0.95em,
    linebreaks: "optimized")

  set page(
    paper: brand.layout.paper,
    margin: (x: brand.layout.margin_in * 1in, top: brand.layout.margin_in * 1in, bottom: brand.layout.margin_in * 1in),
    header-ascent: 38%,
    footer-descent: 38%,
    header: context {
      if here().page() > 1 {
        set text(font: sans, size: 7.5pt, fill: muted)
        grid(columns: (1fr, auto),
          text(weight: "semibold", tracking: 1.6pt, fill: navy)[#brand.org.wordmark],
          text[#meta.short_title])
        v(-4pt)
        line(length: 100%, stroke: 0.5pt + rule)
      }
    },
    footer: context {
      if here().page() > 1 {
        set text(font: sans, size: 7.5pt, fill: muted)
        grid(columns: (1fr, auto),
          text[#meta.report_type#if meta.report_id != none [ · #meta.report_id] · #meta.date],
          text(weight: "semibold", fill: navy)[#counter(page).display()])
      }
    },
  )

  // links: blue, hairline underline
  show link: it => underline(stroke: 0.4pt + blue.lighten(45%), offset: 1.8pt, evade: true,
    text(fill: blue, it))

  // lists
  set list(indent: 2pt, body-indent: 8pt, spacing: 0.55em,
    marker: (text(fill: accent, size: 0.9em)[■], text(fill: muted)[–]))
  set enum(indent: 2pt, body-indent: 6pt, spacing: 0.55em,
    numbering: n => text(font: sans, weight: "bold", fill: blue, size: 0.92em)[#n.])

  show raw.where(block: true): it => block(width: 100%, fill: _c(brand, "tint"), inset: 10pt, radius: 2pt,
    text(size: 8pt, it))
  show raw.where(block: false): set text(size: 0.92em)

  // headings
  // Section openers: the page break is emitted *before* the heading by
  // hh-section-break() so outline page numbers and PDF bookmarks are right.
  show heading.where(level: 1): it => {
    set text(hyphenate: false)
    set par(justify: false, leading: 0.3em)
    block(width: 100%, above: 0pt, below: 20pt)[
      #if it.numbering != none {
        text(font: sans, size: 8.5pt, weight: "bold", tracking: 2pt, fill: blue)[SECTION #it.supplement]
        v(8pt)
      } else {
        text(font: sans, size: 8.5pt, weight: "bold", tracking: 2pt, fill: blue)[#upper(meta.short_title)]
        v(8pt)
      }
      #text(font: brand.fonts.serif_display, size: 25pt, weight: "semibold", fill: navy)[#it.body]
      #v(12pt)
      #box(width: 46pt, height: 3pt, fill: accent)
    ]
  }
  show heading.where(level: 2): it => block(above: 17pt, below: 8pt, sticky: true)[
    #set par(justify: false, leading: 0.4em)
    #set text(hyphenate: false)
    #set text(font: sans, size: 12.5pt, weight: "semibold", fill: navy)
    #if it.numbering != none [#text(fill: blue)[#counter(heading).display(it.numbering)]#h(9pt)]#it.body
  ]
  show heading.where(level: 3): it => block(above: 13pt, below: 6pt, sticky: true)[
    #set par(justify: false)
    #text(font: sans, size: 10.5pt, weight: "semibold", fill: navy)[#it.body]
  ]

  // ---- cover
  _cover(meta, brand)

  // ---- inside cover: about this report + contents
  {
    set par(justify: false)
    block(width: 100%, below: 18pt)[
      #text(font: sans, size: 8.5pt, weight: "bold", tracking: 2pt, fill: blue)[ABOUT THIS REPORT]
      #v(6pt)
      #set text(size: 10.5pt)
      #set par(justify: true)
      #meta.abstract
      #if meta.keywords.len() > 0 {
        v(4pt)
        text(font: sans, size: 8pt, fill: muted)[#text(weight: "semibold")[Keywords:] #meta.keywords.join(" · ")]
      }
    ]
    line(length: 100%, stroke: 0.5pt + rule)
    v(10pt)
    text(font: sans, size: 8.5pt, weight: "bold", tracking: 2pt, fill: blue)[CONTENTS]
    v(4pt)
    show outline.entry: set text(font: sans, size: 8.8pt)
    show outline.entry.where(level: 1): it => {
      set text(weight: "semibold", fill: navy, size: 10pt)
      v(5pt)
      it
    }
    // two columns keep the contents and the abstract on a single page
    columns(2, gutter: 22pt, outline(title: none, depth: meta.toc_depth, indent: 1.2em))
  }

  body

  place.flush()
  _back(meta, brand)
}
