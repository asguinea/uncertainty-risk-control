"""Verify the frozen MB1 evidence and regenerate descriptive statistics."""

import hashlib
from importlib.resources import files
import json
import math
from pathlib import Path

from ..count_replay import replay_count_prefix
from ..selected_risk import _counts, _integer, clopper_pearson_upper, exact_binomial_lower_tail_scipy
from ._aggregate_reference import REQUESTED_TIERS, aggregate_runs, milestones

BUDGETS = (0.05, 0.1, 0.15, 0.2)
BUDGET_KEYS = tuple(map(str, BUDGETS))
EXPECTED_FILES = {
    "study.json", "design.json", "calibration.json", "evaluations.json",
    "warmup_runs.json", "expected.json", "development_history.json",
}
BASELINES = {"REVIEW_ALL", "ACCEPT_ALL_TOP_TAGS", "RAW_CONFIDENCE_GE_0_5", "RAW_CONFIDENCE_GE_0_8", "RAW_CONFIDENCE_GE_0_9"}
PROJECTION_FILES = {
    "src/uncertainty_risk_control/count_replay.py",
    "src/uncertainty_risk_control/goemotions/projection.py",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def strict_json(content):
    def invalid(value):
        raise ValueError(f"nonfinite JSON number: {value}")
    def finite_float(value):
        number = float(value)
        require(math.isfinite(number), "nonfinite JSON number")
        return number
    return json.loads(content, object_pairs_hook=_unique_pairs, parse_constant=invalid, parse_float=finite_float)


def compare(actual, expected, path="result"):
    """Exact structural/integer comparison; at most 1e-12 for probabilities/rates."""
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), f"{path}: fields differ")
        for key in expected:
            compare(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), f"{path}: length differs")
        for index, (left, right) in enumerate(zip(actual, expected)):
            compare(left, right, f"{path}[{index}]")
    elif type(expected) is float:
        require(type(actual) in (int, float) and math.isfinite(actual) and abs(actual - expected) <= 1e-12, f"{path}: numeric mismatch")
    else:
        require(type(actual) is type(expected) and actual == expected, f"{path}: exact value mismatch")


def metrics(row):
    require(set(row) == {"n", "selected", "harmful"}, "unexpected aggregate count fields")
    h, s = _counts(row["harmful"], row["selected"])
    n = _integer(row["n"], "n")
    require(n >= s, "selected count exceeds population")
    return {"n": n, "selected": s, "harmful": h, "automation": s / n if n else None,
            "selected_error": h / s if s else None, "supported": s - h,
            "review_count": n - s, "review_rate": 1 - s / n if n else None}


def controller_summary(replayed):
    result = replayed["controller"]
    return {
        **{key: getattr(result, key) for key in ("state", "threshold", "selected", "harmful", "p_value", "cp_upper", "stopped_at_index")},
        "tested": len(replayed["tests"]), "certified": len(result.certified_thresholds),
    }


def load_bundle(directory):
    root = Path(directory).resolve()
    manifest_bytes = (root / "manifest.json").read_bytes()
    manifest = strict_json(manifest_bytes)
    require(manifest["schema_version"] == 1 and manifest["study_id"] == "GOEMOTIONS_MB1", "unsupported study manifest")
    require(set(manifest["files"]) == EXPECTED_FILES, "unexpected evidence file set")
    bundle = {}
    for name, expected_hash in manifest["files"].items():
        path = root / name
        require(not path.is_symlink(), "evidence symlinks are not supported")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == expected_hash, f"evidence hash mismatch: {name}")
        bundle[name.removesuffix(".json")] = strict_json(raw)
    require(set(manifest["projection_code"]) == PROJECTION_FILES, "unexpected projection code list")
    package = files("uncertainty_risk_control")
    for name, expected_hash in manifest["projection_code"].items():
        relative = name.removeprefix("src/uncertainty_risk_control/")
        require(hashlib.sha256(package.joinpath(relative).read_bytes()).hexdigest() == expected_hash, "projection implementation differs from recorded extraction")
    return bundle, hashlib.sha256(manifest_bytes).hexdigest()


