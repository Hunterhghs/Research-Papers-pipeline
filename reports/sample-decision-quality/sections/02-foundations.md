# The Science of Heuristics {#foundations}

## From perfect rationality to bounded rationality

For much of the twentieth century, economic models assumed that decision-makers were perfectly rational: they knew all relevant alternatives, could compute the consequences of each, and chose whichever maximized expected utility. Herbert Simon challenged this picture in a series of papers beginning with [*A Behavioral Model of Rational Choice*](https://doi.org/10.2307/1884852) in 1955. Real people, Simon argued, operate under limits of information, time and computational capacity. They do not optimize; they *satisfice*, searching until they find an option that is good enough and then stopping.

Simon's concept of [bounded rationality](https://en.wikipedia.org/wiki/Bounded_rationality) reframed the question. The interesting issue was no longer whether people are rational in some absolute sense, but which strategies allow a bounded mind to perform well in a given environment. Simon's own metaphor was a pair of scissors: one blade is the mind's cognitive limitations, the other is the structure of the environment, and behavior can only be understood by looking at how the two blades fit together.

This framing remains the most useful starting point for leaders. It implies that the right question about any decision rule, whether a rule of thumb, a scoring model or an AI system, is not "is it rational?" but "does it fit the environment in which we are using it?"

## Heuristics and biases

In the 1970s, Amos Tversky and Daniel Kahneman launched a research program that documented systematic departures from the predictions of rational choice theory. Their 1974 paper in *Science*, [*Judgment under Uncertainty: Heuristics and Biases*](https://doi.org/10.1126/science.185.4157.1124), described three general-purpose heuristics people use to estimate probabilities and quantities:

- **Representativeness.** Judging the probability that something belongs to a category by how much it resembles the category's stereotype, often while neglecting base rates.
- **Availability.** Judging frequency or probability by how easily examples come to mind, which inflates vivid, recent or emotionally salient events.
- **Anchoring and adjustment.** Starting from an initial value and adjusting insufficiently, even when the anchor is arbitrary.

Their 1979 [prospect theory](https://doi.org/10.2307/1914185) added a descriptive model of choice under risk: people evaluate outcomes as gains and losses relative to a reference point, weigh losses more heavily than equivalent gains, and overweight small probabilities. Together, these findings gave rise to a catalogue of [cognitive biases](https://en.wikipedia.org/wiki/List_of_cognitive_biases) that now runs to well over a hundred entries.

The heuristics-and-biases program has been enormously influential, and its core findings are robust. But its emphasis on errors can leave a misleading impression: that heuristics are defects to be engineered away. The biases were identified precisely by designing situations in which a normally useful heuristic would produce a wrong answer. Outside those situations, the same heuristics often work well.

## Ecological rationality: when simple rules win

A second research tradition, associated with Gerd Gigerenzer and colleagues, studies [ecological rationality](https://en.wikipedia.org/wiki/Ecological_rationality): the conditions under which simple heuristics perform well. Its central finding is counterintuitive. In environments with high uncertainty, limited data and many potential predictors, simple rules that ignore much of the available information frequently predict as well as, or better than, complex statistical models.

The reason is the [bias–variance trade-off](https://en.wikipedia.org/wiki/Bias%E2%80%93variance_tradeoff). A complex model fitted to limited data captures noise along with signal, so it performs well on past data and poorly on new cases. A simple rule has more bias but far less variance, and when data are scarce or the environment is shifting, lower variance wins. The "1/N" rule for allocating investments equally across options, for example, has been shown to be competitive with optimized portfolio models when estimation windows are short.

```chart
type: line
id: biasvariance
caption: "Simple rules hold up better out of sample when data are scarce"
source: "Illustrative simulation pattern for this pipeline sample, consistent with the bias–variance trade-off described in the forecasting literature."
categories: ["20", "50", "100", "200", "500", "1,000", "2,000", "5,000"]
x_label: "Training observations"
y_label: "Out-of-sample accuracy (%)"
suffix: "%"
zero_base: false
series:
  - name: Simple heuristic (tallying)
    values: [68, 70, 71, 72, 72, 73, 73, 73]
  - name: Complex model (many predictors)
    values: [58, 63, 67, 70, 74, 77, 79, 81]
```

@fig:biasvariance illustrates the typical pattern. With few observations, a tallying heuristic that counts favorable cues outperforms a model that estimates a weight for each cue. As data accumulate and the environment remains stable, the complex model eventually overtakes the heuristic. The crossover point is not fixed; it depends on how noisy and how stable the environment is. Leaders rarely know where it lies, which is itself an argument for robust, simple decision rules in novel or volatile situations.

## Reconciling the two traditions

The heuristics-and-biases and ecological-rationality schools are sometimes presented as rivals. For practical purposes they are better seen as complementary. The first tells us where intuitive judgment predictably fails; the second tells us where simple rules are a strength rather than a weakness. Taken together, they suggest a contingency view summarized in @fig:environments.

```chart
type: matrix
id: environments
caption: "Which decision approach fits which environment"
source: "H Heuristics framework drawing on Kahneman and Klein (2009) and the ecological rationality literature."
x_label: "Availability of reliable, relevant data  →"
y_label: "Environment stability and feedback quality  →"
quadrants:
  - title: "Trained intuition"
    text: "Stable, high-feedback settings with little codified data. Expert pattern recognition works if experts got rapid, accurate feedback while learning."
  - title: "Models and algorithms"
    text: "Stable settings with rich data. Statistical models typically match or beat expert judgment; humans should audit, not override by default."
  - title: "Robust heuristics"
    text: "Volatile settings with scarce data. Simple, transparent rules and diversified bets outperform optimized but fragile models."
  - title: "Structured judgment"
    text: "Volatile settings with abundant but noisy data. Use models as one input, aggregate independent views and update often."
```

The quadrant that deserves most attention is the upper-left. Kahneman and the naturalistic decision researcher Gary Klein, often seen as representing opposed camps, co-authored an influential paper, [*Conditions for Intuitive Expertise: A Failure to Disagree*](https://doi.org/10.1037/a0016755), concluding that intuition can be trusted when two conditions hold: the environment is regular enough to be predictable, and the expert has had extensive practice with rapid, unambiguous feedback. Firefighters, chess players and anaesthetists often meet these conditions. Stock pickers, political pundits and many corporate strategists do not.

## Implications for organizations

Three implications follow from this body of research.

First, **match the decision method to the environment**. Organizations often apply the same decision process to everything, from routine pricing to once-a-decade strategic bets. The research suggests that routine, data-rich decisions are prime candidates for models and decision rules, while novel and volatile decisions benefit from structured human judgment supported by simple, robust heuristics.

Second, **be sceptical of intuitive confidence**. Subjective confidence is a poor guide to accuracy, especially in environments without fast feedback. A senior executive's strong conviction about a market entry carries information, but much less than the conviction suggests. Asking "how would we know if we were wrong?" is a practical antidote.

Third, **design for the bias, not against the person**. Because biases arise from general-purpose cognitive mechanisms, they affect experts and novices alike, and they are largely invisible from the inside. Training people to "be less biased" has a weak track record. Changing the decision process, for instance by requiring independent estimates before discussion, has a much stronger one. The next section examines where these process failures most commonly appear.
