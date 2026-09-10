"""Explicit aggregate projections; no source rows, text, identities or paths emitted."""

from ..selected_risk import _counts, _integer


def evaluation(record, *, priority_total=None):
    n = _integer(record["n"], "n")
    selected = record["selected"]
    harmful = record.get("priority_selected_errors", record.get("priority_errors"))
    _counts(harmful, selected)
    if priority_total is None:
        priority_total = record.get("y1")
    if priority_total is None and "priority_retained_for_review_count" in record:
        priority_total = record["priority_retained_for_review_count"] + harmful
    if priority_total is None and "priority_prevalence" in record:
        unrounded = record["priority_prevalence"] * n
        priority_total = round(unrounded)
        if abs(unrounded - priority_total) > 1e-9:
            raise ValueError("prevalence does not recover an integer count")
    return {"n": n, "selected": selected, "harmful": harmful,
            "priority_total": _integer(priority_total, "priority_total")}


def recorded_metrics(record):
    aliases = {
        "automation_rate": ("automation_rate", "auto_deprioritization_rate"),
        "selected_error": ("observed_selected_error",),
        "review_rate": ("review_rate",),
        "priority_recall_to_review": ("priority_recall_to_review", "priority_signal_recall_to_review"),
    }
    return {key: next(record[name] for name in names if name in record)
            for key, names in aliases.items()}


def controller(record, *, warmup=False, target=False):
    if warmup:
        stopped = record["stopped_at_sequence_index"]
        return {
            "state": record["certification_state"], "threshold": record["tau"],
            "selected": record["calibration_selected"], "harmful": record["calibration_harmful"],
            "p_value": record["exact_p_value"], "cp_upper": record["exact_cp_upper"],
            "certified": record["thresholds_certified"], "stopped_at_index": stopped,
            "tested": 21 if stopped is None else stopped + 1,
        }
    prefix = "thresholds" if target else "hypotheses"
    tested = record[prefix + "_tested_before_stop"]
    return {
        "state": record["certification_state"], "threshold": record["tau"],
        "selected": record["selected"], "harmful": record["harmful"],
        "p_value": record["exact_p_value"], "cp_upper": record["cp_upper_95"],
        "certified": record[prefix + "_certified"], "tested": tested,
        "stopped_at_index": (tested - 1 if target else record["stopped_at_sequence_index"]),
    }


def warmup_run(record, *, priority_total):
    return {
        "n": record["n"], "replicate": record["replicate"],
        "controller": controller(record, warmup=True),
        "evaluation": evaluation(record["evaluation"], priority_total=priority_total),
    }


def design(record):
    fields = ("threshold", "development_selected", "development_harmful",
              "development_selected_fraction", "development_empirical_selected_error", "requested_fractions")
    return {
        "construction_n": record["construction_n"],
        "construction_years": record["construction_years"],
        "content_sha256": record["content_sha256"],
        "ordering": list(record["ordering"]),
        "family": [{"threshold": row["threshold"], "requested_fractions": row["requested_fractions"]}
                   for row in record["family"]],
        "sequence": [{key: row[key] for key in fields} for row in record["sequence"]],
    }
