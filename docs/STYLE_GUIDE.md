# H Heuristics House Style

The standard every report must meet before it is published.

## Voice

- **Lead with the answer.** Every section opens with its conclusion, then the evidence.
- **Analytical, not promotional.** No hype words (*revolutionary, game-changing, unprecedented,
  cutting-edge, seamless, robust ecosystem*). No marketing superlatives.
- **Plain English.** Short sentences, active voice, concrete nouns. Define jargon on first use.
- **First person plural** for H Heuristics' own analysis ("we estimate", "our analysis").
- **Calibrated.** Distinguish what the evidence shows, what we infer, and what is uncertain.
  Use probabilities or ranges for forecasts ("60–70% likely", "USD 40–55bn").
- US English spelling unless the brief says otherwise.

## Structure

| Part | Length | Must contain |
|---|---|---|
| Abstract | 120–180 words | question, why now, evidence base, headline conclusion |
| Executive Summary | 700–1,000 words | answer first, `keyfindings` box (4–6 items), `stats` row, implications, recommendations |
| Each numbered section | 1,100–1,500 words | 3–5 subsections, 1–2 figures or tables, inline source links |
| References | all sources | numbered, full citations with working links |
| Whole report | 9,000–13,000 words | 6–9 numbered sections, 8–14 figures, 4–8 tables, 25+ links |

Paragraphs: 60–150 words. No single-sentence paragraphs except for emphasis, at most once per
section. Bullet lists: 3–7 items, parallel grammar, no list longer than the text around it.

## Evidence and sourcing (non-negotiable)

1. **Every factual claim, statistic and quotation is linked inline** to the most primary
   source available (statistical agency, regulator, company filing, peer-reviewed paper,
   official dataset) — not to a news article that cites it, where the original is reachable.
2. **Never invent a number, quote, study, author or URL.** If a figure cannot be found, say so
   or remove the claim. A shorter true report beats a longer invented one.
3. **Verify every URL** by opening it. `./hh make` checks all links live and verifies DOIs
   against the DOI registry; a broken link fails QA.
4. **Label estimates.** Numbers produced by H Heuristics analysis are marked
   "H Heuristics estimate" with the method summarised in the text or a note.
5. **Date your data.** State the year or period for every statistic ("in 2025", "as of Q2 2026").
6. **Prefer recent sources** (last 3 years) unless the point is historical.
7. Chart data must come from a cited source or be explicitly labelled as estimates/illustrative
   in the `source:` line.

## Numbers

- Numerals for 10 and above; words for one to nine except with units (5%, 3 km, $2m).
- Currency: `$4.2bn`, `$350m`, `€1.1tn`; state the currency if not USD.
- Percentages: `42%` in text and charts; "percentage points" (pp) for differences of rates.
- Ranges with an en dash: `2020–2025`, `40–55%`.
- Round sensibly: two or three significant figures in prose.

## Figures and tables

- Captions state the **insight** ("Adoption doubled in two years"), not the topic ("Adoption").
- Every figure and table has a source line.
- Refer to each figure/table in the text with `@fig:id` / `@tbl:id` before or near it.
- Spread visuals out: at least two or three paragraphs between consecutive figures.
- Choose the chart for the job: lines for time, bars for comparison, `barh` for rankings,
  stacked bars for composition, dumbbell for change between two points, waterfall for bridges.
  Donuts only for a single share-of-whole with ≤5 parts.

## Headings

- Sentence case ("Where organizational decisions fail"), no trailing punctuation.
- Section titles 2–7 words; subsection titles may state the finding.

## Recommendations

Numbered, specific, assigned to an audience, and actionable within a stated time frame.
"Establish a decision log for all investments above $5m by Q3" — not "consider improving
governance".
