# Measuring Decision Quality {#measurement}

## Why measurement is hard and why it matters

Measuring decision quality is difficult for the same reason improving it is valuable: outcomes are noisy, delayed and confounded. A single decision cannot be graded by its result. But a portfolio of decisions can be assessed, and the process behind each decision can be evaluated at the time it is made. Organizations that build both kinds of measurement gain a feedback loop that most lack, and with it the ability to learn faster than competitors.

Measurement also changes behavior. When forecasts are written down and scored, people become more careful about the probabilities they state. When decision records are reviewed, teams take more care in writing them. The act of measuring is itself one of the most effective interventions available, a version of the [Hawthorne effect](https://en.wikipedia.org/wiki/Hawthorne_effect) that leaders should welcome rather than discount.

## A balanced scorecard for decisions

We recommend tracking four families of indicators. Process indicators are leading, available immediately and under the organization's control. Accuracy indicators accumulate over months as forecasts resolve. Outcome indicators lag further still. Learning indicators show whether the feedback loop is actually operating.

Table: Indicators for a decision-quality scorecard {#scorecard}

| Family | Indicator | How it is measured | Typical cadence |
|:--|:--|:--|:--|
| Process | Protocol adherence | Share of tier-one decisions with complete records | Monthly |
| Process | Alternatives considered | Average number of genuine options per decision | Monthly |
| Process | Independence | Share of decisions with private estimates before discussion | Monthly |
| Accuracy | Brier score | Mean squared error of resolved probability forecasts | Quarterly |
| Accuracy | Calibration gap | Difference between stated and observed frequencies | Quarterly |
| Accuracy | Range hit rate | Share of outcomes falling within stated 80% ranges | Quarterly |
| Outcome | Value versus plan | Realized versus forecast value for major decisions | Annually |
| Outcome | Reversal rate | Share of decisions reversed within 12 months | Annually |
| Learning | Review completion | Share of decisions reviewed on schedule | Quarterly |
| Learning | Lessons applied | Changes to templates or base rates from reviews | Semi-annually |

Source: H Heuristics framework.

The scorecard should be used diagnostically, not punitively. A high reversal rate, for example, may indicate poor initial decisions, or it may indicate a healthy willingness to change course when evidence shifts. A rising Brier score may reflect worse judgment, or a deliberate move into harder questions. The indicators are prompts for conversation rather than targets to be hit, and they lose their value quickly if people are rewarded for gaming them, as [Goodhart's law](https://en.wikipedia.org/wiki/Goodhart%27s_law) warns.

## Scoring forecasts in practice

The accuracy indicators depend on forecasts being stated in a scorable form. That requires three things: a clear question with an unambiguous resolution criterion, a probability or range, and a resolution date. "The launch will go well" cannot be scored. "There is a 65 percent chance that the product reaches 10,000 paying users by 30 June" can.

Once forecasts are recorded, scoring is straightforward. Each resolved forecast receives a Brier score; scores are averaged by forecaster, team and decision type; and calibration curves are plotted once enough forecasts have accumulated, typically after fifty to a hundred. AI tools can automate much of this bookkeeping, including reminding forecast owners when resolution dates arrive and drafting a review of what was learned.

```chart
type: area
id: improvement
caption: "Forecast accuracy over the first eight quarters of a decision-quality program"
source: "Illustrative trajectory for this pipeline sample; real programs vary widely in starting point and pace."
categories: ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8"]
y_label: "Range hit rate for 80% intervals"
suffix: "%"
zero_base: true
series:
  - name: Range hit rate
    values: [48, 54, 59, 64, 68, 71, 74, 76]
annotations:
  - {x: "Q3", y: 59, text: "Calibration training introduced", dx: 12, dy: 26}
  - {x: "Q6", y: 71, text: "AI-assisted base rates added", dx: -60, dy: 26}
```

@fig:improvement shows a pattern that programs commonly report. Initially, stated 80 percent ranges capture the outcome only about half the time, a clear sign of overprecision. Simple feedback, followed by calibration training and better access to base rates, steadily widens ranges where needed and narrows them where justified. The goal is not to reach exactly 80 percent but to approach it while keeping ranges informative.

## Reviewing decisions

Decision reviews are the mechanism that converts measurement into learning. Effective reviews share several features. They are scheduled in advance, at the date recorded in the decision record, rather than triggered by a bad outcome. They examine the process separately from the outcome, asking whether the decision was reasonable given what was known at the time. And they focus on lessons that can be applied to future decisions, such as updating a base rate, improving a template or recognizing a recurring blind spot.

```chart
type: stacked_barh
id: reviews
caption: "Classification of reviewed decisions by process and outcome quality"
source: "Illustrative distribution for this pipeline sample. The off-diagonal categories are where learning is concentrated."
categories: ["Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"]
x_label: "Number of decisions reviewed"
series:
  - name: Good process, good outcome
    values: [9, 11, 14, 16]
  - name: Good process, bad outcome
    values: [4, 5, 6, 6]
  - name: Poor process, good outcome
    values: [7, 6, 4, 3]
  - name: Poor process, bad outcome
    values: [6, 5, 3, 2]
```

A useful classification, shown in @fig:reviews, crosses process quality with outcome quality. Decisions with good process and bad outcomes, sometimes called "bad breaks", should not be punished; they are the price of taking sensible risks. Decisions with poor process and good outcomes, "dumb luck", are the most dangerous, because they reinforce habits that will eventually fail. A review culture that can distinguish these two categories has grasped the essential idea of decision quality.

## Benchmarks and maturity

Organizations at different stages need different measures. @tbl:maturity outlines a simple maturity model that can be used to set realistic goals and to communicate progress to boards and executive teams.

Table: Decision-quality maturity model {#maturity}

| Level | Description | Typical evidence |
|:--|:--|:--|
| 1. Ad hoc | Decisions made informally; outcomes drive evaluation | No written records; post-mortems only after failures |
| 2. Documented | Major decisions recorded; rationale captured | Decision records for most tier-one decisions |
| 3. Quantified | Key forecasts stated as probabilities and scored | Brier scores and calibration curves by team |
| 4. Learning | Reviews scheduled; lessons feed into templates and base rates | Updated reference classes; trend in accuracy |
| 5. Adaptive | Human and AI judgment combined and benchmarked continuously | Comparative accuracy of human, AI and blended forecasts |

Source: H Heuristics framework.

Most organizations we encounter operate at level one or two. Reaching level three is the most important step, because it creates the objective record of accuracy on which everything else depends. It is also the step at which the comparison between human and AI judgment becomes possible on fair terms, using the same questions, the same scoring rules and the same resolution criteria for both.
