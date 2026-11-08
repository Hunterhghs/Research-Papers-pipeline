# Lessons from Forecasting Science {#forecasting}

## Why forecasting is the right test bed

Most decisions embed a forecast. Approving a product launch implies a forecast of demand; hiring a candidate implies a forecast of performance; delaying an investment implies a forecast that conditions will improve. Yet in most organizations these forecasts remain implicit, unquantified and unscored. Forecasting research is valuable precisely because it makes the implicit explicit: it asks people to state probabilities for well-defined events, waits for the events to resolve, and scores the results. This turns judgment into something that can be measured and improved.

The modern science of forecasting owes much to Philip Tetlock. His long-running study of expert political judgment, published in 2005, asked hundreds of experts to make thousands of predictions about political and economic events. The headline finding was sobering: on many long-range questions, experts performed only slightly better than simple extrapolation rules, and the most famous experts were often the least accurate. But the study also found meaningful differences between forecasters. Those who drew on many perspectives, held their views tentatively and updated readily, whom Tetlock called "foxes", consistently outperformed confident "hedgehogs" who viewed the world through a single big idea.

## The forecasting tournaments

Between 2011 and 2015, the U.S. Intelligence Advanced Research Projects Activity ran the [Aggregative Contingent Estimation (ACE)](https://www.iarpa.gov/research-programs/ace) program, a set of large forecasting tournaments on geopolitical questions. Several research teams competed to produce the most accurate probability forecasts. The [Good Judgment Project](https://en.wikipedia.org/wiki/Good_Judgment_Project), led by Tetlock and Barbara Mellers, won decisively, and its experiments produced some of the most useful evidence available on how to improve human judgment.

Three interventions stood out in the published results, notably [Mellers et al. (2014)](https://doi.org/10.1177/0956797614524255):

1. **Training.** A one-hour module on probabilistic reasoning, covering base rates, reference classes, averaging across sources and common biases, improved accuracy for the rest of the tournament.
2. **Teaming.** Forecasters working in teams, sharing information and challenging each other's reasoning, outperformed those working alone, provided the teams were structured to encourage constructive disagreement.
3. **Tracking.** Identifying the most accurate forecasters each year and placing them in elite teams, the so-called [superforecasters](https://en.wikipedia.org/wiki/Superforecasting:_The_Art_and_Science_of_Prediction), produced further gains, and their accuracy did not regress to the mean as much as luck alone would predict.

```chart
type: bar
id: interventions
caption: "Forecast error by intervention (lower is better)"
source: "Illustrative Brier-score pattern for this pipeline sample, reflecting the ordering of effects reported in [Mellers et al. (2014)](https://doi.org/10.1177/0956797614524255)."
categories: ["Untrained individuals", "Trained individuals", "Trained teams", "Superforecaster teams", "Aggregated and extremized"]
y_label: "Mean Brier score"
format: "{:.2f}"
highlight: ["Superforecaster teams", "Aggregated and extremized"]
values: [0.37, 0.32, 0.28, 0.23, 0.20]
```

A fourth finding concerned aggregation. Combining many individual forecasts, weighting more accurate forecasters more heavily, and then *extremizing* the result, pushing the aggregate probability further from 50 percent, produced the most accurate forecasts of all. Extremizing works because each individual holds only part of the available information; when many independent forecasters lean the same way, the combined evidence is stronger than any single forecaster's confidence reflects.

## Measuring accuracy: the Brier score and calibration

Forecasting science depends on proper scoring rules, the most common of which is the [Brier score](https://en.wikipedia.org/wiki/Brier_score): the mean squared difference between the forecast probability and the outcome, coded as 1 if the event occurred and 0 if it did not. A perfect forecaster scores 0; always guessing 50 percent on binary questions scores 0.25; confident wrong forecasts are punished heavily. Because the score is proper, the strategy that minimizes it is to report one's true belief, which removes the incentive to hedge or exaggerate.

The Brier score can be decomposed into two components that matter for organizations. *Calibration* asks whether events forecast at 70 percent happen about 70 percent of the time. *Resolution*, sometimes called discrimination, asks whether the forecaster assigns meaningfully different probabilities to events that do and do not occur. A forecaster who always says 50 percent may be perfectly calibrated and entirely useless. The goal is high resolution with good calibration: confident when there are grounds for confidence, and right about as often as that confidence implies.

```chart
type: line
id: calibration
caption: "Calibration curves: stated confidence versus observed frequency"
source: "Illustrative calibration data for this pipeline sample. A perfectly calibrated forecaster lies on the diagonal."
categories: ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%"]
x_label: "Stated probability"
y_label: "Observed frequency"
suffix: "%"
series:
  - name: Perfect calibration
    values: [10, 20, 30, 40, 50, 60, 70, 80, 90]
  - name: Trained forecasters
    values: [12, 21, 31, 41, 50, 58, 67, 76, 85]
  - name: Untrained experts
    values: [22, 29, 36, 43, 50, 54, 58, 62, 66]
```

@fig:calibration shows the characteristic pattern of overconfidence. Untrained experts' high-confidence forecasts come true far less often than claimed, and their low-confidence forecasts come true more often. Training flattens this distortion considerably. For organizations, the practical point is that calibration is visible only when probabilities are written down and scored over time. Without that record, overconfidence is invisible and therefore uncorrectable.

## What makes good forecasters different

The superforecaster research identified a recognizable cluster of habits. None depends on unusual intelligence or specialist access to information. Most can be adopted by anyone willing to practise them.

::: callout Habits of accurate forecasters
- **Start with the outside view.** Begin with the base rate for the class of event, then adjust for specifics.
- **Decompose the question.** Break a hard question into smaller, more tractable parts, an approach often called [Fermi estimation](https://en.wikipedia.org/wiki/Fermi_problem).
- **Update frequently, in small steps.** Revise forecasts as news arrives, avoiding both stubbornness and overreaction.
- **Seek out disagreement.** Actively look for the strongest version of the opposing view.
- **Think in fine-grained probabilities.** Distinguish 60 percent from 70 percent; the distinction carries real information.
- **Keep score.** Review past forecasts honestly, especially the ones that turned out well for the wrong reasons.
:::

Two further findings are relevant to organizational design. First, superforecasters spend a large share of their effort on *question clarification*: understanding exactly what would count as the event occurring. Many organizational forecasts fail not because the probability was wrong but because the question was vague. Second, accuracy depends heavily on time horizon. Forecasts more than a year or two out degrade sharply towards chance for most geopolitical questions, which argues for planning processes that build in frequent re-forecasting rather than relying on a single long-range projection.

## Prediction markets and crowd forecasting

[Prediction markets](https://en.wikipedia.org/wiki/Prediction_market) and crowd-forecasting platforms such as [Metaculus](https://www.metaculus.com/) and [Good Judgment Open](https://www.gjopen.com/) offer another way to aggregate dispersed information. Internal corporate prediction markets, tried by a number of large technology and consumer companies, have sometimes produced forecasts of launch dates and sales volumes that were more accurate than official plans. Their record is mixed, however: thin participation, politically sensitive questions and the temptation to manipulate prices for signalling purposes have limited their adoption.

Table: Comparison of forecast aggregation methods {#aggregation}

| Method | Strengths | Limitations | Best suited to |
|:--|:--|:--|:--|
| Simple average of experts | Cheap; reduces noise; easy to explain | Ignores differences in skill | Frequent, routine estimates |
| Weighted, extremized aggregate | Highest accuracy in tournaments | Needs track records to weight | Recurring strategic questions |
| Internal prediction market | Continuous updating; incentives to share | Thin markets; cultural friction | Large firms with many informed staff |
| Delphi panel | Structured iteration; anonymity | Slow; can converge prematurely | Long-horizon, expert-heavy topics |
| Model-generated forecast | Consistent; scalable; fast | Correlated errors; opaque failure | Data-rich, stable domains |

Source: H Heuristics synthesis; see also [Delphi method](https://en.wikipedia.org/wiki/Delphi_method).

## Implications

Forecasting research offers the clearest evidence that judgment can be measurably improved through process. The interventions are modest: brief training, structured teamwork, aggregation and, above all, keeping score. Organizations that adopt even a few of these practices gain something most lack entirely, which is an objective record of whose judgment has been reliable and under what conditions. That record becomes even more valuable when AI systems begin to produce forecasts of their own, because it provides the benchmark against which machine judgment can be fairly compared.
