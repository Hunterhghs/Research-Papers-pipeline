---
trigger: always_on
---

# H Heuristics report standards (always on)

- This workspace produces research reports with `./hh` (see AGENTS.md). Read AGENTS.md,
  docs/AUTHORING_GUIDE.md and docs/STYLE_GUIDE.md before writing or editing any report.
- Never invent numbers, quotations, studies, authors or URLs. Every factual claim carries an
  inline Markdown link to a source you opened during this task. Prefer primary sources.
- Date every statistic; label H Heuristics estimates as such; chart `source:` lines are required.
- Only edit files under `reports/<slug>/` and `queue/topics.csv` unless the user asks otherwise.
- Never hand-edit `build/` or `output/`. Never add manual page breaks or HTML for layout.
- A report is finished only when `./hh make <slug>` reports PASS, page count is 30–50, there are
  no unresolved fill warnings, and you have looked at `build/<slug>/preview.png`.
- Write in the H Heuristics voice: answer first, analytical, plain English, calibrated
  uncertainty, no hype words.
