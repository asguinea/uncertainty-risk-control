"""Render publication figures only after replaying the frozen evidence bundle.

Run from a source checkout with the optional, locked ``figures`` dependency group.
No training, inference, additional calibration candidates, or raw data are used.
"""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter, ScalarFormatter

from uncertainty_risk_control.goemotions.replay import BUDGET_KEYS, replay
from uncertainty_risk_control.provenance import environment, reference_integrity


COLORS = ("#0072B2", "#D55E00", "#009E73", "#8A508F")
MARKERS = ("o", "s", "^", "D")
TIERS = (50, 100, 200, 500, 1000, 2000, 4000)


def plot_data(result):
    """Keep the exact verified numbers behind every point, plus its denominator."""
    return {
        "schema_version": 1,
        "study_id": result["study_id"],
        "evidence_manifest_sha256": result["evidence_manifest_sha256"],
        "reference_integrity": reference_integrity(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "environment": {**environment(), "matplotlib": matplotlib.__version__},
        "locked": result["evaluations"]["LOCKED_TEST"],
        "warmup": result["warmup"],
        "display": {
            "rate_scale": "fractions in JSON; percentages in figures",
            "locked_uncertainty_intervals": "none; descriptive observed rates",
            "review_all": "retained in JSON; omitted from scatter because selected error is undefined",
            "warmup_tiers_plotted": list(TIERS),
            "warmup_full_pool": "retained in JSON and tables; omitted from curves because it has one run",
            "warmup_bands": "empirical p05 to p95 over all 100 runs, including review-all as zero automation; not confidence intervals",
            "warmup_lines": "visual guides between recorded tiers, not interpolation estimates",
            "reproduction": "final-calibration replay and aggregate regeneration; no model or warm-up prefix reproduction",
        },
    }


def style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 10,
        "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.labelsize": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.edgecolor": "#AAB3BC",
        "text.color": "#203040", "axes.labelcolor": "#203040",
        "xtick.color": "#435363", "ytick.color": "#435363",
        "figure.facecolor": "white", "axes.facecolor": "white",
        "svg.fonttype": "none", "svg.hashsalt": "goemotions-mb1-figures-v1",
    })


def frame(ax):
    ax.grid(color="#E6EAEE", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))


def save(fig, output, name, description):
    # Omit timestamps so repeated rendering in the same locked environment is stable.
    fig.savefig(output / f"{name}.svg", metadata={
        "Date": None, "Creator": "uncertainty-risk-control",
        "Title": name.replace("_", " "), "Description": description,
    })
    # Matplotlib puts trailing spaces in path attributes; keep generated Git diffs clean.
    svg = output / f"{name}.svg"
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    fig.savefig(output / f"{name}.png", dpi=180, metadata={
        "Software": "uncertainty-risk-control", "Description": description,
    })
    plt.close(fig)


def risk_automation(data, output):
    locked = data["locked"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.2), gridspec_kw={"width_ratios": [1.35, 1]})
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.24, top=0.74, wspace=0.28)
    fig.suptitle("Risk control can leave most work for review", x=0.075, y=0.965,
                 ha="left", fontsize=19, fontweight="bold")
    fig.text(0.075, 0.905, "GoEmotions MB1 · 10,853 locked comments · one frozen classifier and meta-risk scorer", fontsize=10)
    baseline_styles = (
        ("RAW_CONFIDENCE_GE_0_5", "Confidence ≥ 0.5", (-10, 13), "right"),
        ("RAW_CONFIDENCE_GE_0_8", "Confidence ≥ 0.8", (-10, 8), "right"),
        ("RAW_CONFIDENCE_GE_0_9", "Confidence ≥ 0.9", (11, -15), "left"),
        ("ACCEPT_ALL_TOP_TAGS", "Accept all", (-9, 11), "right"),
    )
    for ax in axes:
        frame(ax)
        ax.set_xlabel("Automation (accepted / all comments)")
        ax.set_ylabel("Observed error among accepted tags")
    axes[0].set(title="All recorded nonempty policies", xlim=(-0.025, 1.045), ylim=(-0.013, 0.445))
    axes[1].set(title="Detail: strict budgets", xlim=(0, 0.11), ylim=(0, 0.078))
    for index, key in enumerate(BUDGET_KEYS):
        row = locked["controllers"][key]
        for ax in axes:
            if ax is axes[1] and float(key) > 0.1:
                continue
            ax.scatter(row["automation"], row["selected_error"], color=COLORS[index],
                       marker=MARKERS[index], s=74, edgecolor="white", linewidth=0.7, zorder=4)
            if ax is axes[0] and float(key) <= 0.1:
                continue  # Their labels and exact counts appear in the detail panel.
            label = f"{float(key):.0%} budget"
            if ax is axes[1]:
                label += f"\n{row['harmful']} / {row['selected']} unsupported"
            offset = (10, -31) if key == "0.05" else ((10, -22) if key == "0.15" else (10, 11))
            ax.annotate(label, (row["automation"], row["selected_error"]),
                        xytext=offset, textcoords="offset points", fontsize=9, color=COLORS[index])
    for key, label, offset, align in baseline_styles:
        row = locked["baselines"][key]
        for ax in axes:
            if ax is axes[1] and key != "RAW_CONFIDENCE_GE_0_9":
                continue
            ax.scatter(row["automation"], row["selected_error"], color="#677584", marker="x", s=50, zorder=3)
            actual_offset = (-8, 12) if ax is axes[1] else offset
            actual_align = "right" if ax is axes[1] else align
            ax.annotate(label, (row["automation"], row["selected_error"]), xytext=actual_offset,
                        textcoords="offset points", ha=actual_align, fontsize=9, color="#526170")
    handles = [Line2D([], [], marker=MARKERS[i], color=COLORS[i], linestyle="none", label=f"{float(key):.0%} budget")
               for i, key in enumerate(BUDGET_KEYS)]
    handles.append(Line2D([], [], marker="x", color="#677584", linestyle="none", label="Descriptive baseline"))
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.068, 0.885), ncol=5, frameon=False, fontsize=9)
    fig.text(0.075, 0.135, "5% and 10% budgets automate under 5% of comments. The remaining comments require review.", fontsize=10, fontweight="bold", va="top")
    fig.text(0.075, 0.085, "Points show locked observations, not risk bounds. Each budget uses δ = 0.05 separately; no joint or subgroup guarantee.\nReview-all is omitted: its conditional error is undefined. Error means absence from the agreed-label reference.", fontsize=9, linespacing=1.6, va="top")
    save(fig, output, "risk_automation", "Descriptive locked automation and selected error, with strict-budget detail. No confidence intervals; no joint guarantee.")


