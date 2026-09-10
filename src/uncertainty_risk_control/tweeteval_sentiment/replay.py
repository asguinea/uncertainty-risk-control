"""Strict sufficient-statistics replay of the frozen TweetEval Sentiment study."""

from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path

from ..count_replay import replay_count_prefix
from ..selected_risk import _counts, _integer, _probability, clopper_pearson_upper, exact_binomial_lower_tail_scipy
from . import _aggregate_reference as historical
from .projection import CLASSES

BUDGETS = {"0.025": 1, "0.05": 8, "0.1": 12, "0.15": 14}
ROLES = {"MODEL_DEVELOPMENT": 26188, "WARMUP_CALIBRATION": 7142, "WARMUP_EVALUATION": 7142, "FINAL_CALIBRATION": 7143, "LOCKED_TEST": 12284}
FILES = {"study.json", "design.json", "calibration.json", "evaluations.json", "warmup_runs.json", "expected.json"}
BASELINES = {"review_all", "accept_all", "raw_confidence_0.5", "raw_confidence_0.8", "raw_confidence_0.9"}
CONTROLLER_FIELDS = {"state", "threshold", "selected", "harmful", "p_value", "cp_upper", "certified", "tested", "stopped_at_index"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), "unexpected evidence schema fields")


def compare(actual, expected, path="result"):
    if type(expected) is dict:
        keys(actual, expected)
        for key in expected:
            compare(actual[key], expected[key], path + "." + key)
    elif type(expected) is list:
        require(type(actual) is list and len(actual) == len(expected), path + " list mismatch")
        for i, (a, e) in enumerate(zip(actual, expected)):
            compare(a, e, f"{path}[{i}]")
    elif type(expected) is float:
        require(type(actual) in (int, float) and math.isfinite(actual) and math.isfinite(expected) and abs(actual - expected) <= 1e-12, path + " numerical mismatch")
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


def metrics(counts, *, classes=True):
    keys(counts, {"n", "selected", "harmful", "selected_by_class"} if classes else {"n", "selected", "harmful"})
    n = _integer(counts["n"], "n")
    h, s = _counts(counts["harmful"], counts["selected"])
    require(n > 0 and s <= n, "invalid selection population")
    if classes:
        keys(counts["selected_by_class"], CLASSES)
        values = [_integer(counts["selected_by_class"][name], name) for name in CLASSES]
        require(all(v >= 0 for v in values) and sum(values) == s, "selected class counts do not partition selections")
    return {"automation": s / n, "selected_error": h / s if s else None, "review_rate": 1 - s / n}


def winner(result):
    c = result["controller"]
    return {k: v for k, v in asdict(c).items() if k != "certified_thresholds"} | {"certified": len(c.certified_thresholds), "tested": len(result["tests"])}


def validate_controller(c, *, n, sequence, alpha):
    keys(c, CONTROLLER_FIELDS)
    h, s = _counts(c["harmful"], c["selected"])
    require(s <= n, "winner exceeds calibration population")
    tested, certified = (_integer(c[k], k) for k in ("tested", "certified"))
    require(1 <= tested <= 20 and 0 <= certified <= tested, "invalid prefix length")
    stop = c["stopped_at_index"]
    if stop is None:
        require(tested == certified == 20, "incomplete controller prefix")
    else:
        require(_integer(stop, "stop") == tested - 1 == certified, "inconsistent first failure")
    if c["state"] == "REVIEW_ALL":
        require(s == h == certified == 0 and c["threshold"] is c["p_value"] is c["cp_upper"] is None, "review-all requires zero actions and undefined winner diagnostics")
    else:
        require(c["state"] == "CERTIFIED" and certified > 0 and s > 0, "invalid certification state")
        tau = _probability(c["threshold"], "threshold", endpoints=True)
        require(tau in [r["threshold"] for r in sequence[:certified]], "winner outside passing prefix")
        p = exact_binomial_lower_tail_scipy(h, s, alpha)
        compare(p, c["p_value"])
        compare(clopper_pearson_upper(h, s, .05), c["cp_upper"])
        require(p <= .05, "winner does not pass")


