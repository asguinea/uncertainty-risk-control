import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from uncertainty_risk_control.goemotions.projection import emotion_counts, warmup_run
from uncertainty_risk_control.goemotions.replay import (
    load_bundle, replay, strict_json, verify_design, verify_evaluations, verify_warmup,
)
from uncertainty_risk_control.goemotions.report import render

EVIDENCE = Path(__file__).resolve().parents[1] / "experiments/goemotions/evidence"


class GoEmotionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle, cls.manifest_hash = load_bundle(EVIDENCE)
        cls.result = replay(EVIDENCE)

    def test_historical_controllers_and_counts_match(self):
        expected = {"0.05": (219, 5, 3, 419, 10), "0.1": (267, 11, 5, 530, 16),
                    "0.15": (1470, 194, 13, 2931, 414), "0.2": (1938, 316, 14, 3892, 683)}
        for key, values in expected.items():
            cal = self.result["final_controllers"][key]
            locked = self.result["evaluations"]["LOCKED_TEST"]["controllers"][key]
            self.assertEqual((cal["selected"], cal["harmful"], cal["tested"], locked["selected"], locked["harmful"]), values)
            self.assertFalse(self.result["candidate_tests"][key][-1]["passes"])
        self.assertEqual(self.result["scope"]["final_candidate_tests_replayed"], 35)

    def test_review_all_and_sparse_emotion_errors_remain_undefined(self):
        locked = self.result["evaluations"]["LOCKED_TEST"]
        self.assertIsNone(locked["baselines"]["REVIEW_ALL"]["selected_error"])
        sparse = locked["predicted_emotion"]["0.05"]["admiration"]
        self.assertFalse(sparse["adequate_selected_n"])
        self.assertIsNone(sparse["harmful"])
        self.assertIsNone(sparse["selected_error"])
        self.assertIn("not reported", render(self.result))

    def test_warmup_milestones_and_negative_history_retained(self):
        self.assertEqual(self.result["warmup"]["0.05"]["milestones"]["first_any_certification"], 2000)
        self.assertIsNone(self.result["warmup"]["0.05"]["milestones"]["first_median_automation_at_least_5_percent"])
        self.assertEqual(self.result["development_history"]["D1"]["full_pool_state"], "REVIEW_ALL")
        self.assertEqual(self.result["development_history"]["D1S"]["evaluation"]["selected"], 227)
        self.assertEqual(self.result["scope"]["warmup_candidate_prefix_replay"], "NOT_INCLUDED")

    def test_integrity_and_manifest_path_changes_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "evidence"
            shutil.copytree(EVIDENCE, dest)
            path = dest / "calibration.json"
            path.write_text(path.read_text() + " ")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                replay(dest)
            manifest = json.loads((dest / "manifest.json").read_text())
            manifest["files"]["../outside.json"] = "0" * 64
            (dest / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "file set"):
                replay(dest)

    def test_incomplete_or_changed_calibration_fails_even_if_hash_is_updated(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "evidence"
            shutil.copytree(EVIDENCE, dest)
            path = dest / "calibration.json"
            content = json.loads(path.read_text())
            content["counts"] = content["counts"][:-1]
            path.write_text(json.dumps(content))
            manifest = json.loads((dest / "manifest.json").read_text())
            manifest["files"]["calibration.json"] = hashlib.sha256(path.read_bytes()).hexdigest()
            (dest / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "scope changed"):
                replay(dest)

    def test_design_reordering_fails(self):
        design = copy.deepcopy(self.bundle["design"])
        design["sequence"][0], design["sequence"][1] = design["sequence"][1], design["sequence"][0]
        with self.assertRaisesRegex(ValueError, "ordering"):
            verify_design(design)

    def test_slice_denominator_mismatch_and_fabricated_sparse_errors_fail(self):
        for variant in (0, 1):
            evidence = copy.deepcopy(self.bundle["evaluations"])
            if variant == 0:
                evidence["LOCKED_TEST"]["consensus"]["0.05"]["HIGH_CONSENSUS"]["n"] += 1
            else:
                evidence["LOCKED_TEST"]["predicted_emotion"]["0.05"]["admiration"]["harmful"] = 0
            with self.assertRaises(ValueError):
                verify_evaluations(evidence, self.bundle["study"]["emotions"])

    def test_missing_or_duplicate_warmup_record_fails(self):
        for runs in (self.bundle["warmup_runs"][:-1], [self.bundle["warmup_runs"][0]] * 2804):
            with self.assertRaises(ValueError):
                verify_warmup(runs, self.bundle["design"]["sequence"])

    def test_projection_discards_unapproved_fields(self):
        original = self.bundle["warmup_runs"][0]
        cal = original["calibration"]
        source = {**original, "opaque_comment_identity": "test-only-identity", "text": "unrequested example",
                  "calibration": {"state": cal["state"], "threshold": cal["threshold"], "selected": cal["selected"], "unsupported": cal["harmful"], "exact_p_value": cal["p_value"], "cp_upper_95": cal["cp_upper"], "hypotheses_tested": cal["tested"], "hypotheses_certified": cal["certified"], "stopped_at_index": cal["stopped_at_index"], "private_path": "test-only-path"},
                  "evaluation": {**original["evaluation"], "unsupported": original["evaluation"]["harmful"]}}
        projected = warmup_run(source)
        self.assertEqual(projected, original)
        self.assertNotIn("test-only", json.dumps(projected))
        sparse = emotion_counts({"predicted_count": 100, "selected_count": 3, "adequate_selected_n": False, "unsupported": 2})
        self.assertIsNone(sparse["harmful"])

    def test_duplicate_keys_and_nonfinite_json_rejected(self):
        for content in ('{"n":1,"n":2}', '{"p":NaN}', '{"p":Infinity}', '{"p":1e309}'):
            with self.assertRaises(ValueError):
                strict_json(content)


if __name__ == "__main__":
    unittest.main()
