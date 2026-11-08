# Why Decision Quality Matters Now {#introduction}

## Decisions as the unit of performance

Every strategy, budget and operating plan is the visible residue of a sequence of decisions. Some are large and deliberate: entering a market, acquiring a company, committing capital to a multi-year program. Most are small and frequent: approving a hire, setting a price, escalating an incident, choosing which customer complaint to act on first. The cumulative effect of these choices determines whether an organization compounds its advantages or slowly erodes them. Yet most management systems measure activity and outcomes, not the quality of the decisions that connect the two.

This gap matters because outcomes are a noisy signal. A forecast of 70 percent that a project will finish on time is not wrong when the project slips; it implies that roughly three in ten such projects should slip. Judging the forecaster by the single outcome punishes good calibration and rewards lucky overconfidence. The psychologist and poker champion Annie Duke calls this tendency "resulting"; the statistician would call it ignoring the base rate. Either way, organizations that learn only from outcomes learn slowly, and often learn the wrong lessons.

Decision quality, by contrast, can be assessed at the moment of choice. Did the team frame the problem correctly and consider genuine alternatives? Did it gather the information that was reasonably available, and weigh it without obvious bias? Did it state its uncertainty honestly, and did it commit to a course of action with a clear view of what would cause it to change course? These questions have defensible answers before the outcome is known, which is precisely what makes them useful.

## Three forces raising the stakes

Three developments make the quality of organizational judgment more consequential today than a decade ago.

The first is **speed**. Product cycles, capital markets and competitive responses move faster, which compresses the time available for deliberation. Compressed time does not merely reduce the hours spent analysing a choice; it changes which cognitive processes dominate. Under time pressure, people rely more heavily on fast, intuitive judgment, the mode Daniel Kahneman labelled [System 1](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow), and less on slow, effortful reasoning. That is not inherently bad, but it raises the premium on having good intuitions and on knowing when they cannot be trusted.

The second is **information abundance**. Leaders now face more dashboards, reports and alerts than they can reasonably process. More information does not automatically improve decisions; beyond a point, it increases confidence faster than it increases accuracy. Classic experiments with horse-race handicappers and clinical psychologists found that adding information raised judges' confidence while leaving their accuracy almost unchanged. The constraint on modern decision-making is rarely access to data. It is attention, and the discipline to separate signal from noise.

The third is **machine assistance**. Generative AI and predictive models are now embedded in the tools where analysis happens: spreadsheets, documents, customer systems and code. These systems produce fluent, confident output at almost no marginal cost. They can be excellent at summarizing evidence, generating options and estimating probabilities from historical data. They can also be wrong in ways that are hard to detect, and their fluency can make weak reasoning look rigorous. Whether AI improves decisions depends on how it is placed within the decision process, a theme we return to in @sec:ai.

```chart
type: line
id: pressure
caption: "Decision volume and available time are moving in opposite directions"
source: "Illustrative index (2016 = 100) constructed for this pipeline sample; not survey data."
categories: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
y_label: "Index, 2016 = 100"
series:
  - name: Decisions requiring senior sign-off
    values: [100, 104, 109, 113, 121, 128, 134, 141, 149, 158, 166]
  - name: Information inputs per decision
    values: [100, 108, 117, 126, 138, 151, 163, 178, 196, 214, 233]
  - name: Time available per decision
    values: [100, 98, 95, 93, 88, 85, 83, 80, 77, 74, 72]
```

## What we mean by decision quality

We use the term *decision quality* to mean the degree to which a decision process is likely to produce good outcomes across many similar decisions. This definition has three consequences. It is probabilistic, so a single bad outcome does not prove a poor decision. It is process-oriented, so it can be evaluated before results arrive. And it is comparative, so the relevant question is whether one process beats another over time, not whether any process guarantees success.

Practitioners in the [decision analysis](https://en.wikipedia.org/wiki/Decision_analysis) tradition often break decision quality into six elements, sometimes drawn as a chain whose overall strength is set by its weakest link. We adopt a slightly simplified version, summarized in @tbl:elements, because it maps cleanly onto practices organizations can adopt.

Table: The six elements of decision quality {#elements}

| Element | Guiding question | Common failure |
|:--|:--|:--|
| Frame | Are we solving the right problem, at the right scope? | Narrow framing; treating a symptom as the problem |
| Alternatives | Have we considered genuinely different options? | "Whether or not" choices with a single option |
| Information | Do we have the relevant facts and their uncertainty? | Confirmatory search; ignoring base rates |
| Values and trade-offs | Are we clear on what we want and what we will give up? | Unstated objectives; conflicting goals hidden |
| Reasoning | Is the logic connecting information to choice sound? | Overconfidence; anchoring on a first estimate |
| Commitment | Will we act, and do we know what would change our mind? | Analysis paralysis or escalation of commitment |

Source: H Heuristics synthesis adapted from the decision analysis literature; see [Decision quality](https://en.wikipedia.org/wiki/Decision_quality) for an overview.

A useful property of this framework is that each element can be strengthened by a specific, low-cost practice. Framing improves when teams write a one-paragraph problem statement and have it challenged. Alternatives improve when a rule requires at least three options, including the status quo. Information improves when estimates are anchored on base rates from comparable cases. The rest of this report examines the evidence behind these practices and how they interact with AI tools.

## Scope and approach

This report synthesizes research from cognitive psychology, behavioral economics, forecasting science, human factors engineering and the emerging literature on human–AI collaboration. We focus on decisions made by professionals inside organizations, rather than consumer choices, and on decisions where uncertainty is material and outcomes are delayed. We draw on peer-reviewed studies, well-documented field experiments and authoritative frameworks such as the [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework).

Because this document is a sample produced to demonstrate H Heuristics' publication pipeline, the quantitative series shown in charts and some tables are illustrative. They are designed to show the shape of the relationships discussed in the literature and are labelled as such in every source note. The qualitative findings and the studies cited are real, and each is linked so that readers can consult the original work.

Readers in a hurry may wish to begin with @sec:operating-model, which translates the evidence into an operating model, and @sec:measurement, which sets out how to track progress. Readers interested in why the recommended practices work should read the sections in order, since each builds on the evidence presented before it.
