"""Explicit field projections used to prepare the public evidence bundle.

No function emits row identities, raw text, paths, model coefficients, or weights.
The private adapter binds input hashes and supplies these already recorded
aggregate objects; calibration score/label vectors remain in memory there.
"""

from ..selected_risk import _counts, _integer, _probability


def counts(record, *, selected="selected", harmful="unsupported", population="n"):
    h, s = _counts(record[harmful], record[selected])
    n = _integer(record[population], population)
    if n < s:
        raise ValueError("invalid aggregate denominator")
    return {"n": n, "selected": s, "harmful": h}


def controller(record):
    """Preserve historical winner statistics and stop metadata as expectations."""
    return {
        "state": record["state"], "threshold": record["threshold"],
        "selected": record["selected"], "harmful": record["unsupported"],
        "p_value": record["exact_p_value"], "cp_upper": record["cp_upper_95"],
        "tested": record["hypotheses_tested"],
        "certified": record["hypotheses_certified"],
        "stopped_at_index": record["stopped_at_index"],
    }


def warmup_run(record):
    return {
        "alpha": _probability(record["alpha"], "alpha"),
        "replicate": record["replicate"],
        "requested_n": _integer(record["requested_n"], "requested_n"),
        "realized_n": _integer(record["realized_n"], "realized_n"),
        "calibration": controller(record["calibration"]),
        "evaluation": counts(record["evaluation"]),
    }


def emotion_counts(record):
    n = _integer(record["predicted_count"], "predicted_count")
    s = _integer(record["selected_count"], "selected_count")
    if not 0 <= s <= n:
        raise ValueError("invalid predicted-emotion counts")
    # The historical reporting floor suppresses errors in sparse slices.
    # Keep these missing, including for zero selection, rather than inventing them.
    h = record["unsupported"] if record["adequate_selected_n"] else None
    if h is not None:
        _counts(h, s)
    return {"n": n, "selected": s, "harmful": h,
            "adequate_selected_n": record["adequate_selected_n"]}
