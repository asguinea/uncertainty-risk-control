# Frozen HumAID research protocol

## Action and reference

A frozen RoBERTa-base binary scorer produces `p_priority`. A threshold automatically deprioritizes posts with `p_priority <= threshold`, including ties; other posts remain for review. Selected risk is the fraction of **priority-reference posts among those deprioritized**, not the fraction of all priority posts missed. Priority recall to review uses the separate denominator of all priority-reference posts.

The seven priority categories are `caution_and_advice`, `displaced_people_and_evacuations`, `infrastructure_and_utility_damage`, `injured_or_dead_people`, `missing_or_found_people`, `requests_or_urgent_needs`, and `rescue_volunteering_or_donation_effort`. The lower/nonprimary categories are `not_humanitarian`, `other_relevant_information`, and `sympathy_and_support`. The protocol excludes `dont_know_cant_judge`; that ambiguous category is absent from the released classification inputs used here. These categories are operational research references, not determinations of factual urgency or truth.

The scorer was trained on 37,213 eligible posts from 2016–2017. Historical normalization applies Unicode NFC, replaces URLs with `HTTPURL` and mentions with `@USER`, collapses whitespace, and preserves hashtag text, punctuation and emoji. The scorer is unchanged throughout the 2018 source and 2019 target sequence. This package does not distribute or rerun it.

## Populations and chronology

| Population | Warm-up calibration | Fixed warm-up evaluation | Final calibration | Locked evaluation |
| --- | ---: | ---: | ---: | ---: |
| 2018 source | 4,774 | 4,774 | 4,774 | 9,559 |
| 2019 target | 3,075 | 3,075 | 3,075 | 6,159 |

The threshold design uses development scores and labels from 2016–2017 and was frozen before the 2018 calibration labels. Source warm-up evaluates label requirements, then D2 final calibration freezes each policy before source locked evaluation. D3 applies the source primary policy to TARGET_WARMUP_EVAL, then conducts target-local warm-up and final calibration before target locked evaluation. The source zero-shot result and target local locked result have different evaluation roles and denominators. No policy is retuned after its locked evaluation.

Older records describing 2019 as protected refer to earlier phases. The completed 2019 sequence is included here with its actual chronology. Freeze assertions and source hashes are historical evidence; this later publication is not a public preregistration.

## Fixed sequence and decisions

Nearest-rank development quantiles use `sorted_score[ceil(fraction*N)-1]`; equal thresholds are deduplicated. The 22-member family includes a zero-score boundary. The executed sequence has 21 nonzero-development-selection candidates. The zero boundary is not an additional tested candidate, and a score-zero boundary is not equivalent to a universal review-all policy if exact-zero scores occur.

The fixed candidate order is development empirical selected error ascending, development selected fraction descending, then threshold ascending. This differs from the GoEmotions ordering recipe. [Design evidence](evidence/design.json) preserves every candidate's threshold and development counts.

For each candidate, compute `P[Binomial(selected, alpha) <= harmful]`. A nonempty candidate passes when this exact lower-tail probability is at most delta 0.05. Stop at the first failure, including it in the trace. Choose the maximum selected count in the passing prefix, breaking ties by higher threshold. If none passes, return `REVIEW_ALL`, with zero actions and undefined conditional error. The public implementation reuses the [unchanged method](../../docs/method.md).

Source budgets 0.025, 0.05 and 0.10 have recorded prefixes of 3, 4 and 5 tests. The target uses alpha 0.05 and four tests. The public union contains five source and four target candidate-count rows. Only historical executed prefixes are projected or replayed.

## Guarantee and evaluation limits

Each budget separately uses delta 0.05 under the fixed-sequence and sampling assumptions. There is no simultaneous confidence statement across budgets, studies, events or years. The exact-binomial model requires the relevant Bernoulli sampling assumptions; role separation and tweet-level assignment alone do not establish independence. Related posts, event clustering and a changing event mixture can undermine those assumptions.

The source guarantee does not transfer formally to 2019. Target-local calibration supports its own population statement under its assumptions; it does not establish automatic drift handling or robustness to arbitrary future shifts. The CP upper values are fixed-candidate diagnostics, not a confidence band for the adaptively selected curve. Locked rates and event slices are empirical observations. In particular, source locked Kerala selected error is above 5%; the pooled controller is not an every-event guarantee.

## Warm-up interpretation

Each period uses six nested sizes (50, 100, 200, 500, 1,000 and 2,000), with 100 deterministic subsampling replicates per size, and a single full-pool run (4,774 or 3,075). All runs within a period reuse the fixed warm-up evaluation pool. The exported records preserve each chosen controller, its count diagnostics, and aggregate evaluation counts; they omit the complete per-run candidate traces and row membership.

Historical quantiles retain all runs for automation, only nonzero evaluation selections for conditional error, and only certified runs for threshold and winner diagnostics. Missing values remain undefined. Percentile bands are descriptive. The full-pool milestone in the source is a single run, not a 100-replicate stability estimate. Label requirements describe this frozen study, not universal sample complexity, staffing costs or monetary ROI.
