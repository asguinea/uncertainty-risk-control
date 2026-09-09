# Third-party notices

The runtime installs NumPy and SciPy from their upstream packages; their source is not vendored in this repository. Both use BSD-style licensing and include further bundled-component notices in their distributions. Keep the license files provided with the exact installed wheels when redistributing those dependencies.

| Dependency | Role | Upstream |
| --- | --- | --- |
| NumPy 2.4.6 | Numerical arrays and synthetic random sampling | [NumPy](https://numpy.org/) |
| SciPy 1.17.1 | Binomial probabilities and beta quantiles | [SciPy](https://scipy.org/) |
| Hatchling 1.27.0 | Isolated build backend; not a runtime import | [Hatch](https://hatch.pypa.io/) |

The selected-risk source and synthetic fixtures were developed within the EyeTrustAI research program; their extraction and modifications are described in [provenance](docs/provenance.md). The underlying statistical work is credited in [method references](docs/method.md#references). No code from the cited papers is copied here.

The planned GoEmotions study will add its own dataset/model citations and asset-specific notices when that material is included. Mentioning a planned study does not distribute or relicense its assets.
