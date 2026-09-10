"""Validate frozen sufficient statistics and regenerate HumAID research summaries."""

from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path

from ..count_replay import replay_count_prefix
from ..selected_risk import _counts, _integer, _probability, clopper_pearson_upper, exact_binomial_lower_tail_scipy
from . import _aggregate_reference as historical

FILES = {"study.json", "design.json", "calibration.json", "evaluations.json", "warmup_runs.json", "expected.json"}
PERIODS = {"source_2018": (4774, 9559, 3141), "target_2019": (3075, 6159, 1778)}
CONTROLLER_FIELDS = {"state", "threshold", "selected", "harmful", "p_value", "cp_upper", "tested", "certified", "stopped_at_index"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), "unexpected aggregate schema fields")


def compare(actual, expected, path="result"):
    if type(expected) is dict:
        keys(actual, expected)
        for key in expected:
            compare(actual[key], expected[key], path + "." + key)
    elif type(expected) is list:
        require(type(actual) is list and len(actual) == len(expected), path + " list mismatch")
        for index, (a, e) in enumerate(zip(actual, expected)):
            compare(a, e, f"{path}[{index}]")
    elif type(expected) is float:
        require(type(actual) in (int, float) and math.isfinite(actual) and math.isfinite(expected)
                and abs(actual - expected) <= 1e-12, path + " numerical mismatch")
    else:
        require(type(actual) is type(expected) and actual == expected, path + " exact mismatch")


def strict_json(raw):
    def pairs(items):
        output = {}
        for key, value in items:
            require(key not in output, "duplicate JSON field")
            output[key] = value
        return output
    def finite(value):
        number = float(value)
        require(math.isfinite(number), "nonfinite JSON number")
        return number
    def invalid(value):
        raise ValueError("nonfinite JSON constant")
    return json.loads(raw, object_pairs_hook=pairs, parse_float=finite, parse_constant=invalid)


def metrics(counts):
    keys(counts, {"n", "selected", "harmful", "priority_total"})
    n = _integer(counts["n"], "n")
    h, s = _counts(counts["harmful"], counts["selected"])
    total = _integer(counts["priority_total"], "priority_total")
    require(0 <= h <= total <= n and s <= n and s - h <= n - total and n > 0, "invalid priority contingency counts")
    return {"automation_rate": s / n, "selected_error": h / s if s else None,
            "review_rate": 1 - s / n, "priority_recall_to_review": (total - h) / total if total else None}


def winner(result):
    c = result["controller"]
    return {key: value for key, value in asdict(c).items() if key != "certified_thresholds"} | {
        "certified": len(c.certified_thresholds), "tested": len(result["tests"])}


def validate_controller(c, *, n, sequence, alpha):
    keys(c, CONTROLLER_FIELDS)
    h, s = _counts(c["harmful"], c["selected"])
    require(s <= n, "calibration selected count exceeds population")
    tested, certified = (_integer(c[key], key) for key in ("tested", "certified"))
    require(1 <= tested <= len(sequence) and 0 <= certified <= tested, "invalid controller prefix length")
    stop = c["stopped_at_index"]
    if stop is None:
        require(tested == certified == len(sequence), "missing first failure")
    else:
        require(_integer(stop, "stop") == tested - 1 == certified, "inconsistent first failure")
    if c["state"] == "REVIEW_ALL":
        require(s == h == certified == 0 and c["threshold"] is c["p_value"] is c["cp_upper"] is None,
                "review-all must have undefined risk and no selected action")
    else:
        require(c["state"] == "CERTIFIED" and certified > 0 and s > 0, "invalid certification state")
        threshold = _probability(c["threshold"], "threshold", endpoints=True)
        require(threshold in [row["threshold"] for row in sequence[:certified]], "winner outside passing prefix")
        p = exact_binomial_lower_tail_scipy(h, s, alpha)
        compare(p, c["p_value"], "winner p-value")
        compare(clopper_pearson_upper(h, s, .05), c["cp_upper"], "winner CP")
        require(p <= .05, "recorded winner fails risk test")


def check_design(d):
    keys(d, {"construction_n", "construction_years", "content_sha256", "ordering", "family", "sequence"})
    require(d["construction_n"] == 37213 and d["construction_years"] == [2016, 2017], "development population changed")
    require(d["ordering"] == ["development empirical selected error ascending", "development selected fraction descending", "threshold ascending"], "ordering changed")
    sequence = d["sequence"]
    require(len(sequence) == 21 and len(d["family"]) == 22, "candidate cardinality changed")
    family = []
    for row in d["family"]:
        keys(row, {"threshold", "requested_fractions"})
        family.append(_probability(row["threshold"], "threshold", endpoints=True))
        require(type(row["requested_fractions"]) is list, "invalid fractions")
        for fraction in row["requested_fractions"]:
            _probability(fraction, "fraction", endpoints=True)
    require(len(set(family)) == 22 and family[0] == 0, "family duplicates or boundary changed")
    for row in sequence:
        keys(row, {"threshold", "development_selected", "development_harmful", "development_selected_fraction", "development_empirical_selected_error", "requested_fractions"})
        h, s = _counts(row["development_harmful"], row["development_selected"])
        require(0 < s <= 37213 and row["threshold"] in family[1:], "invalid development candidate")
        compare(s / 37213, row["development_selected_fraction"])
        compare(h / s, row["development_empirical_selected_error"])
        compare(row["requested_fractions"], d["family"][family.index(row["threshold"])]["requested_fractions"])
    require(set(row["threshold"] for row in sequence) == set(family[1:]), "sequence membership changed")
    require(sequence == sorted(sequence, key=lambda row: (row["development_empirical_selected_error"], -row["development_selected_fraction"], row["threshold"])), "sequence not in frozen development order")
    return sequence