def verify_design(design):
    keys(design, {"family_sha256", "sequence_sha256", "ordering", "family", "sequence"})
    require(design["ordering"] == ["CP upper ascending", "automation descending", "tau ascending"], "fixed ordering changed")
    family, sequence = design["family"], design["sequence"]
    require(len(family) == len(sequence) == 20, "candidate count changed")
    thresholds = []
    for row in family:
        keys(row, {"threshold", "requested_fractions", "development", "expected"})
        tau = _probability(row["threshold"], "threshold", endpoints=True)
        thresholds.append(tau)
        require(type(row["requested_fractions"]) is list and row["requested_fractions"], "missing development fractions")
        for f in row["requested_fractions"]:
            _probability(f, "fraction")
        d = row["development"]
        require(_integer(d["n"], "n") == 26188, "development population changed")
        m = metrics(d, classes=False)
        require(d["selected"] > 0, "empty development candidate")
        compare({"automation": m["automation"], "selected_error": m["selected_error"],
                 "p_value": exact_binomial_lower_tail_scipy(d["harmful"], d["selected"], .05),
                 "cp_upper": clopper_pearson_upper(d["harmful"], d["selected"], .05)}, row["expected"])
    require(thresholds == sorted(set(thresholds)), "family thresholds must be unique and ordered")
    for row in sequence:
        keys(row, {"threshold"})
        _probability(row["threshold"], "threshold", endpoints=True)
    ordered = sorted(family, key=lambda r: (r["expected"]["cp_upper"], -r["expected"]["automation"], r["threshold"]))
    require(sequence == [{"threshold": r["threshold"]} for r in ordered], "sequence differs from frozen development CP order")
    return sequence


def verify_warmup(runs, sequence):
    keys(runs, BUDGETS)
    rebuilt = {}
    fixed_evaluation = {}
    for alpha, groups in runs.items():
        keys(groups, {str(tier) for tier in historical.TIERS})
        rebuilt[alpha] = {}
        for size, rows in groups.items():
            require(type(rows) is list, "warm-up rows must be a list")
            expected_ids = ["full"] if size == "7142" else list(range(100))
            require([r["replicate"] for r in rows] == expected_ids, "warm-up replicate coverage changed")
            rebuilt[alpha][size] = []
            for r in rows:
                keys(r, {"requested_n", "realized_n", "replicate", "calibration", "evaluation"})
                require(_integer(r["requested_n"], "requested_n") == _integer(r["realized_n"], "realized_n") == int(size), "historical realized size changed")
                if r["replicate"] != "full":
                    _integer(r["replicate"], "replicate")
                c, e = r["calibration"], r["evaluation"]
                validate_controller(c, n=r["realized_n"], sequence=sequence, alpha=float(alpha))
                m = metrics(e)
                require(e["n"] == 7142, "warm-up evaluation population changed")
                certified = c["state"] == "CERTIFIED"
                require(certified or e["selected"] == 0, "review-all selected evaluation rows")
                tau = c["threshold"]
                require(tau not in fixed_evaluation or fixed_evaluation[tau] == e, "same threshold changed on fixed warm-up evaluation pool")
                fixed_evaluation[tau] = e
                s, h = c["selected"], c["harmful"]
                old = {"certified": certified, "review_all": not certified, "threshold": tau,
                       "selected": s, "errors": h, "automation": s / r["realized_n"], "selected_error": h / s if s else None,
                       "p_value": c["p_value"], "cp_upper": c["cp_upper"], "certified_hypotheses": c["certified"], "stopped_at": c["stopped_at_index"]}
                rebuilt[alpha][size].append({"requested_n": r["requested_n"], "realized_n": r["realized_n"], "replicate": r["replicate"],
                    "calibration": old, "evaluation": {**m, "selected": e["selected"], "errors": e["harmful"], "selected_class_distribution": e["selected_by_class"]}})
    result = historical.aggregate(rebuilt)
    return {"records": sum(len(rows) for groups in runs.values() for rows in groups.values()),
            "aggregation": result["aggregation"], "milestones": result["milestones"]}


