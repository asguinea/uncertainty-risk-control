"""Optional reader-side acquisition and verification of pinned upstream resources."""

import hashlib
from pathlib import Path
import re
import tempfile
import urllib.request

from .replay import require, strict_json

REVISION = "041338718b4e8151372fd63677104c65b73a0a4e"
REPO_BASE = f"https://raw.githubusercontent.com/google-research/google-research/{REVISION}"
SOURCE_URLS = {
    **{f"raw/goemotions_{part}.csv": f"https://storage.googleapis.com/gresearch/goemotions/data/full_dataset/goemotions_{part}.csv" for part in (1, 2, 3)},
    **{f"official/{name}": f"{REPO_BASE}/goemotions/data/{name}" for name in ("train.tsv", "dev.tsv", "test.tsv", "emotions.txt")},
    "metadata/README.md": f"{REPO_BASE}/goemotions/README.md",
    "metadata/google_research_LICENSE": f"{REPO_BASE}/LICENSE",
}


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checked_download(url, destination, expected_hash, expected_bytes):
    """Install a verified download atomically; never replace an existing file."""
    require(not destination.exists(), "download destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".download-", delete=False) as output:
            temporary = Path(output.name)
            request = urllib.request.Request(url, headers={"User-Agent": "uncertainty-risk-control/0.1"})
            total = 0
            with urllib.request.urlopen(request, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    require(total <= expected_bytes, "download exceeds pinned byte size")
                    output.write(chunk)
        require(total == expected_bytes and file_sha256(temporary) == expected_hash, "download differs from pinned source bytes")
        # Link creation fails if a file appeared during download; it cannot overwrite it.
        destination.hardlink_to(temporary)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def verify_or_acquire(manifest_path, directory, *, download=False):
    raw = Path(manifest_path).read_bytes()
    manifest = strict_json(raw)
    require(manifest["schema_version"] == 1 and manifest["repository_revision"] == REVISION, "unsupported source manifest")
    rows = manifest["sources"]
    require(len(rows) == len(SOURCE_URLS) and {row["relative_path"] for row in rows} == set(SOURCE_URLS), "source resource set changed")
    root = Path(directory).resolve()
    receipts = []
    for row in rows:
        require(set(row) == {"relative_path", "source_url", "sha256", "bytes"}, "unexpected source resource fields")
        name = row["relative_path"]
        require(row["source_url"] == SOURCE_URLS[name], "source URL differs from authoritative pinned location")
        require(re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None and type(row["bytes"]) is int and row["bytes"] > 0, "invalid source hash/size")
        destination = root / name
        require(destination.resolve().is_relative_to(root) and not destination.is_symlink(), "source destination escapes the requested directory")
        if not destination.exists():
            require(download, f"missing source {name}; use --download to acquire upstream files")
            checked_download(row["source_url"], destination, row["sha256"], row["bytes"])
        require(destination.is_file() and destination.stat().st_size == row["bytes"] and file_sha256(destination) == row["sha256"], f"source hash/size mismatch: {name}")
        receipts.append({"relative_path": name, "sha256": row["sha256"], "bytes": row["bytes"]})
    return {"kind": "goemotions_upstream_source_verification", "source_manifest_sha256": hashlib.sha256(raw).hexdigest(), "sources": receipts, "download_requested": download,
            "scope": "Pinned upstream byte verification only; no label/role reconstruction, model training or benchmark evaluation."}
