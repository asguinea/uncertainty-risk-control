# Reproducing the methods and study evidence

Start with the [small walkthrough](../examples/README.md) to inspect the stopping rule, or run `uqrc goemotions` to replay frozen benchmark evidence and regenerate aggregate tables. The optional figure script renders the study charts from verified aggregates. See the [GoEmotions reproduction contract](../experiments/goemotions/reproduction.md) for the distinction between these workflows and historical model reproduction.

## Environment and commands

Use the root `.python-version` (3.11.13) and `uv.lock`. NumPy and SciPy are pinned to the original method environment; the build backend is also pinned. The lock uses public PyPI URLs and hashes. An initial installation needs internet access or a populated package cache; the installed commands themselves need no network. The package declares Python 3.11 or newer, while the acceptance environment is Python 3.11.13 on macOS arm64. Other environments need their own verification.

```sh
uv sync --locked
uv run --locked python examples/selected_risk_walkthrough.py
uv run --locked python -m unittest discover -s tests -v
uv run --locked uqrc verify --output results/method-verification.json
uv run --locked uqrc synthetic --config experiments/synthetic/config.toml --output results/synthetic.json
uv build
```

The verification command performs the original numerical geometry and bounded recurrence comparisons, strengthened stopping/tie fixtures, and five seeded Monte Carlo scenarios. The original simulation design uses 30,000 draws of 400 calibration observations per scenario, at `alpha = delta = 0.05`, with a pre-existing acceptance tolerance of 0.055 for the empirical false-certification frequency. Its vectorized simulation checks the fixed-sequence logic under synthetic populations; direct unit fixtures exercise the public calibration function. The simulations are neither a proof of the bound nor evidence of independence in a real dataset.

For a quick deterministic CLI check, add `--skip-monte-carlo`; the receipt explicitly records the skipped portion. The unit suite additionally checks direct Decimal probability sums at 5%, 10%, 15%, and 20%, source integrity, valid-input equivalence, malformed-input rejection, and unchanged candidate design across calibration calls.

The synthetic TOML schema contains exactly `schema_version`, `seed`, `development_n`, `calibration_n`, `alpha`, and `delta`. Its frozen population has a uniform risk score and mistake probability `0.005 + 0.12 * score**2`. Independent random streams generate the two roles. Repeating the same config and environment reproduces the result; changing the seed or population defines a different synthetic run. `status: PASS` means the command completed its checks, while `calibration.state` reports whether a policy passed or review-all was returned.

JSON outputs record method identifiers, source integrity, package/Python versions, seeds or config hashes, and the scope executed. Caller-provided output paths are resolved from the caller's working directory. No original workstation, mounted volume, private commit, or dataset identity is needed. Avoid reusing a result filename after a failed run; only a zero exit status indicates a successful new receipt.

## Study tables and figures

```sh
uv run --locked uqrc goemotions \
  --evidence experiments/goemotions/evidence \
  --output results/goemotions/replay.json \
  --report results/goemotions/tables.md
uv sync --locked --group figures
uv run --locked --group figures python experiments/goemotions/scripts/plot_results.py \
  --evidence experiments/goemotions/evidence \
  --output results/goemotions/figures
```

The first command produces a JSON receipt and Markdown tables. The second workflow adds Matplotlib through the optional, locked `figures` group and produces two SVGs, two PNGs, and `plot_data.json`. It replays the evidence before plotting, so it does not trust an arbitrary saved result file. No dataset or model download is involved. The [figure guide](../experiments/goemotions/report/figures/README.md) explains every plotted quantity, omitted point, variability band, and caption.

Expected checks: the receipt reports 35 final candidate tests, 14 unique executed candidates out of the frozen 21, and 2,804 warm-up aggregate records. Its controller counts and stopping positions must agree exactly with the evidence expectations. The regenerated tables should match `experiments/goemotions/report/results.md` byte for byte in the locked environment. Figure numerical inputs retain full precision; displayed percentages are rounded. Image-byte agreement is only claimed for the checked local environment, not across platforms.

## Independent wheel installation

Install the wheel built under `dist/` into a new virtual environment and run `uqrc verify` from another directory. This tests package resources and imports without an editable source checkout. The source archive includes tests, examples, configs, evidence, the plotting script and figures, documentation, and extraction manifests. The wheel includes the method, CLI, GoEmotions replay/report modules, and hash resources; study evidence, examples, and the plotting workflow need the source archive or checkout. Matplotlib is not a base package dependency.

## Benchmark reproduction

GoEmotions MB1 supports report regeneration from public counts and final-calibration replay from sufficient statistics, including first failures. It also provides an optional upstream byte-verification/acquisition utility. Historical training and sampling retain unresolved assignment/order dependencies on private identity generation; no source-data/model reproduction command is claimed. Publishing a new seed would define a new replication protocol, not exact historical reproduction.
