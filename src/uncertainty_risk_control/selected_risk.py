"""Validated interface to the unchanged historical numerical implementation.

Freeze the scorer, candidates, and their order independently of calibration.
An array API cannot establish that independence; it is a protocol requirement.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from numbers import Integral, Real

import numpy as np

from ._reference import selected_risk_v1 as _core

METHOD_ID = "EXACT_BINOMIAL_SELECTED_RISK_LTT_V1"
SEQUENCE_ID = "SELECTED_RISK_FIXED_SEQUENCE_V1"
ALPHA = _core.ALPHA
DELTA = _core.DELTA
CalibrationResult = _core.CalibrationResult
ThresholdEvidence = _core.ThresholdEvidence


def _integer(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer, excluding booleans")
    return int(value)


def _counts(harmful: int, selected: int) -> tuple[int, int]:
    harmful, selected = _integer(harmful, "harmful"), _integer(selected, "selected")
    if not 0 <= harmful <= selected:
        raise ValueError("require 0 <= harmful <= selected")
    return harmful, selected


def _probability(value: float, name: str, *, endpoints: bool = False) -> float:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    valid = 0 <= result <= 1 if endpoints else 0 < result < 1
    if not math.isfinite(result) or not valid:
        interval = "[0, 1]" if endpoints else "(0, 1)"
        raise ValueError(f"{name} must be finite and in {interval}")
    return result


def _scores(scores: Sequence[float], *, allow_empty: bool = True) -> np.ndarray:
    raw = np.asarray(scores)
    if raw.dtype.kind not in "iuf" or raw.ndim != 1:
        raise ValueError("scores must be a one-dimensional real numeric vector")
    values = raw.astype(np.float64)
    if not np.all(np.isfinite(values)) or np.any((values < 0) | (values > 1)):
        raise ValueError("scores must be finite and in [0, 1]")
    if not allow_empty and not values.size:
        raise ValueError("development scores must be non-empty")
    return values


def _rows(scores: Sequence[float], outcomes: Sequence[int], *, allow_empty: bool = True):
    values = _scores(scores, allow_empty=allow_empty)
    raw = np.asarray(outcomes)
    if raw.shape != values.shape or raw.dtype.kind not in "biuf":
        raise ValueError("outcomes must be a binary vector matching scores")
    # Validate before int8 conversion: e.g. 256 and 0.5 must never become zero.
    if not np.all(np.isfinite(raw)) or not np.all((raw == 0) | (raw == 1)):
        raise ValueError("outcomes must contain only 0 (no mistake) or 1 (mistake)")
    return values, raw.astype(np.int8)


def _candidates(candidates: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    copied = []
    for candidate in candidates:
        if not isinstance(candidate, Mapping) or "threshold" not in candidate:
            raise ValueError("each candidate must be a mapping containing threshold")
        copied.append({**candidate, "threshold": _probability(candidate["threshold"], "threshold", endpoints=True)})
    return copied


def exact_binomial_lower_tail_scipy(harmful: int, selected: int, alpha: float = ALPHA) -> float:
    """P[Binomial(selected, alpha) <= harmful]; return 1 for no selection."""
    harmful, selected = _counts(harmful, selected)
    return _core.exact_binomial_lower_tail_scipy(harmful, selected, _probability(alpha, "alpha"))


def clopper_pearson_upper(harmful: int, selected: int, delta: float = DELTA) -> float | None:
    """One-sided 1-delta upper bound; undefined (None) for no selection."""
    harmful, selected = _counts(harmful, selected)
    return _core.clopper_pearson_upper(harmful, selected, _probability(delta, "delta"))


def certifies(harmful: int, selected: int, alpha: float = ALPHA, delta: float = DELTA) -> bool:
    """Whether a single candidate passes; sequence stopping is a separate rule."""
    harmful, selected = _counts(harmful, selected)
    return _core.certifies(harmful, selected, _probability(alpha, "alpha"), _probability(delta, "delta"))


def minimum_selected_for_harmful(harmful: int, alpha: float = ALPHA, delta: float = DELTA, maximum: int = 1_000_000) -> int:
    """Search the historical sample-size boundary, subject to a finite limit."""
    harmful, maximum = _counts(harmful, maximum)
    return _core.minimum_selected_for_harmful(harmful, _probability(alpha, "alpha"), _probability(delta, "delta"), maximum)


def build_threshold_family(scores: Sequence[float]) -> list[dict[str, object]]:
    """Historical nearest-rank family, using development scores only.

    This helper is not the frozen GoEmotions MB1 candidate family.
    """
    return _core.build_threshold_family(_scores(scores, allow_empty=False))


def order_thresholds_from_development(family: Iterable[Mapping[str, object]], scores: Sequence[float], outcomes: Sequence[int]) -> list[dict[str, object]]:
    """Order candidates on development rows; exclude candidates selecting none."""
    values, labels = _rows(scores, outcomes, allow_empty=False)
    return _core.order_thresholds_from_development(_candidates(family), values, labels)


def calibrate_fixed_sequence(ordered_thresholds: Sequence[Mapping[str, object]], scores: Sequence[float], outcomes: Sequence[int], alpha: float = ALPHA, delta: float = DELTA) -> CalibrationResult:
    """Test a frozen sequence, stopping at its first failed test.

    Accept score <= threshold, including ties. Among the passing prefix, choose
    maximum selected count, breaking ties by higher threshold. An empty prefix
    returns REVIEW_ALL. This function never learns or reorders candidates.
    """
    values, labels = _rows(scores, outcomes)
    return _core.calibrate_fixed_sequence(_candidates(ordered_thresholds), values, labels, _probability(alpha, "alpha"), _probability(delta, "delta"))