def verify_design(design):
    candidates, sequence = design["candidates"], design["sequence"]
    require(len(candidates) == len(sequence) == 21, "MB1 requires 21 frozen candidates")
    require(design["design_n"] == 8139 and design["canonical_development_n"] == 27131, "design population changed")
    require(design["review_all_boundary_tested"] is False, "review-all boundary must remain untested")
    require(len({row["threshold"] for row in candidates}) == 21, "candidate thresholds must be distinct")
    require(design["review_all_boundary"] < min(row["threshold"] for row in candidates), "review-all boundary changed")
    for row in candidates:
        _counts(row["design_harmful"], row["design_selected"])
        require(0 < row["design_selected"] <= 8139, "invalid design selected count")
        require(0 < _integer(row["canonical_selected"], "canonical_selected") <= 27131, "invalid canonical count")
        compare(clopper_pearson_upper(row["design_harmful"], row["design_selected"]), row["design_cp_upper"], "design.cp_upper")
    ordered = sorted(candidates, key=lambda row: (row["design_cp_upper"], -row["design_selected"] / 8139, row["threshold"]))
    # Thresholds/order are identities, so equality here is exact, not tolerant.
    require([row["threshold"] for row in ordered] == [row["threshold"] for row in sequence], "frozen sequence disagrees with design-only ordering")
    require([row["threshold"] for row in candidates] == [row["threshold"] for row in sequence], "candidate/sequence correspondence changed")
    return sequence


def verify_evaluations(evaluations, emotions):
    result = {}
    require(set(evaluations) == {"LOCKED_TEST", "WARMUP_EVALUATION"}, "evaluation roles changed")
    for role, evidence in evaluations.items():
        n = 10853 if role == "LOCKED_TEST" else 5426
        floor = 30 if role == "LOCKED_TEST" else 20
        require(evidence["n"] == n and evidence["emotion_reporting_floor"] == floor, "evaluation denominator/floor changed")
        require(set(evidence["controllers"]) == set(BUDGET_KEYS), "controller budgets changed")
        require(set(evidence["baselines"]) == BASELINES, "baseline set changed")
        require(set(evidence["consensus"]) == set(evidence["predicted_emotion"]) == set(BUDGET_KEYS), "subgroup budgets changed")
        totals = {key: metrics(row) for key, row in evidence["controllers"].items()}
        baselines = {key: metrics(row) for key, row in evidence["baselines"].items()}
        require(all(row["n"] == n for row in [*totals.values(), *baselines.values()]), "pooled denominator changed")
        require(baselines["REVIEW_ALL"]["selected"] == 0 and baselines["ACCEPT_ALL_TOP_TAGS"]["selected"] == n, "extreme baseline semantics changed")
        consensus, emotion = {}, {}
        for key in BUDGET_KEYS:
            slices = evidence["consensus"][key]
            require(set(slices) == {"HIGH_CONSENSUS", "MEDIUM_CONSENSUS", "LOW_CONSENSUS"}, "consensus strata changed")
            consensus[key] = {name: metrics(row) for name, row in slices.items()}
            for field in ("n", "selected", "harmful"):
                require(sum(row[field] for row in slices.values()) == totals[key][field], "consensus slices do not reconcile to pooled counts")
            slices = evidence["predicted_emotion"][key]
            require(set(slices) == set(emotions), "predicted-emotion taxonomy changed")
            for field in ("n", "selected"):
                require(sum(row[field] for row in slices.values()) == totals[key][field], "emotion slices do not reconcile to pooled counts")
            emotion[key] = {}
            known_harmful, unreported_selected = 0, 0
            for name, row in slices.items():
                require(set(row) == {"n", "selected", "harmful", "adequate_selected_n"}, "unexpected emotion fields")
                n_slice, selected = _integer(row["n"], "n"), _integer(row["selected"], "selected")
                require(0 <= selected <= n_slice, "invalid emotion counts")
                require(type(row["adequate_selected_n"]) is bool and row["adequate_selected_n"] == (selected >= floor), "emotion reporting floor mismatch")
                if row["adequate_selected_n"]:
                    measured = metrics({field: row[field] for field in ("n", "selected", "harmful")})
                    known_harmful += measured["harmful"]
                    emotion[key][name] = {**measured, "adequate_selected_n": True}
                else:
                    require(row["harmful"] is None, "historically unreported sparse error must remain missing")
                    unreported_selected += selected
                    emotion[key][name] = {**row, "automation": selected / n_slice if n_slice else None, "selected_error": None}
            require(known_harmful <= totals[key]["harmful"] <= known_harmful + unreported_selected, "reported emotion errors contradict pooled count")
        result[role] = {"controllers": totals, "baselines": baselines, "consensus": consensus,
                        "predicted_emotion": emotion, "emotion_reporting_floor": floor}
    return result


