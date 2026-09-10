# TweetEval Sentiment provenance

This addition projects original aggregate research evidence from EyeTrustAI's completed TweetEval Sentiment D1/D2 sequence. It retains the development/full-pool evidence, four final budgets and official test observations, including negative and sparse results. Original study artifacts and the earlier GoEmotions/HumAID scientific files remain unchanged.

[Study metadata](evidence/study.json) binds source basenames and SHA-256 values. [The manifest](evidence/manifest.json) hashes the six aggregate evidence files and projection/count/aggregation modules. Source basenames and hashes establish correspondence; they are not public downloads or independent attestations of historical timing.

## Controlled final count projection

The historical D2 summaries record the final winners and prefix lengths (1, 8, 12, 14), but not complete candidate-count traces. The internal export verified the historical D0/D1/D2 bindings, frozen role manifest, official-identity map, source label files and final score file against recorded hashes.

The official-identity map already contains the released-text hash, source split and original row index. The export reconstructed identities from that map and the existing local key, selecting exactly 7,143 FINAL_CALIBRATION rows. It decoded only the corresponding train/validation label offsets, yielding 1,118 negative, 3,220 neutral and 2,805 positive references. No raw tweet text or official TEST label file was opened, and no replacement identity key was created. Complete train/validation label-file bytes were read for hashing; only final-calibration entries were decoded as references.

Those labels were joined to the frozen score file; errors are predicted class unequal to reference class. The public [count projection](../../src/uncertainty_risk_control/count_replay.py) produced only the union of 14 historically executed candidates. All 35 replayed tests, final winners and stops match the original numerical adapter and controller summaries. The 2.5% first failed candidate has 134 selections and one error; the review-all result has zero actions and undefined winner diagnostics. New candidate diagnostics are computed from frozen count evidence, not represented as an original recorded trace.

The existing key remained unchanged and was not exported or fingerprinted in public metadata. Input hashes were checked again after export. No new scoring, training, threshold choice, experiment or post-test adaptation was performed.

## Preserved aggregation and numerical parity

The original `q` and `milestone` function bodies and the aggregation loop inside the historical runner's `main` are retained in [the pure aggregation module](../../src/uncertainty_risk_control/tweeteval_sentiment/_aggregate_reference.py). A small wrapper supplies the original budget/tier constants, accepts already projected runs and returns summaries. AST formatting changes source layout; the function bodies and aggregation-loop AST hashes are preserved in [the extraction record](../../provenance/tweeteval_sentiment_extraction.json). The original runner and private imports are excluded.

The original TweetEval adapter implements the same exact-binomial / first-failure / maximum-passing-selection method as the existing public core. Four pure numerical function bodies were loaded internally for parity checks across all 35 final tests, limited to each recorded prefix. They are not shipped as a second calibration engine. Public replay reuses the existing core and count API.

[Projection functions](../../src/uncertainty_risk_control/tweeteval_sentiment/projection.py) explicitly select aggregate fields. Counts and reconstructed rates, winning p/CP values, full-pool results and all 2,804 records regenerate the original quantiles and milestone trees within `1e-12`. This does not recover complete historical warm-up candidate traces or subset membership.

## Scope and attribution

Dataset, model and scholarly attribution are in the [study entry point](README.md#attribution-and-relationship) and [third-party notices](../../THIRD_PARTY_NOTICES.md#tweeteval-sentiment-and-bertweet). Publication includes original code, aggregate counts and analytical output. Source tweets, tweet/row identities, per-row scores/labels, the identity key, models and product runtime remain excluded.

Alejandro Sanchez Guinea maintains the personal research repository and owns EyeTrustAI, where the work originated. Shared evidence must not be described as independent replication across the two portfolios. The study does not establish product readiness, live shift control or causal recalibration benefits. The later Negative N1/N2 series retains its separate chronology and publication scope.
