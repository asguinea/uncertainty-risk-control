# TweetEval Sentiment: risk tolerance, automation and calibration labels

Generated from frozen D1/D2 aggregate evidence. An accepted sentiment tag is wrong when it differs from the released human reference. These are benchmark research results, not objective sentiment truth or product-readiness evidence.

Replayed **35 final candidate tests** and regenerated **2,804 warm-up aggregate records**. The scorer, candidate design and historical results remain fixed.

## Final calibration: a passing warm-up need not pass the final role

Final calibration contains 7,143 rows. Each budget separately uses delta 0.05. The ordered sequence has 20 candidates; the first failure is included and later candidates are not replayed.

| Budget | State | Winning threshold | Selected / errors | Winner exact p | CP upper diagnostic | Passing / tested | First failed candidate selected / errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2.5000% | REVIEW_ALL | none | 0 / 0 | undefined | undefined | 0 / 1 | 134 / 1 |
| 5.0000% | CERTIFIED | 0.0295229992319207 | 631 / 12 | 4.58345080875e-05 | 3.0631% | 7 / 8 | 1,288 / 68 |
| 10.0000% | CERTIFIED | 0.061477750631934946 | 1,928 / 149 | 0.000339418077357 | 8.8030% | 11 / 12 | 2,539 / 246 |
| 15.0000% | CERTIFIED | 0.11842140197479434 | 3,226 / 385 | 2.93870974231e-07 | 12.9143% | 13 / 14 | 3,940 / 567 |

At 2.5%, the first candidate selects 134 calibration rows with 1 error; its exact p-value is 0.149142012709, above 0.05. The resulting review-all controller has zero actions and undefined winner p-value, CP bound and conditional error. The failed candidate's observed counts are not zero and must not be replaced by the fallback counts.

CP values are fixed-candidate diagnostics, not an adaptive confidence band. A calibration result is conditional on the frozen design and sampling assumptions; it is not a joint guarantee across budgets or classes, nor a guarantee for a shifted test population.

## Locked test: risk and review workload

Official TEST contains 12,284 rows, separate from the train/validation source calibration pool. All four controllers were frozen before the historical D2 test-label access; no post-test adaptation was performed in D2.

| Budget | Accepted | Wrong | Automation | Selected error | Correct accepted | Reviewed | Review rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2.5000% | 0 | 0 | 0.0000% | undefined | 0 | 12,284 | 100.0000% |
| 5.0000% | 785 | 32 | 6.3904% | 4.0764% | 753 | 11,499 | 93.6096% |
| 10.0000% | 3,041 | 301 | 24.7558% | 9.8981% | 2,740 | 9,243 | 75.2442% |
| 15.0000% | 5,333 | 810 | 43.4142% | 15.1884% | 4,523 | 6,951 | 56.5858% |

The 15% policy has observed test selected error **15.1884%**, slightly above its nominal budget; this result is retained. Source calibration does not establish the same guarantee for the separate official TEST population. Observed proportions can also fluctuate even under matched sampling assumptions; this finite test result alone does not diagnose the cause of the excess.

## Baselines

Raw confidence thresholds are descriptive policies without a selected-risk certificate. Review-all conditional error remains undefined.

| Evaluation role | Policy | Accepted | Wrong | Automation | Selected error | Review rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| LOCKED_TEST | Accept all | 12,284 | 3,609 | 100.0000% | 29.3797% | 0.0000% |
| LOCKED_TEST | Confidence ≥ 0.5 | 12,031 | 3,470 | 97.9404% | 28.8422% | 2.0596% |
| LOCKED_TEST | Confidence ≥ 0.8 | 7,404 | 1,430 | 60.2735% | 19.3139% | 39.7265% |
| LOCKED_TEST | Confidence ≥ 0.9 | 4,730 | 651 | 38.5054% | 13.7632% | 61.4946% |
| LOCKED_TEST | Review all | 0 | 0 | 0.0000% | undefined | 100.0000% |
| WARMUP_EVALUATION | Accept all | 7,142 | 1,832 | 100.0000% | 25.6511% | 0.0000% |
| WARMUP_EVALUATION | Confidence ≥ 0.5 | 7,005 | 1,750 | 98.0818% | 24.9822% | 1.9182% |
| WARMUP_EVALUATION | Confidence ≥ 0.8 | 4,350 | 654 | 60.9073% | 15.0345% | 39.0927% |
| WARMUP_EVALUATION | Confidence ≥ 0.9 | 2,867 | 278 | 40.1428% | 9.6965% | 59.8572% |
| WARMUP_EVALUATION | Review all | 0 | 0 | 0.0000% | undefined | 100.0000% |

