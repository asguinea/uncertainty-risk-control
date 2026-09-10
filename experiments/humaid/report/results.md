# HumAID: risk-controlled crisis-post deprioritization

Generated from frozen aggregate evidence. Human-agreed crisis categories define priority; these are research observations, not verified incident truth or product readiness.

Verified **16 final candidate tests** and regenerated **1,202 warm-up aggregate records**. No new training, inference or experiment was performed.

## Final calibration

A post is automatically deprioritized when its frozen priority score is at or below the selected threshold. Error is the priority-label fraction among deprioritized posts. Each budget uses delta 0.05 separately.

| Calibration population | Budget | Threshold | Selected | Priority errors | Exact p-value | CP upper diagnostic | Passing / tested | First failure index |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_2018 (n=4,774) | 2.50% | 0.017609769478440285 | 361 | 2 | 0.00568544308307 | 1.73% | 2 / 3 | 2 |
| source_2018 (n=4,774) | 5.00% | 0.051400627940893173 | 658 | 17 | 0.00142455135677 | 3.85% | 3 / 4 | 3 |
| source_2018 (n=4,774) | 10.00% | 0.13397836685180664 | 939 | 52 | 5.96315225154e-07 | 6.93% | 4 / 5 | 4 |
| target_2019 (n=3,075) | 5.00% | 0.051400627940893173 | 531 | 13 | 0.00236250146604 | 3.86% | 3 / 4 | 3 |

Indices are zero-based. The first failed test is included; later candidates are not replayed. CP bounds are fixed-candidate diagnostics, not an adaptive confidence band. The guarantee depends on the frozen design and sampling assumptions; it is not joint across budgets, events or periods.

## Pooled evaluation and baselines

| Population / role | Policy | Budget | n | Deprioritized | Priority errors | Automation | Selected error | Priority retained for review |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| source_2018 / locked_evaluation | AUTO_DEPRIORITIZE_ALL | — | 9,559 | 9,559 | 6,270 | 100.00% | 65.59% | 0/6,270 (0.00%) |
| source_2018 / locked_evaluation | RAW_0_5_CLASSIFIER_THRESHOLD | — | 9,559 | 2,916 | 468 | 30.51% | 16.05% | 5,802/6,270 (92.54%) |
| source_2018 / locked_evaluation | REVIEW_ALL | — | 9,559 | 0 | 0 | 0.00% | undefined | 6,270/6,270 (100.00%) |
| source_2018 / locked_evaluation | calibrated | 2.50% | 9,559 | 760 | 11 | 7.95% | 1.45% | 6,259/6,270 (99.82%) |
| source_2018 / locked_evaluation | calibrated | 5.00% | 9,559 | 1,327 | 45 | 13.88% | 3.39% | 6,225/6,270 (99.28%) |
| source_2018 / locked_evaluation | calibrated | 10.00% | 9,559 | 1,860 | 110 | 19.46% | 5.91% | 6,160/6,270 (98.25%) |
| source_2018 / warmup_evaluation | calibrated | 5.00% | 4,774 | 649 | 21 | 13.59% | 3.24% | 3,120/3,141 (99.33%) |
| target_2019 / locked_evaluation | AUTO_DEPRIORITIZE_ALL | — | 6,159 | 6,159 | 3,580 | 100.00% | 58.13% | 0/3,580 (0.00%) |
| target_2019 / locked_evaluation | RAW_0_5_CLASSIFIER_THRESHOLD | — | 6,159 | 2,190 | 260 | 35.56% | 11.87% | 3,320/3,580 (92.74%) |
| target_2019 / locked_evaluation | REVIEW_ALL | — | 6,159 | 0 | 0 | 0.00% | undefined | 3,580/3,580 (100.00%) |
| target_2019 / locked_evaluation | calibrated | 5.00% | 6,159 | 1,115 | 32 | 18.10% | 2.87% | 3,548/3,580 (99.11%) |
| target_2019 / warmup_evaluation | AUTO_DEPRIORITIZE_ALL | — | 3,075 | 3,075 | 1,778 | 100.00% | 57.82% | 0/1,778 (0.00%) |
| target_2019 / warmup_evaluation | RAW_0_5_CLASSIFIER_THRESHOLD | — | 3,075 | 1,054 | 124 | 34.28% | 11.76% | 1,654/1,778 (93.03%) |
| target_2019 / warmup_evaluation | REVIEW_ALL | — | 3,075 | 0 | 0 | 0.00% | undefined | 1,778/1,778 (100.00%) |
| target_2019 / warmup_evaluation | calibrated | 5.00% | 3,075 | 522 | 9 | 16.98% | 1.72% | 1,769/1,778 (99.49%) |
| target_2019 / warmup_evaluation | zero_shot | 5.00% | 3,075 | 522 | 9 | 16.98% | 1.72% | 1,769/1,778 (99.49%) |

