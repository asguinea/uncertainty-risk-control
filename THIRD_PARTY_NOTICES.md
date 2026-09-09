# Third-party notices

The runtime installs NumPy and SciPy from their upstream packages; their source is not vendored in this repository. Both use BSD-style licensing and include further bundled-component notices in their distributions. Keep the license files provided with the exact installed wheels when redistributing those dependencies.

| Dependency | Role | Upstream |
| --- | --- | --- |
| NumPy 2.4.6 | Numerical arrays and synthetic random sampling | [NumPy](https://numpy.org/) |
| SciPy 1.17.1 | Binomial probabilities and beta quantiles | [SciPy](https://scipy.org/) |
| Hatchling 1.27.0 | Isolated build backend; not a runtime import | [Hatch](https://hatch.pypa.io/) |

The selected-risk source and synthetic fixtures were developed within the EyeTrustAI research program; their extraction and modifications are described in [provenance](docs/provenance.md). The underlying statistical work is credited in [method references](docs/method.md#references). No code from the cited papers is copied here.

## GoEmotions and RoBERTa

The GoEmotions MB1 study uses the dataset described by Demszky et al. (2020), [GoEmotions: A Dataset of Fine-Grained Emotions](https://aclanthology.org/2020.acl-main.372/), DOI `10.18653/v1/2020.acl-main.372`. Source metadata is pinned to Google Research revision `041338718b4e8151372fd63677104c65b73a0a4e`; the repository's [upstream Apache-2.0 license](https://raw.githubusercontent.com/google-research/google-research/041338718b4e8151372fd63677104c65b73a0a4e/LICENSE) applies to its governed upstream material. This is not a blanket grant over underlying Reddit content.

The classifier derives from Liu et al. (2019), [RoBERTa: A Robustly Optimized BERT Pretraining Approach](https://arxiv.org/abs/1907.11692), with the base revision recorded in the study protocol. The historical model metadata reports MIT, but no classifier, tokenizer, base weights, or fitted meta-model is redistributed by this snapshot. A future model-asset release needs its own included notices and scope.

This repository includes original aggregate projections, their sufficient-statistics replay, and new derived tables. Raw comments, rater judgments/identities, row-level scores, source assignment maps, model weights, paper PDFs, and model-card PDFs are excluded. The optional acquisition utility retrieves nine byte-pinned upstream resources into a caller-owned directory, including the original README and license; those downloads are not part of this repository's distribution.
