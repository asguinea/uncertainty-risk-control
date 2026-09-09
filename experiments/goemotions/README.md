# From confidence scores to risk-controlled emotion tagging

This study asks how separate 5%, 10%, 15%, and 20% selected-risk budgets change the automation/review trade-off for one frozen emotion classifier and one frozen error-risk scorer. It also investigates calibration sample size and heterogeneity across annotation agreement and predicted emotions.

**Implemented scope:** replay the historical final-calibration tests from sufficient statistics and regenerate aggregate tables from recorded counts. Model training, checkpoint inference, and historical sampling-order reconstruction are not included. See [reproduction scope](reproduction.md) for the precise boundary.

## Main result

The four final controllers passed their separate calibration procedures. On 10,853 locked comments:

| Risk budget | Automatically accepted | Unsupported tags | Automation | Observed selected error |
| --- | --- | --- | --- | --- |
| 5% | 419 | 10 | 3.8607% | 2.3866% |
| 10% | 530 | 16 | 4.8834% | 3.0189% |
| 15% | 2,931 | 414 | 27.0064% | 14.1249% |
| 20% | 3,892 | 683 | 35.8611% | 17.5488% |

Strict budgets produced very little automation. Accepting all top tags produced 4,245 unsupported tags, or 39.1136% error. Raw-confidence filters at 0.5, 0.8, and 0.9 provide descriptive baselines; they do not carry a formal risk guarantee. Review-all has undefined conditional error, not useful perfect accuracy. All exact counts, first failures, baselines, warm-up summaries, and subgroup tables are in the [regenerated results](report/results.md).

![Locked automation and observed selected error, including strict-budget detail and descriptive baselines.](report/figures/risk_automation.svg)

*Observed rates on the study's locked role, not risk bounds. Each budget uses delta 0.05 separately; no joint or subgroup guarantee. [Complete caption and numerical inputs](report/figures/README.md#locked-risk-and-automation).*

## Calibration size and remaining review work

![Passing frequency and median warm-up automation versus requested calibration size.](report/figures/calibration_size.svg)

*100 recorded whole-group samples per budget and requested tier. Bands are empirical 5th–95th percentiles, including review-all as zero automation; they are not confidence intervals. Realized sizes can be smaller than requested. Runs share development data and sample orders across budgets and tiers. The single full-pool run is retained in the tables. [Complete caption](report/figures/README.md#calibration-sample-size).*

At the 5% budget, the 2,000-comment tier has 32 passing runs out of 100; at 4,000, all 100 pass, but median automation is only 4.1836%. The [research note](../../docs/research-note.md) develops this finding alongside the locked trade-off, annotation-consensus differences, and unsuccessful development steps. The [figure guide](report/figures/README.md#regenerate) provides the plotting command and downloadable SVG/PNG assets.

## Run it

From the repository root, after `uv sync --locked`:

```sh
uv run --locked uqrc goemotions \
  --evidence experiments/goemotions/evidence \
  --output results/goemotions/replay.json \
  --report results/goemotions/tables.md
```

This command requires no dataset download, GPU, checkpoint, credentials, private commit, or original workstation. It verifies the bundle hashes, checks the development-only candidate ordering, replays each final-calibration prefix through its first failure, compares the controllers with the historical expectations, and regenerates rates, warm-up quantiles, and milestones. A changed count, missing failure, reordered candidate, inconsistent slice, or missing warm-up replicate causes failure.

## Target and protocol

[GoEmotions](https://aclanthology.org/2020.acl-main.372/) contains English Reddit comments annotated for 27 emotions plus neutral. This experiment defines a comment's reference as **all labels supported by at least two recorded raters**. The accepted top tag is unsupported if it is absent from that set. This is agreement with an annotation reference, not psychological truth.

The frozen [RoBERTa](https://arxiv.org/abs/1907.11692) classifier has 28 independent sigmoid outputs. A development-only logistic model transforms 97 probability-derived features into an estimated top-tag error risk. The action accepts the classifier's top tag when that score is at most the selected threshold; it never changes the predicted label.

The experiment uses its own group-preserving roles: 27,131 model-development comments; 5,427 warm-up calibration; 5,426 warm-up evaluation; 5,426 final calibration; and 10,853 locked evaluation. The official train/dev/test splits are reconciliation references, not these role definitions. In particular, the locked role is not the official GoEmotions test set.

The method is the [exact-binomial fixed-sequence LTT implementation](../../docs/method.md), with the original 21-candidate sequence. Its design uses an 8,139-comment development subset. Each budget uses delta 0.05 separately. There is no simultaneous four-budget 95% claim, per-emotion guarantee, or per-consensus-stratum guarantee. The locked rates are descriptive observations; the formal statement concerns sampling over calibration under the method's assumptions.

## Development history and limits

The original confidence-derived score (D1) returned review-all on the full warm-up pool. Exploratory candidate/order refinement (D1R) remained unsupported. A logistic meta-risk adapter (D1S) obtained a passing 5% controller but only 4.1836% automation on warm-up evaluation. MB1 retained that scorer and sequence and evaluated separate final-calibration and locked roles. These earlier results are development evidence, not independent replications of MB1. Separate batch-selective and compact-emotion-set explorations use different risk contracts and are outside this executable study.

Grouping links comments sharing a submission identity or exact normalized text. It reduces obvious cross-role leakage but does not establish independent Bernoulli observations. Annotation disagreement, dependence, benchmark selection, the English Reddit population, and development reuse limit interpretation. Sparse predicted-emotion slices retain the original reporting floor rather than displaying unsupported precision.

This research was developed in connection with EyeTrustAI, owned by the maintainer. It supports investigation of statistical methods and benchmark trade-offs. It does not establish product readiness or external validation. [Protocol details](protocol.md), [provenance](provenance.md), and [reproduction limits](reproduction.md) accompany the executable evidence.
