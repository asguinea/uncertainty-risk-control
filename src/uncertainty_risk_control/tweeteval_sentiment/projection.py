"""Explicit aggregate field selection; no source text, identities or private paths."""

CLASSES = ("negative", "neutral", "positive")


def counts(record, n):
    return {"n": n, "selected": record["selected"], "harmful": record["errors"],
            "selected_by_class": {name: record["selected_class_distribution"][name] for name in CLASSES}}


def recorded_metrics(record):
    return {key: record[key] for key in ("automation", "selected_error", "review_rate")}


def controller(record, *, final=False):
    certified = record["hypotheses_certified" if final else "certified_hypotheses"]
    stop = record["stopped_at"]
    return {
        "state": "CERTIFIED" if record["certified"] else "REVIEW_ALL",
        "threshold": record["threshold"], "selected": record["selected"], "harmful": record["errors"],
        "p_value": record["p_value"], "cp_upper": record["cp_upper"],
        "certified": certified, "tested": record["hypotheses_tested"] if final else (20 if stop is None else stop + 1),
        "stopped_at_index": stop,
    }


def warmup(record):
    return {"requested_n": record["requested_n"], "realized_n": record["realized_n"],
            "replicate": record["replicate"], "calibration": controller(record["calibration"]),
            "evaluation": counts(record["evaluation"], 7142)}


def predicted_slice(record):
    return {"n": record.get("total_predicted", record.get("total_predictions")),
            "selected": record["selected"], "harmful": record["wrong_selected"],
            "expected": {"automation": record["automation"], "selected_error": record["selected_error"]}}


def reference_slice(record, *, final=False):
    n = record["support" if final else "reference_n"]
    review = record["review" if final else "review_n"]
    return {"n": n, "review": review, "accepted": record["auto_accepted"] if final else n - review,
            "expected_review_fraction": record["review_fraction"]}


def candidate(record):
    dev = record["development"]
    return {"threshold": record["threshold"], "requested_fractions": list(record["requested_fractions"]),
            "development": {"n": 26188, "selected": dev["selected"], "harmful": dev["errors"]},
            "expected": {key: dev[key] for key in ("automation", "selected_error", "p_value", "cp_upper")}}