## Development full-pool results

Warm-up calibration and warm-up evaluation each contain 7,142 rows. Each full-pool row is one run, not 100 independent replications. The 2.5% development controller passes here but returns review-all in final calibration; development success is not a replacement for final evidence.

| Budget | Development threshold | Calibration selected / errors | Warm-up accepted / errors | Evaluation automation | Selected error |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2.5000% | 0.021523669158594383 | 355 / 3 | 350 / 1 | 4.9006% | 0.2857% |
| 5.0000% | 0.0295229992319207 | 680 / 13 | 642 / 11 | 8.9891% | 1.7134% |
| 10.0000% | 0.08568221332232251 | 2,596 / 225 | 2,568 / 218 | 35.9563% | 8.4891% |
| 15.0000% | 0.1656113623980724 | 3,964 / 511 | 3,896 / 512 | 54.5505% | 13.1417% |

## Reference composition and class slices

| Reference class | Warm-up evaluation (n=7,142) | Final calibration (n=7,143) | Locked TEST (n=12,284) |
| --- | ---: | ---: | ---: |
| negative | 1,142 (15.9899%) | 1,118 (15.6517%) | 3,972 (32.3347%) |
| neutral | 3,180 (44.5253%) | 3,220 (45.0791%) | 5,937 (48.3312%) |
| positive | 2,820 (39.4847%) | 2,805 (39.2692%) | 2,375 (19.3341%) |

Class proportions differ across the source roles and official TEST. These marginals do not establish pure label shift or explain the difference causally. Predicted-class automation uses the predicted-class population; reference-class review uses the human-reference population. Neither is a class-specific guarantee.

| Role | Budget | Predicted class | Total predictions | Accepted | Wrong | Within-class automation | Selected error |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| LOCKED_TEST | 2.5000% | negative | 4,128 | 0 | 0 | 0.0000% | undefined |
| LOCKED_TEST | 2.5000% | neutral | 5,245 | 0 | 0 | 0.0000% | undefined |
| LOCKED_TEST | 2.5000% | positive | 2,911 | 0 | 0 | 0.0000% | undefined |
| LOCKED_TEST | 5.0000% | negative | 4,128 | 253 | 10 | 6.1289% | 3.9526% |
| LOCKED_TEST | 5.0000% | neutral | 5,245 | 1 | 0 | 0.0191% | 0.0000% |
| LOCKED_TEST | 5.0000% | positive | 2,911 | 531 | 22 | 18.2412% | 4.1431% |
| LOCKED_TEST | 10.0000% | negative | 4,128 | 1,382 | 139 | 33.4787% | 10.0579% |
| LOCKED_TEST | 10.0000% | neutral | 5,245 | 672 | 65 | 12.8122% | 9.6726% |
| LOCKED_TEST | 10.0000% | positive | 2,911 | 987 | 97 | 33.9059% | 9.8278% |
| LOCKED_TEST | 15.0000% | negative | 4,128 | 2,228 | 359 | 53.9729% | 16.1131% |
| LOCKED_TEST | 15.0000% | neutral | 5,245 | 1,710 | 233 | 32.6025% | 13.6257% |
| LOCKED_TEST | 15.0000% | positive | 2,911 | 1,395 | 218 | 47.9217% | 15.6272% |
| WARMUP_EVALUATION | 2.5000% | negative | 1,157 | 0 | 0 | 0.0000% | undefined |
| WARMUP_EVALUATION | 2.5000% | neutral | 2,995 | 0 | 0 | 0.0000% | undefined |
| WARMUP_EVALUATION | 2.5000% | positive | 2,990 | 350 | 1 | 11.7057% | 0.2857% |
| WARMUP_EVALUATION | 5.0000% | negative | 1,157 | 42 | 1 | 3.6301% | 2.3810% |
| WARMUP_EVALUATION | 5.0000% | neutral | 2,995 | 2 | 0 | 0.0668% | 0.0000% |
| WARMUP_EVALUATION | 5.0000% | positive | 2,990 | 598 | 10 | 20.0000% | 1.6722% |
| WARMUP_EVALUATION | 10.0000% | negative | 1,157 | 447 | 67 | 38.6344% | 14.9888% |
| WARMUP_EVALUATION | 10.0000% | neutral | 2,995 | 749 | 72 | 25.0083% | 9.6128% |
| WARMUP_EVALUATION | 10.0000% | positive | 2,990 | 1,372 | 79 | 45.8863% | 5.7580% |
| WARMUP_EVALUATION | 15.0000% | negative | 1,157 | 656 | 127 | 56.6984% | 19.3598% |
| WARMUP_EVALUATION | 15.0000% | neutral | 2,995 | 1,403 | 199 | 46.8447% | 14.1839% |
| WARMUP_EVALUATION | 15.0000% | positive | 2,990 | 1,837 | 186 | 61.4381% | 10.1252% |

