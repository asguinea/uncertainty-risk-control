# From confidence scores to risk-controlled emotion tagging

An uncertainty score can rank predictions without telling us which acceptance policy meets a specified error budget. This study examines the step from a score to a calibrated decision rule, and the workload that remains after calibration. The central finding is practical: obtaining a passing policy can still leave almost everything for review.

## Research question and target

For a frozen model, we ask how four separate selected-risk budgets—5%, 10%, 15%, and 20%—change automation, observed mistakes, and review workload. We also examine calibration sample size and differences across annotation agreement. This is a retrospective benchmark investigation, with executable final-calibration replay and aggregate regeneration.

The benchmark is [GoEmotions](https://aclanthology.org/2020.acl-main.372/), an English Reddit emotion dataset. The prediction is the top tag from a frozen 28-output [RoBERTa](https://arxiv.org/abs/1907.11692) classifier. The reference contains every label supported by at least two recorded raters. An accepted tag is counted as unsupported when it is absent from that reference. The measurement concerns annotation agreement; it does not reveal a person's true emotional state.

A development-only logistic model uses 97 features derived from the classifier's probabilities to estimate top-tag error risk. A threshold accepts sufficiently low scores and sends the rest for review. It does not change the predicted tag. The estimated score and the controlled quantity are different: the score helps define candidate policies; the statistical procedure concerns the error probability conditional on acceptance.

## From a score to a policy

The development procedure fixes 21 candidates and their order. Final calibration then runs exact-binomial tests at one specified budget, stopping at the first failure. It selects the candidate with the greatest selected count from the passing prefix. If that prefix is empty, the policy reviews every comment.

This is a selected-risk application of [Learn then Test](https://arxiv.org/abs/2110.01052), not a new statistical theorem. The guarantee requires valid individual tests and a candidate sequence fixed independently of calibration. Here the comment-level binomial model assumes independent, identically distributed calibration units from the target population. Group-preserving splits reduce obvious thread and duplicate leakage, but do not establish that assumption. The [method note](method.md) gives the exact statement and implementation details.

Each budget uses delta 0.05 separately. The four procedures do not establish one simultaneous 95% guarantee. Locked observed error rates are descriptive outcomes, distinct from the probability statement over calibration. Comparing those rates with budgets is informative, but observing a rate below a budget does not itself prove the guarantee.

## Finding 1: strict budgets leave substantial review work

The experiment uses 5,426 final-calibration comments and a separate locked role of 10,853 comments, from its own group-preserving allocation. This locked role is not the official GoEmotions test split.

| Budget | Locked accepted / all | Unsupported / accepted | Automation | Observed selected error | Review |
| --- | --- | --- | --- | --- | --- |
| 5% | 419 / 10,853 | 10 / 419 | 3.86% | 2.39% | 96.14% |
| 10% | 530 / 10,853 | 16 / 530 | 4.88% | 3.02% | 95.12% |
| 15% | 2,931 / 10,853 | 414 / 2,931 | 27.01% | 14.12% | 72.99% |
| 20% | 3,892 / 10,853 | 683 / 3,892 | 35.86% | 17.55% | 64.14% |

![Observed locked automation and selected error, including descriptive confidence baselines.](../experiments/goemotions/report/figures/risk_automation.svg)

*Discrete policy observations, with a strict-budget detail panel. No confidence intervals or continuous trade-off frontier are shown. [Figure source and caption](../experiments/goemotions/report/figures/README.md#locked-risk-and-automation).*

Accepting all top tags gives 4,245 unsupported tags out of 10,853, or 39.11% error. A raw-confidence cutoff of 0.9 accepts 884 tags, of which 48 are unsupported: 8.15% automation and 5.43% observed selected error. These baselines carry no formal calibration claim. Their inclusion prevents the calibrated policies from being presented as a demonstrated dominance result over all simpler filters. No policy selection or new tuning is performed using the locked comparison.

## Finding 2: more calibration data helps, but passing is not utility

The warm-up study records 100 whole-group-prefix samples for each requested calibration size from 50 to 4,000 comments and each budget. All policies are evaluated on the same 5,426-comment warm-up evaluation role. Realized sample sizes can be smaller than the requested size because groups are kept whole.

![Warm-up passing frequency and median automation versus requested calibration sample size.](../experiments/goemotions/report/figures/calibration_size.svg)

*Automation bands show empirical 5th–95th percentiles across all runs, with review-all counted as zero automation. They are not confidence intervals. Shared development data and sample orders make these repeated observations dependent. Lines guide the eye between recorded tiers. The single full-pool run per budget is in the [tables](../experiments/goemotions/report/results.md#warm-up-sample-size-summaries), outside the plotted curves.*

At the 5% budget, the first requested tier with any passing run is 2,000 comments: 32 of 100 runs pass. At 4,000, all 100 pass, but median automation is only 4.18%. At the 20% budget, 56 of 100 runs pass at the 500-comment tier, and 99 pass at 1,000; median automation at 1,000 is 26.94%.

These are summaries of reused development evidence, not universal sample-size requirements or fresh independent replications. The public replay regenerates their arithmetic from 2,804 aggregate records, including four full-pool runs. It does not reconstruct the original warm-up sample orders or every candidate test in those runs.

## Finding 3: an aggregate budget does not describe every subgroup

The locked 20% policy has 17.55% observed selected error overall, but the descriptive breakdown by annotation consensus is:

| Consensus | All comments | Accepted | Unsupported | Automation | Observed selected error |
| --- | --- | --- | --- | --- | --- |
| High | 2,790 | 1,597 | 63 | 57.24% | 3.94% |
| Medium | 5,877 | 1,809 | 453 | 30.78% | 25.04% |
| Low | 2,186 | 486 | 167 | 22.23% | 34.36% |

Consensus is maximum label votes divided by number of raters: high is at least 0.80, medium is at least 0.60 but below 0.80, and low is below 0.60. These strata are descriptive, with no subgroup guarantee. The displayed 20% policy illustrates the heterogeneity; the [complete table](../experiments/goemotions/report/results.md#locked-consensus-strata) includes all four budgets. Lower-budget low-consensus selections are particularly small: five comments at 5% and seven at 10%.

Predicted-emotion slices are also reported with denominators and selected counts. Below the historical floor of 30 selected comments, unsupported counts and error rates remain unreported. A missing rate is not zero. These slices identify limits of an aggregate interpretation; they do not establish causal effects of disagreement or population-wide fairness.

## What the development history adds

The original confidence-derived score (D1) returned review-all on the full warm-up pool. Exploratory candidate/order refinement (D1R), which reused warm-up calibration information, also remained unsupported. The development-only logistic meta-risk adapter (D1S) obtained a passing 5% policy, but only 4.18% warm-up automation. MB1 retained that scorer and sequence before using separate final-calibration and locked roles.

Preserving these outcomes explains why the research examines both calibration and utility. The earlier phases are development history, not independent confirmations of MB1. Separate batch-selective and compact-emotion-set explorations use other risk contracts and are outside the executable scope here.

## What the executable evidence supports

The repository replays all 35 executed final-calibration tests across the four budgets, including each first failure, and checks exact controller, threshold, count, and stopping correspondence. It regenerates aggregate rates, warm-up summaries, tables, and figures. Numerical probability comparisons use the documented tolerance; the tolerance never changes a pass decision.

This is narrower than retraining or reproducing model predictions from source comments. The historical model assets and later assignment/sampling orders are not published. Hashes and counts support integrity and replay correspondence, but cannot independently authenticate the original predictions, the timing of the freeze, or the validity of sampling assumptions. See the [reproduction contract](../experiments/goemotions/reproduction.md).

The study is limited by annotation disagreement, potential dependence, development reuse, benchmark selection, and its English Reddit setting. It supplies no monetary benefit estimate, product-readiness conclusion, subgroup certificate, or evidence of transfer to another population. The work was developed in connection with EyeTrustAI, owned by the maintainer; the [contribution statement](contributions.md) makes that relationship explicit.
