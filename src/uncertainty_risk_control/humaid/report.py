"""Deterministic Markdown tables from checked HumAID aggregate evidence."""

from .replay import metrics


def percent(value):
    return "undefined" if value is None else f"{100 * value:.2f}%"


def render(result):
    lines = [
        "# HumAID: risk-controlled crisis-post deprioritization", "",
        "Generated from frozen aggregate evidence. Human-agreed crisis categories define priority; these are research observations, not verified incident truth or product readiness.", "",
        f"Verified **{result['final_candidate_tests']} final candidate tests** and regenerated **{result['warmup_records']:,} warm-up aggregate records**. No new training, inference or experiment was performed.", "",
        "## Final calibration", "",
        "A post is automatically deprioritized when its frozen priority score is at or below the selected threshold. Error is the priority-label fraction among deprioritized posts. Each budget uses delta 0.05 separately.", "",
        "| Calibration population | Budget | Threshold | Selected | Priority errors | Exact p-value | CP upper diagnostic | Passing / tested | First failure index |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for period, budgets in result["final_calibration"].items():
        n = 4774 if period == "source_2018" else 3075
        for alpha, item in budgets.items():
            c = item["controller"]
            lines.append(f"| {period} (n={n:,}) | {percent(float(alpha))} | {c['threshold']:.17g} | {c['selected']:,} | {c['harmful']} | {c['p_value']:.12g} | {percent(c['cp_upper'])} | {c['certified']} / {c['tested']} | {c['stopped_at_index']} |")
    lines += ["", "Indices are zero-based. The first failed test is included; later candidates are not replayed. CP bounds are fixed-candidate diagnostics, not an adaptive confidence band. The guarantee depends on the frozen design and sampling assumptions; it is not joint across budgets, events or periods.", "", "## Pooled evaluation and baselines", "", "| Population / role | Policy | Budget | n | Deprioritized | Priority errors | Automation | Selected error | Priority retained for review |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in result["evaluations"]:
        if row["event"] is not None:
            continue
        c, m = row["counts"], metrics(row["counts"])
        budget = "—" if row["alpha"] is None else percent(row["alpha"])
        lines.append(f"| {row['period']} / {row['role']} | {row['policy']} | {budget} | {c['n']:,} | {c['selected']:,} | {c['harmful']:,} | {percent(m['automation_rate'])} | {percent(m['selected_error'])} | {c['priority_total'] - c['harmful']:,}/{c['priority_total']:,} ({percent(m['priority_recall_to_review'])}) |")
    lines += ["", "The source primary locked policy deprioritizes 1,327/9,559 posts with 45 priority errors (3.39%). The target locally calibrated locked policy deprioritizes 1,115/6,159 with 32 errors (2.87%).", "", "Zero-shot uses the unchanged source controller on TARGET_WARMUP_EVAL (3,075 posts): 522 selected, nine errors (1.72%). Local locked evaluation uses a different role (6,159 posts). Their difference is not a paired or causal estimate of recalibration benefit. The 2018 certificate does not formally transfer to 2019. The scorer remains unchanged.", "", "Review-all error is undefined because its selected denominator is zero. Baselines have no selected-risk certificate. Warm-up evaluation is development evidence and is reused across the warm-up runs.", "", "## Event slices", "", "| Period / role | Policy | Event | n | Deprioritized | Priority errors | Automation | Selected error |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in result["evaluations"]:
        if row["event"] is None:
            continue
        c, m = row["counts"], metrics(row["counts"])
        lines.append(f"| {row['period']} / {row['role']} | {row['policy']} | {row['event']} | {c['n']:,} | {c['selected']:,} | {c['harmful']} | {percent(m['automation_rate'])} | {percent(m['selected_error'])} |")
    lines += ["", "All slices describe the primary 5% policy. They partition their corresponding pooled evaluation. Kerala's source locked selected error exceeds 5%; the pooled certificate is not an event-specific guarantee.", "", "## Calibration-label warm-up", "", "Every size below the full pool has 100 deterministic, nested subsampling runs. Each full pool has one run. All runs use the same period-specific warm-up evaluation pool. The 5th and 95th percentiles are descriptive; repeated/nested runs are not independent experiments or confidence intervals.", ""]
    for period, summary in result["warmup"].items():
        target = period == "target_2019"
        utility = "evaluation_automation_rate" if target else "evaluation_auto_deprioritization_rate"
        error = "evaluation_selected_error_nonzero" if target else "evaluation_selected_error_nonzero_selection"
        lines += [f"### {period}", "", "| Calibration labels | Runs | Certified | Median automation | Automation p05–p95 | Nonzero evaluation runs | Median nonzero selected error |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for n in sorted(summary["aggregates"], key=int):
            a = summary["aggregates"][n]
            u, e = a[utility], a[error]
            label = f"{int(n):,}" + (" (single full pool)" if a["runs"] == 1 else "")
            lines.append(f"| {label} | {a['runs']} | {a['certified_runs']} ({percent(a['certification_frequency'])}) | {percent(u['median'])} | {percent(u['p05'])}–{percent(u['p95'])} | {a['evaluation_nonzero_selection_runs']} | {percent(e['median'] if e else None)} |")
        lines += ["", "| Historical milestone | First labels |", "| --- | ---: |"]
        for name, value in summary["milestones"].items():
            lines.append(f"| {name.replace('_', ' ')} | {value if value is not None else 'not reached'} |")
        lines += [""]
    lines += ["The combined ≥90% certification / ≥10% median automation milestone is 4,774 labels in the source and 2,000 in the target. The source full-pool row is a single observation; its 100% frequency is not evidence of 100-run stability. These are descriptive label requirements for the frozen study, not universal annotation requirements.", "", "## Reproduction boundary", "", "This replay recomputes final fixed-sequence decisions and checks aggregate counts, metrics, warm-up winner diagnostics, historical quantiles and milestones. Warm-up winner/stop summaries do not contain every candidate count, so complete warm-up prefix reconstruction is unavailable. Source rows, assignments, model weights, historical training and checkpoint inference are not distributed.", "", f"Evidence manifest SHA-256: `{result['evidence_manifest_sha256']}`.", ""]
    return "\n".join(lines)
