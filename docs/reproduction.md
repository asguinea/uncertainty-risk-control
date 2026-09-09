# Reproducing this foundation

The generic commands verify the method and run a synthetic illustration. The separate `goemotions` command replays frozen benchmark evidence and regenerates aggregate tables. See the [GoEmotions reproduction contract](../experiments/goemotions/reproduction.md) for that command's scope and limitations.

## Environment and commands

Use the root `.python-version` (3.11.13) and `uv.lock`. NumPy and SciPy are pinned to the original method environment; the build backend is also pinned. The lock uses public PyPI URLs and hashes. An initial installation needs internet access or a populated package cache; the installed commands themselves need no network. The package declares Python 3.11 or newer, while the acceptance environment is Python 3.11.13 on macOS arm64. Other environments need their own verification.

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked uqrc verify --output results/method-verification.json
uv run --locked uqrc synthetic --config experiments/synthetic/config.toml --output results/synthetic.json
uv build
```

The verification command performs the original numerical geometry and bounded recurrence comparisons, strengthened stopping/tie fixtures, and five seeded Monte Carlo scenarios. The original simulation design uses 30,000 draws of 400 calibration observations per scenario, at `alpha = delta = 0.05`, with a pre-existing acceptance tolerance of 0.055 for the empirical false-certification frequency. Its vectorized simulation checks the fixed-sequence logic under synthetic populations; direct unit fixtures exercise the public calibration function. The simulations are neither a proof of the bound nor evidence of independence in a real dataset.

For a quick deterministic CLI check, add `--skip-monte-carlo`; the receipt explicitly records the skipped portion. The unit suite additionally checks direct Decimal probability sums at 5%, 10%, 15%, and 20%, source integrity, valid-input equivalence, malformed-input rejection, and unchanged candidate design across calibration calls.

The synthetic TOML schema contains exactly `schema_version`, `seed`, `development_n`, `calibration_n`, `alpha`, and `delta`. Its frozen population has a uniform risk score and mistake probability `0.005 + 0.12 * score**2`. Independent random streams generate the two roles. Repeating the same config and environment reproduces the result; changing the seed or population defines a different synthetic run. `status: PASS` means the command completed its checks, while `calibration.state` reports whether a policy passed or review-all was returned.

JSON outputs record method identifiers, source integrity, package/Python versions, seeds or config hashes, and the scope executed. Caller-provided output paths are resolved from the caller's working directory. No original workstation, mounted volume, private commit, or dataset identity is needed. Avoid reusing a result filename after a failed run; only a zero exit status indicates a successful new receipt.

## Independent wheel installation

Install the wheel built under `dist/` into a new virtual environment and run `uqrc verify` from another directory. This tests package resources and imports without an editable source checkout. The source archive also includes the synthetic config, tests, method documentation, and extraction manifest. The wheel includes the method, CLI, and frozen-core hash manifest; source-only tests/configs need the source archive.

## Benchmark reproduction

GoEmotions MB1 supports report regeneration from public counts and final-calibration replay from sufficient statistics, including first failures. It also provides an optional upstream byte-verification/acquisition utility. Historical training and sampling retain unresolved assignment/order dependencies on private identity generation; no source-data/model reproduction command is claimed. Publishing a new seed would define a new replication protocol, not exact historical reproduction.
