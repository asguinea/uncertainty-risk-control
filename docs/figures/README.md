# Three-study map

[SVG](study_map.svg) · [PNG](study_map.png) · [Structured inputs and provenance](study_map_data.json)

The map introduces emotion tagging, crisis triage and sentiment classification. Each card identifies the action, human error reference and evaluation context. It is a navigation and reproduction-inventory figure, with no performance axis or pooled result. The 86 final candidate tests and 6,810 warm-up records are counts of replayed work, not counts of independent studies or statistical guarantees.

Run `uv run --locked --group figures python scripts/plot_social_media_studies.py --output results/social-media` from the repository root. The [generator](../../scripts/plot_social_media_studies.py) replays all three evidence bundles and checks each card's inventory. Its output mirrors the repository paths under the requested output directory. The JSON records the generator hash, environment and three evidence-manifest hashes.

The [research note](../social-media-research.md) gives the numerical context and links each study. Attribute the original analytical presentation to Alejandro Sanchez Guinea / EyeTrustAI and cite the underlying datasets and methods as applicable. See [license scope](../../LICENSE_SCOPE.md).
