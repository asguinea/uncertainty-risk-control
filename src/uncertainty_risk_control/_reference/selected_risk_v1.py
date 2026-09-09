#!/usr/bin/env python3
"""Exact-binomial selected-risk calibration for the HumAID D1 program."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.stats import beta, binom


METHOD_ID = "HUMAID_EXACT_BINOMIAL_SELECTED_RISK_LTT_V1"
SEQUENCE_ID = "HUMAID_SELECTED_RISK_FIXED_SEQUENCE_V1"
ALPHA = 0.05
DELTA = 0.05
REQUESTED_FRACTIONS = tuple([index / 100 for index in range(5, 100, 5)] + [0.975, 0.99])


@dataclass(frozen=True)
class ThresholdEvidence:
    threshold: float
    selected: int
    harmful: int
    p_value: float
    cp_upper: float | None


@dataclass(frozen=True)
class CalibrationResult:
    state: str
    threshold: float | None
    selected: int
    harmful: int
    p_value: float | None
    cp_upper: float | None
    certified_thresholds: tuple[ThresholdEvidence, ...]
    stopped_at_index: int | None


def exact_binomial_lower_tail_scipy(harmful: int, selected: int, alpha: float = ALPHA) -> float:
    _validate_counts(harmful, selected)
    if selected == 0:
        return 1.0
    return float(binom.cdf(harmful, selected, alpha))


def exact_binomial_lower_tail_recurrence(
    harmful: int, selected: int, alpha: float = ALPHA
) -> float:
    """Independent stable sum of Binomial(selected, alpha) mass from 0 through harmful."""

    _validate_counts(harmful, selected)
    if selected == 0:
        return 1.0
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between zero and one")
    term = math.exp(selected * math.log1p(-alpha))
    terms = [term]
    odds = alpha / (1.0 - alpha)
    for index in range(1, harmful + 1):
        term *= ((selected - index + 1) / index) * odds
        terms.append(term)
    return min(1.0, math.fsum(terms))


def clopper_pearson_upper(harmful: int, selected: int, delta: float = DELTA) -> float | None:
    _validate_counts(harmful, selected)
    if selected == 0:
        return None
    if harmful == selected:
        return 1.0
    return float(beta.ppf(1.0 - delta, harmful + 1, selected - harmful))


def certifies(harmful: int, selected: int, alpha: float = ALPHA, delta: float = DELTA) -> bool:
    if selected == 0:
        return False
    return exact_binomial_lower_tail_scipy(harmful, selected, alpha) <= delta


def minimum_selected_for_harmful(
    harmful: int, alpha: float = ALPHA, delta: float = DELTA, maximum: int = 1_000_000
) -> int:
    for selected in range(max(1, harmful), maximum + 1):
        if certifies(harmful, selected, alpha, delta):
            return selected
    raise ValueError(f"no certifying selected count found through {maximum}")


def build_threshold_family(scores: Sequence[float]) -> list[dict[str, object]]:
    values = np.asarray(scores, dtype=np.float64)
    if values.ndim != 1 or len(values) == 0 or not np.all(np.isfinite(values)):
        raise ValueError("scores must be a non-empty finite vector")
    if np.any((values < 0.0) | (values > 1.0)):
        raise ValueError("scores must be probabilities")
    ordered = np.sort(values, kind="stable")
    requested: dict[float, list[float]] = {}
    for fraction in REQUESTED_FRACTIONS:
        rank = max(1, math.ceil(fraction * len(ordered)))
        threshold = float(ordered[rank - 1])
        requested.setdefault(threshold, []).append(fraction)
    family = [
        {
            "threshold": 0.0,
            "requested_fractions": [],
            "boundary": "review-all unless an exact-zero score exists",
        }
    ]
    family.extend(
        {
            "threshold": threshold,
            "requested_fractions": fractions,
            "boundary": None,
        }
        for threshold, fractions in sorted(requested.items())
        if threshold != 0.0
    )
    return family


def order_thresholds_from_development(
    family: Iterable[dict[str, object]], scores: Sequence[float], outcomes: Sequence[int]
) -> list[dict[str, object]]:
    values = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(outcomes, dtype=np.int8)
    if values.shape != labels.shape:
        raise ValueError("score/outcome shape mismatch")
    ordered = []
    for candidate in family:
        threshold = float(candidate["threshold"])
        mask = values <= threshold
        selected = int(mask.sum())
        if selected == 0:
            continue
        harmful = int(labels[mask].sum())
        ordered.append(
            {
                **candidate,
                "development_selected": selected,
                "development_selected_fraction": selected / len(values),
                "development_harmful": harmful,
                "development_empirical_selected_error": harmful / selected,
            }
        )
    return sorted(
        ordered,
        key=lambda candidate: (
            candidate["development_empirical_selected_error"],
            -candidate["development_selected_fraction"],
            candidate["threshold"],
        ),
    )


def calibrate_fixed_sequence(
    ordered_thresholds: Sequence[dict[str, object]],
    scores: Sequence[float],
    outcomes: Sequence[int],
    alpha: float = ALPHA,
    delta: float = DELTA,
) -> CalibrationResult:
    values = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(outcomes, dtype=np.int8)
    if values.shape != labels.shape:
        raise ValueError("score/outcome shape mismatch")
    rejected = []
    stopped_at = None
    for index, candidate in enumerate(ordered_thresholds):
        threshold = float(candidate["threshold"])
        mask = values <= threshold
        selected = int(mask.sum())
        harmful = int(labels[mask].sum())
        p_value = exact_binomial_lower_tail_scipy(harmful, selected, alpha)
        cp_upper = clopper_pearson_upper(harmful, selected, delta)
        evidence = ThresholdEvidence(threshold, selected, harmful, p_value, cp_upper)
        if selected > 0 and p_value <= delta:
            rejected.append(evidence)
        else:
            stopped_at = index
            break
    if not rejected:
        return CalibrationResult(
            "REVIEW_ALL", None, 0, 0, None, None, tuple(), stopped_at
        )
    chosen = max(rejected, key=lambda item: (item.selected, item.threshold))
    return CalibrationResult(
        "CERTIFIED",
        chosen.threshold,
        chosen.selected,
        chosen.harmful,
        chosen.p_value,
        chosen.cp_upper,
        tuple(rejected),
        stopped_at,
    )


def _validate_counts(harmful: int, selected: int) -> None:
    if not isinstance(harmful, int) or not isinstance(selected, int):
        raise TypeError("harmful and selected must be integers")
    if selected < 0 or harmful < 0 or harmful > selected:
        raise ValueError("require 0 <= harmful <= selected")
