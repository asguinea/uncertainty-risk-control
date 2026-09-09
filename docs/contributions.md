# Contributions and research context

**Alejandro Sanchez Guinea** maintains this personal research repository and owns **EyeTrustAI**, where the underlying validation work originated. The repository makes selected methods and benchmark evidence inspectable outside the product development environment.

## Contribution represented by this repository

The portfolio contribution is the research and engineering work around an existing statistical framework:

- Defining the selected-risk target, acceptance/review action, annotation reference, data roles, and comparison protocol.
- Implementing and verifying the exact-binomial fixed-sequence procedure, including first-failure stopping and review-all behavior.
- Investigating a development-only meta-risk scorer, separate risk budgets, calibration sample size, and performance across annotation agreement and predicted emotions.
- Preserving unsuccessful and low-utility development outcomes alongside the final findings.
- Preparing a traceable aggregate evidence bundle, executable calibration replay, and reproducible tables and figures with explicit limits.

The [method extraction record](provenance.md) and [study provenance](../experiments/goemotions/provenance.md) identify the historical source material and subsequent adaptations. The presentation layer uses those projected aggregates; it adds no model fit, benchmark evaluation, or calibration search.

## Prior work and attribution

Exact binomial inference, Clopper–Pearson bounds, and Learn then Test are prior statistical methods. Google Research created GoEmotions, and the RoBERTa authors supplied the base-model research. This repository claims no invention of those methods, dataset, or architecture. Original notices and source attribution remain in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) and the protocol's references.

The investigation is not presented as peer reviewed, publicly preregistered, independently replicated, or externally mathematically audited. Replaying projected sufficient statistics is a specific reproducibility contribution, with a narrower scope than independently rebuilding the original predictions.

## Relationship to a future EyeTrustAI repository

This personal repository concentrates on uncertainty scores, selective prediction, statistical assumptions, and benchmark observations. A planned EyeTrustAI companion repository will document correspondence to particular product versions, implementation requirements, and workflow validation.

The companion should cite an immutable release and its evidence identifiers here, explain any shared inputs, and separately identify any additional tests. Shared ownership and origin should be disclosed in both places. Reusing these benchmark results does not create an independent replication. No companion repository is represented as existing in this snapshot.

The scope of the [license](../LICENSE_SCOPE.md) is the selected material included here. Maintaining it in a personal account does not transfer authorship or extend its license to the EyeTrustAI product.