The source primary locked policy deprioritizes 1,327/9,559 posts with 45 priority errors (3.39%). The target locally calibrated locked policy deprioritizes 1,115/6,159 with 32 errors (2.87%).

Zero-shot uses the unchanged source controller on TARGET_WARMUP_EVAL (3,075 posts): 522 selected, nine errors (1.72%). Local locked evaluation uses a different role (6,159 posts). Their difference is not a paired or causal estimate of recalibration benefit. The 2018 certificate does not formally transfer to 2019. The scorer remains unchanged.

Review-all error is undefined because its selected denominator is zero. Baselines have no selected-risk certificate. Warm-up evaluation is development evidence and is reused across the warm-up runs.

## Event slices

| Period / role | Policy | Event | n | Deprioritized | Priority errors | Automation | Selected error |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| source_2018 / locked_evaluation | calibrated | california_wildfires_2018 | 2,951 | 473 | 7 | 16.03% | 1.48% |
| source_2018 / locked_evaluation | calibrated | greece_wildfires_2018 | 606 | 111 | 1 | 18.32% | 0.90% |
| source_2018 / locked_evaluation | calibrated | hurricane_florence_2018 | 2,508 | 303 | 12 | 12.08% | 3.96% |
| source_2018 / locked_evaluation | calibrated | kerala_floods_2018 | 3,196 | 377 | 23 | 11.80% | 6.10% |
| source_2018 / locked_evaluation | calibrated | maryland_floods_2018 | 298 | 63 | 2 | 21.14% | 3.17% |
| source_2018 / warmup_evaluation | calibrated | california_wildfires_2018 | 1,475 | 235 | 4 | 15.93% | 1.70% |
| source_2018 / warmup_evaluation | calibrated | greece_wildfires_2018 | 303 | 57 | 3 | 18.81% | 5.26% |
| source_2018 / warmup_evaluation | calibrated | hurricane_florence_2018 | 1,252 | 150 | 3 | 11.98% | 2.00% |
| source_2018 / warmup_evaluation | calibrated | kerala_floods_2018 | 1,596 | 173 | 11 | 10.84% | 6.36% |
| source_2018 / warmup_evaluation | calibrated | maryland_floods_2018 | 148 | 34 | 0 | 22.97% | 0.00% |
| target_2019 / locked_evaluation | calibrated | cyclone_idai_2019 | 1,575 | 158 | 6 | 10.03% | 3.80% |
| target_2019 / locked_evaluation | calibrated | hurricane_dorian_2019 | 3,047 | 530 | 19 | 17.39% | 3.58% |
| target_2019 / locked_evaluation | calibrated | midwestern_us_floods_2019 | 752 | 111 | 3 | 14.76% | 2.70% |
| target_2019 / locked_evaluation | calibrated | pakistan_earthquake_2019 | 785 | 316 | 4 | 40.25% | 1.27% |
| target_2019 / warmup_evaluation | zero_shot | cyclone_idai_2019 | 786 | 67 | 1 | 8.52% | 1.49% |
| target_2019 / warmup_evaluation | zero_shot | hurricane_dorian_2019 | 1,522 | 233 | 6 | 15.31% | 2.58% |
| target_2019 / warmup_evaluation | zero_shot | midwestern_us_floods_2019 | 376 | 54 | 1 | 14.36% | 1.85% |
| target_2019 / warmup_evaluation | zero_shot | pakistan_earthquake_2019 | 391 | 168 | 1 | 42.97% | 0.60% |

