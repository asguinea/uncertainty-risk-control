"""Historical correspondence, scientific boundaries and malformed evidence failures."""

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

from uncertainty_risk_control.humaid import _aggregate_reference, projection
from uncertainty_risk_control.humaid.replay import check_design, metrics, replay, strict_json, warmup_summary
from uncertainty_risk_control.humaid.report import render

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "experiments/humaid/evidence"


class HumAidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = replay(EVIDENCE)
        cls.design = json.loads((EVIDENCE / "design.json").read_text())
        cls.runs = json.loads((EVIDENCE / "warmup_runs.json").read_text())

    def changed_bundle(self, name, change, message, *, rehash=True):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / "evidence"
            shutil.copytree(EVIDENCE, dest)
            p = dest / name
            value = json.loads(p.read_text())
            change(value)
            p.write_text(json.dumps(value))
            if rehash:
                manifest = json.loads((dest / "manifest.json").read_text())
                manifest["files"][name] = hashlib.sha256(p.read_bytes()).hexdigest()
                (dest / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, message):
                replay(dest)

    def test_historical_final_winners_and_first_failures(self):
        expected = {("source_2018", "0.025"): (361, 2, 3, .017609769478440285),
                    ("source_2018", "0.05"): (658, 17, 4, .05140062794089317),
                    ("source_2018", "0.1"): (939, 52, 5, .13397836685180664),
                    ("target_2019", "0.05"): (531, 13, 4, .05140062794089317)}
        self.assertEqual(self.result["final_candidate_tests"], 16)
        for (period, alpha), values in expected.items():
            r = self.result["final_calibration"][period][alpha]
            c = r["controller"]
            self.assertEqual((c["selected"], c["harmful"], c["tested"], c["threshold"]), values)
            self.assertTrue(all(test["passes"] for test in r["tests"][:-1]))
            self.assertFalse(r["tests"][-1]["passes"])

    def test_primary_counts_roles_and_event_exception(self):
        selected = {}
        for r in self.result["evaluations"]:
            if r["event"] is None and r["alpha"] == .05:
                c = r["counts"]
                selected[(r["period"], r["role"], r["policy"])] = (c["n"], c["selected"], c["harmful"])
            if r["event"] == "kerala_floods_2018" and r["role"] == "locked_evaluation":
                self.assertGreater(metrics(r["counts"])["selected_error"], .05)
        self.assertEqual(selected[("source_2018", "locked_evaluation", "calibrated")], (9559, 1327, 45))
        self.assertEqual(selected[("target_2019", "warmup_evaluation", "zero_shot")], (3075, 522, 9))
        self.assertEqual(selected[("target_2019", "locked_evaluation", "calibrated")], (6159, 1115, 32))

    def test_full_pool_is_one_run_and_zero_risk_remains_undefined(self):
        self.assertEqual(self.result["warmup_records"], 1202)
        for period, full, milestone in (("source_2018", "4774", 4774), ("target_2019", "3075", 2000)):
            w = self.result["warmup"][period]
            self.assertEqual(w["runs"], 601)
            self.assertEqual(w["aggregates"][full]["runs"], 1)
            self.assertEqual(w["milestones"]["first_90pct_certification_and_10pct_utility"], milestone)
        for row in self.result["evaluations"]:
            if row["policy"] == "REVIEW_ALL":
                self.assertIsNone(metrics(row["counts"])["selected_error"])
        self.assertIn("single full pool", render(self.result))

    def test_missing_final_failure_rejected_after_rehash(self):
        self.changed_bundle("calibration.json", lambda b: b["target_2019"]["counts"].pop(), "count union length")

    def test_sub_tolerance_threshold_change_still_fails_exactly(self):
        def change(b):
            b["target_2019"]["budgets"]["0.05"]["threshold"] += 1e-16
        self.changed_bundle("calibration.json", change, "winner outside passing prefix")

    def test_corrupted_evidence_rejected_without_rehash(self):
        self.changed_bundle("calibration.json", lambda b: b["target_2019"]["counts"].pop(), "hash mismatch", rehash=False)

    def test_missing_or_duplicate_warmup_runs_fail(self):
        for duplicate in (False, True):
            groups = copy.deepcopy(self.runs["source_2018"])
            if duplicate:
                groups["50"][1] = groups["50"][0]
            else:
                groups["4774"] = []
            with self.assertRaisesRegex(ValueError, "replicate coverage"):
                warmup_summary(groups, self.design["sequence"], period="source_2018")

    def test_reordered_design_and_impossible_priority_counts_fail(self):
        d = copy.deepcopy(self.design)
        d["sequence"][0], d["sequence"][1] = d["sequence"][1], d["sequence"][0]
        with self.assertRaisesRegex(ValueError, "frozen development order"):
            check_design(d)
        for counts in ({"n": 10, "selected": 8, "harmful": 0, "priority_total": 9},
                       {"n": 10, "selected": 2, "harmful": True, "priority_total": 3}):
            with self.assertRaises((ValueError, TypeError)):
                metrics(counts)

    def test_event_partition_change_rejected_after_matching_rates(self):
        def change(rows):
            r = next(row for row in rows if row["event"] == "kerala_floods_2018" and row["role"] == "locked_evaluation")
            r["counts"]["n"] += 1
            r["expected"] = metrics(r["counts"])
        self.changed_bundle("evaluations.json", change, "do not partition")

    def test_json_and_manifest_path_injection_fail(self):
        for raw in ('{"n":1,"n":2}', '{"p":NaN}', '{"p":Infinity}', '{"p":1e309}'):
            with self.assertRaises(ValueError):
                strict_json(raw)
        self.changed_bundle("manifest.json", lambda b: b["files"].update({"../private.json": "0" * 64}), "schema fields", rehash=False)

    def test_original_aggregate_function_bodies_match_extraction(self):
        records = json.loads((ROOT / "provenance/humaid_source_extraction.json").read_text())["functions"]
        tree = ast.parse(Path(_aggregate_reference.__file__).read_text())
        nodes = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
        for row in records:
            body = ast.Module(body=nodes[row["exported_function"]].body, type_ignores=[])
            sha = hashlib.sha256(ast.dump(body, include_attributes=False).encode()).hexdigest()
            self.assertEqual(sha, row["body_ast_sha256"])

    def test_projection_drops_unapproved_content(self):
        r = {"n": 10, "selected": 2, "priority_selected_errors": 1, "y1": 4,
             "text": "synthetic extra content", "opaque_identity": "synthetic id", "private_path": "synthetic path"}
        self.assertEqual(projection.evaluation(r), {"n": 10, "selected": 2, "harmful": 1, "priority_total": 4})

    def test_cli_from_unrelated_directory_and_report_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            output, report = Path(directory) / "replay.json", Path(directory) / "tables.md"
            environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
            command = [sys.executable, "-m", "uncertainty_risk_control.cli", "humaid", "--evidence", str(EVIDENCE), "--output", str(output), "--report", str(report)]
            result = subprocess.run(command, cwd=directory, env=environment, capture_output=True, text=True, check=True)
            data = json.loads(output.read_text())
            self.assertEqual(data, json.loads(result.stdout))
            self.assertEqual(data["status"], "PASS")
            self.assertEqual(report.read_text(), render(self.result))
            self.assertEqual(report.read_text(), (ROOT / "experiments/humaid/report/results.md").read_text())
            command[command.index(str(EVIDENCE))] = str(Path(directory) / "missing")
            output.unlink(); report.unlink()
            failed = subprocess.run(command, cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertFalse(output.exists())
            self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main()
