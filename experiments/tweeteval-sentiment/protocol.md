# Frozen TweetEval Sentiment protocol

## Action, loss and scorer

The action is automatic acceptance of a frozen classifier's argmax sentiment tag, with canonical class order negative / neutral / positive breaking probability ties. The binary loss is one when that tag differs from the released human reference. Selected risk is the wrong-tag fraction among accepted tags; automation is the accepted fraction of the evaluation population. Remaining tags require review.

The score is `risk = 1 - max(probabilities)`. Acceptance uses `risk <= threshold`, including ties. A review-all fallback selects nothing and has undefined conditional error. Confidence itself is not a calibrated guarantee that an individual tag is correct.

The historical scorer is `TWEETEVAL_BERTWEET_SENTIMENT_SCORER_V1`, based on `vinai/bertweet-base` revision `b349c1243407b0dcffeabb2337497477286e27ab`, with a three-class head. The canonical scorer was trained on 26,188 MODEL_DEVELOPMENT rows for three fixed epochs, maximum sequence length 64, seed 1729. Its frozen model hash is `04e7d79beaf30060b3d5911b9856df6b813a05f93d87c3ac3065532b09c0fe07`. The selected-risk score uses frozen inference outputs; this package does not rerun training or inference.

Historical input normalization uses released TweetEval text with the pinned BERTweet handle/URL/emoji and token-whitespace rules. Source identifiers and model bindings are retained in [study metadata](evidence/study.json); tokenizer assets and model weights are excluded.

## Populations and chronology

The authoritative source is the cleaned TweetEval sentiment release at Cardiff NLP revision `4fbd22cd78421f05b1ecdb4fc5725bc7a7bd8f66`. Official train (45,615) and validation (2,000) form the 47,615-row source pool. Official TEST (12,284) is a separate population. The historical normalized-text source/test intersection is empty, so these populations retain all their rows.

| Role | Rows | Use |
| --- | ---: | --- |
| MODEL_DEVELOPMENT | 26,188 | Fit scorer and fix candidates/order |
| WARMUP_CALIBRATION | 7,142 | Deterministic nested calibration-label experiments |
| WARMUP_EVALUATION | 7,142 | Fixed development evaluation pool reused by warm-up runs |
| FINAL_CALIBRATION | 7,143 | Independently calibrate the four declared budgets |
| LOCKED_TEST | 12,284 | Evaluate all frozen final policies on official TEST |

Source role assignment orders whole normalized-text components by an unsalted deterministic hash and cuts at nearest row-count boundaries. The source has 47,586 components, with up to three rows per component, and no component crosses source roles. Group-preserving splits reduce duplicate leakage; they do not make every row independent.

D1 fixes the scorer, development candidate family/order and budget grid before final calibration. D2 writes and verifies all four controllers before opening official TEST labels. D2 performs no post-locked adaptation. Those are historical freeze assertions, not a public preregistration. Later Negative N1/N2 work reused the benchmark in a different evidence sequence; it is not included here or relabeled as a new pristine test.

## Fixed sequence

The 20 target development fractions are 0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.975 and 0.99. Nearest-rank empirical quantiles use `sorted_score[ceil(fraction*N)-1]`; equal thresholds are deduplicated. The review-all boundary is separate from the 20 tested candidates.

Candidates are ordered by development one-sided 95% Clopper–Pearson upper bound ascending, then development automation descending, then threshold ascending. Warm-up outcomes are not used to set the order. This order is not monotone in the threshold and differs from HumAID's empirical-error recipe. [Design evidence](evidence/design.json) preserves all development counts and the sequence.

For each candidate, compute `P[Binomial(selected, alpha) <= harmful]`. A nonempty candidate passes if this probability is at most delta 0.05. Stop at the first failure and choose the maximum selected count in the passing prefix, breaking equal-count ties by higher threshold. No passing candidate means review-all. The numerical engine and [count replay](../../src/uncertainty_risk_control/count_replay.py) are unchanged.

Budgets 0.025, 0.05, 0.10 and 0.15 have recorded prefixes of 1, 8, 12 and 14 tests, totaling 35. The public count union has 14 rows. The first failed 2.5% candidate selects 134 rows with one error; its counts are separate from the fallback controller's zero actions and undefined winner diagnostics.

## Claims and population shift

Each budget uses its own delta 0.05 statement under the fixed-sequence and Bernoulli sampling assumptions. There is no simultaneous four-budget, class-specific or per-item guarantee. Duplicate grouping, shared topics and correlated posts can affect independence; these aggregates do not prove the assumptions.

Source calibration and official TEST have different class proportions. Source calibration therefore must not be presented as establishing the same risk guarantee for a shifted TEST population or future live traffic. The observed 15% test selected error is 15.1884%; it is retained, without post-test threshold adjustment. A finite test proportion can fluctuate under matched sampling as well, so that excess alone does not establish why performance changed. Marginal class differences alone do not establish pure label shift or causal effects.

Predicted-class automation divides by all predictions of that class. Reference-class review divides by all human-reference rows of that class. At the 5% budget only one predicted-neutral test post is accepted; its zero observed error is sparse evidence. Fixed-candidate CP values are diagnostics, not an adaptive confidence band for selected policies.

## Warm-up summaries

Each budget uses requested sizes 50, 100, 200, 500, 1,000, 2,000 and 4,000 with 100 deterministic nested whole-component replicates, plus one full-pool run at 7,142. All requested sizes were realized exactly. The 701 records per budget total 2,804. The warm-up evaluation pool is reused across all runs and budgets.

Historical aggregation retains min/p05/median/p95/max; empty conditional summaries retain all five values as undefined. Automation includes review-all; selected error conditions on nonzero evaluation selection; threshold summaries include non-null winners. Percentiles are descriptive, not confidence intervals or independent replication. The 2.5% full-pool warm-up certification is one observation and does not override final review-all. Label milestones describe this frozen scorer/study, not universal sample complexity or monetary ROI.
