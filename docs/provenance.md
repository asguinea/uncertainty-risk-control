# Extraction provenance

This repository starts with new local Git history. Its numerical method originated in the EyeTrustAI research validation program. Three allowlisted original files were used: the selected-risk engine, its unit fixtures, and its synthetic verification script. No product runtime code or private Git objects are required to execute this package.

[The extraction manifest](../provenance/extraction.json) records each source filename, its SHA-256, the destination, the extracted-file hash, and transformations. The source engine was copied without a byte change; the package also contains a hash manifest that both CLI commands verify at runtime. Original domain-specific method identifiers remain in this frozen reference for traceability. The public identifiers remove the domain prefix while retaining numerical version V1; they are aliases, not a newly invented method.

The verification script preserves its numerical, geometry, population, simulation-count, seed convention, and tolerance choices. Imports point to the public interface, its old filesystem CLI is replaced by the package CLI, and an actual equal-count tie fixture now supports a previously descriptive success flag. Original unit-test bodies are retained with imports and the introductory description adapted. New public-interface and protocol tests are separately identifiable.

The public wrapper deliberately tightens invalid-input behavior while preserving results on supported valid inputs. The original core's recurrence remains internal with its bounded numerical scope documented. Any future change to the core requires a new provenance record and equivalence review; updating a hash alone is not evidence of correctness.

These hashes establish integrity and extraction correspondence. They do not establish a public preregistration date, independent replication, external mathematical review, or the validity of dataset assumptions. Detailed internal source locations and private revision bindings remain in the internal extraction audit; they are not runtime dependencies or resolvable public citations.

The maintainer is Alejandro Sanchez Guinea. The historical numerical source has no copyright header or accompanying notice to remove; its original docstring and identifiers remain intact. Attribution to the EyeTrustAI research context is retained. Publication does not change authorship merely because the repository is maintained in a personal account.
