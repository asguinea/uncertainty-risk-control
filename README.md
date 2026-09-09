# Uncertainty and risk control

Research on selective prediction: deciding when to accept a model output and when to send it for review, using a statistical bound on the error among accepted outputs.

**Status: local research snapshot, version `0.1.0.dev0`.** This repository contains an exact-binomial fixed-sequence method, synthetic verification, and [GoEmotions MB1](experiments/goemotions/README.md): executable replay of frozen final-calibration evidence and regeneration of benchmark aggregate tables. Historical model retraining and checkpoint inference are not included; the [reproduction scope](experiments/goemotions/reproduction.md) explains why. Synthetic illustrations remain separate from benchmark evidence.

## Run the foundation

The reference environment uses Python 3.11.13, NumPy 2.4.6, and SciPy 1.17.1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the repository root:

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
uv run --locked uqrc verify --output results/method-verification.json
uv run --locked uqrc synthetic --config experiments/synthetic/config.toml --output results/synthetic.json
uv run --locked uqrc goemotions --evidence experiments/goemotions/evidence --output results/goemotions/replay.json --report results/goemotions/tables.md
```

Verification includes numerical fixtures and five synthetic Monte Carlo scenarios, with 30,000 trials each. It requires no dataset, trained model, GPU, product checkout, or credentials. The synthetic illustration uses separate development and calibration draws, records the frozen candidate order, and writes aggregate results. Output paths are supplied by the caller; generated results are ignored by Git.

## Use the method

```python
from uncertainty_risk_control import calibrate_fixed_sequence

# Illustration only: fix this sequence independently of calibration data.
sequence = [{"threshold": 0.1}, {"threshold": 0.2}]
result = calibrate_fixed_sequence(
    sequence,
    scores=[0.1] * 59,
    outcomes=[0] * 59,  # 1 means a mistake; 0 means no mistake
    alpha=0.05,
    delta=0.05,
)
print(result.state, result.threshold, result.selected)
# CERTIFIED 0.2 59
```

Lower scores mean lower estimated risk. A candidate accepts `score <= threshold`, including ties. Tests run in the supplied order and stop at the first failure. The method returns `REVIEW_ALL` if no candidate passes. Zero accepted observations have undefined conditional error.

`CERTIFIED` is a method outcome under the sampling and protocol assumptions; it is not a certification of a product. Read the [method and assumptions](docs/method.md), [reproduction instructions](docs/reproduction.md), and [extraction provenance](docs/provenance.md) before interpreting results.

## Research context and attribution

Maintainer: Alejandro Sanchez Guinea. This research was developed in connection with EyeTrustAI, which the maintainer owns. This repository presents research methods and benchmark experiments. A planned companion EyeTrustAI repository will describe their relationship to specific product implementations and validation requirements; it will cite research releases rather than present the same study as an independent replication.

The contribution here is the implementation, protocol, verification, and experimental investigation. Exact binomial inference and [Learn then Test](https://arxiv.org/abs/2110.01052) are existing statistical methods. See [CITATION.cff](CITATION.cff) for this software's citation metadata and [method references](docs/method.md#references) for the underlying work.

Original material is provided under [Apache-2.0](LICENSE), subject to [license scope](LICENSE_SCOPE.md) and [third-party notices](THIRD_PARTY_NOTICES.md). This snapshot distributes projected aggregate evidence, not raw comments, row-level datasets, or model weights. It does not license underlying social-media content.