def verify_evaluations(evaluations, finals, runs):
    keys(evaluations, {"WARMUP_EVALUATION", "LOCKED_TEST"})
    for role, group in evaluations.items():
        keys(group, {"n", "controllers", "baselines"})
        require(_integer(group["n"], "n") == ROLES[role], "evaluation role size changed")
        keys(group["controllers"], BUDGETS)
        keys(group["baselines"], BASELINES)
        fixed_predicted, fixed_reference = None, None
        by_threshold = {}
        for alpha, row in group["controllers"].items():
            keys(row, {"counts", "expected", "threshold", "predicted_class", "reference_class"})
            c = finals[alpha]["controller"] if role == "LOCKED_TEST" else runs[alpha]["7142"][0]["calibration"]
            require(row["threshold"] == c["threshold"], "evaluation controller threshold mismatch")
            e = row["counts"]
            require(e["n"] == group["n"], "evaluation count denominator changed")
            compare(metrics(e), row["expected"])
            require(c["state"] != "REVIEW_ALL" or e["selected"] == 0, "review-all evaluation has selections")
            if role == "WARMUP_EVALUATION":
                compare(e, runs[alpha]["7142"][0]["evaluation"])
            keys(row["predicted_class"], CLASSES)
            keys(row["reference_class"], CLASSES)
            predicted, reference = {}, {}
            for name in CLASSES:
                p, r = row["predicted_class"][name], row["reference_class"][name]
                keys(p, {"n", "selected", "harmful", "expected"})
                m = metrics({k: p[k] for k in ("n", "selected", "harmful")}, classes=False)
                compare({k: m[k] for k in ("automation", "selected_error")}, p["expected"])
                require(p["selected"] == e["selected_by_class"][name], "predicted class selection mismatch")
                keys(r, {"n", "review", "accepted", "expected_review_fraction"})
                n, review, accepted = (_integer(r[k], k) for k in ("n", "review", "accepted"))
                require(n > 0 and 0 <= review <= n and accepted == n - review, "invalid reference review counts")
                compare(review / n, r["expected_review_fraction"])
                correct = p["selected"] - p["harmful"]
                reference_errors = accepted - correct
                require(reference_errors >= 0 and p["harmful"] + reference_errors <= e["harmful"],
                        "predicted and reference margins cannot describe the same selected labels")
                predicted[name], reference[name] = p["n"], n
            require(sum(predicted.values()) == sum(reference.values()) == group["n"], "class populations do not partition evaluation")
            require(sum(p["harmful"] for p in row["predicted_class"].values()) == e["harmful"], "class errors do not partition selected errors")
            require(sum(r["accepted"] for r in row["reference_class"].values()) == e["selected"], "reference selections do not partition selections")
            require(fixed_predicted is None or predicted == fixed_predicted, "predicted population changed between budgets")
            require(fixed_reference is None or reference == fixed_reference, "reference population changed between budgets")
            fixed_predicted, fixed_reference = predicted, reference
            if row["threshold"] is not None:
                require(row["threshold"] not in by_threshold or by_threshold[row["threshold"]] == e,
                        "same threshold has different evaluation counts")
                by_threshold[row["threshold"]] = e
        for name, row in group["baselines"].items():
            keys(row, {"counts", "expected"})
            e = row["counts"]
            require(e["n"] == group["n"], "baseline population changed")
            compare(metrics(e), row["expected"])
            require(all(e["selected_by_class"][c] <= fixed_predicted[c] for c in CLASSES), "baseline class selection exceeds population")
            if name == "review_all":
                require(e["selected"] == 0, "review-all baseline changed")
            elif name == "accept_all":
                require(e["selected"] == group["n"] and e["selected_by_class"] == fixed_predicted, "accept-all baseline changed")
        ordered = sorted(by_threshold.items())
        for (_, low), (_, high) in zip(ordered, ordered[1:]):
            ds, dh = high["selected"] - low["selected"], high["harmful"] - low["harmful"]
            require(0 <= dh <= ds and all(high["selected_by_class"][c] >= low["selected_by_class"][c] for c in CLASSES), "nonnested evaluation selections")
    locked = evaluations["LOCKED_TEST"]["controllers"]["0.05"]["reference_class"]
    require({name: locked[name]["n"] for name in CLASSES} == {"negative": 3972, "neutral": 5937, "positive": 2375}, "locked reference support changed")