def milestones(aggregates, *, target):
    utility_key = "evaluation_automation_rate" if target else "evaluation_auto_deprioritization_rate"
    ordered = sorted(aggregates, key=int)
    def first(predicate):
        return next((int(n) for n in ordered if predicate(aggregates[n])), None)
    result = {"first_any_certification": first(lambda a: a["certified_runs"] > 0)}
    for percent in (50, 80, 90):
        result[f"first_certification_frequency_ge_{percent}pct"] = first(lambda a: a["certification_frequency"] >= percent / 100)
    for percent in ((10, 25, 50) if target else (10, 25, 50, 75)):
        result[f"first_median_utility_ge_{percent}pct"] = first(lambda a: a[utility_key]["median"] >= percent / 100)
    for percent in (10, 25, 50):
        result[f"first_90pct_certification_and_{percent}pct_utility"] = first(lambda a: a["certification_frequency"] >= .9 and a[utility_key]["median"] >= percent / 100)
    return result


def warmup_summary(groups, sequence, *, period):
    full, _, priority_total = PERIODS[period]
    target = period == "target_2019"
    keys(groups, {str(n) for n in (50, 100, 200, 500, 1000, 2000, full)})
    aggregates = {}
    evaluation_by_threshold = {}
    for size in sorted(groups, key=int):
        rows = groups[size]
        require(type(rows) is list, "warm-up runs must be a list")
        expected_ids = ["FULL_POOL"] if int(size) == full else list(range(100))
        require([row["replicate"] for row in rows] == expected_ids, "warm-up replicate coverage changed")
        rebuilt = []
        for row in rows:
            keys(row, {"n", "replicate", "controller", "evaluation"})
            require(_integer(row["n"], "n") == int(size), "warm-up size mismatch")
            if row["replicate"] != "FULL_POOL":
                _integer(row["replicate"], "replicate")
            c, e = row["controller"], row["evaluation"]
            validate_controller(c, n=int(size), sequence=sequence, alpha=.05)
            m = metrics(e)
            require(e["n"] == full and e["priority_total"] == priority_total, "warm-up evaluation population changed")
            certified = c["state"] == "CERTIFIED"
            require(certified or e["selected"] == 0, "review-all selected evaluation rows")
            threshold = c["threshold"]
            require(threshold not in evaluation_by_threshold or evaluation_by_threshold[threshold] == e,
                    "same policy has inconsistent counts on fixed warm-up evaluation pool")
            evaluation_by_threshold[threshold] = e
            rebuilt.append({"certified": certified, "tau": c["threshold"], "calibration_selected": c["selected"],
                            "calibration_harmful": c["harmful"], "exact_cp_upper": c["cp_upper"],
                            "evaluation": {"selected": e["selected"], "observed_selected_error": m["selected_error"],
                                           "automation_rate": m["automation_rate"], "auto_deprioritization_rate": m["automation_rate"]}})
        fn = historical.aggregate_target if target else historical.aggregate_source
        aggregates[size] = fn(rebuilt)
    return {"runs": sum(len(rows) for rows in groups.values()), "aggregates": aggregates,
            "milestones": milestones(aggregates, target=target)}


