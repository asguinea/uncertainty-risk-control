# HumAID extraction and evidence provenance

The research addition projects original aggregate evidence from the completed EyeTrustAI HumAID D1 source warm-up, D2 source final evaluation, and D3 event-year transfer/local-calibration series. Historical artifacts remain unchanged. The public source set includes no product runtime or private Git history.

[Study metadata](evidence/study.json) records source basenames and SHA-256 bindings. The [bundle manifest](evidence/manifest.json) binds six aggregate files and three projection/count/aggregation modules. Basenames and hashes identify correspondence; they are not publicly resolvable source downloads or independent attestations.

## Calibration counts

D2 already recorded full source traces. The export retains their five unique count rows and each budget's exact prefix, including the failure. All 12 source probability/CP values and decisions are checked against that historical trace.

D3 recorded the winning controller and four-test prefix length but omitted the individual test counts. The controlled local export verified the frozen score-corpus and final-label file hashes, joined exactly 3,075 target final-calibration rows (1,832 priority labels), and projected only the four recorded candidate counts with the public [count projection](../../src/uncertainty_risk_control/count_replay.py). It did not test a later candidate, choose a new prefix, regenerate scores or change a controller. The resulting winner, three passing tests and first failure match the historical summary. Target candidate diagnostic values are recomputed from those projected counts; they are not an original recorded trace.

Input hashes were checked again after export. Opaque identities remained local and were used only for the join. No raw tweet text, identity salt, model weight or row record entered the candidate. The internal source-location adapter and its detailed receipt remain outside this repository.

## Warm-up functions and counts

The two historical aggregation recipes have slightly different field names. Their `quantiles`/`q` and `aggregate` function bodies are preserved in [the extracted module](../../src/uncertainty_risk_control/humaid/_aggregate_reference.py), with the two aggregate names disambiguated. The [extraction record](../../provenance/humaid_source_extraction.json) binds each complete source file and each function-body AST. No original runner is imported or executed.

[Projection functions](../../src/uncertainty_risk_control/humaid/projection.py) use explicit field selection. Each public warm-up record contains only size/replicate, historical winner/stop statistics and aggregate evaluation counts. Source warm-up evaluation priority totals are recovered from the original event-prevalence aggregates, with exact integer recovery checked, then summed to 3,141; the target total of 1,778 is independently present in the zero-shot aggregate. Rates are checked against every original run before export. Public replay regenerates all historical quantiles and milestones and checks them against the frozen summaries.

This is aggregation equivalence and count replay. Winning statistics alone cannot reconstruct all historical warm-up candidate decisions or establish the membership of the reused subsets.

## Method and attribution

The HumAID historical selected-risk core is byte-identical to the published reference core, SHA-256 `5f74c71232a4a8ac938da792ea10f003b008f4bec3a1eede58d29a9cd3d88266`. The addition reuses the existing count API. GoEmotions scientific evidence, method files and figures are preserved.

See the [study citation](README.md#attribution-and-asset-boundary), [statistical references](../../docs/method.md#references), [RoBERTa paper](https://arxiv.org/abs/1907.11692), and [HumAID notices](../../THIRD_PARTY_NOTICES.md#humaid). Authorship and shared ownership are stated in the repository [contribution note](../../docs/contributions.md). Neither a personal GitHub account nor EyeTrustAI ownership grants rights to underlying dataset content.
