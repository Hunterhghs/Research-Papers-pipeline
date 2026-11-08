---
description: Research, write, build and quality-check one H Heuristics report end to end
---

1. Read `AGENTS.md`, `docs/AUTHORING_GUIDE.md`, `docs/STYLE_GUIDE.md`, and skim
   `reports/sample-decision-quality/` as the model of a finished report.
2. Agree the topic, slug, audience and angle with the user (or take them from the
   `queue/topics.csv` row you are working on). Set that row's status to `in-progress`.
// turbo
3. Scaffold: `./hh new <slug> --title "<title>"`
4. Research: search the web and open 30–50 sources, mostly primary. Record title, publisher,
   date, URL and the exact facts you will use in `reports/<slug>/research-notes.md`.
5. Outline: retitle `reports/<slug>/sections/*.md` into 6–9 sections with ids and 3–5
   subsections each; plan 8–14 figures and 4–8 tables and the data each needs.
6. Write the front matter and Executive Summary in `report.md`, then each section file in turn
   (1,100–1,500 words each), linking every claim inline. After each file run the next step.
// turbo
7. Lint: `./hh lint <slug>` — fix any errors before continuing.
// turbo
8. Build and gate: `./hh make <slug>`
9. Apply every "How to fix" item QA prints (page count, section tail fill, gaps, broken links,
   missing sources). Re-run step 8 after each round. Repeat until PASS with no fill warnings.
10. Open `build/<slug>/preview.png` and inspect every page; fix crowded charts, near-empty pages
    or clustered visuals, then re-run step 8.
11. Walk the final checklist in AGENTS.md section 8.
12. Set the queue row to `done`, then commit: `git add reports/<slug> output/<slug> queue/topics.csv && git commit -m "Report: <title>"`.
13. Report back with the page count, figure/table/link counts, and the paths to the PDF and DOCX.