All slices describe the primary 5% policy. They partition their corresponding pooled evaluation. Kerala's source locked selected error exceeds 5%; the pooled certificate is not an event-specific guarantee.

## Calibration-label warm-up

Every size below the full pool has 100 deterministic, nested subsampling runs. Each full pool has one run. All runs use the same period-specific warm-up evaluation pool. The 5th and 95th percentiles are descriptive; repeated/nested runs are not independent experiments or confidence intervals.

### source_2018

| Calibration labels | Runs | Certified | Median automation | Automation p05–p95 | Nonzero evaluation runs | Median nonzero selected error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 100 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 200 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 500 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 1,000 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 2,000 | 100 | 5 (5.00%) | 0.00% | 0.00%–0.13% | 5 | 1.61% |
| 4,774 (single full pool) | 1 | 1 (100.00%) | 13.59% | 13.59%–13.59% | 1 | 3.24% |

| Historical milestone | First labels |
| --- | ---: |
| first any certification | 2000 |
| first certification frequency ge 50pct | 4774 |
| first certification frequency ge 80pct | 4774 |
| first certification frequency ge 90pct | 4774 |
| first median utility ge 10pct | 4774 |
| first median utility ge 25pct | not reached |
| first median utility ge 50pct | not reached |
| first median utility ge 75pct | not reached |
| first 90pct certification and 10pct utility | 4774 |
| first 90pct certification and 25pct utility | not reached |
| first 90pct certification and 50pct utility | not reached |

### target_2019

| Calibration labels | Runs | Certified | Median automation | Automation p05–p95 | Nonzero evaluation runs | Median nonzero selected error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 100 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 200 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 500 | 100 | 0 (0.00%) | 0.00% | 0.00%–0.00% | 0 | undefined |
| 1,000 | 100 | 63 (63.00%) | 7.48% | 0.00%–16.98% | 63 | 0.78% |
| 2,000 | 100 | 100 (100.00%) | 16.98% | 7.48%–16.98% | 100 | 1.72% |
| 3,075 (single full pool) | 1 | 1 (100.00%) | 16.98% | 16.98%–16.98% | 1 | 1.72% |

| Historical milestone | First labels |
| --- | ---: |
| first any certification | 1000 |
| first certification frequency ge 50pct | 1000 |
| first certification frequency ge 80pct | 2000 |
| first certification frequency ge 90pct | 2000 |
| first median utility ge 10pct | 2000 |
| first median utility ge 25pct | not reached |
| first median utility ge 50pct | not reached |
| first 90pct certification and 10pct utility | 2000 |
| first 90pct certification and 25pct utility | not reached |
| first 90pct certification and 50pct utility | not reached |

The combined ≥90% certification / ≥10% median automation milestone is 4,774 labels in the source and 2,000 in the target. The source full-pool row is a single observation; its 100% frequency is not evidence of 100-run stability. These are descriptive label requirements for the frozen study, not universal annotation requirements.

## Reproduction boundary

This replay recomputes final fixed-sequence decisions and checks aggregate counts, metrics, warm-up winner diagnostics, historical quantiles and milestones. Warm-up winner/stop summaries do not contain every candidate count, so complete warm-up prefix reconstruction is unavailable. Source rows, assignments, model weights, historical training and checkpoint inference are not distributed.

Evidence manifest SHA-256: `b4062067ce2e5c147f28ebfa9592ebfae45b2b02f113336ee73280f5179ff4ba`.
