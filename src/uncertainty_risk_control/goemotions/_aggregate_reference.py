"""Historical MB1 aggregate formulas, extracted without its I/O or execution phases."""

from __future__ import annotations

from collections import Counter
import numpy as np

REQUESTED_TIERS = (50, 100, 200, 500, 1000, 2000, 4000)


def quantiles(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"p05": None, "median": None, "p95": None}
    array = np.asarray(values, dtype=np.float64)
    return {
        "p05": float(np.quantile(array, 0.05)),
        "median": float(np.median(array)),
        "p95": float(np.quantile(array, 0.95)),
    }


def threshold_stability(values: list[float]) -> dict[str, object]:
    if not values:
        return {"non_review_all": 0, "unique_thresholds": 0, "mode": None, "mode_fraction": None}
    counts = Counter(values)
    mode, count = max(counts.items(), key=lambda item: (item[1], -item[0]))
    return {"non_review_all": len(values), "unique_thresholds": len(counts), "mode": mode, "mode_fraction": count / len(values)}


def aggregate_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    certified = [run for run in runs if run["calibration"]["certified"]]
    nonzero = [run for run in runs if run["evaluation"]["selected"] > 0]
    return {
        "replicates": len(runs),
        "certification_frequency": len(certified) / len(runs),
        "review_all_frequency": 1.0 - len(certified) / len(runs),
        "realized_n": {"min": min(run["realized_n"] for run in runs), "max": max(run["realized_n"] for run in runs)},
        "median_calibration_selected": float(np.median([run["calibration"]["selected"] for run in runs])),
        "evaluation_automation": quantiles([run["evaluation"]["automation"] for run in runs]),
        "evaluation_selected_error_nonzero": {**quantiles([run["evaluation"]["selected_error"] for run in nonzero]), "runs": len(nonzero)},
        "threshold": quantiles([run["calibration"]["threshold"] for run in certified]),
        "threshold_stability": threshold_stability([run["calibration"]["threshold"] for run in certified]),
    }


def milestone(aggregates: dict[str, dict[str, object]], predicate) -> int | str | None:
    for tier in [*map(str, REQUESTED_TIERS), "FULL"]:
        if predicate(aggregates[tier]):
            return 5_427 if tier == "FULL" else int(tier)
    return None


def milestones(aggregates: dict[str, dict[str, object]]) -> dict[str, int | str | None]:
    result = {
        "first_any_certification": milestone(aggregates, lambda item: item["certification_frequency"] > 0),
        "first_at_least_50_percent_certification": milestone(aggregates, lambda item: item["certification_frequency"] >= .50),
        "first_at_least_80_percent_certification": milestone(aggregates, lambda item: item["certification_frequency"] >= .80),
        "first_at_least_90_percent_certification": milestone(aggregates, lambda item: item["certification_frequency"] >= .90),
    }
    for fraction in (.05, .10, .25, .50, .75):
        result[f"first_median_automation_at_least_{int(fraction * 100)}_percent"] = milestone(
            aggregates, lambda item, fraction=fraction: item["evaluation_automation"]["median"] >= fraction
        )
    for fraction in (.05, .10, .25):
        result[f"first_90_percent_certification_and_{int(fraction * 100)}_percent_automation"] = milestone(
            aggregates,
            lambda item, fraction=fraction: item["certification_frequency"] >= .90 and item["evaluation_automation"]["median"] >= fraction,
        )
    return result
