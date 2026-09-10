# TweetEval Sentiment reproduction contract

**Available in this local v0.2.0 candidate:** frozen D1/D2 final sufficient-statistics replay and aggregate regeneration. The immutable v0.1.0 tag predates this study addition.

```sh
uv sync --locked
uv run --locked uqrc tweeteval-sentiment --evidence experiments/tweeteval-sentiment/evidence --output results/tweeteval-sentiment/replay.json --report results/tweeteval-sentiment/tables.md
```

Expected outputs: `status: PASS`, `final_candidate_tests: 35`, `warmup_records: 2804`. The regenerated report matches [the tracked results](report/results.md), allowing platform line-ending normalization. Selected thresholds, states, integer counts, pass/fail decisions and stopping positions must match exactly. Probability and historical aggregation comparisons use absolute tolerance `1e-12`.

The wheel contains code and CLI; the source archive contains the aggregate evidence and reports. NumPy and SciPy suffice for replay, without Matplotlib, source tweets, row labels/scores, the original identity key, a model, GPU or private product checkout.

| Layer | Reproduced | Outside this addition |
| --- | --- | --- |
| Final calibration | 35 executed candidate tests from 14 sufficient-statistic rows, including every first failure and the review-all result | Recomputing source scores/labels from a newly acquired benchmark |
| Evaluation | Pooled, baseline, predicted-class and reference-class counts/rates, with partition and consistency checks | Row-level prediction/reference audits |
| Warm-up | 2,804 winner/stop summaries, winning p/CP diagnostics, original quantiles and milestones | All per-run candidate prefixes and original subset memberships |
| Scorer | Frozen model/source identifiers and provenance | Historical training, inference, weights and tokenizer assets |

`PASS` means the bundle and replay checks agree. It does not independently authenticate original model predictions, establish freeze timing, prove sampling assumptions or constitute independent replication. An edited manifest describes an edited bundle, not proof that a new result is correct.

The [package verifier](../../scripts/verify_reproduction.py) builds a wheel and source distribution, installs the wheel into a fresh unrelated environment, and exercises this study against the source archive's evidence. It retains the existing GoEmotions, HumAID and synthetic checks:

```sh
uv run --locked --group figures python scripts/verify_reproduction.py --output results/ci
```

The original source-role assignment uses unsalted normalized-text group ordering; sanity and warm-up orders depend on opaque group identities. Not every assignment is inherently unreconstructible merely because a secret exists. This release nevertheless provides no complete public source-to-assignment reconstruction or dataset acquisition utility.

The export used a hash-bound historical official-identity map, the existing local identity key, source-label offsets and frozen final scores to establish an exact join. That work remains internal; public replay consumes only aggregate counts. The key and source records are neither included nor required by the public command.

## Figures

The [figure guide](report/figures/README.md) provides SVG/PNG outputs, full captions and provenance. From the repository root, use `uv run --locked --group figures python scripts/plot_social_media_studies.py --output results/social-media`. This replays all public evidence before rendering, without fitting a scorer or recalibrating a policy.
