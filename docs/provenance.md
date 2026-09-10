# Extraction provenance

This repository starts with new local Git history. Its numerical method originated in the EyeTrustAI research validation program. Three allowlisted original files were used: the selected-risk engine, its unit fixtures, and its synthetic verification script. No product runtime code or private Git objects are required to execute this package.

[The extraction manifest](../provenance/extraction.json) records each source filename, its SHA-256, the destination, the extracted-file hash, and transformations. The source engine was copied without a byte change; the package also contains a hash manifest that both CLI commands verify at runtime. Original domain-specific method identifiers remain in this frozen reference for traceability. The public identifiers remove the domain prefix while retaining numerical version V1; they are aliases, not a newly invented method.

The verification script preserves its numerical, geometry, population, simulation-count, seed convention, and tolerance choices. Imports point to the public interface, its old filesystem CLI is replaced by the package CLI, and an actual equal-count tie fixture now supports a previously descriptive success flag. Original unit-test bodies are retained with imports and the introductory description adapted. New public-interface and protocol tests are separately identifiable.

The public wrapper deliberately tightens invalid-input behavior while preserving results on supported valid inputs. The original core's recurrence remains internal with its bounded numerical scope documented. Any future change to the core requires a new provenance record and equivalence review; updating a hash alone is not evidence of correctness.

These hashes establish integrity and extraction correspondence. They do not establish a public preregistration date, independent replication, external mathematical review, or the validity of dataset assumptions. Detailed internal source locations and private revision bindings remain in the internal extraction audit; they are not runtime dependencies or resolvable public citations.

The maintainer is Alejandro Sanchez Guinea. The historical numerical source has no copyright header or accompanying notice to remove; its original docstring and identifiers remain intact. Attribution to the EyeTrustAI research context is retained. Publication does not change authorship merely because the repository is maintained in a personal account.

The GoEmotions [study provenance](../experiments/goemotions/provenance.md) separately records its pure feature/aggregate extraction and controlled evidence projection. The [figure generator](../experiments/goemotions/scripts/plot_results.py) is new presentation code: it consumes verified public aggregates and records its source hash and numerical inputs in `plot_data.json`. It makes no change to the frozen numerical core, study evidence, historical controller choices, or original aggregate formulas. The [walkthrough](../examples/README.md) is newly constructed synthetic teaching material.

The local [HumAID expansion provenance](../experiments/humaid/provenance.md) records four extracted aggregation functions, 12 source trace tests, four target tests projected from the frozen final-calibration inputs, and 1,202 warm-up aggregate records. It reuses the published numerical core and count API. Its internal input-location adapter remains outside the research distribution.

The [TweetEval Sentiment provenance](../experiments/tweeteval-sentiment/provenance.md) records the projection of 14 final candidate-count rows, parity across 35 tests with the original numerical adapter, and preservation of historical aggregation for 2,804 warm-up records. The public method engine remains shared. The original identity map/key and source-label join stay outside the public distribution.

## v0.2.0 presentation

The repository is now named `risk-controlled-social-media-analysis`; the Python distribution, import and CLI names remain stable. The presentation adds a [three-study note](social-media-research.md), figure guides, and [a generator](../scripts/plot_social_media_studies.py) that consumes only verified public aggregate evidence. Each new figure JSON records the generator SHA-256, evidence identity and environment.

The expansion preserves the scientific implementation and all existing evidence bundles, report tables, and original GoEmotions figures and generator. It adds no model fitting, source-data acquisition, threshold search, historical artifact modification or new evaluation. The v0.1.0 release remains immutable. The [release notes](releases/v0.2.0.md) describe the versioned artifacts and verification record.

During release verification, Linux and Windows exposed last-bit differences in unplotted final-test probabilities and confidence bounds embedded in the new figure JSON. Figure-input schema 2 records the verified evaluation/warm-up aggregates instead. Full replay, numerical tolerances, evidence and plotted values remain unchanged; the five new SVG/PNG pairs are byte-identical to the reviewed presentation. The verifier reports bounded field-level diagnostics for future mismatches.
