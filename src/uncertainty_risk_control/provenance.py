"""Verify the packaged historical core without access to its original repository."""

import hashlib
import json
import platform
from importlib.metadata import version
from importlib.resources import files


def reference_integrity() -> dict[str, object]:
    package = files("uncertainty_risk_control")
    record = json.loads(package.joinpath("reference_manifest.json").read_text(encoding="utf-8"))
    actual = hashlib.sha256(package.joinpath(record["packaged_path"]).read_bytes()).hexdigest()
    if actual != record["source_sha256"]:
        raise ValueError("historical numerical core differs from the recorded source bytes")
    return {"status": "PASS", "sha256": actual, "legacy_method_id": record["legacy_method_id"]}


def environment() -> dict[str, str]:
    return {"python": platform.python_version(), **{name: version(name) for name in ("uncertainty-risk-control", "numpy", "scipy")}}
