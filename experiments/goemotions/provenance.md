# Evidence and extraction provenance

The [manifest](evidence/manifest.json) binds seven public JSON evidence files and the public projection implementation. The repository's Git commit additionally binds the replay and reporting code, documentation, source metadata, and generated tables. Source-artifact hashes are provenance identifiers, not links to public assets or evidence of a public preregistration date.

| File | Projection |
| --- | --- |
| `study.json` | Study target, role counts, budgets, reference, recorded freeze assertions, and explicit reproduction scope |
| `design.json` | All 21 thresholds, requested quantiles, development counts/CP bounds, frozen order, and untested review-all boundary |
| `calibration.json` | 5,426-comment denominator and selected/unsupported counts for the first 14 sequence positions only |
| `evaluations.json` | Recorded locked and warm-up controller/baseline/consensus/predicted-emotion aggregates; sparse error counts remain missing |
| `warmup_runs.json` | 2,804 aggregate run records with requested/realized sizes, winner statistics and stop metadata, and evaluation counts |
| `expected.json` | Historical final controller expectations, locked rates/baselines, and warm-up summary/milestone expectations |
| `development_history.json` | D1 review-all, D1R unsuccessful exploratory refinement, and D1S low-automation evidence |

`harmful` is the generic engine's mistake-count field. In this study it means an accepted top tag unsupported by the agreed-label reference; it does not measure psychological or clinical harm. The public projections explicitly map the original `unsupported` field to `harmful`.

The controlled internal export checked source code and accepted artifact hashes before reading them, joined frozen final-calibration scores to their reference labels in memory, and projected only counts for the already executed candidate positions. It did not decode locked reference labels, access the identity key, rerun model scoring/training, or write to the source artifact directories. Each of the four final controllers matched the historical threshold, counts, probability/bound, and first-failure metadata exactly. The private adapter and original source-location map remain in the internal audit; the reusable [count projection](../../src/uncertainty_risk_control/count_replay.py) and [aggregate field projection](../../src/uncertainty_risk_control/goemotions/projection.py) are public.

Locked and warm-up aggregate evidence was projected from the already frozen records. Recomputed rates and warm-up summaries are compared with their recorded expectations. This verifies the published projection's arithmetic and method decisions; without the original row-level inputs a reader cannot independently authenticate the source model predictions or the correspondence of every aggregate to its original rows.

[Source extraction metadata](../../provenance/goemotions_source_extraction.json) identifies the original pure feature functions, aggregate formulas, and feature tests. Their function/test bodies are preserved, with module imports and headers adapted. The full private runners, path assumptions, protected-phase execution entry points, and opaque identity machinery are not exported.

[Upstream source metadata](configs/source_inputs.json) contains authoritative resource URLs, byte sizes and hashes. It does not contain the resources themselves. Dataset and model attribution and scope are described in [third-party notices](../../THIRD_PARTY_NOTICES.md). Private source hashes do not create a dependency on private Git history.
