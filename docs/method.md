# Exact-binomial selected-risk calibration

For a frozen prediction rule, let `E` be a binary mistake indicator and `S` its risk score. A fixed threshold `t` accepts the output when `S <= t`. The quantity of interest is `R(t) = P(E = 1 | S <= t)`, where the conditioning event has positive probability. Scores need not themselves be calibrated probabilities; this implementation requires a finite score scale in `[0, 1]`.

For one fixed candidate, calibration supplies a selected count `n` and mistake count `h`. The test statistic is the lower-tail probability `P[Binomial(n, alpha) <= h]`. A candidate passes when this probability is at most `delta` and `n > 0`. The one-sided Clopper–Pearson upper bound is also reported, using `Beta(h + 1, n - h)` at quantile `1 - delta`, with upper bound 1 when every selected observation is a mistake. With no selection, the test value is 1 and the upper bound is undefined.

## Fixed-sequence rule

1. Learn the scorer and design the candidate family and order using development data, independently of calibration.
2. Test candidates in exactly that frozen order, at the specified `alpha` and `delta`.
3. Stop at the first candidate that does not pass, including one selecting zero observations. Do not test or rescue a later candidate.
4. Among the passing prefix, choose the candidate with the greatest selected count, breaking ties by the higher threshold. If the prefix is empty, return `REVIEW_ALL` with no threshold.

This is fixed-sequence Learn then Test: under valid individual tests, the first true null in the frozen sequence bounds the chance of any false rejection by `delta`. Candidate risks need not be monotone in threshold. The [LTT framework](https://arxiv.org/abs/2110.01052) supplies the multiple-testing perspective; this repository implements the selected-risk specialization described above and does not introduce a new theorem.

At `alpha = delta = 0.05`, zero mistakes require at least 59 selected observations. For 0 through 5 mistakes, the first certifying sample sizes are respectively 59, 93, 124, 153, 181, and 208. These are verified numerical boundary fixtures, not sample-size recommendations for a dataset study.

## Assumptions and interpretation

Conditional binomial inference here assumes independent, identically distributed calibration units from the target population, a binary reference error, and a scorer/selection family frozen independently of calibration. Subject to those assumptions and the fixed-sequence rule, the probability over calibration that the returned nonempty policy has selected risk above `alpha` is at most `delta`. No useful-automation guarantee follows: `REVIEW_ALL` is possible, and a passing controller may accept very little.

The API cannot determine whether a caller reused calibration data to learn the scorer or candidate order. Its development helpers and calibration function are separate, and the synthetic runner demonstrates separate draws, but protocol independence must also be established in each study. Clustering, dependence, distribution shift, annotation error, or repeated adaptive use can invalidate an application of the stated bound.

Each invocation at a different risk budget has its own confidence statement. Four invocations with `delta = 0.05` do not give a simultaneous 95% guarantee across all four budgets. Reported Clopper–Pearson values are fixed-candidate statistics, not a simultaneous confidence band for every adaptively displayed candidate. Test decisions retain the historical `p <= delta` rule and SciPy numerical evaluation; no comparison tolerance is added to make a candidate pass.

## Implementation boundary

The historical numerical core is preserved byte for byte under `_reference/`. The public interface validates binary outcomes **before** integer conversion, rejects invalid scores, thresholds, counts, and probabilities, and delegates valid inputs to that core. Native and NumPy integer counts are accepted, excluding booleans. Zero selection and empty candidate sequences produce review-all behavior. Invalid inputs fail even when a numerical shortcut would otherwise return early.

The historical nearest-rank development helper uses 5% increments through 95%, then 97.5% and 99%, deduplicates score ties, and includes a zero boundary. Development ordering drops candidates selecting no development observations. GoEmotions MB1 instead uses its own frozen family and design-CP ordering, specified in the [study protocol](../experiments/goemotions/protocol.md).

The inherited probability-mass recurrence is used only as a verification oracle over the original bounded fixtures at `alpha = 0.05`. Despite its historical “stable sum” docstring, its initial mass can underflow for larger `n` or `alpha`, so it is not exported as a general numerical API. Additional high-precision direct-sum tests check all four study risk budgets against SciPy. The Clopper–Pearson cross-check uses a second SciPy API and therefore is not a fully independent library implementation.

## References

- Angelopoulos, Bates, Candès, Jordan, and Lei. [Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control](https://arxiv.org/abs/2110.01052).
- SciPy [binomial distribution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html), [beta distribution](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html), and [exact binomial test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html) implementation documentation. The environment lock specifies the executed library versions.
