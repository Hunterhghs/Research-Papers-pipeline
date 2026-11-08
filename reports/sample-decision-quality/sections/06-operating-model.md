# A Decision-Quality Operating Model {#operating-model}

## Design principles

The evidence reviewed so far points to a small number of design principles for organizations that want to improve decision quality in an era of machine assistance. The operating model in this section is built on five of them.

1. **Tier decisions by consequence and reversibility.** Not every decision deserves the same process. Effort should concentrate on decisions that are both consequential and hard to reverse.
2. **Separate the process from the outcome.** Evaluate decisions on the quality of the process at the time they were made, and review outcomes separately to learn about the environment.
3. **Independence before discussion.** Collect individual judgments, human and machine, before any group deliberation, to preserve the diversity of information.
4. **Make uncertainty explicit.** State key forecasts as probabilities or ranges, and write them down where they can be scored later.
5. **Close the loop.** Build a routine in which past decisions are reviewed, forecasts are scored and lessons are fed back into the process.

None of these principles is novel on its own. What distinguishes high-performing organizations is that they apply them consistently, with lightweight tools, and without making the process so burdensome that people route around it.

## Tiering decisions

The first step is to decide which decisions warrant a structured process at all. A useful heuristic, popularized by Amazon's distinction between "one-way" and "two-way" doors, is to classify decisions by how consequential and how reversible they are. @fig:tiers maps the four resulting categories to an appropriate level of process.

```chart
type: matrix
id: tiers
caption: "Decision tiers by consequence and reversibility"
source: "H Heuristics framework."
x_label: "Consequence of getting it wrong  →"
y_label: "Ease of reversal  →"
quadrants:
  - title: "Delegate and move fast"
    text: "Low stakes, easily reversed. Push to the front line; use simple rules or automate; review only in aggregate."
  - title: "Experiment"
    text: "High stakes but reversible. Run pilots, set clear stop criteria and decide with data from small, fast tests."
  - title: "Standardize"
    text: "Low stakes but sticky. Use checklists and templates so the decision is made well by default."
  - title: "Full decision process"
    text: "High stakes and hard to reverse. Apply the complete protocol: frame, outside view, independent estimates, pre-mortem, decision record."
```

In practice, fewer than one in twenty decisions in a typical organization will fall into the full-process quadrant. Those decisions, however, account for a disproportionate share of value created or destroyed. The tiering exercise also clarifies where AI can be given more autonomy: low-stakes, reversible decisions in data-rich environments are natural candidates for automation, provided outcomes are monitored in aggregate.

## The core protocol

For decisions in the full-process tier, we recommend a protocol of six steps. Each step is supported by a specific practice with a research basis, and each produces a short written artefact. The complete set fits comfortably into a decision record of one to three pages.

```chart
type: process
id: protocol
caption: "The H Heuristics decision protocol for high-stakes decisions"
source: "H Heuristics framework; practices drawn from the literature cited in @sec:failures and @sec:forecasting."
steps:
  - title: Frame
    text: "One-paragraph problem statement, challenged by someone outside the team."
  - title: Options
    text: "At least three genuine alternatives, including the status quo."
  - title: Outside view
    text: "Base rates from a reference class before any inside-view analysis."
  - title: Independent
    text: "Private estimates from each participant and the AI model."
  - title: Pre-mortem
    text: "Assume failure in two years; list the most likely causes."
  - title: Record
    text: "Decision, probabilities, kill criteria and review date written down."
```

**Frame.** The problem statement should name the decision, the objective, the time horizon and the constraints. Having it challenged by someone outside the team surfaces hidden assumptions early, when they are cheap to change.

**Options.** Requiring at least three options, one of which is the status quo, breaks the "whether or not" framing that research on organizational decisions has found to be common and costly.

**Outside view.** Before building a bespoke business case, the team identifies a reference class and its distribution of outcomes. This is where AI assistance is often most valuable, retrieving comparable cases quickly, provided the cases are verified.

**Independent estimates.** Each participant, and the AI model if one is used, submits key estimates privately. Divergence between estimates is treated as information to be explored rather than noise to be averaged away. Treating the model as one independent voice among several preserves its value while limiting automation bias.

**Pre-mortem.** The team imagines that the decision has failed and writes down the most plausible reasons. Gary Klein's [pre-mortem technique](https://hbr.org/2007/09/performing-a-project-premortem) legitimizes dissent and has been found to increase the identification of risks compared with conventional risk reviews.

**Record.** The decision record captures the choice, the key forecasts with probabilities, the conditions that would trigger a review, and a scheduled date to revisit the decision. Without this artefact, later learning is impossible.

## Roles for AI within the protocol

The protocol makes it possible to be precise about where AI fits. @tbl:airoles sets out recommended roles for each step, together with the guardrails that limit the failure modes discussed in @sec:ai.

Table: Recommended roles and guardrails for AI in the decision protocol {#airoles}

| Step | Recommended AI role | Guardrail |
|:--|:--|:--|
| Frame | Critic: identify ambiguities and alternative framings | Human owns the final problem statement |
| Options | Generator: propose additional alternatives | Team must evaluate at least one AI-proposed option seriously |
| Outside view | Researcher: retrieve reference cases and base rates | Every cited source is verified and linked |
| Independent estimates | Independent forecaster | Model estimate revealed only after human estimates are locked |
| Pre-mortem | Red team: generate failure scenarios | Team ranks scenarios; model does not |
| Record | Scribe: draft the decision record | Decision owner edits and signs the record |

Source: H Heuristics framework.

Two guardrails deserve emphasis. The first is sequencing: revealing the model's estimate only after humans have committed to their own preserves independence and avoids anchoring. The second is verification: every factual claim and citation that enters a decision record from an AI tool should be checked against its source. This is tedious but essential; fabricated or misattributed sources are among the most common and damaging AI errors in professional settings.

## Making it stick

Process improvements fail most often not because they are wrong but because they are abandoned. Three design choices increase the odds that a decision-quality program survives contact with day-to-day pressures.

::: callout Three conditions for adoption
**Keep it light.** A decision record that takes more than an hour to write will not be written. Templates, AI-assisted drafting and a strict page limit help.

**Make leaders go first.** When senior leaders publish their own decision records, including forecasts that turned out wrong, the practice becomes a norm rather than a compliance exercise.

**Reward process, not luck.** Performance conversations should include the quality of decisions, assessed on the record, alongside results. Otherwise people will rationally optimize for outcomes they can attribute to themselves.
:::
