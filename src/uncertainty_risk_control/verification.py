#!/usr/bin/env python3
"""Independent numerical, boundary, brute-force, and Monte Carlo verification."""

from __future__ import annotations

import math

import numpy as np
from scipy.stats import binom, binomtest

from .selected_risk import (
    ALPHA,
    DELTA,
    calibrate_fixed_sequence,
    certifies,
    clopper_pearson_upper,
    exact_binomial_lower_tail_scipy,
    minimum_selected_for_harmful,
)

from ._reference.selected_risk_v1 import exact_binomial_lower_tail_recurrence


EXPECTED_GEOMETRY = {0: 59, 1: 93, 2: 124, 3: 153, 4: 181, 5: 208}
MONTE_CARLO_RUNS_PER_SCENARIO = 30_000
MONTE_CARLO_TOLERANCE = 0.055


SCENARIOS = {
    "monotone_selected_risk": {
        "probabilities": [0.16, 0.16, 0.16, 0.16, 0.12, 0.10, 0.08, 0.06],
        "bin_risks": [0.01, 0.02, 0.04, 0.07, 0.10, 0.14, 0.20, 0.28],
        "sequence": [1, 2, 3, 4, 5, 6, 7, 8],
    },
    "nonmonotone_selected_risk": {
        "probabilities": [0.12, 0.13, 0.13, 0.12, 0.14, 0.12, 0.12, 0.12],
        "bin_risks": [0.01, 0.12, 0.01, 0.13, 0.02, 0.18, 0.03, 0.20],
        "sequence": [1, 3, 5, 2, 4, 6, 7, 8],
    },
    "score_ties": {
        "probabilities": [0.30, 0.00, 0.20, 0.00, 0.20, 0.00, 0.15, 0.15],
        "bin_risks": [0.02, 0.02, 0.06, 0.06, 0.12, 0.12, 0.18, 0.25],
        "sequence": [1, 3, 5, 7, 8],
    },
    "highly_imbalanced": {
        "probabilities": [0.10, 0.10, 0.10, 0.10, 0.15, 0.15, 0.15, 0.15],
        "bin_risks": [0.001, 0.003, 0.008, 0.02, 0.06, 0.10, 0.18, 0.30],
        "sequence": [1, 2, 3, 4, 5, 6, 7, 8],
    },
    "rare_or_no_selection": {
        "probabilities": [0.001, 0.004, 0.015, 0.03, 0.10, 0.20, 0.30, 0.35],
        "bin_risks": [0.20, 0.15, 0.10, 0.08, 0.07, 0.09, 0.12, 0.18],
        "sequence": [1, 2, 3, 4, 5, 6, 7, 8],
    },
}


