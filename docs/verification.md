# Verification and repository checks

The [Research checks workflow](../.github/workflows/research.yml) runs on pushes, pull requests, and manual dispatch. Its matrix targets Python 3.11.13 on Ubuntu 24.04, macOS 15, and Windows 2025. A successful run establishes only the checks recorded for that commit and those runner environments; it does not extend the benchmark's statistical assumptions or historical reproduction scope.

## What the workflow checks

Each platform builds a wheel and source archive, extracts the source archive into a temporary directory, and installs the wheel into a fresh environment. Imports must resolve to the installed wheel, outside the checkout. It then runs:

1. The complete unit suite and the synthetic walkthrough, with no Matplotlib installed in the base environment.
2. The numerical and stopping-rule verification, including all 150,000 seeded synthetic Monte Carlo trials.
3. The separate synthetic example and GoEmotions final-calibration replay, using the source archive's configurations and evidence.
4. Aggregate table regeneration, compared with the tracked report after normalizing platform line endings.
5. Figure regeneration after installing the optional plotting dependencies from a hash-locked requirements export. Numerical figure inputs must match exactly, excluding only recorded environment metadata. Image-byte identity is not required across platforms.

Controller states, counts, selected thresholds, and first-failure positions remain exact replay requirements. Probability comparisons retain the original documented tolerance. CI never relaxes pass/fail decisions or changes the frozen candidate sequence to accommodate a platform.

The [distribution check](../scripts/check_distribution.py) inspects tracked file boundaries, local Markdown links and anchors, and every reachable historical file version. A separate Linux job runs checksum-pinned Gitleaks with its default rules over complete reachable history, with redacted output and no custom finding exclusions. Workflow actions are pinned to full commit hashes, use read-only repository permissions, and do not persist checkout credentials.

## Run the checks locally

From a full Git checkout:

```sh
uv run --locked python scripts/check_distribution.py --history --output results/distribution.json
uv run --locked --group figures python scripts/verify_reproduction.py --output results/ci
```

The second command builds and installs packages in temporary environments, so it may need internet access or a populated package cache. It does not download the benchmark dataset or any model. Detailed command logs and build archives stay under the caller's ignored output directory. The summary receipt records platform, dependency versions, package hashes, executed checks, and reproduction scope without workstation paths.

On Windows, CI enables Python UTF-8 mode and the checkout's `.gitattributes` preserves LF bytes in tracked text. For the same local invocation in PowerShell, set `$env:PYTHONUTF8 = "1"` before running the commands. Generated Markdown can use native line endings; the text comparison normalizes them and separately records whether the raw bytes also match. Frozen source/evidence hashes are never normalized or weakened.

## Logs, artifacts, and release interpretation

The artifact upload is an explicit list: distribution and execution receipts, numerical verification, synthetic and GoEmotions replay JSON, tables, and generated figure files. Dependency-install logs, environment directories, raw source downloads, and built distribution archives are not uploaded as CI artifacts. The checked artifacts are retained for 14 days; a release should separately preserve its reviewed evidence and verification record.

Automated scans are useful checks, not a proof that no sensitive content exists. Before public release, inspect the full intended Git history, repository metadata, workflow logs and artifacts, citation/license scope, and the exact candidate. Any new domain, source-locator mapping, model asset, or raw-data distribution needs its own explicit scope. The current [reproduction contract](../experiments/goemotions/reproduction.md) still excludes historical retraining, checkpoint inference, and warm-up candidate-prefix reconstruction.
