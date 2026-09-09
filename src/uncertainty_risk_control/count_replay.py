"""Replay a recorded fixed-sequence prefix from binomial sufficient statistics."""

from dataclasses import asdict

from .selected_risk import (
    ALPHA, DELTA, CalibrationResult, ThresholdEvidence,
    _candidates, _counts, _integer, _probability, _rows,
    clopper_pearson_upper, exact_binomial_lower_tail_scipy,
)


def project_counts(ordered_thresholds, scores, outcomes, *, tested_count):
    """Project only a previously recorded executed prefix; do not search further.

    The caller supplies the historical prefix length. This function computes
    counts only and neither calibrates a controller nor chooses that length.
    """
    sequence = _candidates(ordered_thresholds)
    values, labels = _rows(scores, outcomes)
    tested_count = _integer(tested_count, "tested_count")
    if not 0 <= tested_count <= len(sequence):
        raise ValueError("tested_count exceeds the supplied frozen sequence")
    result = []
    for index, candidate in enumerate(sequence[:tested_count]):
        mask = values <= candidate["threshold"]
        result.append({
            "index": index, "threshold": candidate["threshold"],
            "selected": int(mask.sum()), "harmful": int(labels[mask].sum()),
        })
    return result


def replay_count_prefix(ordered_thresholds, counts, *, n, alpha=ALPHA, delta=DELTA):
    """Return the historical controller and every tested hypothesis, including failure.

    The counts must cover exactly the executed prefix for this budget. Missing
    failures, extra tests after a failure, and reordered/misaligned counts fail.
    A fully passing trace must cover the entire frozen sequence.
    """
    sequence = _candidates(ordered_thresholds)
    n = _integer(n, "n")
    alpha, delta = _probability(alpha, "alpha"), _probability(delta, "delta")
    if n < 0 or len(counts) > len(sequence):
        raise ValueError("invalid population size or prefix length")
    passing, tested = [], []
    stopped = None
    for index, row in enumerate(counts):
        if set(row) != {"index", "threshold", "selected", "harmful"}:
            raise ValueError("unexpected count-trace fields")
        if _integer(row["index"], "index") != index:
            raise ValueError("count trace must be a contiguous zero-based prefix")
        threshold = _probability(row["threshold"], "threshold", endpoints=True)
        if threshold != sequence[index]["threshold"]:
            raise ValueError("count threshold differs from frozen sequence")
        harmful, selected = _counts(row["harmful"], row["selected"])
        if selected > n:
            raise ValueError("selected count exceeds calibration population")
        p_value = exact_binomial_lower_tail_scipy(harmful, selected, alpha)
        upper = clopper_pearson_upper(harmful, selected, delta)
        evidence = ThresholdEvidence(threshold, selected, harmful, p_value, upper)
        passes = selected > 0 and p_value <= delta
        tested.append({"index": index, **asdict(evidence), "passes": passes})
        if passes:
            passing.append(evidence)
        else:
            stopped = index
            if index != len(counts) - 1:
                raise ValueError("trace contains tests after the first failure")
            break
    if stopped is None and len(counts) != len(sequence):
        raise ValueError("incomplete trace: the first failure or remaining tests are missing")
    # Threshold selection is nested even when the tested order is nonmonotone.
    ordered = sorted(counts, key=lambda row: row["threshold"])
    for lower, higher in zip(ordered, ordered[1:]):
        delta_selected = higher["selected"] - lower["selected"]
        delta_harmful = higher["harmful"] - lower["harmful"]
        if not 0 <= delta_harmful <= delta_selected:
            raise ValueError("counts are inconsistent with nested threshold selection")
        if lower["threshold"] == higher["threshold"] and delta_selected:
            raise ValueError("equal thresholds have unequal counts")
    if passing:
        chosen = max(passing, key=lambda item: (item.selected, item.threshold))
        result = CalibrationResult(
            "CERTIFIED", chosen.threshold, chosen.selected, chosen.harmful,
            chosen.p_value, chosen.cp_upper, tuple(passing), stopped,
        )
    else:
        result = CalibrationResult("REVIEW_ALL", None, 0, 0, None, None, (), stopped)
    return {"controller": result, "tests": tested}
