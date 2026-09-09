# What can be reproduced

| Workflow | Available now | Inputs and limits |
| --- | --- | --- |
| Final-calibration method replay | Yes | Frozen 21-candidate sequence and counts for each executed prefix, including first failures; exact controller/count/threshold correspondence and `1e-12` probability tolerance |
| Aggregate report regeneration | Yes | Locked/warm-up baseline and subgroup counts; all 2,804 warm-up aggregate records; original quantile and milestone formulas |
| Upstream source acquisition/verification | Yes, as a separate utility | Nine official resources with frozen byte sizes and hashes; no downstream reference/role/model reconstruction is implied |
| Historical warm-up sampling and every candidate test | No | Group orders and per-run candidate-prefix statistics are not distributed; winner statistics are checked, and aggregate summaries are regenerated |
| Checkpoint-assisted model inference | No | Fine-tuned classifier and meta-model assets are not included, and a public source-to-historical-record mapping has not been released |
| Complete historical retraining | No | Original training order, OOF assignment, meta-split and warm-up order depend on private opaque identities; public inputs do not currently specify those assignments |

## Replay and regenerate

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked uqrc goemotions \
  --evidence experiments/goemotions/evidence \
  --output results/goemotions/replay.json \
  --report results/goemotions/tables.md
```

The command verifies file and projection-code hashes, then recomputes 35 tests across the four controller prefixes. It does not evaluate later candidates after a failure. Controller states, thresholds, integer counts, selected candidates, and stopping decisions must match exactly; a comparison tolerance applies only to probabilities and derived rates, never to test decisions.

The JSON receipt reports the executed scope and identifies the input manifest hash, reference-core hash, Python and dependency versions. `status: PASS` refers to this verification and arithmetic. It does not authenticate the original predictions or establish the dataset's statistical assumptions. No original private repository or mounted volume is required. The method and aggregate tables run on CPU in the base environment.

## Obtain upstream data separately

Use a caller-owned directory, normally the Git-ignored `data/` directory:

```sh
uv run --locked uqrc goemotions-sources \
  --inputs experiments/goemotions/configs/source_inputs.json \
  --directory data/goemotions/source \
  --download \
  --output results/goemotions/source-verification.json
```

Omit `--download` to verify files already present. A mismatching existing file is rejected rather than overwritten; a download is installed only after its expected size and SHA-256 pass. URLs for repository files are pinned to the original Google Research commit. Google-hosted raw CSV URLs are byte-pinned by their recorded hashes. The manifest includes the upstream README and license; PDFs and model weights are not downloaded by this utility.

Acquisition requires internet access. Source files remain local and are not added to this repository. The source utility verifies bytes only: it does not reconstruct the reference, allocate roles, create identities, score a model, or claim a new experimental result. The regression tests use synthetic download bytes, and the recorded source-verification check used the existing official local files. A fresh download of all raw files was not rerun for this batch.

## Why historical end-to-end reproduction is unavailable

The D0 primary role assignment uses unsalted source identifiers and can be reconstructed in principle. Later steps depend on HMAC-derived identities: D1 input ordering and sanity split; D1S out-of-fold assignment, meta-train/design split, and training order; and warm-up group ordering. A new identity key changes those assignments or orders. The original seed alone is therefore insufficient, and replacing the key would define a different experiment.

A possible future exact route would release a narrowly scoped source-locator-to-assignment/order mapping, together with portable training/preprocessing code and a verified numerical comparison. A checkpoint route would additionally need approved classifier/tokenizer/meta-model assets, asset-specific notices, source mapping, and an inference comparison. Neither route is offered as completed here. An independent publicly seeded replication would need a separately versioned protocol and results; it must not silently replace the historical MB1 evidence.

This snapshot makes the supported reproducibility claims concrete and executable while retaining that limit. All original frozen inputs remain unchanged. The public bundle contains no secret identity key, comment-level IDs, source-linked assignments, row-level scores/labels, raw text, or trained weights.
