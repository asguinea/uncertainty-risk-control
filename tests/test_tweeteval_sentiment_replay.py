"""Frozen counts, review-all distinction, class denominators and failure handling."""

import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from uncertainty_risk_control.tweeteval_sentiment import _aggregate_reference, projection
from uncertainty_risk_control.tweeteval_sentiment.replay import load_bundle, metrics, replay, strict_json, verify_design, verify_evaluations, verify_warmup
from uncertainty_risk_control.tweeteval_sentiment.report import render

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "experiments/tweeteval-sentiment/evidence"


class TweetEvalSentimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle, _ = load_bundle(EVIDENCE)
        cls.result = replay(EVIDENCE)

    def changed_bundle(self, name, change, message, *, rehash=True):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "evidence"
            shutil.copytree(EVIDENCE, dest)
            path = dest / name
            value = json.loads(path.read_text())
            change(value)
            path.write_text(json.dumps(value))
            if rehash:
                manifest = json.loads((dest / "manifest.json").read_text())
                manifest["files"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
                (dest / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, message):
                replay(dest)

    def test_four_historical_winners_stops_and_locked_counts(self):
        expected = {"0.025": (0, 0, 1, None, 0, 0), "0.05": (631, 12, 8, .0295229992319207, 785, 32),
                    "0.1": (1928, 149, 12, .061477750631934946, 3041, 301), "0.15": (3226, 385, 14, .11842140197479434, 5333, 810)}
        self.assertEqual(self.result["final_candidate_tests"], 35)
        for alpha, values in expected.items():
            r = self.result["final_calibration"][alpha]; c = r["controller"]
            e = self.result["evaluations"]["LOCKED_TEST"]["controllers"][alpha]["counts"]
            self.assertEqual((c["selected"], c["harmful"], c["tested"], c["threshold"], e["selected"], e["harmful"]), values)
            self.assertTrue(all(t["passes"] for t in r["tests"][:-1]))
            self.assertFalse(r["tests"][-1]["passes"])

    def test_nonempty_failed_candidate_is_not_review_all_counts(self):
        r = self.result["final_calibration"]["0.025"]
        self.assertEqual((r["tests"][0]["selected"], r["tests"][0]["harmful"]), (134, 1))
        self.assertGreater(r["tests"][0]["p_value"], .05)
        c = r["controller"]
        self.assertEqual(c["state"], "REVIEW_ALL")
        for key in ("threshold", "p_value", "cp_upper"):
            self.assertIsNone(c[key])
        self.assertEqual(c["selected"], 0)
        self.assertEqual(self.result["warmup_full_controllers"]["0.025"]["state"], "CERTIFIED")

    def test_test_exception_sparse_neutral_and_separate_reference_populations(self):
        locked = self.result["evaluations"]["LOCKED_TEST"]["controllers"]
        self.assertGreater(metrics(locked["0.15"]["counts"])["selected_error"], .15)
        self.assertEqual(locked["0.05"]["predicted_class"]["neutral"]["selected"], 1)
        self.assertEqual(self.result["final_reference_support"]["negative"], 1118)
        self.assertEqual(locked["0.05"]["reference_class"]["negative"]["n"], 3972)
        self.assertIn("15.1884%", render(self.result))
        self.assertIn("not a joint guarantee", render(self.result))

    def test_warmup_cardinality_single_full_pool_and_milestones(self):
        w = self.result["warmup"]
        self.assertEqual(w["records"], 2804)
        for alpha, groups in w["aggregation"].items():
            self.assertEqual(groups["7142"]["replicates"], 1)
            self.assertEqual(groups["4000"]["replicates"], 100)
            self.assertTrue(all(v is None for v in groups["50"]["evaluation_selected_error_nonzero"].values()))
        expected = {"0.025": (7142, None), "0.05": (4000, None), "0.1": (1000, 4000), "0.15": (500, 2000)}
        for alpha, values in expected.items():
            m = w["milestones"][alpha]
            self.assertEqual((m["any_certification"], m["combined_90_certification_automation_0.1"]), values)

    def test_manifest_corruption_and_path_injection_fail(self):
        self.changed_bundle("calibration.json", lambda b: b["counts"].pop(), "hash mismatch", rehash=False)
        self.changed_bundle("manifest.json", lambda b: b["files"].update({"../outside.json": "0" * 64}), "schema fields", rehash=False)

    def test_missing_failure_or_threshold_perturbation_fails_after_rehash(self):
        self.changed_bundle("calibration.json", lambda b: b["counts"].pop(), "count union length")
        def change(b):
            b["budgets"]["0.05"]["threshold"] += 1e-16
        self.changed_bundle("calibration.json", change, "outside passing prefix")

    def test_development_order_is_not_threshold_order(self):
        d = copy.deepcopy(self.bundle["design"])
        self.assertNotEqual(d["sequence"], sorted(d["sequence"], key=lambda r: r["threshold"]))
        d["sequence"].sort(key=lambda r: r["threshold"])
        with self.assertRaisesRegex(ValueError, "development CP order"):
            verify_design(d)

    def test_missing_duplicate_or_changed_size_warmup_fails(self):
        for mutation in range(3):
            runs = copy.deepcopy(self.bundle["warmup_runs"])
            if mutation == 0:
                runs["0.025"]["7142"] = []
            elif mutation == 1:
                runs["0.05"]["50"][1] = runs["0.05"]["50"][0]
            else:
                runs["0.1"]["200"][0]["realized_n"] += 1
            with self.assertRaises(ValueError):
                verify_warmup(runs, self.bundle["design"]["sequence"])

    def test_predicted_class_error_partition_fails_even_with_matching_rates(self):
        e = copy.deepcopy(self.bundle["evaluations"])
        p = e["LOCKED_TEST"]["controllers"]["0.05"]["predicted_class"]["positive"]
        p["harmful"] += 1
        p["expected"]["selected_error"] = p["harmful"] / p["selected"]
        with self.assertRaises(ValueError):
            verify_evaluations(e, self.result["final_calibration"], self.bundle["warmup_runs"])

    def test_impossible_reference_margin_fails(self):
        e = copy.deepcopy(self.bundle["evaluations"])
        r = e["LOCKED_TEST"]["controllers"]["0.05"]["reference_class"]["positive"]
        r["accepted"] = 0; r["review"] = r["n"]; r["expected_review_fraction"] = 1.0
        with self.assertRaisesRegex(ValueError, "cannot describe the same"):
            verify_evaluations(e, self.result["final_calibration"], self.bundle["warmup_runs"])

    def test_projection_discards_source_fields_and_invalid_counts_fail(self):
        row = {"selected": 3, "errors": 1, "selected_class_distribution": {"negative": 1, "neutral": 0, "positive": 2}, "text": "synthetic extra", "opaque_row_identity": "synthetic identity", "private_path": "synthetic path"}
        p = projection.counts(row, 10)
        self.assertNotIn("synthetic", json.dumps(p))
        self.assertEqual(metrics(p)["selected_error"], 1 / 3)
        p["selected_by_class"]["neutral"] = 1
        with self.assertRaisesRegex(ValueError, "partition"):
            metrics(p)
        p["harmful"] = True
        with self.assertRaises(TypeError):
            metrics(p)

    def test_nonfinite_and_duplicate_json_fail(self):
        for raw in ('{"n":1,"n":2}', '{"p":NaN}', '{"p":Infinity}', '{"p":1e309}'):
            with self.assertRaises(ValueError):
                strict_json(raw)

    def test_preserved_aggregate_function_and_loop_asts(self):
        p = json.loads((ROOT / "provenance/tweeteval_sentiment_extraction.json").read_text())
        tree = ast.parse(Path(_aggregate_reference.__file__).read_text())
        functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        def digest(nodes):
            return hashlib.sha256(ast.dump(ast.Module(body=nodes, type_ignores=[]), include_attributes=False).encode()).hexdigest()
        for row in p["function_bodies"]:
            self.assertEqual(digest(functions[row["name"]].body), row["body_ast_sha256"])
        loop = next(n for n in functions["aggregate"].body if isinstance(n, ast.For))
        self.assertEqual(digest([loop]), p["aggregation_loop_ast_sha256"])

    def test_cli_report_matches_and_failure_does_not_emit_success(self):
        with tempfile.TemporaryDirectory() as directory:
            output, report = Path(directory) / "result.json", Path(directory) / "tables.md"
            environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
            args = [sys.executable, "-m", "uncertainty_risk_control.cli", "tweeteval-sentiment", "--evidence", str(EVIDENCE), "--output", str(output), "--report", str(report)]
            r = subprocess.run(args, cwd=directory, env=environment, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(output.read_text()), json.loads(r.stdout))
            self.assertEqual(json.loads(r.stdout)["status"], "PASS")
            self.assertEqual(report.read_text(), render(self.result))
            self.assertEqual(report.read_text(), (ROOT / "experiments/tweeteval-sentiment/report/results.md").read_text())
            args[args.index(str(EVIDENCE))] = str(Path(directory) / "missing")
            output.unlink(); report.unlink()
            failed = subprocess.run(args, cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(output.exists())
            self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main()
