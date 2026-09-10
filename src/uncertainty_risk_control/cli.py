"""Portable, data-free commands for the initial research foundation."""

import argparse
import hashlib
import json
import tomllib
from pathlib import Path

from . import METHOD_ID, SEQUENCE_ID, synthetic, verification
from .provenance import environment, reference_integrity


def main() -> None:
    parser = argparse.ArgumentParser(prog="uqrc")
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="run historical synthetic method verification")
    verify.add_argument("--skip-monte-carlo", action="store_true", help="run deterministic verification only")
    example = commands.add_parser("synthetic", help="run a synthetic illustration with separate data roles")
    example.add_argument("--config", type=Path, required=True)
    goemotions = commands.add_parser("goemotions", help="replay frozen GoEmotions MB1 evidence and regenerate aggregates")
    goemotions.add_argument("--evidence", type=Path, required=True)
    goemotions.add_argument("--report", type=Path, help="write the regenerated Markdown research tables")
    humaid = commands.add_parser("humaid", help="replay frozen HumAID source/target evidence and regenerate aggregates")
    humaid.add_argument("--evidence", type=Path, required=True)
    humaid.add_argument("--report", type=Path, help="write the regenerated Markdown research tables")
    tweeteval = commands.add_parser("tweeteval-sentiment", help="replay frozen TweetEval Sentiment evidence and regenerate aggregates")
    tweeteval.add_argument("--evidence", type=Path, required=True)
    tweeteval.add_argument("--report", type=Path, help="write the regenerated Markdown research tables")
    sources = commands.add_parser("goemotions-sources", help="verify reader-side upstream files; optionally download them")
    sources.add_argument("--inputs", type=Path, required=True)
    sources.add_argument("--directory", type=Path, required=True)
    sources.add_argument("--download", action="store_true", help="download missing pinned resources from upstream")
    for command in (verify, example, goemotions, humaid, tweeteval, sources):
        command.add_argument("--output", type=Path, help="write JSON here as well as stdout")
    args = parser.parse_args()
    try:
        integrity = reference_integrity()
        if args.command == "verify":
            result = {
                "kind": "synthetic_method_verification",
                "alpha": verification.ALPHA,
                "delta": verification.DELTA,
                "numerical": verification.numerical_verification(),
                "boundary_fixtures": verification.brute_force_fixtures(),
            }
            result["monte_carlo"] = None if args.skip_monte_carlo else {
                name: {"seed": 1729 + index, **verification.monte_carlo_scenario(name, config, 1729 + index)}
                for index, (name, config) in enumerate(verification.SCENARIOS.items())
            }
            result["monte_carlo_status"] = "SKIPPED" if args.skip_monte_carlo else "PASS"
            result["monte_carlo_total_experiments"] = 0 if args.skip_monte_carlo else sum(item["experiments"] for item in result["monte_carlo"].values())
        elif args.command == "synthetic":
            raw = args.config.read_bytes()
            result = synthetic.run(tomllib.loads(raw.decode("utf-8")))
            result["config_sha256"] = hashlib.sha256(raw).hexdigest()
        elif args.command == "goemotions":
            from .goemotions.replay import replay
            result = replay(args.evidence)
        elif args.command == "humaid":
            from .humaid.replay import replay
            result = replay(args.evidence)
        elif args.command == "tweeteval-sentiment":
            from .tweeteval_sentiment.replay import replay
            result = replay(args.evidence)
        else:
            from .goemotions.sources import verify_or_acquire
            result = verify_or_acquire(args.inputs, args.directory, download=args.download)
        result = {"schema_version": 1, "status": "PASS", "method_id": METHOD_ID, "sequence_id": SEQUENCE_ID, "reference_integrity": integrity, "environment": environment(), **result}
        output = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        if args.command in {"goemotions", "humaid", "tweeteval-sentiment"} and args.report:
            if args.command == "goemotions":
                from .goemotions.report import render
            elif args.command == "humaid":
                from .humaid.report import render
            else:
                from .tweeteval_sentiment.report import render
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(render(result), encoding="utf-8")
        print(output, end="")
    except (ValueError, TypeError, OSError, AssertionError, KeyError) as error:
        parser.exit(1, f"uqrc: {error}\n")


if __name__ == "__main__":
    main()