def replay(evidence):
    evidence = Path(evidence)
    require(evidence.is_dir() and not evidence.is_symlink(), "ordinary evidence directory required")
    require((evidence / "manifest.json").is_file() and not (evidence / "manifest.json").is_symlink(), "ordinary manifest file required")
    raw_manifest = (evidence / "manifest.json").read_bytes()
    manifest = strict_json(raw_manifest)
    keys(manifest, {"schema_version", "study", "files", "implementation"})
    require(manifest["schema_version"] == 1 and manifest["study"] == "humaid", "unsupported evidence manifest")
    keys(manifest["files"], FILES)
    require({p.name for p in evidence.iterdir()} == FILES | {"manifest.json"}, "unexpected evidence files")
    bundle = {}
    for name, digest in manifest["files"].items():
        p = evidence / name
        require(p.is_file() and not p.is_symlink(), "ordinary evidence file required")
        raw = p.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest, "evidence hash mismatch: " + name)
        bundle[name[:-5]] = strict_json(raw)
    code = {"count_replay.py": Path(__file__).parents[1] / "count_replay.py",
            "projection.py": Path(__file__).with_name("projection.py"),
            "_aggregate_reference.py": Path(__file__).with_name("_aggregate_reference.py")}
    keys(manifest["implementation"], code)
    for name, p in code.items():
        require(hashlib.sha256(p.read_bytes()).hexdigest() == manifest["implementation"][name], "implementation hash mismatch")
    study = bundle["study"]
    keys(study, {"schema_version", "study", "source_hashes", "roles", "scope"})
    require(study["schema_version"] == 1 and study["study"] == "humaid", "unsupported study")
    require(study["roles"] == {"source_2018": {"warmup_calibration": 4774, "warmup_evaluation": 4774, "final_calibration": 4774, "locked_evaluation": 9559}, "target_2019": {"warmup_calibration": 3075, "warmup_evaluation": 3075, "final_calibration": 3075, "locked_evaluation": 6159}}, "role sizes changed")
    sequence = check_design(bundle["design"])
    keys(bundle["calibration"], PERIODS)
    finals = {}
    for period, (n, _, _) in PERIODS.items():
        group = bundle["calibration"][period]
        keys(group, {"n", "priority_total", "counts", "budgets"})
        require(group["n"] == n and group["priority_total"] == (3149 if period == "source_2018" else 1832), "final calibration population changed")
        budgets = {"0.025": 3, "0.05": 4, "0.1": 5} if period == "source_2018" else {"0.05": 4}
        keys(group["budgets"], budgets)
        require(len(group["counts"]) == max(budgets.values()), "unexpected count union length")
        for row in group["counts"]:
            metrics({"n": n, "selected": row["selected"], "harmful": row["harmful"], "priority_total": group["priority_total"]})
        finals[period] = {}
        for alpha, tested in budgets.items():
            expected = group["budgets"][alpha]
            validate_controller(expected, n=n, sequence=sequence, alpha=float(alpha))
            require(expected["tested"] == tested, "historical prefix length changed")
            result = replay_count_prefix(sequence, group["counts"][:tested], n=n, alpha=float(alpha), delta=.05)
            actual = winner(result)
            require(actual["threshold"] == expected["threshold"], "winner threshold differs exactly")
            compare(actual, expected)
            finals[period][alpha] = {"controller": actual, "tests": result["tests"]}
    evaluations = bundle["evaluations"]
    require(type(evaluations) is list, "evaluations must be a list")
    ids = set()
    for row in evaluations:
        keys(row, {"id", "period", "role", "policy", "alpha", "threshold", "event", "counts", "expected"})
        require(row["id"] not in ids, "duplicate evaluation id")
        ids.add(row["id"])
        require(row["period"] in PERIODS and row["role"] in {"warmup_evaluation", "locked_evaluation"}, "unknown evaluation role")
        compare(metrics(row["counts"]), row["expected"])
        require(row["policy"] in {"calibrated", "zero_shot", "AUTO_DEPRIORITIZE_ALL", "RAW_0_5_CLASSIFIER_THRESHOLD", "REVIEW_ALL"}, "unknown policy")
        if row["event"] is None:
            require(row["counts"]["n"] == study["roles"][row["period"]][row["role"]], "evaluation denominator changed")
        if row["policy"] == "REVIEW_ALL":
            require(row["counts"]["selected"] == 0 and row["threshold"] is None, "review-all evaluation changed")
        elif row["policy"] == "AUTO_DEPRIORITIZE_ALL":
            require(row["counts"]["selected"] == row["counts"]["n"] and row["threshold"] == 1., "auto-all changed")
        elif row["policy"] == "RAW_0_5_CLASSIFIER_THRESHOLD":
            require(row["threshold"] == .5, "baseline threshold changed")
        elif row["role"] == "locked_evaluation":
            require(row["threshold"] == finals[row["period"]][str(row["alpha"])]["controller"]["threshold"], "evaluation not bound to frozen controller")
        elif row["policy"] == "zero_shot":
            require(row["period"] == "target_2019" and row["threshold"] == finals["source_2018"]["0.05"]["controller"]["threshold"], "zero-shot source policy changed")
    # Event partitions must sum to their pooled action and reference counts.
    for pooled in (row for row in evaluations if row["event"] is None):
        slices = [row for row in evaluations if row["event"] is not None and all(row[k] == pooled[k] for k in ("period", "role", "policy", "alpha"))]
        if slices:
            for key in ("n", "selected", "harmful", "priority_total"):
                require(sum(row["counts"][key] for row in slices) == pooled["counts"][key], "event counts do not partition pooled evaluation")
    keys(bundle["warmup_runs"], PERIODS)
    summaries = {period: warmup_summary(bundle["warmup_runs"][period], sequence, period=period) for period in PERIODS}
    expected = bundle["expected"]
    keys(expected, {"warmup", "evaluation_ids", "source_trace_tests"})
    require(sorted(ids) == expected["evaluation_ids"], "evaluation coverage changed")
    compare(summaries, expected["warmup"])
    compare(finals["source_2018"], expected["source_trace_tests"])
    return {"kind": "humaid_aggregate_replay", "scope": study["scope"],
            "evidence_manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
            "final_candidate_tests": sum(len(r["tests"]) for group in finals.values() for r in group.values()),
            "warmup_records": sum(r["runs"] for r in summaries.values()),
            "final_calibration": finals, "warmup": summaries, "evaluations": evaluations}
