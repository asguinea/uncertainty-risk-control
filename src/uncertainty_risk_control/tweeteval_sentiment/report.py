"""Regenerated research tables, retaining review-all and the observed test exception."""

from .projection import CLASSES
from .replay import metrics


def percent(value):
    return "undefined" if value is None else f"{100 * value:.4f}%"


def number(value):
    return "undefined" if value is None else f"{value:.12g}"


def render(result):
    lines = [
        "# TweetEval Sentiment: risk tolerance, automation and calibration labels", "",
        "Generated from frozen D1/D2 aggregate evidence. An accepted sentiment tag is wrong when it differs from the released human reference. These are benchmark research results, not objective sentiment truth or product-readiness evidence.", "",
        f"Replayed **{result['final_candidate_tests']} final candidate tests** and regenerated **{result['warmup_records']:,} warm-up aggregate records**. The scorer, candidate design and historical results remain fixed.", "",
        "## Final calibration: a passing warm-up need not pass the final role", "",
        "Final calibration contains 7,143 rows. Each budget separately uses delta 0.05. The ordered sequence has 20 candidates; the first failure is included and later candidates are not replayed.", "",
        "| Budget | State | Winning threshold | Selected / errors | Winner exact p | CP upper diagnostic | Passing / tested | First failed candidate selected / errors |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for alpha, item in result["final_calibration"].items():
        c, failure = item["controller"], item["tests"][-1]
        tau = "none" if c["threshold"] is None else repr(c["threshold"])
        lines.append(f"| {percent(float(alpha))} | {c['state']} | {tau} | {c['selected']:,} / {c['harmful']:,} | {number(c['p_value'])} | {percent(c['cp_upper'])} | {c['certified']} / {c['tested']} | {failure['selected']:,} / {failure['harmful']:,} |")
    first = result["final_calibration"]["0.025"]["tests"][0]
    lines += ["", f"At 2.5%, the first candidate selects {first['selected']} calibration rows with {first['harmful']} error; its exact p-value is {number(first['p_value'])}, above 0.05. The resulting review-all controller has zero actions and undefined winner p-value, CP bound and conditional error. The failed candidate's observed counts are not zero and must not be replaced by the fallback counts.", "",
              "CP values are fixed-candidate diagnostics, not an adaptive confidence band. A calibration result is conditional on the frozen design and sampling assumptions; it is not a joint guarantee across budgets or classes, nor a guarantee for a shifted test population.", "",
              "## Locked test: risk and review workload", "",
              "Official TEST contains 12,284 rows, separate from the train/validation source calibration pool. All four controllers were frozen before the historical D2 test-label access; no post-test adaptation was performed in D2.", "",
              "| Budget | Accepted | Wrong | Automation | Selected error | Correct accepted | Reviewed | Review rate |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    locked = result["evaluations"]["LOCKED_TEST"]
    for alpha, row in locked["controllers"].items():
        c, m = row["counts"], metrics(row["counts"])
        lines.append(f"| {percent(float(alpha))} | {c['selected']:,} | {c['harmful']:,} | {percent(m['automation'])} | {percent(m['selected_error'])} | {c['selected'] - c['harmful']:,} | {c['n'] - c['selected']:,} | {percent(m['review_rate'])} |")
    lines += ["", "The 15% policy has observed test selected error **15.1884%**, slightly above its nominal budget; this result is retained. Source calibration does not establish the same guarantee for the separate official TEST population. Observed proportions can also fluctuate even under matched sampling assumptions; this finite test result alone does not diagnose the cause of the excess.", "", "## Baselines", "",
              "Raw confidence thresholds are descriptive policies without a selected-risk certificate. Review-all conditional error remains undefined.", "",
              "| Evaluation role | Policy | Accepted | Wrong | Automation | Selected error | Review rate |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    names = {"review_all": "Review all", "accept_all": "Accept all", "raw_confidence_0.5": "Confidence ≥ 0.5", "raw_confidence_0.8": "Confidence ≥ 0.8", "raw_confidence_0.9": "Confidence ≥ 0.9"}
    for role, group in result["evaluations"].items():
        for policy, row in group["baselines"].items():
            c, m = row["counts"], metrics(row["counts"])
            lines.append(f"| {role} | {names[policy]} | {c['selected']:,} | {c['harmful']:,} | {percent(m['automation'])} | {percent(m['selected_error'])} | {percent(m['review_rate'])} |")
    lines += ["", "## Development full-pool results", "",
              "Warm-up calibration and warm-up evaluation each contain 7,142 rows. Each full-pool row is one run, not 100 independent replications. The 2.5% development controller passes here but returns review-all in final calibration; development success is not a replacement for final evidence.", "",
              "| Budget | Development threshold | Calibration selected / errors | Warm-up accepted / errors | Evaluation automation | Selected error |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for alpha, row in result["evaluations"]["WARMUP_EVALUATION"]["controllers"].items():
        c = result["warmup_full_controllers"][alpha]
        e, m = row["counts"], metrics(row["counts"])
        lines.append(f"| {percent(float(alpha))} | {repr(c['threshold'])} | {c['selected']:,} / {c['harmful']:,} | {e['selected']:,} / {e['harmful']:,} | {percent(m['automation'])} | {percent(m['selected_error'])} |")
    lines += ["", "## Reference composition and class slices", "",
              "| Reference class | Warm-up evaluation (n=7,142) | Final calibration (n=7,143) | Locked TEST (n=12,284) |",
              "| --- | ---: | ---: | ---: |"]
    for name in CLASSES:
        warm = result["evaluations"]["WARMUP_EVALUATION"]["controllers"]["0.05"]["reference_class"][name]["n"]
        cal = result["final_reference_support"][name]
        test = locked["controllers"]["0.05"]["reference_class"][name]["n"]
        lines.append(f"| {name} | {warm:,} ({percent(warm / 7142)}) | {cal:,} ({percent(cal / 7143)}) | {test:,} ({percent(test / 12284)}) |")
    lines += ["", "Class proportions differ across the source roles and official TEST. These marginals do not establish pure label shift or explain the difference causally. Predicted-class automation uses the predicted-class population; reference-class review uses the human-reference population. Neither is a class-specific guarantee.", "",
              "| Role | Budget | Predicted class | Total predictions | Accepted | Wrong | Within-class automation | Selected error |",
              "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for role, group in result["evaluations"].items():
        for alpha, row in group["controllers"].items():
            for name, p in row["predicted_class"].items():
                m = metrics({k: p[k] for k in ("n", "selected", "harmful")}, classes=False)
                lines.append(f"| {role} | {percent(float(alpha))} | {name} | {p['n']:,} | {p['selected']:,} | {p['harmful']:,} | {percent(m['automation'])} | {percent(m['selected_error'])} |")
    lines += ["", "| Role | Budget | Reference class | Support | Accepted | Reviewed | Review fraction |", "| --- | --- | --- | ---: | ---: | ---: | ---: |"]
    for role, group in result["evaluations"].items():
        for alpha, row in group["controllers"].items():
            for name, r in row["reference_class"].items():
                lines.append(f"| {role} | {percent(float(alpha))} | {name} | {r['n']:,} | {r['accepted']:,} | {r['review']:,} | {percent(r['review'] / r['n'])} |")
    lines += ["", "The 5% locked policy accepts only one predicted-neutral post; zero observed error in that slice is sparse evidence. Its predicted-positive acceptance is much larger. Pooled automation conceals this uneven usefulness.", "", "## Calibration-label warm-up", "",
              "Each budget has seven non-full sizes with 100 deterministic nested whole-component runs per size, plus one full-pool run. All requested sizes were realized exactly. Every run uses the same warm-up evaluation pool. Automation summaries include review-all; conditional-error summaries include only nonzero selections. Percentile ranges are descriptive, not confidence intervals or independent-replication evidence.", ""]
    for alpha, tiers in result["warmup"]["aggregation"].items():
        lines += [f"### Budget {percent(float(alpha))}", "", "| Labels | Runs | Certification | Median automation | Automation p05–p95 | Median nonzero selected error |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for n in sorted(tiers, key=int):
            a = tiers[n]; u = a["evaluation_automation"]; e = a["evaluation_selected_error_nonzero"]
            label = f"{int(n):,}" + (" (single full pool)" if a["replicates"] == 1 else "")
            lines.append(f"| {label} | {a['replicates']} | {percent(a['certification_frequency'])} | {percent(u['median'])} | {percent(u['p05'])}–{percent(u['p95'])} | {percent(e['median'])} |")
        lines += [""]
    lines += ["| Budget | First certification | First ≥90% certification | First ≥90% certification and ≥10% median automation | ≥25% automation | ≥50% automation |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for alpha, m in result["warmup"]["milestones"].items():
        vals = [m[k] for k in ("any_certification", "certification_90", "combined_90_certification_automation_0.1", "combined_90_certification_automation_0.25", "combined_90_certification_automation_0.5")]
        lines.append(f"| {percent(float(alpha))} | " + " | ".join("not reached" if v is None else f"{v:,}" for v in vals) + " |")
    lines += ["", "The last two columns also require ≥90% certification. The 2.5% first-certification milestone at 7,142 labels is a single full-pool observation. These label requirements describe the frozen study and do not establish universal sample complexity, staffing costs or monetary ROI. The JSON receipt preserves every historical quantile and milestone.", "", "## Reproduction boundary", "",
              "Final candidate tests are reconstructed from sufficient statistics. Warm-up winner diagnostics, counts, quantiles and milestones are checked, but complete historical warm-up prefixes and subset membership are unavailable. Source tweets, row labels/scores, identities, the identity key and model assets are excluded. This release does not reproduce training or inference, establish independent replication, or implement the separate Negative N1/N2 follow-up studies.", "", f"Evidence manifest SHA-256: `{result['evidence_manifest_sha256']}`.", ""]
    return "\n".join(lines)
