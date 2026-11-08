# Where Organizational Decisions Fail {#failures}

## Individual biases, organizational consequences

The biases documented in laboratory studies do not disappear when people enter an office. They are amplified or dampened by the structures around them: hierarchy, incentives, meeting norms and the way information flows. Some organizational practices correct individual biases; others compound them. Understanding the difference is the starting point for improvement.

In our review of the literature and of published post-mortems, five failure patterns account for a large share of costly organizational decisions. They are summarized in @tbl:failures and discussed in turn below. None is exotic. Each is familiar to anyone who has sat through a budget review or a project steering committee, which is part of what makes them so persistent.

Table: Five recurrent failure patterns in organizational decisions {#failures}

| Pattern | Mechanism | Typical setting | Process remedy |
|:--|:--|:--|:--|
| Planning fallacy | Inside view; neglect of base rates | Capital projects, product launches | Reference-class forecasting |
| Overconfidence | Narrow intervals; illusion of control | Forecasts, M&A synergies | Calibrated ranges; tracking |
| Groupthink and cascades | Social conformity; early anchors | Executive meetings, committees | Independent estimates first |
| Escalation of commitment | Sunk costs; reputational stakes | Failing programs, R&D bets | Pre-set kill criteria |
| Noise | Unwanted variability between judges | Underwriting, hiring, appraisal | Structured scales; aggregation |

Source: H Heuristics synthesis of the judgment and decision-making literature.

## The planning fallacy and the inside view

The [planning fallacy](https://en.wikipedia.org/wiki/Planning_fallacy), first described by Kahneman and Tversky, is the tendency to underestimate the time, cost and risk of future actions while overestimating their benefits. It persists even when people know that similar past projects ran late. The cause is the *inside view*: planners focus on the specifics of their own project, construct a plausible scenario for how it will unfold, and fail to consider the distribution of outcomes for comparable projects.

The evidence from large projects is striking. Research by Bent Flyvbjerg and colleagues on infrastructure and IT megaprojects, summarized in [*What You Should Know About Megaprojects and Why*](https://doi.org/10.1002/pmj.21409), finds that cost overruns and benefit shortfalls are the norm rather than the exception, and that the pattern has been stable for decades. Flyvbjerg describes this as an "iron law": over budget, over time, under benefits, over and over again.

```chart
type: barh
id: overruns
caption: "Average cost overrun by project type"
source: "Illustrative values for this pipeline sample, reflecting the direction and rough ordering reported in the megaproject literature; consult [Flyvbjerg (2014)](https://doi.org/10.1002/pmj.21409) for measured estimates."
categories: ["IT and digital transformation", "Defense programs", "Rail", "Bridges and tunnels", "Buildings", "Roads"]
suffix: "%"
x_label: "Average cost overrun versus approved budget"
highlight: ["IT and digital transformation"]
values: [107, 89, 39, 34, 32, 20]
```

The remedy with the strongest evidence base is [reference-class forecasting](https://en.wikipedia.org/wiki/Reference_class_forecasting): identify a class of comparable past projects, establish the distribution of their outcomes, and position the current project within that distribution, adjusting only for specific, demonstrable differences. The method forces the outside view onto the table before the inside view has hardened. Several governments now require it for large public investments.

## Overconfidence and the illusion of control

Overconfidence takes several forms. *Overestimation* is believing one's performance is better than it is. *Overplacement* is believing one is better than others. *Overprecision*, the most consequential for forecasting, is excessive certainty about the accuracy of one's beliefs. When asked to give 90 percent confidence intervals for uncertain quantities, people typically produce ranges that contain the true value only about half the time.

In organizations, overprecision shows up as single-point forecasts presented without ranges, synergy estimates that are treated as facts once approved, and scenario plans that span a narrower band of futures than history would suggest. The [overconfidence effect](https://en.wikipedia.org/wiki/Overconfidence_effect) is reinforced by social norms that reward decisive, confident communication and penalize expressed doubt.

::: callout Practice: the calibrated range
Replace every single-number forecast in a decision paper with a range and a confidence level, for example "revenue of $40–55 million (80% confidence)". Record the range. When the outcome is known, check whether it fell inside. After twenty or thirty such forecasts, each forecaster has a personal hit rate. People whose 80% ranges capture the truth only half the time learn quickly to widen them, and the organization learns whose forecasts deserve weight.
:::

## Groupthink, cascades and the loudest voice

Group discussion can aggregate dispersed knowledge, but it often does the opposite. Irving Janis coined the term [groupthink](https://en.wikipedia.org/wiki/Groupthink) to describe cohesive groups that suppress dissent in pursuit of consensus. A subtler mechanism is the *information cascade*: early speakers anchor the discussion, later speakers defer, and the group converges on a view that reflects the first opinions expressed rather than the information everyone holds.

The practical antidote is to collect independent judgments *before* discussion. When each participant writes down an estimate or a recommendation privately, and those views are revealed simultaneously, the group retains the diversity of its information. This is the mechanism behind the [wisdom of crowds](https://en.wikipedia.org/wiki/Wisdom_of_the_crowd): averaging independent estimates cancels individual errors, but only if the errors are not correlated by prior discussion.

## Escalation of commitment

Once a course of action is chosen, people and organizations tend to keep investing in it even as evidence mounts that it is failing. [Escalation of commitment](https://en.wikipedia.org/wiki/Escalation_of_commitment) is driven by the [sunk cost fallacy](https://en.wikipedia.org/wiki/Sunk_cost), by reputational stakes for the sponsors, and by the simple difficulty of admitting error in public. The cost is not only the additional money spent; it is the opportunity cost of resources and attention that could have gone elsewhere.

The most effective defence is to agree, at the moment of commitment, on the conditions that would trigger a review or termination. Pre-set *kill criteria* convert a future emotional decision into a present analytical one. They work best when combined with a separation of roles, so that the people who championed an initiative are not the only ones assessing whether it should continue.

## Noise: the overlooked error

Bias is a systematic deviation in one direction. [Noise](https://en.wikipedia.org/wiki/Noise:_A_Flaw_in_Human_Judgment), as Kahneman, Olivier Sibony and Cass Sunstein argue in their 2021 book, is unwanted variability: different judges reaching different conclusions on the same case, or the same judge reaching different conclusions on different days. Noise audits in insurance underwriting, criminal sentencing and medical diagnosis have found variability far larger than the organizations involved expected.

```chart
type: bar
id: noise
caption: "Expected versus observed variability in professional judgments"
source: "Illustrative pattern for this pipeline sample, modelled on the noise audits described by Kahneman, Sibony and Sunstein (2021)."
categories: ["Insurance premiums", "Claims reserves", "Loan approvals", "Performance ratings"]
suffix: "%"
y_label: "Median difference between two professionals"
series:
  - name: Executives' expectation
    values: [10, 10, 8, 12]
  - name: Observed in audit
    values: [55, 43, 31, 38]
```

Noise is easier to reduce than bias, because reducing it does not require knowing the right answer. Structured judgment scales, checklists, independent assessments and simple averaging all reduce noise. So, notably, do algorithms, which return the same output for the same input. This is one of the clearest benefits of machine assistance, and one reason the next sections focus on how human and machine judgment can be combined without introducing new failure modes.

## How failures compound

The five patterns rarely occur alone. A typical sequence begins with an inside-view plan that understates cost and time. Overconfidence narrows the range of outcomes considered, so the plan contains no contingency for the most likely problems. In the approval meeting, the sponsor speaks first, and a cascade forms around the sponsor's optimistic estimate. When early warning signs appear, the reputational cost of admitting error has grown, and escalation of commitment sets in. Meanwhile, noise in how different reviewers assess progress makes it hard to tell whether the project is genuinely off track or simply being judged by a harsher reviewer this quarter.

Each step in this sequence is individually understandable. Together they produce the familiar pattern of large initiatives that run late, over budget and short of their promised benefits, with warning signs visible in hindsight but discounted at the time. Because the failures reinforce one another, interventions that address only one of them tend to disappoint. Reference-class forecasting improves the initial estimate, but its benefit is lost if a cascade in the approval meeting overrides it. Kill criteria help, but only if the estimates they are compared against were honest in the first place.

This is why the most effective programs bundle several practices into a single, lightweight protocol rather than introducing them one at a time. A decision record that requires an outside-view estimate, independent forecasts, a pre-mortem and pre-set review triggers addresses all five patterns at once, at a cost of a few hours per major decision. We describe such a protocol in @sec:operating-model. Before doing so, we turn to the evidence from forecasting research, which shows most clearly that judgment can be trained and measured.

## Summary

The failure patterns in this section share a common feature: they are predictable. Planning fallacies, overconfidence, cascades, escalation and noise are not random misfortunes; they arise from known mechanisms in known settings. That predictability is the basis for intervention. The practices that address them, from reference-class forecasting to independent estimates and pre-set kill criteria, are cheap relative to the cost of the errors they prevent. The question for leaders is less what to do than how to make these practices routine, a question we address in @sec:operating-model.
