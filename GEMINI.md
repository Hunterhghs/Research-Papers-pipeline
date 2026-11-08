# GEMINI.md

This repository produces H Heuristics research reports (30–50 page PDF + Word) from Markdown.

**Before doing anything, read [AGENTS.md](AGENTS.md)** — it is the full operating manual —
then [docs/AUTHORING_GUIDE.md](docs/AUTHORING_GUIDE.md) and [docs/STYLE_GUIDE.md](docs/STYLE_GUIDE.md).

Non-negotiables:

1. Never fabricate statistics, quotes, sources or URLs. Link every claim inline to a source you opened.
2. Write only in `reports/<slug>/` (and `queue/topics.csv`). Do not modify `hhreport/`, `brand/` or `docs/`.
3. A report is done only when `./hh make <slug>` prints `PASS`, it is 30–50 pages, and you have
   reviewed `build/<slug>/preview.png`.
4. Fix layout warnings by changing content (add/trim words, move figures) — never with manual breaks or HTML.

Workflows (Antigravity): `/new-report`, `/batch-reports`, `/fix-qa` — see `.agent/workflows/`.
