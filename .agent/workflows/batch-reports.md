---
description: Work through queue/topics.csv, producing one finished report per todo row
---

// turbo
1. Show the queue: `./hh queue`
2. Take the first row with `status=todo`. If there is none, stop and report.
3. Run the full `/new-report` workflow for that row, using its `slug`, `title`, `brief`,
   `audience` and `report_type`. Finish it completely (QA PASS, preview reviewed, committed)
   before touching the next row.
4. If the report cannot meet the standard (for example not enough verifiable sources), set the
   row to `blocked`, explain why in `notes`, commit, and move on.
5. Repeat from step 2 until the requested number of reports is done or the queue is empty.
// turbo
6. Re-verify everything: `./hh batch --all --check-links`
7. Summarize: reports completed, pages and link counts per report, anything blocked.
