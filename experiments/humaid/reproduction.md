# HumAID reproduction contract

**Available in this local v0.2.0 candidate:** final-calibration sufficient-statistics replay and aggregate regeneration for the completed D1/D2/D3 humanitarian-research sequence. The immutable v0.1.0 tag predates this addition.

```sh
uv sync --locked
uv run --locked uqrc humaid --evidence experiments/humaid/evidence --output results/humaid/replay.json --report results/humaid/tables.md
```

The command uses the base NumPy/SciPy environment. Evidence ships in the source distribution; code and CLI ship in the wheel. It needs no private checkout, external drive, credentials, source tweets, trained model or GPU.

Expected success: `status: PASS`, `final_candidate_tests: 16`, `warmup_records: 1202`. The regenerated Markdown must match [the tracked results](report/results.md), with platform line-ending normalization permitted. Controller thresholds, integer counts, stop indices and decisions must match exactly; numerical probabilities and historical aggregate summaries use absolute tolerance `1e-12`.

| Layer | What runs | What remains unavailable |
| --- | --- | --- |
| Final calibration | All 12 source and four target candidate tests, including first failures; winner and stopping-rule validation | Recomputing all original scores and source references from downloaded data |
| Evaluation | Rates from integer action/error/reference counts; baseline and event-partition checks | Row-level audits of predictions or reference labels |
| Warm-up | Winner probability/CP checks, count consistency, 601 + 601 records, original quantiles and milestones | Full candidate-prefix replay or reconstruction of historical subset membership |
| Model | Frozen identifiers and source provenance | Original training, checkpoint inference, tokenizer or fitted weights |

`PASS` establishes consistency of this bundle and its replay. It does not authenticate model predictions, establish historical timing independently, prove independence/exchangeability, or constitute independent replication. A changed manifest is a changed evidence bundle; hashes alone do not establish correctness.

The [installed-package verifier](../../scripts/verify_reproduction.py) runs HumAID from a freshly installed wheel against evidence extracted from the source archive, outside the checkout. It also preserves the GoEmotions and synthetic checks:

```sh
uv run --locked --group figures python scripts/verify_reproduction.py --output results/ci
```

HumAID historical role order and warm-up construction largely derive from canonical tweet identities, with opaque identities used for stored joins and some tie-breaking. Missing a secret alone does not inherently make every assignment unreconstructible. Complete public source-to-assignment reconstruction is nevertheless not implemented here, and no restricted input is distributed or acquired by this command.

The bundle permits reviewing thresholds, selected-risk tradeoffs, event heterogeneity and descriptive calibration-label requirements. It does not support a new claim about live drift, model adaptation, causal recalibration benefit, or EyeTrustAI product performance.

## Figures

The [figure guide](report/figures/README.md) provides SVG/PNG outputs, full captions and provenance. From the repository root, use `uv run --locked --group figures python scripts/plot_social_media_studies.py --output results/social-media`. This replays all public evidence before rendering, without fitting a scorer or recalibrating a policy.
