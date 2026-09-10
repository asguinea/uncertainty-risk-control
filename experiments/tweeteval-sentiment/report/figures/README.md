# TweetEval Sentiment figures

[Risk and class selection: SVG](risk_and_class_selection.svg) · [PNG](risk_and_class_selection.png)

[Calibration size: SVG](calibration_size.svg) · [PNG](calibration_size.png)

[Verified numerical inputs and provenance](plot_data.json)

## Risk tolerance and class selection

The left panel shows acceptance / all 12,284 official TEST posts, and disagreements with the human sentiment reference / accepted posts. Colored points are the nonempty 5%, 10% and 15% budget policies. Gray crosses are raw confidence cutoffs 0.5, 0.8, 0.9 and accept-all; their named counts are in the [complete tables](../results.md) and JSON. The 2.5% budget returns review-all with undefined selected error, shown as text rather than a zero-error point. Review-all baseline is also omitted from the scatter.

At the 15% budget, 810/5,333 accepted labels disagree (15.1884%), above the nominal budget. That observation is preserved. Source calibration does not guarantee performance on an arbitrarily shifted TEST population; the observed difference is not a causal diagnosis. Delta = 0.05 applies per budget under the method assumptions, not jointly across budgets or classes.

The right panel shows acceptance within each predicted class at the 5% budget: negative 253/4,128, neutral 1/5,245, positive 531/2,911. Errors among accepted posts are 10, 0, 22 respectively. The neutral slice has one accepted observation, so its zero observed errors provides little evidence. These are predicted-class denominators, not human-reference class supports.

## Calibration sample size

Each plotted requested tier (50, 100, 200, 500, 1,000, 2,000, 4,000) contains 100 recorded runs. The panels show passing frequency and median automation on warm-up evaluation, with review-all included. Shading is descriptive 5th–95th percentile variability, not a confidence interval or independent replication.

The full-pool n = 7,142 row is one run and is excluded from the curves. At 2.5% that single warm-up run passes, but final calibration returns review-all; every smaller recorded tier fails. Final and development outcomes must remain distinct.

## Regeneration and attribution

From the repository root run `uv run --locked --group figures python scripts/plot_social_media_studies.py --output results/social-media`. The [generator](../../../../scripts/plot_social_media_studies.py) reads only the verified public evidence. Outputs mirror these paths under the requested directory. The JSON contains verified evaluation counts and warm-up aggregates, generator hash and environment; full-precision numerical inputs are compared during installed reproduction.

Credit Alejandro Sanchez Guinea / EyeTrustAI for the original analysis, and cite [TweetEval, SemEval-2017 sentiment and BERTweet](../../../../THIRD_PARTY_NOTICES.md#tweeteval-sentiment-and-bertweet) as applicable. Preserve the human-reference definition, review-all outcome, observed excess and sparse neutral slice in reuse.

Figure-input schema 2 excludes unplotted final-test probabilities and confidence-bound diagnostics. The complete evidence replay still runs before plotting and retains its original numerical tolerances. Plotted inputs are compared exactly; no rounding or tolerance is added to figure comparisons.