def verify_warmup(runs, sequence):
    require(len(runs) == 2804, "expected 2804 warm-up aggregate run records")
    thresholds = {row["threshold"] for row in sequence}
    seen, normalized = set(), []
    required_controller = {"state", "threshold", "selected", "harmful", "p_value", "cp_upper", "tested", "certified", "stopped_at_index"}
    for row in runs:
        require(set(row) == {"alpha", "replicate", "requested_n", "realized_n", "calibration", "evaluation"}, "unexpected warm-up fields")
        key = (row["alpha"], row["requested_n"], row["replicate"])
        require(row["alpha"] in BUDGETS and key not in seen, "invalid/duplicate warm-up record")
        seen.add(key)
        requested = _integer(row["requested_n"], "requested_n")
        realized = _integer(row["realized_n"], "realized_n")
        if row["replicate"] == "FULL":
            require(requested == realized == 5427, "full warm-up population changed")
        else:
            require(0 <= _integer(row["replicate"], "replicate") < 100 and requested in REQUESTED_TIERS, "warm-up replicate/tier changed")
            require(0 < realized <= requested, "whole-group prefix exceeds requested size")
        cal = row["calibration"]
        require(set(cal) == required_controller, "unexpected warm-up controller fields")
        h, s = _counts(cal["harmful"], cal["selected"])
        require(s <= realized, "warm-up selected count exceeds population")
        require(cal["state"] in {"CERTIFIED", "REVIEW_ALL"}, "unknown warm-up state")
        certified = cal["state"] == "CERTIFIED"
        passed = _integer(cal["certified"], "certified")
        tested = _integer(cal["tested"], "tested")
        if cal["stopped_at_index"] is None:
            require(passed == tested == 21, "incomplete fully passing warm-up sequence")
        else:
            stopped = _integer(cal["stopped_at_index"], "stopped_at_index")
            require(0 <= stopped < 21 and passed == stopped and tested == stopped + 1, "inconsistent recorded warm-up stop metadata")
        if certified:
            require(s > 0 and passed > 0 and cal["threshold"] in thresholds, "invalid certified warm-up winner")
            p_value = exact_binomial_lower_tail_scipy(h, s, row["alpha"])
            require(p_value <= 0.05, "recorded warm-up winner does not pass")
            compare(p_value, cal["p_value"], "warmup.p_value")
            compare(clopper_pearson_upper(h, s), cal["cp_upper"], "warmup.cp_upper")
        else:
            require(s == h == passed == 0 and cal["threshold"] is None and cal["p_value"] is None and cal["cp_upper"] is None, "review-all must have undefined selected risk and no winner")
        evaluated = metrics(row["evaluation"])
        require(evaluated["n"] == 5426, "warm-up evaluation denominator changed")
        require(certified or evaluated["selected"] == 0, "review-all warm-up run selects evaluation rows")
        normalized.append({**row, "calibration": {**cal, "certified": certified},
                           "evaluation": {**evaluated, "unsupported": evaluated["harmful"]}})
    result = {}
    for alpha in BUDGETS:
        aggregates = {}
        for tier in (*REQUESTED_TIERS, "FULL"):
            subset = [row for row in normalized if row["alpha"] == alpha and (row["replicate"] == "FULL" if tier == "FULL" else row["replicate"] != "FULL" and row["requested_n"] == tier)]
            require(len(subset) == (1 if tier == "FULL" else 100), "incomplete warm-up tier")
            aggregates[str(tier)] = aggregate_runs(subset)
        result[str(alpha)] = {"aggregates": aggregates, "milestones": milestones(aggregates)}
    return result


def verify_history(history):
    require(set(history) == {"D1", "D1R", "D1S"}, "development history is incomplete")
    for phase in ("D1", "D1R"):
        row = history[phase]["first_test"]
        p = exact_binomial_lower_tail_scipy(row["harmful"], row["selected"])
        compare(p, row["p_value"], f"history.{phase}.p_value")
        compare(clopper_pearson_upper(row["harmful"], row["selected"]), row["cp_upper"], f"history.{phase}.cp_upper")
        require(p > 0.05, "historical unsuccessful first test changed")
    cal = history["D1S"]["calibration"]
    compare(exact_binomial_lower_tail_scipy(cal["harmful"], cal["selected"]), cal["p_value"], "history.D1S.p_value")
    compare(clopper_pearson_upper(cal["harmful"], cal["selected"]), cal["cp_upper"], "history.D1S.cp_upper")
    return history