| Role | Budget | Reference class | Support | Accepted | Reviewed | Review fraction |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| LOCKED_TEST | 2.5000% | negative | 3,972 | 0 | 3,972 | 100.0000% |
| LOCKED_TEST | 2.5000% | neutral | 5,937 | 0 | 5,937 | 100.0000% |
| LOCKED_TEST | 2.5000% | positive | 2,375 | 0 | 2,375 | 100.0000% |
| LOCKED_TEST | 5.0000% | negative | 3,972 | 245 | 3,727 | 93.8318% |
| LOCKED_TEST | 5.0000% | neutral | 5,937 | 31 | 5,906 | 99.4779% |
| LOCKED_TEST | 5.0000% | positive | 2,375 | 509 | 1,866 | 78.5684% |
| LOCKED_TEST | 10.0000% | negative | 3,972 | 1,308 | 2,664 | 67.0695% |
| LOCKED_TEST | 10.0000% | neutral | 5,937 | 829 | 5,108 | 86.0367% |
| LOCKED_TEST | 10.0000% | positive | 2,375 | 904 | 1,471 | 61.9368% |
| LOCKED_TEST | 15.0000% | negative | 3,972 | 2,055 | 1,917 | 48.2628% |
| LOCKED_TEST | 15.0000% | neutral | 5,937 | 2,024 | 3,913 | 65.9087% |
| LOCKED_TEST | 15.0000% | positive | 2,375 | 1,254 | 1,121 | 47.2000% |
| WARMUP_EVALUATION | 2.5000% | negative | 1,142 | 0 | 1,142 | 100.0000% |
| WARMUP_EVALUATION | 2.5000% | neutral | 3,180 | 1 | 3,179 | 99.9686% |
| WARMUP_EVALUATION | 2.5000% | positive | 2,820 | 349 | 2,471 | 87.6241% |
| WARMUP_EVALUATION | 5.0000% | negative | 1,142 | 41 | 1,101 | 96.4098% |
| WARMUP_EVALUATION | 5.0000% | neutral | 3,180 | 13 | 3,167 | 99.5912% |
| WARMUP_EVALUATION | 5.0000% | positive | 2,820 | 588 | 2,232 | 79.1489% |
| WARMUP_EVALUATION | 10.0000% | negative | 1,142 | 417 | 725 | 63.4851% |
| WARMUP_EVALUATION | 10.0000% | neutral | 3,180 | 812 | 2,368 | 74.4654% |
| WARMUP_EVALUATION | 10.0000% | positive | 2,820 | 1,339 | 1,481 | 52.5177% |
| WARMUP_EVALUATION | 15.0000% | negative | 1,142 | 627 | 515 | 45.0963% |
| WARMUP_EVALUATION | 15.0000% | neutral | 3,180 | 1,490 | 1,690 | 53.1447% |
| WARMUP_EVALUATION | 15.0000% | positive | 2,820 | 1,779 | 1,041 | 36.9149% |