def calibration_size(data, output):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
    fig.subplots_adjust(left=0.075, right=0.97, bottom=0.26, top=0.74, wspace=0.24)
    fig.suptitle("Passing calibration and useful automation are different outcomes", x=0.075, y=0.965,
                 ha="left", fontsize=17, fontweight="bold")
    fig.text(0.075, 0.905, "GoEmotions MB1 · warm-up evidence · 100 recorded samples per budget and requested size", fontsize=10)
    handles = []
    for index, key in enumerate(BUDGET_KEYS):
        rows = [data["warmup"][key]["aggregates"][str(tier)] for tier in TIERS]
        auto = [row["evaluation_automation"] for row in rows]
        color, marker = COLORS[index], MARKERS[index]
        line, = axes[0].plot(TIERS, [row["certification_frequency"] for row in rows],
                            color=color, marker=marker, linewidth=1.7, markersize=5, label=f"{float(key):.0%} budget")
        axes[1].fill_between(TIERS, [row["p05"] for row in auto], [row["p95"] for row in auto], color=color, alpha=0.10)
        axes[1].plot(TIERS, [row["median"] for row in auto], color=color, marker=marker, linewidth=1.7, markersize=5)
        handles.append(line)
    for ax in axes:
        frame(ax)
        ax.set_xscale("log")
        ax.set_xticks(TIERS)
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.minorticks_off()
        ax.tick_params(axis="x", labelsize=9)
        ax.set_xlabel("Requested calibration comments (log scale)")
        ax.set_xlim(43, 4700)
    axes[0].set(title="How often does a nonempty policy pass?", ylabel="Passing runs / 100 recorded runs", ylim=(-0.035, 1.075))
    axes[1].set(title="How much does that policy automate?", ylabel="Warm-up evaluation automation", ylim=(-0.015, 0.405))
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.068, 0.885), ncol=4, frameon=False, fontsize=9)
    fig.text(0.075, 0.16, "At 5%, all 100 runs pass at requested n = 4,000; median automation is still only 4.18%.", fontsize=10, fontweight="bold", va="top")
    fig.text(0.075, 0.112, "Right: median and empirical 5th–95th percentiles, including review-all as zero automation; bands are not confidence intervals.\nWhole-group samples can be smaller than requested. Runs reuse development data and sample orders across budgets and tiers.\nLines guide the eye. FULL (5,427 comments; one run per budget) is in the tables, not these curves.", fontsize=9, linespacing=1.6, va="top")
    save(fig, output, "calibration_size", "Descriptive warm-up passing frequencies and median automation. Bands are empirical p05-p95, not confidence intervals. FULL omitted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    # Integrity and protocol checks finish before any output directory is created.
    data = plot_data(replay(args.evidence))
    style()
    args.output.mkdir(parents=True, exist_ok=True)
    risk_automation(data, args.output)
    calibration_size(data, args.output)
    (args.output / "plot_data.json").write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("Wrote two SVG figures, two PNG figures, and plot_data.json after evidence replay.")


if __name__ == "__main__":
    main()