def replay(directory):
    bundle, manifest_hash = load_bundle(directory)
    study, expected = bundle["study"], bundle["expected"]
    require(study["budgets"] == list(BUDGETS) and study["delta"] == 0.05, "MB1 budget protocol changed")
    require(study["roles"] == {"MODEL_DEVELOPMENT": 27131, "WARMUP_CALIBRATION": 5427, "WARMUP_EVALUATION": 5426, "FINAL_CALIBRATION": 5426, "LOCKED_TEST": 10853}, "MB1 population roles changed")
    require(len(study["emotions"]) == len(set(study["emotions"])) == 28, "taxonomy requires 28 distinct labels")
    sequence = verify_design(bundle["design"])
    cal = bundle["calibration"]
    require(cal["n"] == 5426 and len(cal["counts"]) == 14, "final count trace scope changed")
    require(set(expected["final_controllers"]) == set(BUDGET_KEYS), "expected controller budgets changed")
    controllers, tests = {}, {}
    for key in BUDGET_KEYS:
        expected_controller = expected["final_controllers"][key]
        count = _integer(expected_controller["tested"], "tested")
        require(0 < count <= len(cal["counts"]), "invalid recorded prefix length")
        result = replay_count_prefix(sequence, cal["counts"][:count], n=cal["n"], alpha=float(key))
        controllers[key] = controller_summary(result)
        # Identity and discrete decisions remain exact even though probability comparisons allow 1e-12.
        for field in ("state", "threshold", "selected", "harmful", "tested", "certified", "stopped_at_index"):
            require(controllers[key][field] == expected_controller[field], f"{key}: exact controller {field} mismatch")
        compare(controllers[key], expected_controller, f"controllers.{key}")
        tests[key] = result["tests"]
    require(max(row["tested"] for row in controllers.values()) == len(cal["counts"]), "exported unexecuted calibration statistics")
    evaluations = verify_evaluations(bundle["evaluations"], study["emotions"])
    compare(evaluations["LOCKED_TEST"]["controllers"], expected["locked_metrics"], "locked")
    compare(evaluations["LOCKED_TEST"]["baselines"], expected["locked_baselines"], "baselines")
    warmup = verify_warmup(bundle["warmup_runs"], sequence)
    compare(warmup, expected["warmup"], "warmup")
    history = verify_history(bundle["development_history"])
    full_runs = {str(row["alpha"]): row for row in bundle["warmup_runs"] if row["replicate"] == "FULL"}
    for key in BUDGET_KEYS:
        compare(full_runs[key]["evaluation"], bundle["evaluations"]["WARMUP_EVALUATION"]["controllers"][key], "full_warmup_evaluation")
    compare(history["D1S"]["evaluation"], full_runs["0.05"]["evaluation"], "D1S_MB1_development_correspondence")
    locked = evaluations["LOCKED_TEST"]["controllers"]
    transitions = []
    for lower, higher in zip(BUDGET_KEYS, BUDGET_KEYS[1:]):
        a, b = locked[lower], locked[higher]
        transitions.append({"from": float(lower), "to": float(higher),
                            "additional_selected": b["selected"] - a["selected"],
                            "automation_gain_percentage_points": 100 * (b["automation"] - a["automation"]),
                            "additional_unsupported_per_1000_auto_tagged": 1000 * (b["selected_error"] - a["selected_error"])})
    return {"kind": "goemotions_frozen_evidence_replay", "study_id": "GOEMOTIONS_MB1",
            "evidence_manifest_sha256": manifest_hash, "final_controllers": controllers,
            "candidate_tests": tests, "evaluations": evaluations, "warmup": warmup,
            "development_history": history, "price_of_strictness": transitions,
            "checks": {"final_controller_replay": "PASS", "design_order": "PASS", "aggregate_reconciliation": "PASS", "warmup_summary_regeneration": "PASS", "development_history_retained": "PASS"},
            "scope": {"source_model_retraining": "NOT_INCLUDED", "checkpoint_inference": "NOT_INCLUDED", "warmup_candidate_prefix_replay": "NOT_INCLUDED", "final_candidate_tests_replayed": sum(len(value) for value in tests.values()), "unique_final_candidates": 14, "frozen_sequence_size": 21, "warmup_aggregate_records": len(bundle["warmup_runs"])}}