The 5% locked policy accepts only one predicted-neutral post; zero observed error in that slice is sparse evidence. Its predicted-positive acceptance is much larger. Pooled automation conceals this uneven usefulness.

## Calibration-label warm-up

Each budget has seven non-full sizes with 100 deterministic nested whole-component runs per size, plus one full-pool run. All requested sizes were realized exactly. Every run uses the same warm-up evaluation pool. Automation summaries include review-all; conditional-error summaries include only nonzero selections. Percentile ranges are descriptive, not confidence intervals or independent-replication evidence.

### Budget 2.5000%

| Labels | Runs | Certification | Median automation | Automation p05–p95 | Median nonzero selected error |
| --- | ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 100 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 200 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 500 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 1,000 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 2,000 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 4,000 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 7,142 (single full pool) | 1 | 100.0000% | 4.9006% | 4.9006%–4.9006% | 0.2857% |

### Budget 5.0000%

| Labels | Runs | Certification | Median automation | Automation p05–p95 | Median nonzero selected error |
| --- | ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 100 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 200 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 500 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 1,000 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 2,000 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 4,000 | 100 | 100.0000% | 8.9891% | 8.9891%–8.9891% | 1.7134% |
| 7,142 (single full pool) | 1 | 100.0000% | 8.9891% | 8.9891%–8.9891% | 1.7134% |

### Budget 10.0000%

| Labels | Runs | Certification | Median automation | Automation p05–p95 | Median nonzero selected error |
| --- | ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 100 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 200 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 500 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 1,000 | 100 | 5.0000% | 0.0000% | 0.0000%–0.4495% | 1.7134% |
| 2,000 | 100 | 98.0000% | 8.9891% | 8.9891%–8.9891% | 1.7134% |
| 4,000 | 100 | 100.0000% | 35.9563% | 26.7432%–35.9563% | 8.4891% |
| 7,142 (single full pool) | 1 | 100.0000% | 35.9563% | 35.9563%–35.9563% | 8.4891% |

### Budget 15.0000%

| Labels | Runs | Certification | Median automation | Automation p05–p95 | Median nonzero selected error |
| --- | ---: | ---: | ---: | ---: | ---: |
| 50 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 100 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 200 | 100 | 0.0000% | 0.0000% | 0.0000%–0.0000% | undefined |
| 500 | 100 | 1.0000% | 0.0000% | 0.0000%–0.0000% | 1.7134% |
| 1,000 | 100 | 73.0000% | 8.9891% | 0.0000%–8.9891% | 1.7134% |
| 2,000 | 100 | 100.0000% | 50.0070% | 8.9891%–54.5505% | 12.0220% |
| 4,000 | 100 | 100.0000% | 54.5505% | 45.4635%–54.5505% | 13.1417% |
| 7,142 (single full pool) | 1 | 100.0000% | 54.5505% | 54.5505%–54.5505% | 13.1417% |

| Budget | First certification | First ≥90% certification | First ≥90% certification and ≥10% median automation | ≥25% automation | ≥50% automation |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2.5000% | 7,142 | 7,142 | not reached | not reached | not reached |
| 5.0000% | 4,000 | 4,000 | not reached | not reached | not reached |
| 10.0000% | 1,000 | 2,000 | 4,000 | 4,000 | not reached |
| 15.0000% | 500 | 2,000 | 2,000 | 2,000 | 2,000 |

The last two columns also require ≥90% certification. The 2.5% first-certification milestone at 7,142 labels is a single full-pool observation. These label requirements describe the frozen study and do not establish universal sample complexity, staffing costs or monetary ROI. The JSON receipt preserves every historical quantile and milestone.

## Reproduction boundary

Final candidate tests are reconstructed from sufficient statistics. Warm-up winner diagnostics, counts, quantiles and milestones are checked, but complete historical warm-up prefixes and subset membership are unavailable. Source tweets, row labels/scores, identities, the identity key and model assets are excluded. This release does not reproduce training or inference, establish independent replication, or implement the separate Negative N1/N2 follow-up studies.

Evidence manifest SHA-256: `88a28b009c1c04ff295de35f493222558c429d4d9d7d91e3486f4f193666de0c`.
