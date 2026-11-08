# AGENTS.md — Operating manual for AI agents

You are producing **H Heuristics research reports**: 30–50 page, publication-ready PDF and
Word documents, written in Markdown and rendered by this repository's pipeline. This file is
the contract. Read it fully before starting, then read `docs/AUTHORING_GUIDE.md` (syntax) and
`docs/STYLE_GUIDE.md` (writing and sourcing rules).

## Ground rules

1. **Truth over length.** Never invent statistics, quotes, studies, authors or URLs. Every
   factual claim gets an inline link to a source you actually opened. If you cannot verify
   something, drop it. The QA gate checks every link live and fails on broken ones.
2. **Only write inside `reports/<slug>/`** (and update `queue/topics.csv`). Do not edit
   `hhreport/`, `brand/`, `docs/`, `reports/_template/` or anything in `build/` or `output/`
   unless the user explicitly asks. Never hand-edit generated files (`build/*/report.typ`,
   PDFs, DOCX).
3. **The pipeline does the design.** Do not try to control layout with HTML, manual page breaks,
   blank lines or invisible characters. Write content; fix layout problems by changing content
   length, as described below.
4. **Done means QA PASS with no warnings you have not deliberately accepted**, page count in
   30–50, and a visual review of the preview image.

## Setup (once per machine)

```bash
./setup.sh            # creates .venv and installs requirements (Python 3.10+)
./hh qa _features     # smoke test: must print "QA  _features  ->  PASS"
```

## Workflow for one report

### 1. Scaffold

```bash
./hh new <slug> --title "Working Title"
```

`<slug>` is lowercase-with-hyphens, e.g. `ai-in-commercial-insurance-2027`. This copies
`reports/_template/` to `reports/<slug>/` with `report.md` (front matter + Executive Summary)
and `sections/01-…08-*.md` + `sections/99-references.md`.

### 2. Research first

Before writing prose, build an evidence base in `reports/<slug>/research-notes.md` (this file
is not rendered). For each source record: title, publisher, date, URL, and the specific facts
or numbers you will use. Aim for **30–50 sources**, mostly primary: statistical agencies,
regulators, central banks, international organizations, company filings, peer-reviewed papers,
established research institutes. Open every URL. Note the data year for every number.

### 3. Outline

Rename/re-title the section files to fit the topic (6–9 numbered sections; keep the `NN-`
prefix order). Give each section an id (`# Title {#id}`) and 3–5 `##` subsections. Decide where
each figure and table goes and what data it needs. Plan **8–14 figures** and **4–8 tables**,
spread across sections, with at least two or three paragraphs between consecutive visuals.

### 4. Draft section by section

Write one section file at a time, 1,100–1,500 words each (Executive Summary 700–1,000).
After each file:

```bash
./hh lint <slug>      # fast: syntax, captions, cross-references, links count
```

### 5. Build and run the quality gate

```bash
./hh make <slug>      # build PDF + DOCX, run QA, check every link live
```

Outputs: `output/<slug>/<slug>.pdf`, `output/<slug>/<slug>.docx`. QA details:
`build/<slug>/qa.json`; page thumbnails: `build/<slug>/preview.png`.

### 6. Fix what QA reports — iterate until clean

QA prints errors, warnings and a **How to fix** list with concrete instructions. Typical fixes:

| QA message | What to do |
|---|---|
| `Report is N pages; minimum is 30` | Add substantive analysis: deepen thin sections, add a case study, a data table, or a figure. The message tells you roughly how many words. |
| `Report is N pages; maximum is 50` | Cut repetition, merge overlapping subsections, move detail into tables. |
| `Section 'X' ends on pN at 18% page fill` | Every section starts on a new page, so a short final page leaves white space. **Either add the suggested number of words (or a figure/table) to that section, or trim the suggested number so it ends one page earlier.** Prefer adding real analysis when the section is thin; prefer trimming when it is padded. |
| `pN is only 62% full but is not the end of a section` / `blank gap inside the page` | Usually two visuals too close together or a big table. Move one figure later in the text, add text between visuals, or set `placement: top` on a figure. |
| `Broken link` | Find the correct URL by searching for the exact document; replace or remove the claim. Never guess URLs. |
| `Link could not be verified (site blocks bots)` | Acceptable if you opened the page yourself and it is correct. |
| `Unresolved cross-reference @fig:x` | Fix the id or the reference. |
| `Figure N has no source note` | Add `source:` to the chart block. |

Section tail warnings are resolved independently per section (each section starts on its own
page), so fix them one at a time and rebuild. Aim for every section's last page to be at least
~60% full.

### 7. Visual review

Open `build/<slug>/preview.png` (contact sheet of every page) and check: no near-empty pages,
charts legible, no overlapping labels, tables not cramped, visuals spread evenly. Open a few
individual chart PNGs in `build/<slug>/figures/` at full size if anything looks wrong. Fix by
changing chart data/labels (shorter category names, fewer series, `barh` for long labels).

### 8. Final checklist (all must be true)

- [ ] `./hh make <slug>` prints `PASS`; zero broken links
- [ ] 30–50 pages; 6–9 numbered sections; 8–14 figures; 4–8 tables; 25+ in-text links
- [ ] No section tail below ~45% without a reason
- [ ] Every statistic dated and linked; every estimate labelled "H Heuristics estimate"
- [ ] Every figure/table has a caption that states the insight, a source line, and is referenced in the text
- [ ] Executive Summary stands alone and leads with the answer
- [ ] `sample:` is absent or `false` in front matter (it adds an "illustrative data" badge)
- [ ] References section lists every source cited
- [ ] `research-notes.md` kept in the report folder for audit

### 9. Record and commit

Set the report's row in `queue/topics.csv` to `done` (if it came from the queue), then:

```bash
git add reports/<slug> output/<slug> queue/topics.csv
git commit -m "Report: <title>"
```

## Batch production

`queue/topics.csv` holds the backlog (`slug,title,brief,audience,report_type,status,notes`).
To work the queue: take the first row with `status=todo`, set it to `in-progress`, run the full
workflow above, set it to `done` (or `blocked` with a note), commit, then continue with the next
row. Finish one report completely before starting the next. `./hh queue` shows status;
`./hh batch --all` rebuilds and re-checks every report.

## Command reference

| Command | Purpose |
|---|---|
| `./hh new <slug> --title "…"` | scaffold a report from the template |
| `./hh lint <slug>` | parse and validate Markdown only (seconds) |
| `./hh build <slug>` | render PDF + DOCX |
| `./hh qa <slug>` | build + quality gate (no live link check) |
| `./hh make <slug>` | build + quality gate + live link check — **use this before declaring done** |
| `./hh batch --all [--check-links]` | build + QA every report; summary table |
| `./hh queue` | show the topic queue |
| options | `--pdf-only`, `--docx-only`, `--docx-preview` (LibreOffice render of the DOCX), `--no-preview`, `--strict` |

## Reference reports

- `reports/sample-decision-quality/` — a complete 32-page report that passes the gate with no
  warnings. Use it as the model for structure, density, tone, figure use and linking.
- `reports/_features/` — one of every element and chart type.
