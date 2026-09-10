"""Exercise a built wheel and source archive from an unrelated fresh environment."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile

from check_distribution import check_file, require


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def differences(expected, actual, path="root"):
    """Give bounded, useful diagnostics for already-public figure input JSON."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(expected.keys() | actual.keys()):
            if key not in expected or key not in actual:
                yield f"{path}.{key}: key missing"
            else:
                yield from differences(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            yield f"{path}: lengths {len(expected)} != {len(actual)}"
        for i, (a, b) in enumerate(zip(expected, actual)):
            yield from differences(a, b, f"{path}[{i}]")
    elif expected != actual:
        yield f"{path}: expected {str(expected)[:100]!r}, actual {str(actual)[:100]!r}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    logs = output / "logs"
    logs.mkdir(exist_ok=True)
    env = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"}}
    env["PYTHONUTF8"] = "1"
    commands = []

    def run(label, arguments, cwd):
        result = subprocess.run([str(item) for item in arguments], cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8")
        (logs / f"{label}.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        commands.append({"check": label, "exit_code": result.returncode})
        require(result.returncode == 0, f"{label} failed; inspect the local log for this check:\n{result.stderr[-4000:]}")
        return result

    dist = output / "dist"
    run("build", ["uv", "build", "--out-dir", dist], root)
    wheels, archives = list(dist.glob("*.whl")), list(dist.glob("*.tar.gz"))
    require(len(wheels) == len(archives) == 1, "expected one wheel and one source archive")
    wheel, sdist = wheels[0], archives[0]
    with zipfile.ZipFile(wheel) as archive:
        metadata = archive.read(next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))).decode("utf-8")
        requirements = re.findall(r"^Requires-Dist: (.+)$", metadata, re.M)
        require(set(requirements) == {"numpy==2.4.6", "scipy==1.17.1"}, "base wheel dependencies changed")
        package_files = [name for name in archive.namelist() if name.startswith("uncertainty_risk_control/")]
        for name in package_files:
            require(archive.read(name) == (root / "src" / name).read_bytes(), f"wheel/source mismatch: {name}")

    with tempfile.TemporaryDirectory(prefix="uqrc-reproduction-") as directory:
        scratch = Path(directory).resolve()
        source = scratch / "source"
        source.mkdir()
        with tarfile.open(sdist) as archive:
            for member in archive.getmembers():
                require(member.isfile() and not member.issym() and not member.islnk(), "source archive must contain ordinary files only")
                name = member.name.split("/", 1)[1]
                dest = source / name
                require(dest.resolve().is_relative_to(source), "source archive path escape")
                data = archive.extractfile(member).read()
                if name != "PKG-INFO":
                    check_file(name, data)
                    require((root / name).is_file() and data == (root / name).read_bytes(), f"source archive mismatch: {name}")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
        for required in ("examples/selected_risk_walkthrough.py", "scripts/verify_reproduction.py", "experiments/goemotions/scripts/plot_results.py", "experiments/goemotions/evidence/manifest.json", "experiments/humaid/evidence/manifest.json", "provenance/humaid_source_extraction.json"):
            require((source / required).is_file(), f"missing source asset: {required}")
        for required in ("experiments/tweeteval-sentiment/evidence/manifest.json", "provenance/tweeteval_sentiment_extraction.json", "scripts/plot_social_media_studies.py", "docs/social-media-research.md", "CITATION.cff", "docs/releases/v0.2.0.md"):
            require((source / required).is_file(), f"missing source asset: {required}")

        venv = scratch / "venv"
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run("create-environment", ["uv", "venv", "--python", sys.executable, venv], scratch)
        run("install-wheel", ["uv", "pip", "install", "--python", python, wheel], scratch)
        module = run("installed-import", [python, "-c", "import uncertainty_risk_control; print(uncertainty_risk_control.__file__)"], scratch)
        require(Path(module.stdout.strip()).resolve().is_relative_to(venv), "package import escaped the isolated wheel environment")
        run("base-without-matplotlib", [python, "-c", "import importlib.util; assert importlib.util.find_spec('matplotlib') is None"], scratch)
        tests = run("unit-tests", [python, "-m", "unittest", "discover", "-s", source / "tests", "-v"], scratch)
        test_text = tests.stdout + tests.stderr
        match = re.search(r"Ran (\d+) tests", test_text)
        require(match is not None and "\nOK\n" in test_text, "unit suite did not complete")
        run("walkthrough", [python, source / "examples/selected_risk_walkthrough.py"], scratch)
        cli = [python, "-m", "uncertainty_risk_control.cli"]
        run("method-verification", [*cli, "verify", "--output", output / "verification.json"], scratch)
        run("synthetic", [*cli, "synthetic", "--config", source / "experiments/synthetic/config.toml", "--output", output / "synthetic.json"], scratch)
        run("goemotions", [*cli, "goemotions", "--evidence", source / "experiments/goemotions/evidence", "--output", output / "replay.json", "--report", output / "tables.md"], scratch)
        require((output / "tables.md").read_text(encoding="utf-8") == (source / "experiments/goemotions/report/results.md").read_text(encoding="utf-8"), "regenerated table text differs")
        run("humaid", [*cli, "humaid", "--evidence", source / "experiments/humaid/evidence", "--output", output / "humaid-replay.json", "--report", output / "humaid-tables.md"], scratch)
        require((output / "humaid-tables.md").read_text(encoding="utf-8") == (source / "experiments/humaid/report/results.md").read_text(encoding="utf-8"), "regenerated HumAID table text differs")
        run("tweeteval-sentiment", [*cli, "tweeteval-sentiment", "--evidence", source / "experiments/tweeteval-sentiment/evidence", "--output", output / "tweeteval-sentiment-replay.json", "--report", output / "tweeteval-sentiment-tables.md"], scratch)
        require((output / "tweeteval-sentiment-tables.md").read_text(encoding="utf-8") == (source / "experiments/tweeteval-sentiment/report/results.md").read_text(encoding="utf-8"), "regenerated TweetEval Sentiment table text differs")

        # Install plotting dependencies from the same hash-locked export, then restore the wheel.
        requirements_file = scratch / "requirements.txt"
        run("export-plotting-lock", ["uv", "export", "--locked", "--group", "figures", "--no-emit-project", "--output-file", requirements_file], source)
        run("install-plotting-lock", ["uv", "pip", "sync", "--python", python, "--require-hashes", requirements_file], scratch)
        run("restore-wheel", ["uv", "pip", "install", "--python", python, "--no-deps", wheel], scratch)
        run("figures", [python, source / "experiments/goemotions/scripts/plot_results.py", "--evidence", source / "experiments/goemotions/evidence", "--output", output / "figures"], scratch)
        original = json.loads((source / "experiments/goemotions/report/figures/plot_data.json").read_text(encoding="utf-8"))
        current = json.loads((output / "figures/plot_data.json").read_text(encoding="utf-8"))
        original.pop("environment")
        current.pop("environment")
        require(current == original, "figure numerical inputs or generator hash changed")

        run("social-media-figures", [python, source / "scripts/plot_social_media_studies.py", "--source-root", source, "--output", output / "social-media"], scratch)
        figure_inputs = ["experiments/humaid/report/figures/plot_data.json", "experiments/tweeteval-sentiment/report/figures/plot_data.json", "docs/figures/study_map_data.json"]
        for name in figure_inputs:
            original = json.loads((source / name).read_text(encoding="utf-8"))
            current = json.loads((output / "social-media" / name).read_text(encoding="utf-8"))
            original.pop("environment")
            current.pop("environment")
            if current != original:
                from itertools import islice
                detail = "; ".join(islice(differences(original, current), 8))
                raise ValueError(f"social media figure inputs or generator hash changed: {name}; {detail}")
        figure_stems = ["experiments/humaid/report/figures/risk_and_transfer", "experiments/humaid/report/figures/calibration_size", "experiments/tweeteval-sentiment/report/figures/risk_and_class_selection", "experiments/tweeteval-sentiment/report/figures/calibration_size", "docs/figures/study_map"]
        for stem in figure_stems:
            for suffix in (".svg", ".png"):
                for directory in (source, output / "social-media"):
                    require((directory / (stem + suffix)).is_file(), f"missing figure: {stem + suffix}")

    verification = json.loads((output / "verification.json").read_text(encoding="utf-8"))
    replay = json.loads((output / "replay.json").read_text(encoding="utf-8"))
    humaid = json.loads((output / "humaid-replay.json").read_text(encoding="utf-8"))
    require(humaid["status"] == "PASS" and humaid["final_candidate_tests"] == 16 and humaid["warmup_records"] == 1202, "HumAID replay scope changed")
    sentiment = json.loads((output / "tweeteval-sentiment-replay.json").read_text(encoding="utf-8"))
    require(sentiment["status"] == "PASS" and sentiment["final_candidate_tests"] == 35 and sentiment["warmup_records"] == 2804, "TweetEval Sentiment replay scope changed")
    require(verification["monte_carlo_total_experiments"] == 150000 and verification["monte_carlo_status"] == "PASS", "full synthetic verification required")
    receipt = {
        "schema_version": 1, "status": "PASS", "system": platform.system(), "machine": platform.machine(),
        "environment": replay["environment"], "unit_tests": int(match.group(1)),
        "synthetic_monte_carlo_trials": verification["monte_carlo_total_experiments"],
        "base_runs_without_matplotlib": True, "wheel_package_files": len(package_files),
        "wheel_sha256": sha(wheel), "source_archive_sha256": sha(sdist),
        "table_text_identical": True,
        "table_bytes_identical": (output / "tables.md").read_bytes() == (root / "experiments/goemotions/report/results.md").read_bytes(),
        "figure_inputs_exact_match_excluding_environment": True,
        "social_media_figure_inputs_exact_match_excluding_environment": True,
        "social_media_figure_input_files": figure_inputs,
        "total_svg_png_figure_pairs": 7,
        "total_final_candidate_tests": replay["scope"]["final_candidate_tests_replayed"] + humaid["final_candidate_tests"] + sentiment["final_candidate_tests"],
        "total_warmup_aggregate_records": replay["scope"]["warmup_aggregate_records"] + humaid["warmup_records"] + sentiment["warmup_records"],
        "figure_byte_comparison": "not required across platforms; exact numerical inputs are required",
        "evidence_manifest_sha256": replay["evidence_manifest_sha256"], "study_scope": replay["scope"],
        "humaid": {"evidence_manifest_sha256": humaid["evidence_manifest_sha256"], "final_candidate_tests": humaid["final_candidate_tests"], "warmup_records": humaid["warmup_records"], "table_text_identical": True, "scope": humaid["scope"]},
        "tweeteval_sentiment": {"evidence_manifest_sha256": sentiment["evidence_manifest_sha256"], "final_candidate_tests": sentiment["final_candidate_tests"], "warmup_records": sentiment["warmup_records"], "table_text_identical": True, "scope": sentiment["scope"]},
        "checks": commands,
    }
    (output / "checks.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: isolated wheel; {match.group(1)} tests; 150,000 synthetic trials; exact study figure inputs; regenerated tables.")


if __name__ == "__main__":
    main()