def load_bundle(evidence):
    evidence = Path(evidence)
    require(evidence.is_dir() and not evidence.is_symlink(), "ordinary evidence directory required")
    p = evidence / "manifest.json"
    require(p.is_file() and not p.is_symlink(), "ordinary manifest required")
    raw = p.read_bytes()
    manifest = strict_json(raw)
    keys(manifest, {"schema_version", "study", "files", "implementation"})
    require(manifest["schema_version"] == 1 and manifest["study"] == "tweeteval-sentiment", "unsupported evidence manifest")
    keys(manifest["files"], FILES)
    require({p.name for p in evidence.iterdir()} == FILES | {"manifest.json"}, "unexpected evidence files")
    bundle = {}
    for name, digest in manifest["files"].items():
        p = evidence / name
        require(p.is_file() and not p.is_symlink(), "ordinary evidence file required")
        data = p.read_bytes()
        require(hashlib.sha256(data).hexdigest() == digest, "evidence hash mismatch: " + name)
        bundle[name[:-5]] = strict_json(data)
    code = {"count_replay.py": Path(__file__).parents[1] / "count_replay.py", "projection.py": Path(__file__).with_name("projection.py"), "_aggregate_reference.py": Path(__file__).with_name("_aggregate_reference.py")}
    keys(manifest["implementation"], code)
    for name, path in code.items():
        require(hashlib.sha256(path.read_bytes()).hexdigest() == manifest["implementation"][name], "implementation hash mismatch")
    return bundle, hashlib.sha256(raw).hexdigest()


def replay(evidence):
    bundle, manifest_hash = load_bundle(evidence)
    study = bundle["study"]
    keys(study, {"schema_version", "study", "classes", "roles", "source_revision", "scorer", "source_hashes", "scope"})
    require(study["schema_version"] == 1 and study["study"] == "tweeteval-sentiment", "unsupported study")
    require(study["classes"] == list(CLASSES) and study["roles"] == ROLES, "study populations changed")
    sequence = verify_design(bundle["design"])
    calibration = bundle["calibration"]
    keys(calibration, {"n", "reference_support", "counts", "budgets"})
    require(_integer(calibration["n"], "n") == 7143 and calibration["reference_support"] == {"negative": 1118, "neutral": 3220, "positive": 2805}, "final calibration population changed")
    keys(calibration["budgets"], BUDGETS)
    require(len(calibration["counts"]) == 14, "historical count union length changed")
    finals = {}
    for alpha, length in BUDGETS.items():
        expected = calibration["budgets"][alpha]
        validate_controller(expected, n=7143, sequence=sequence, alpha=float(alpha))
        require(expected["tested"] == length, "historical prefix length changed")
        result = replay_count_prefix(sequence, calibration["counts"][:length], n=7143, alpha=float(alpha), delta=.05)
        actual = winner(result)
        require(actual["threshold"] == expected["threshold"], "winner threshold differs exactly")
        compare(actual, expected)
        finals[alpha] = {"controller": actual, "tests": result["tests"]}
    warmup = verify_warmup(bundle["warmup_runs"], sequence)
    keys(bundle["expected"], {"aggregation", "milestones"})
    compare({k: warmup[k] for k in ("aggregation", "milestones")}, bundle["expected"])
    verify_evaluations(bundle["evaluations"], finals, bundle["warmup_runs"])
    return {"kind": "tweeteval_sentiment_aggregate_replay", "scope": study["scope"],
            "evidence_manifest_sha256": manifest_hash, "final_candidate_tests": sum(len(r["tests"]) for r in finals.values()),
            "warmup_records": warmup["records"], "final_calibration": finals, "warmup": warmup,
            "warmup_full_controllers": {a: groups["7142"][0]["calibration"] for a, groups in bundle["warmup_runs"].items()},
            "final_reference_support": calibration["reference_support"], "evaluations": bundle["evaluations"]}
