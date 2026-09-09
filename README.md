# Uncertainty and risk control

**When should a model answer, and when should it ask for review?** This repository studies selective prediction: using uncertainty scores and statistical calibration to control errors among automatically accepted outputs, then measuring how much work can actually be automated.

The first study, [GoEmotions MB1](experiments/goemotions/README.md), turns a frozen emotion classifier's outputs into four acceptance/review policies. At the 5% and 10% risk budgets, fewer than 5% of locked comments are accepted. Higher budgets increase automation alongside the observed error rate. Passing calibration and obtaining useful automation are distinct outcomes.

![Locked automation and observed selected error for four risk budgets and descriptive baselines, including a detail panel showing less than 5% automation for the strict budgets.](experiments/goemotions/report/figures/risk_automation.svg)

*10,853 locked comments from the study's own group-preserving split. Each budget uses delta 0.05 separately; the points are observed rates, not bounds or a joint guarantee. “Error” means the top tag is absent from the agreed-label reference. [Counts, captions, and figure sources](experiments/goemotions/report/figures/README.md).*

## What you can inspect and run

| Component | What it establishes |
| --- | --- |
| [Exact-binomial method](docs/method.md) | Fixed-sequence calibration with explicit assumptions, first-failure stopping, and review-all behavior |
| [Synthetic walkthrough](examples/selected_risk_walkthrough.py) | A small example of passing, stopping, count replay, and insufficient evidence |
| [GoEmotions evidence replay](experiments/goemotions/reproduction.md) | Recomputes all 35 executed final-calibration tests across four budgets, including their first failures |
| [Tables and figures](experiments/goemotions/report/figures/README.md) | Regenerates locked observations and sample-size summaries from published aggregate evidence |
| [Research note](docs/research-note.md) | Explains calibration, annotation disagreement, development history, and the limits of the findings |

**Status: research snapshot, `0.1.0.dev0`; no public release yet.** The runnable benchmark scope is final-calibration replay and aggregate regeneration. Full historical training, checkpoint inference, and warm-up sampling/prefix reproduction are unavailable. The [reproduction contract](experiments/goemotions/reproduction.md) states the missing inputs. Synthetic examples are labeled separately from benchmark results.

## Quick start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from the repository root. The reference environment is Python 3.11.13 with locked dependencies.

```sh
uv sync --locked
uv run --locked python examples/selected_risk_walkthrough.py
uv run --locked uqrc goemotions --evidence experiments/goemotions/evidence --output results/goemotions/replay.json --report results/goemotions/tables.md
```

The replay requires no dataset download, trained weights, GPU, credentials, or product checkout. It produces a JSON verification receipt and the research tables. `status: PASS` means the replay checks passed; it does not authenticate the original model predictions or verify the dataset's sampling assumptions.

To regenerate the figures, install the optional plotting dependencies:

```sh
uv sync --locked --group figures
uv run --locked --group figures python experiments/goemotions/scripts/plot_results.py --evidence experiments/goemotions/evidence --output results/goemotions/figures
```

The plotting command replays the evidence before rendering two SVG/PNG figures and their exact numerical inputs. See the [reproduction guide](docs/reproduction.md) for method verification, synthetic simulations, packaging, and expected outputs.

## How to read the method

A frozen scorer gives lower values to outputs it estimates are less likely to be wrong. A threshold accepts `score <= threshold`, including ties. Calibration tests candidates in an independently fixed order, stops at the first failure, and chooses the largest accepted set within the passing prefix. If none passes, it returns `REVIEW_ALL`; conditional error is undefined when nothing is accepted.

The target is **error conditional on acceptance**, not the model's overall accuracy or the reliability of every individual probability. Under the stated sampling and protocol assumptions, each calibrated nonempty policy has a selected-risk guarantee at its own budget. `CERTIFIED` is the implementation's name for that method outcome. Read the [assumptions and exact statement](docs/method.md#assumptions-and-interpretation) before applying it elsewhere.

## Author, research context, and citation

Maintained by **Alejandro Sanchez Guinea**, owner of EyeTrustAI. This research originated in EyeTrustAI's validation work. The personal repository focuses on the experimental protocol, implementation, verification, and investigation of uncertainty and selective prediction. [Contribution and relationship details](docs/contributions.md) distinguish those contributions from the underlying statistical methods, dataset, and base model.

A planned EyeTrustAI companion repository will connect immutable research releases to specific product implementations and validation requirements. It will identify the shared evidence and ownership; it will not present the same benchmark as an independent replication. This benchmark alone does not establish product readiness.

Use [CITATION.cff](CITATION.cff) for the software's current metadata and cite the underlying [statistical methods](docs/method.md#references), [GoEmotions](https://aclanthology.org/2020.acl-main.372/), and [RoBERTa](https://arxiv.org/abs/1907.11692) as applicable. [Reusable portfolio copy](docs/portfolio.md) accompanies the research note.

Original material is under [Apache-2.0](LICENSE), subject to [license scope](LICENSE_SCOPE.md) and [third-party notices](THIRD_PARTY_NOTICES.md). The repository distributes projected aggregate evidence and derived figures. It includes no raw comments, row-level datasets, model weights, or product runtime.
