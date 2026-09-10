"""Check publication file boundaries, local links, and optionally all Git history.

This scoped check complements a secret scanner and human review; it cannot prove
that a repository is free of sensitive information or validate research claims.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote, urlsplit


ROOT_FILES = {".gitignore", ".gitattributes", ".python-version", "README.md", "LICENSE", "LICENSE_SCOPE.md", "THIRD_PARTY_NOTICES.md", "CITATION.cff", "pyproject.toml", "uv.lock"}
ROOT_DIRS = {"src", "tests", "docs", "experiments", "provenance", "examples", "scripts", ".github"}
EXCLUDED_DIRS = {"data", "models", "checkpoints", "logs", "results", ".git", ".venv", "__pycache__"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".toml", ".cff", ".lock", ".yml", ".yaml", ".svg", ".txt", ""}
FIGURE_DIRS = {"experiments/goemotions/report/figures", "experiments/humaid/report/figures", "experiments/tweeteval-sentiment/report/figures", "docs/figures"}
# Construct patterns without embedding an actual workstation path in the source.
PRIVATE_PATHS = tuple("/" + name + "/" for name in ("Users", "Volumes", "private/var")) + ("file" + "://",)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_file(name, data):
    path = PurePosixPath(name)
    require(not path.is_absolute() and ".." not in path.parts, f"unsafe member: {name}")
    require(name in ROOT_FILES or path.parts[0] in ROOT_DIRS, f"unreviewed top-level path: {name}")
    require(not set(path.parts[:-1]) & EXCLUDED_DIRS, f"excluded asset directory: {name}")
    require(not re.search(r"(^|/)(\.env($|\.)|identity_salt)|\.(pem|key|salt)$", name), f"excluded credential path: {name}")
    require(len(data) < 5_000_000, f"unreviewed large asset: {name}")
    if path.suffix == ".png":
        require(str(path.parent) in FIGURE_DIRS, f"unreviewed image: {name}")
        require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"invalid PNG: {name}")
        return
    require(path.suffix in TEXT_SUFFIXES or name in ROOT_FILES, f"unreviewed file type: {name}")
    text = data.decode("utf-8")
    require(not any(token in text for token in PRIVATE_PATHS), f"workstation path in: {name}")
    require(not re.search(r"[A-Z]:\\(?:Users|Documents)\\", text), f"workstation path in: {name}")


def anchors(text):
    result, counts = set(), {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M):
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).replace(" ", "-")
        index = counts.get(slug, 0)
        result.add(slug + (f"-{index}" if index else ""))
        counts[slug] = index + 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=root)

    names = git("ls-files", "-z").decode().rstrip("\0").split("\0")
    links = 0
    for name in names:
        path = root / name
        require(path.is_file() and not path.is_symlink(), f"missing or linked file: {name}")
        check_file(name, path.read_bytes())
        if path.suffix != ".md":
            continue
        for target in re.findall(r"!?\[[^\]\n]+\]\(([^)\n]+)\)", path.read_text(encoding="utf-8")):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            dest = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            require(dest.is_relative_to(root) and dest.is_file(), f"broken local link in {name}: {target}")
            require(dest.relative_to(root).as_posix() in names, f"link to untracked asset in {name}: {target}")
            if parsed.fragment and dest.suffix == ".md":
                require(unquote(parsed.fragment) in anchors(dest.read_text(encoding="utf-8")), f"broken anchor in {name}: {target}")
            links += 1
    commits, checked = [], set()
    if args.history:
        require(git("rev-parse", "--is-shallow-repository").strip() == b"false", "full history is required")
        commits = git("rev-list", "--all").decode().splitlines()
        for commit in commits:
            for record in git("ls-tree", "-r", "-z", commit).split(b"\0"):
                if not record:
                    continue
                metadata, raw_name = record.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                name = raw_name.decode()
                require(mode in {"100644", "100755"} and kind == "blob", f"linked or non-blob history member: {name}")
                pair = (name, oid)
                if pair not in checked:
                    check_file(name, git("cat-file", "blob", oid))
                    checked.add(pair)
    receipt = {
        "schema_version": 1, "status": "PASS", "head": git("rev-parse", "HEAD").decode().strip(),
        "tracked_files": len(names), "local_links_and_anchors": links,
        "history_requested": args.history, "reachable_commits": len(commits), "historical_file_versions": len(checked),
        "scope": "file boundary and workstation-path checks, current local links; secret scanning and human review are separate",
        "files": [{"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()} for name in names],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(names)} files; {links} links; {len(commits)} commits; {len(checked)} historical file versions.")


if __name__ == "__main__":
    main()
