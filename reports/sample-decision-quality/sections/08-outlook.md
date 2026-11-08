# Outlook and Recommendations {#outlook}

## The next five years

Three trends are likely to shape organizational decision-making over the next five years. Each raises the importance of the practices described in this report.

**AI agents will move from advising to acting.** Today, most AI systems in organizations draft, summarize and recommend; a human makes the final call. Increasingly, agents will execute decisions within defined limits: reordering inventory, adjusting prices, triaging cases or approving routine requests. This shifts the critical design question from "is the recommendation good?" to "are the limits and monitoring right?" Tiering decisions by consequence and reversibility, as described in @sec:operating-model, provides a natural framework for setting those limits.

**Forecasting will become ambient.** As models become cheaper and better calibrated on structured questions, organizations will be able to attach a machine-generated probability to almost every plan and commitment. The scarce resource will no longer be forecasts but the discipline to state clear questions, compare forecasts honestly and act on the results. Organizations that already keep score will be best placed to know when to trust machine forecasts and when to override them.

**Regulation will formalize oversight.** Obligations under the [EU AI Act](https://artificialintelligenceact.eu/) for high-risk systems, together with sector-specific guidance in finance, health and employment, will require organizations to demonstrate meaningful human oversight of AI-assisted decisions. Meaningful oversight is, in practice, a decision-quality question: it requires knowing who decided what, on what basis, with what uncertainty, and how the decision was reviewed.

```chart
type: timeline
id: roadmap
caption: "An indicative 24-month roadmap for a decision-quality program"
source: "H Heuristics framework. Timing is indicative and should be adapted to organizational context."
events:
  - date: "Month 1"
    title: "Tier decisions"
    text: "Classify recurring decisions by consequence and reversibility"
  - date: "Month 3"
    title: "Pilot protocol"
    text: "Run the full protocol on 10–15 high-stakes decisions"
  - date: "Month 6"
    title: "Start scoring"
    text: "Record probabilistic forecasts and resolution dates"
  - date: "Month 9"
    title: "AI roles defined"
    text: "Agree where models advise, decide or must be overruled"
    highlight: true
  - date: "Month 12"
    title: "First reviews"
    text: "Hold scheduled reviews and publish lessons"
  - date: "Month 18"
    title: "Calibration report"
    text: "Compare human, AI and blended accuracy"
  - date: "Month 24"
    title: "Embed"
    text: "Link decision quality to planning and performance cycles"
```

## Recommendations for leaders

Drawing together the evidence in this report, we offer eight recommendations. They are ordered roughly by the speed with which they can be implemented, and most can begin within a single quarter.

1. **Start a decision log this month.** Ask every member of the executive team to record their next three significant decisions using a one-page template: the choice, the alternatives considered, the key forecast with a probability and a review date.
2. **Separate process reviews from outcome reviews.** Schedule reviews of a sample of decisions irrespective of results, and evaluate the process on its own terms before discussing the outcome.
3. **Require the outside view.** Make a reference class and its base rate a mandatory input to every business case above a set threshold, before any inside-view projections are presented.
4. **Collect independent estimates before meetings.** For consequential decisions, gather private written estimates from participants, and from any AI model in use, before discussion begins.
5. **Institutionalize the pre-mortem.** Add a structured pre-mortem to the approval process for large, hard-to-reverse commitments, and record the risks identified.
6. **Define AI decision rights explicitly.** For each class of decision, specify whether AI advises, decides within limits or is excluded, and who is accountable for monitoring its performance.
7. **Keep score, for humans and machines alike.** Track forecast accuracy with proper scoring rules, publish calibration results internally, and use them to weight future judgments.
8. **Reward good process.** Incorporate decision quality, assessed on the record, into performance conversations and promotion decisions for leaders.

::: keyfindings What success looks like after two years
- Every high-stakes decision has a short written record with explicit probabilities and a scheduled review.
- Forecast accuracy and calibration are reported by team, and improve over time.
- AI tools are used in defined roles, with their accuracy benchmarked against human and blended judgment.
- Leaders can point to specific decisions that were improved, or avoided, because of the process.
:::

## Questions for boards

Boards have a particular role in decision quality because they oversee the most consequential and least reversible choices an organization makes. The following questions can help a board assess whether management's decision processes are fit for purpose, without intruding into operational detail.

- Which decisions in the past year would we classify as high-stakes and hard to reverse, and what process did each follow?
- For our largest commitments, what reference class did management use, and how does the plan compare with the base rate?
- Where do AI systems currently inform or make decisions on our behalf, and who is accountable for monitoring their performance?
- How accurate have management's key forecasts been over the past three years, and how do we know?
- When did we last reverse a major decision on the basis of new evidence, and what did we learn?

## Limitations and open questions

Several questions remain open, and leaders should treat the recommendations in this report as a starting point to be adapted rather than a finished blueprint.

First, most of the forecasting evidence comes from geopolitical and economic questions with clear resolution criteria and horizons of months rather than years. Corporate decisions often involve longer horizons, outcomes that are partly shaped by the decision itself, and questions that are hard to resolve unambiguously. The core lessons, including outside-view anchoring, independence and keeping score, appear to transfer, but the size of the benefits in corporate settings is less well established.

Second, research on human–AI collaboration is moving quickly and is sensitive to the particular model, task and interface studied. Findings from one generation of models may not hold for the next. Organizations should therefore treat their own measured results, gathered through the scorecard in @sec:measurement, as the most relevant evidence, and should revisit AI decision rights at least annually.

Third, decision processes carry costs as well as benefits. Excessive process can slow organizations down, discourage initiative and push decisions into informal channels where they are not recorded at all. The tiering approach described in @sec:operating-model is intended to limit this risk, but the right balance will differ between a regulated bank, a fast-growing software company and a public agency.

Finally, there is a risk that measurement itself becomes the goal. Brier scores and calibration curves are tools for learning, not targets for performance management. Organizations that tie compensation directly to forecast scores may find that people avoid hard questions or game resolution criteria. Used well, the measures in this report support honest conversation about judgment; used badly, they can undermine it.

## Conclusion

The research on judgment and decision-making offers an unusually clear message for leaders. People are not hopelessly irrational, and simple heuristics often serve them well. But in the situations that matter most, those that are novel, high-stakes and slow to provide feedback, intuitive confidence is an unreliable guide, and predictable errors are common. The remedy is not more data or smarter individuals but better process: framing problems carefully, taking the outside view, preserving independent judgment, making uncertainty explicit and keeping score.

AI makes this message more urgent, not less. Machine assistance can reduce noise, widen the search for options and supply base rates at unprecedented speed. It can also amplify overconfidence, correlate errors across teams and erode the human skills needed to catch its mistakes. The organizations that benefit most from AI will be those that treat it as a participant in a well-designed decision process, subject to the same discipline of measurement and review as any human contributor.

Decision quality is, in the end, a capability that compounds. Each recorded forecast, each scheduled review and each lesson applied makes the next decision slightly better. Over years, small improvements in the quality of many decisions add up to a substantial and durable advantage, one that is difficult for competitors to observe and even harder for them to copy.

# References

1. Simon, H. A. (1955). A behavioral model of rational choice. *Quarterly Journal of Economics*, 69(1), 99–118. [doi.org/10.2307/1884852](https://doi.org/10.2307/1884852)
2. Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131. [doi.org/10.1126/science.185.4157.1124](https://doi.org/10.1126/science.185.4157.1124)
3. Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. [doi.org/10.2307/1914185](https://doi.org/10.2307/1914185)
4. Kahneman, D., & Klein, G. (2009). Conditions for intuitive expertise: A failure to disagree. *American Psychologist*, 64(6), 515–526. [doi.org/10.1037/a0016755](https://doi.org/10.1037/a0016755)
5. Flyvbjerg, B. (2014). What you should know about megaprojects and why: An overview. *Project Management Journal*, 45(2), 6–19. [doi.org/10.1002/pmj.21409](https://doi.org/10.1002/pmj.21409)
6. Mellers, B., et al. (2014). Psychological strategies for winning a geopolitical forecasting tournament. *Psychological Science*, 25(5), 1106–1115. [doi.org/10.1177/0956797614524255](https://doi.org/10.1177/0956797614524255)
7. Grove, W. M., Zald, D. H., Lebow, B. S., Snitz, B. E., & Nelson, C. (2000). Clinical versus mechanical prediction: A meta-analysis. *Psychological Assessment*, 12(1), 19–30. [doi.org/10.1037/1040-3590.12.1.19](https://doi.org/10.1037/1040-3590.12.1.19)
8. Dietvorst, B. J., Simmons, J. P., & Massey, C. (2015). Algorithm aversion: People erroneously avoid algorithms after seeing them err. *Journal of Experimental Psychology: General*, 144(1), 114–126. [doi.org/10.1037/xge0000033](https://doi.org/10.1037/xge0000033)
9. Parasuraman, R., & Manzey, D. H. (2010). Complacency and bias in human use of automation: An attentional integration. *Human Factors*, 52(3), 381–410. [doi.org/10.1177/0018720810376055](https://doi.org/10.1177/0018720810376055)
10. Klein, G. (2007). Performing a project premortem. *Harvard Business Review*, 85(9). [hbr.org](https://hbr.org/2007/09/performing-a-project-premortem)
11. Kahneman, D., Sibony, O., & Sunstein, C. R. (2021). *Noise: A Flaw in Human Judgment*. Little, Brown Spark. [Overview](https://en.wikipedia.org/wiki/Noise:_A_Flaw_in_Human_Judgment)
12. National Institute of Standards and Technology (2023). *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. [nist.gov](https://www.nist.gov/itl/ai-risk-management-framework)
13. European Union (2024). *Artificial Intelligence Act*. [artificialintelligenceact.eu](https://artificialintelligenceact.eu/)
14. OECD (2019, updated 2024). *OECD AI Principles*. [oecd.ai](https://oecd.ai/en/ai-principles)
15. Intelligence Advanced Research Projects Activity. *Aggregative Contingent Estimation (ACE) program*. [iarpa.gov](https://www.iarpa.gov/research-programs/ace)
