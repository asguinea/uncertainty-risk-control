# GoEmotions MB1 protocol and implementation correspondence

## Reference and structural roles

The pinned raw release contains 211,225 rater rows across 58,011 comments. The historical source audit recorded a difference of two comments from the paper's reported total. A reference includes every label with at least two votes. The 54,263 comments with a nonempty agreed-label set form the primary population; 3,748 no-agreement comments were outside it. Released judgments flagged unclear are preserved in the reference construction rather than silently removed.

Structural grouping uses connected components over shared submission/thread links and exact text after Unicode NFC normalization and whitespace collapse. It does not lowercase, remove punctuation, or perform semantic deduplication. Components are sorted deterministically using the original namespace and canonical unsalted group identity, then assigned at the nearest whole-group comment-count boundaries for 50/10/10/10/20 proportions. This primary role allocation is reconstructible from upstream data without the private identity salt, but its serialized opaque identities are not.

The resulting role sizes are recorded in [study.json](evidence/study.json). The formal unit remains a comment. Grouping is a leakage-control measure and does not establish the independent, identically distributed sampling assumption used by the binomial method.

## Classifier and meta-risk scorer

The historical classifier uses `roberta-base` at revision `e2da8e2f811d1448a5b465c236feacd80ffbac7b`, maximum length 64, 28 sigmoid outputs, and a two-rater agreed-set multi-hot target with binary cross-entropy on logits. Training used three fixed epochs, AdamW at learning rate 2e-5 and weight decay 0.01, effective batch size 32, and seed 1729. An 80/20 development-only sanity split preceded reinitialization and training on all 27,131 development comments.

Five development-only out-of-fold classifier fits supplied meta-risk training/design features. The group-preserving meta split contained 18,992 training and 8,139 design comments. The logistic model used only classifier probabilities, not comment text, author, subreddit, rater, disagreement, thread, or timestamps. Its 97 features are available as executable [feature functions](../../src/uncertainty_risk_control/goemotions/features.py): 28 probabilities; top three probabilities and two margins; six probability/count summaries; two entropy summaries; 28 indicators of the top label; and 28 top-label/confidence interactions. The original feature order, entropy clipping, and `argmax` tie behavior are retained. No fitted weights are distributed here.

The historical environment records Python 3.11.13, NumPy 2.4.6, SciPy 1.17.1, scikit-learn 1.9.0, torch 2.13.0, transformers 5.16.1, tokenizers 0.23.1, and safetensors 0.8.0 on an Apple M4 Pro with MPS and 48 GiB unified memory. Only NumPy/SciPy are needed and installed for this evidence replay. These training details are provenance, not a tested public training command.

## Candidate family and order

Twenty-one candidate thresholds were selected at nearest-rank canonical-development meta-risk quantiles for fractions 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.075, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, and 0.95. A boundary below the minimum development score represents review-all and is excluded from testing.

The 8,139-comment meta-design subset orders those candidates by one-sided 95% Clopper–Pearson upper bound ascending, then design selected fraction descending, then threshold ascending. This is different from the generic historical development-order helper included with the numerical foundation. **The MB1 command reads the frozen study sequence directly.** It never reconstructs that sequence from final-calibration or locked outcomes.

[design.json](evidence/design.json) retains every candidate, its requested quantile, canonical/design counts, design CP bound, and frozen order. Replay checks the bound and order. The thresholds themselves remain author-provided frozen values: recovering nearest-rank thresholds from the original 27,131 model scores is outside aggregate replay.

## Calibration, evaluation, and warm-up

Each risk budget independently walks the same frozen sequence, stopping at the first failed test, including zero selection. Selection includes equality at a threshold. The passing-prefix candidate with the greatest selected count is chosen, with higher threshold breaking ties. The four executed prefix lengths are 3, 5, 13, and 14, including first failures. Only those 14 unique candidates have final-calibration sufficient statistics in [calibration.json](evidence/calibration.json). The remaining seven have no exported final-calibration counts and are not tested by replay.

The historical record states that the protocol was frozen before final calibration and all four controllers were frozen before locked evaluation, with no subsequent adaptation. This bundle preserves that record as provenance; hashes cannot independently prove its chronology or turn it into public preregistration.

Warm-up used 100 hash-ordered, whole-group-prefix samples per requested size of 50, 100, 200, 500, 1,000, 2,000, and 4,000, plus the full 5,427-comment pool once for each budget. Whole groups are added only while the total remains at or below the requested size. All 2,804 recorded aggregate run records are included. Quantiles use the original NumPy formulas; error quantiles exclude zero-selection runs and report the nonzero-run denominator. A full-pool result is one observation, not 100 independent replicates.

Consensus strength equals maximum emotion votes divided by recorded rater count; strata are high at ≥0.80, medium at ≥0.60 and <0.80, and low below 0.60. Predicted-emotion error reporting requires at least 30 selected locked examples or 20 selected warm-up examples. The source omits sparse-slice error counts, so the public projection retains them as missing. Pooled and consensus totals are checked exactly; emotion selected/population totals reconcile, while suppressed error totals are checked only for consistency bounds.
