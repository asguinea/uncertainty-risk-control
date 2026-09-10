"""Historical HumAID aggregate functions; bodies preserved, names disambiguated.

See provenance/humaid_source_extraction.json in the source distribution.
"""


import numpy as np


ALPHA = 0.05


def quantiles(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    array = np.asarray(values, dtype=np.float64)
    return {
        "p05": float(np.quantile(array, 0.05)),
        "median": float(np.median(array)),
        "mean": float(np.mean(array)),
        "p95": float(np.quantile(array, 0.95)),
    }


def aggregate_source(runs: list[dict[str, object]]) -> dict[str, object]:
    certified = [run for run in runs if run["certified"]]
    cp_available = [run for run in runs if run["exact_cp_upper"] is not None]
    nonzero_eval = [
        run for run in runs if int(run["evaluation"]["selected"]) > 0  # type: ignore[index]
    ]
    return {
        "runs": len(runs),
        "certified_runs": len(certified),
        "certification_frequency": len(certified) / len(runs),
        "review_all_frequency": 1.0 - len(certified) / len(runs),
        "evaluation_auto_deprioritization_rate": quantiles(
            [float(run["evaluation"]["auto_deprioritization_rate"]) for run in runs]  # type: ignore[index]
        ),
        "evaluation_selected_error_nonzero_selection": quantiles(
            [float(run["evaluation"]["observed_selected_error"]) for run in nonzero_eval]  # type: ignore[index]
        ),
        "evaluation_nonzero_selection_runs": len(nonzero_eval),
        "evaluation_fraction_observed_selected_error_le_alpha": (
            sum(
                float(run["evaluation"]["observed_selected_error"]) <= ALPHA  # type: ignore[index]
                for run in nonzero_eval
            )
            / len(nonzero_eval)
            if nonzero_eval
            else None
        ),
        "tau_certified_runs": quantiles([float(run["tau"]) for run in certified]),
        "tau_p05_p95_width": (
            float(np.quantile([float(run["tau"]) for run in certified], 0.95))
            - float(np.quantile([float(run["tau"]) for run in certified], 0.05))
            if certified
            else None
        ),
        "calibration_selected_certified_runs": quantiles(
            [float(run["calibration_selected"]) for run in certified]
        ),
        "calibration_harmful_certified_runs": quantiles(
            [float(run["calibration_harmful"]) for run in certified]
        ),
        "calibration_cp_upper_certified_runs": quantiles(
            [float(run["exact_cp_upper"]) for run in certified]
        ),
        "calibration_all_runs": {
            "median_selected_s": float(
                np.median([int(run["calibration_selected"]) for run in runs])
            ),
            "median_harmful_h": float(
                np.median([int(run["calibration_harmful"]) for run in runs])
            ),
            "median_cp_upper_where_defined": (
                float(np.median([float(run["exact_cp_upper"]) for run in cp_available]))
                if cp_available
                else None
            ),
        },
    }


def q(values: list[float]) -> dict[str, float] | None:
    if not values: return None
    array = np.asarray(values, dtype=np.float64)
    return {"p05": float(np.quantile(array, .05)), "median": float(np.median(array)), "mean": float(np.mean(array)), "p95": float(np.quantile(array, .95))}


def aggregate_target(runs: list[dict[str, object]]) -> dict[str, object]:
    certified = [item for item in runs if item["certified"]]
    nonzero = [item for item in runs if int(item["evaluation"]["selected"]) > 0]
    tau = [float(item["tau"]) for item in certified]
    return {
        "runs": len(runs), "certified_runs": len(certified), "certification_frequency": len(certified) / len(runs), "review_all_frequency": 1.0 - len(certified) / len(runs),
        "evaluation_automation_rate": q([float(item["evaluation"]["automation_rate"]) for item in runs]),
        "evaluation_selected_error_nonzero": q([float(item["evaluation"]["observed_selected_error"]) for item in nonzero]),
        "evaluation_nonzero_selection_runs": len(nonzero),
        "fraction_evaluation_selected_error_le_005": sum(float(item["evaluation"]["observed_selected_error"]) <= .05 for item in nonzero) / len(nonzero) if nonzero else None,
        "tau_certified_runs": q(tau), "tau_p05_p95_width": float(np.quantile(tau, .95) - np.quantile(tau, .05)) if tau else None,
        "calibration_selected_certified": q([float(item["calibration_selected"]) for item in certified]),
        "calibration_harmful_certified": q([float(item["calibration_harmful"]) for item in certified]),
        "calibration_cp_upper_certified": q([float(item["exact_cp_upper"]) for item in certified]),
        "calibration_all_runs": {"median_selected_s": float(np.median([int(item["calibration_selected"]) for item in runs])), "median_harmful_h": float(np.median([int(item["calibration_harmful"]) for item in runs])), "median_cp_upper_where_defined": float(np.median([float(item["exact_cp_upper"]) for item in runs if item["exact_cp_upper"] is not None])) if any(item["exact_cp_upper"] is not None for item in runs) else None},
    }
