"""Installed entry point, portable outputs, and failure propagation."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliTests(unittest.TestCase):
    def test_verify_from_unrelated_working_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "verification.json"
            environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
            result = subprocess.run([sys.executable, "-m", "uncertainty_risk_control.cli", "verify", "--skip-monte-carlo", "--output", str(output)], cwd=directory, env=environment, capture_output=True, text=True, check=True)
            data = json.loads(output.read_text())
            self.assertEqual(data, json.loads(result.stdout))
            self.assertEqual(data["status"], "PASS")
            self.assertEqual(data["monte_carlo_status"], "SKIPPED")
            self.assertEqual(data["reference_integrity"]["status"], "PASS")

    def test_invalid_config_returns_failure_without_result(self):
        with tempfile.TemporaryDirectory() as directory:
            config, output = Path(directory) / "invalid.toml", Path(directory) / "result.json"
            config.write_text("schema_version = 8\n")
            result = subprocess.run([sys.executable, "-m", "uncertainty_risk_control.cli", "synthetic", "--config", str(config), "--output", str(output)], cwd=directory, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
