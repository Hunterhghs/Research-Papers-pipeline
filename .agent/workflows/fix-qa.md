---
description: Bring an existing report to a clean QA pass
---

// turbo
1. Run `./hh make <slug>` and read every ERROR, warning and "How to fix" line.
2. Fix errors first (page count, missing sections/figures/tables/links, broken links), editing only
   files in `reports/<slug>/`. Replace broken links by finding the real document; never guess.
3. Fix section-tail warnings one section at a time: add the suggested words (real analysis, a
   table or a figure) or trim the suggested words so the section ends a page earlier.
4. Fix mid-section gaps by spacing visuals apart or setting `placement: top` on one figure.
// turbo
5. Re-run `./hh make <slug>`; repeat steps 2–4 until PASS with no fill warnings.
6. Open `build/<slug>/preview.png` and confirm every page looks full and the visuals are legible.