def numerical_verification() -> dict[str, object]:
    maximum_difference = 0.0
    fixtures = []
    for selected in (0, 1, 2, 10, 58, 59, 93, 124, 153, 181, 208, 500, 1000, 4774):
        for harmful in sorted({0, min(1, selected), min(5, selected), selected // 20, selected}):
            scipy_value = exact_binomial_lower_tail_scipy(harmful, selected)
            recurrence = exact_binomial_lower_tail_recurrence(harmful, selected)
            difference = abs(scipy_value - recurrence)
            maximum_difference = max(maximum_difference, difference)
            if difference > 1e-12:
                raise AssertionError((harmful, selected, scipy_value, recurrence, difference))
            fixtures.append({"h": harmful, "s": selected, "p": scipy_value})
    geometry = {harmful: minimum_selected_for_harmful(harmful) for harmful in range(6)}
    if geometry != EXPECTED_GEOMETRY:
        raise AssertionError(f"sample-size geometry mismatch: {geometry}")
    if certifies(0, 58) or not certifies(0, 59) or certifies(0, 0):
        raise AssertionError("named zero-error boundary fixture failed")
    for harmful, selected in geometry.items():
        scipy_upper = clopper_pearson_upper(harmful, selected)
        oracle_upper = float(binomtest(harmful, selected).proportion_ci(0.90, method="exact").high)
        if abs(scipy_upper - oracle_upper) > 1e-12:
            raise AssertionError("Clopper-Pearson oracle disagreement")
    return {
        "oracle_agreement_max_absolute_difference": maximum_difference,
        "fixtures_checked": len(fixtures),
        "minimum_selected_geometry": {str(key): value for key, value in geometry.items()},
        "s58_h0_certifies": False,
        "s59_h0_certifies": True,
        "n50_state": "FORMAL_CERTIFICATION_IMPOSSIBLE_BY_SAMPLE_SIZE",
    }


def _true_cumulative_risks(probabilities: np.ndarray, bin_risks: np.ndarray) -> np.ndarray:
    return np.cumsum(probabilities * bin_risks) / np.cumsum(probabilities)


def monte_carlo_scenario(name: str, config: dict[str, list[float]], seed: int) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    probabilities = np.asarray(config["probabilities"], dtype=np.float64)
    risks = np.asarray(config["bin_risks"], dtype=np.float64)
    sequence = list(config["sequence"])
    if not math.isclose(float(probabilities.sum()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise AssertionError(f"scenario probabilities do not sum to one: {name}")
    cumulative_risks = _true_cumulative_risks(probabilities, risks)
    calibration_n = 400
    bins = rng.multinomial(calibration_n, probabilities, size=MONTE_CARLO_RUNS_PER_SCENARIO)
    harms_by_bin = rng.binomial(bins, risks)
    selected = np.cumsum(bins, axis=1)
    harmful = np.cumsum(harms_by_bin, axis=1)
    alive = np.ones(MONTE_CARLO_RUNS_PER_SCENARIO, dtype=bool)
    any_false_certification = np.zeros(MONTE_CARLO_RUNS_PER_SCENARIO, dtype=bool)
    for sequence_index in sequence:
        index = sequence_index - 1
        p_values = binom.cdf(harmful[:, index], selected[:, index], ALPHA)
        rejected = (selected[:, index] > 0) & (p_values <= DELTA)
        any_false_certification |= alive & rejected & (cumulative_risks[index] > ALPHA)
        alive &= rejected
    false_certifications = int(any_false_certification.sum())
    selection_zero_runs = int((selected[:, sequence[0] - 1] == 0).sum())
    rate = false_certifications / MONTE_CARLO_RUNS_PER_SCENARIO
    if rate > MONTE_CARLO_TOLERANCE:
        raise AssertionError(f"Monte Carlo FWER exceeds tolerance for {name}: {rate}")
    return {
        "experiments": MONTE_CARLO_RUNS_PER_SCENARIO,
        "calibration_n": calibration_n,
        "false_certifications": false_certifications,
        "false_certification_rate": rate,
        "tolerance": MONTE_CARLO_TOLERANCE,
        "selection_zero_runs_at_first_threshold": selection_zero_runs,
        "true_cumulative_selected_risks": cumulative_risks.tolist(),
    }


def brute_force_fixtures() -> dict[str, object]:
    candidates = [{"threshold": 0.1}, {"threshold": 0.2}, {"threshold": 0.3}]
    passing_scores = [0.1] * 59 + [0.2] * 41
    passing_outcomes = [0] * 59 + [1] * 41
    result = calibrate_fixed_sequence(candidates, passing_scores, passing_outcomes)
    if len(result.certified_thresholds) != 1 or result.threshold != 0.1:
        raise AssertionError("first-non-rejection fixture failed")
    failing = calibrate_fixed_sequence(candidates, [0.1] * 58, [0] * 58)
    if failing.state != "REVIEW_ALL" or failing.certified_thresholds:
        raise AssertionError("review-all fixture failed")
    no_selection = calibrate_fixed_sequence([{"threshold": 0.0}], [0.1, 0.2], [0, 0])
    if no_selection.state != "REVIEW_ALL":
        raise AssertionError("no-selection fixture failed")
    tied = calibrate_fixed_sequence(candidates, [0.1] * 59, [0] * 59)
    if tied.threshold != 0.3 or len(tied.certified_thresholds) != 3:
        raise AssertionError("equal selected-count tie-break fixture failed")
    return {
        "first_non_rejection_stops": True,
        "only_rejected_hypotheses_returned": True,
        "highest_selected_count_tie_broken_by_higher_threshold": True,
        "s_zero_never_certifies": True,
    }
