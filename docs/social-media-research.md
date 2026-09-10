# Uncertainty and risk control for social media analysis

Social media classifiers can label every post, but unrestricted automation can accept unsupported interpretations or remove priority posts from review. These studies ask how much automation remains when an explicit error tolerance constrains the selected actions, how many calibration labels help, and how results change across populations.

## One method, three distinct decisions

| Study | Automatic action | Error reference | Calibration and evaluation |
| --- | --- | --- | --- |
| [GoEmotions MB1](../experiments/goemotions/README.md) | Accept the top emotion tag | Tag absent from the agreed label set, requiring at least two raters | Own group-preserving split: 5,426 final calibration comments; 10,853 locked comments. This is not the official GoEmotions test split. |
| [HumAID](../experiments/humaid/README.md) | Deprioritize a crisis post | Released human category belongs to one of seven priority categories | 2018 final calibration: 4,774; locked: 9,559. Source-policy transfer uses 3,075 target warm-up evaluation posts; target-local final calibration uses 3,075 distinct posts and locked evaluation uses 6,159. |
| [TweetEval Sentiment](../experiments/tweeteval-sentiment/README.md) | Accept a negative, neutral or positive tag | Tag differs from the released human sentiment label | Source train/validation pool yields 7,143 final calibration posts. Official TEST contains 12,284 posts and is a separate population. |

“Risk” is conditional on the selected action in each row. The error labels have different meanings and the denominators differ. Cross-study error rankings, pooled performance, and monetary savings cannot be inferred from these reports. Annotation agreement is a research reference, not psychological truth, verified incident truth, or objective sentiment.

## Calibration can pass while automation remains limited

GoEmotions' 5% and 10% policies accept 419 and 530 of 10,853 locked comments, respectively. Their observed unsupported-tag counts are 10 and 16. Larger budgets permit more automation, with more observed error. The [original research note](research-note.md) preserves development failures, the agreement analysis, and the frozen final protocol.

HumAID's source 5% policy deprioritizes 1,327 of 9,559 locked posts, including 45 priority posts. A raw 0.5 threshold deprioritizes 2,916, including 468 priority posts. These are frozen-policy observations in humanitarian research; they do not establish an operationally acceptable crisis workflow. The pooled 5% policy also has an event slice with 23 errors among 377 selected Kerala posts (6.10%). The pooled statement gives no event-specific guarantee.

TweetEval's 2.5% budget returns review-all in final calibration: the first tested candidate contains 134 selected posts and one error, and fails its exact test. The fallback's empty counts must not be confused with that failed candidate. At 5%, 785 posts are accepted and 32 disagree with the reference; at 15%, 5,333 are accepted and 810 disagree, or 15.1884%. The observed excess remains in the report. It does not by itself identify its cause or prove violation of a source-population guarantee.

At the TweetEval 5% budget, acceptance rates within predicted negative, neutral and positive classes are 253/4,128, 1/5,245 and 531/2,911. The neutral result has only one accepted observation. Selective automation is highly uneven; a pooled risk statement supplies no class-specific assurance.

## Calibration labels and population changes

All warm-up summaries retain review-all outcomes. The 5th–95th percentile bands describe recorded variability on reused pools; they are not confidence intervals or independent replications. Full-pool rows have one run and are excluded from repeated-run curves.

For GoEmotions at a 5% budget and requested n = 4,000, all 100 recorded runs pass, but median automation is 4.18%. For HumAID source calibration at n = 2,000, only five of 100 pass and median automation is zero. The source's combined 90%-passing/10%-automation milestone at n = 4,774 comes from one full-pool run. Target full-pool size is 3,075; it is a different population and experiment.

TweetEval's 2.5% policy passes in the single full-pool warm-up at n = 7,142, although every smaller recorded tier fails and final calibration returns review-all. A development observation does not promise a later calibration outcome.

HumAID keeps the scorer frozen while studying transfer across event-years. The source 5% threshold selects 522/3,075 target warm-up evaluation posts with nine errors (16.98% automation, 1.72% selected error). The target-local locked policy selects 1,115/6,159 with 32 errors (18.10%, 2.87%). Those are different roles, so their difference is not a paired or causal estimate of recalibration benefit. The source guarantee does not formally transfer to 2019.

TweetEval's source calibration and official TEST have different observed reference-class proportions. Those marginals alone do not demonstrate pure label shift. The locked results were not used here to change a threshold or repair an unfavorable finding. See each study's protocol for chronology and sampling limits.

## What the repository contributes

The [method](method.md) uses exact-binomial tests and a fixed sequence with first-failure stopping. Its statistical framework is prior work. The contribution here is the application-specific protocol, implementation and verification, empirical investigation, and a traceable public aggregate reproduction path.

The three studies replay 35 + 16 + 35 final candidate tests and regenerate 2,804 + 1,202 + 2,804 warm-up aggregate records. The [reproduction guide](reproduction.md) distinguishes final-count replay from full historical retraining, inference and sampling. Neither source independence nor the original predictions is established by matching aggregates.

Original methods, GoEmotions evidence, and prior figures remain byte-preserved in this expansion. New figures read the verified public evidence and add no training, calibration search or new benchmark evaluation. Each budget retains its own delta 0.05; no simultaneous cross-study, budget, class or event guarantee is claimed.

This research originated at EyeTrustAI and is maintained personally by its owner, Alejandro Sanchez Guinea. The [contribution and relationship statement](contributions.md) describes the planned product-validation companion and shared evidence. The candidate is not a claim of product readiness or independent external validation.
