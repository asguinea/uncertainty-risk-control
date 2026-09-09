# Portfolio and article copy

These are reusable drafts for a personal portfolio, EyeTrustAI research page, or an article introduction. They describe the implemented evidence-replay scope. Before publishing an article, link the exact reviewed repository release and replace the development-version citation with that release's metadata.

## Portfolio card

**Uncertainty and risk control**

Research on when a model should answer and when it should ask for review. The first study examines emotion tagging, calibration sample size, and the automation–error trade-off. Includes an exact-binomial method, executable replay of frozen calibration evidence, and reproducible aggregate figures. Developed in connection with EyeTrustAI, which I own.

## Suggested article title and introduction

**A calibrated model can still leave almost everything for review**

How much work can we automate when we place a statistical constraint on the mistakes among accepted predictions? I investigated this question using a frozen emotion classifier and four selected-risk budgets on GoEmotions. At the 5% and 10% budgets, fewer than 5% of locked comments were accepted. Larger calibration samples made passing policies more available, but did not necessarily make strict policies useful. The accompanying research repository lets readers replay the executed final-calibration tests and regenerate aggregate tables and figures. It also documents the unsuccessful development steps, annotation disagreement, sampling assumptions, and the parts of historical model reproduction that remain unavailable.

This work originated in EyeTrustAI's development validation program. I own EyeTrustAI; the personal repository focuses on the methods and benchmark investigation.

## EyeTrustAI research-page description

EyeTrustAI's development validation work informed this study of statistical risk control for emotion tagging. Alejandro Sanchez Guinea, EyeTrustAI's owner, maintains the research repository. It provides frozen-evidence calibration replay and aggregate benchmark reports. A future product-validation repository will document correspondence to specific EyeTrustAI implementations and cite the same research release. The benchmark itself does not establish product readiness or constitute independent external validation.

## Figures and captions to reuse

Use [risk and automation](../experiments/goemotions/report/figures/risk_automation.png) for the main result and [calibration sample size](../experiments/goemotions/report/figures/calibration_size.png) for the sample-size discussion. SVG versions are available in the same directory. Preserve the [full captions](../experiments/goemotions/report/figures/README.md), attribution, and reference definition when embedding or cropping them. The numerical inputs and generator travel with the repository.

## Claims to keep precise

| Topic | Wording supported by this snapshot |
| --- | --- |
| Reproducibility | “Replays frozen final-calibration evidence and regenerates aggregate reports.” |
| Confidence | “Each risk budget uses delta 0.05 separately, under the stated assumptions.” |
| Observed performance | “The 5% policy accepted 419 of 10,853 locked comments; 10 accepted tags were unsupported by the annotation reference.” |
| Sample size | “At the 5% budget and requested n = 4,000, all 100 recorded warm-up runs passed; median automation was 4.18%.” |
| Contribution | “Protocol, implementation, verification, and empirical investigation using existing statistical methods.” |
| Relationship | “Developed in connection with EyeTrustAI, owned by the maintainer.” |

Full retraining, a simultaneous four-budget guarantee, psychological ground truth, and product readiness are not established. Use the [research note](research-note.md) for the full argument, [contributions](contributions.md) for attribution, and [reproduction contract](../experiments/goemotions/reproduction.md) for executable scope.
