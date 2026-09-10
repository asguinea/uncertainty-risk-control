"""Render the social media study map and HumAID/TweetEval aggregate figures.

Only the published evidence is read. No model, threshold, or evaluation is fit.
GoEmotions' original generator and figures remain separate and unchanged.
"""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import PercentFormatter

from uncertainty_risk_control.goemotions.replay import replay as emotion_replay
from uncertainty_risk_control.humaid.replay import replay as crisis_replay
from uncertainty_risk_control.tweeteval_sentiment.replay import replay as sentiment_replay
from uncertainty_risk_control.provenance import environment


COLORS = ["#0072B2", "#D55E00", "#009E73", "#8A508F"]
MARKERS = ["o", "s", "^", "D"]


def save(fig, directory, name):
    directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(directory / f"{name}.png", dpi=180, facecolor="white")
    svg = directory / f"{name}.svg"
    fig.savefig(svg, metadata={"Date": None, "Creator": "Risk-controlled social media analysis"})
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def write_data(directory, name, data):
    directory.mkdir(parents=True, exist_ok=True)
    data = {"schema_version": 1,
            "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "environment": {**environment(), "matplotlib": matplotlib.__version__}, **data}
    (directory / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def axes_style(ax, xlabel, ylabel):
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=.2, zorder=0)
    ax.spines[["top", "right"]].set_visible(False)


def rate_axes(ax):
    axes_style(ax, "Automatically handled (% of posts)", "Observed error (% of selected posts)")
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))


def crisis_risk(data, out):
    fig, axes = plt.subplots(1, 3, figsize=(15, 6.4))
    panels = [("source_2018", "locked_evaluation", "2018 source · locked", "calibrated", 9559),
              ("target_2019", "warmup_evaluation", "2019 transfer · warm-up evaluation", "zero_shot", 3075),
              ("target_2019", "locked_evaluation", "2019 local calibration · locked", "calibrated", 6159)]
    for ax, (period, role, title, policy, n) in zip(axes, panels):
        rows = [r for r in data["evaluations"] if r["period"] == period and r["role"] == role and r["event"] is None
                and r["policy"] in {policy, "RAW_0_5_CLASSIFIER_THRESHOLD"}]
        assert len(rows) == (4 if period == "source_2018" else 2)
        for row in rows:
            c = row["counts"]
            assert c["n"] == n and c["selected"] > 0
            raw = row["policy"] == "RAW_0_5_CLASSIFIER_THRESHOLD"
            label = "Raw 0.5 cutoff" if raw else f"{100 * row['alpha']:g}% budget"
            color = "#667085" if raw else {"0.025": COLORS[0], "0.05": COLORS[1], "0.1": COLORS[2]}[str(row["alpha"])]
            x, y = c["selected"] / n, c["harmful"] / c["selected"]
            ax.scatter(x, y, color=color, marker="x" if raw else "o", s=65, zorder=3)
            ax.annotate(label, (x, y), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=9)
        rate_axes(ax)
        ax.set(xlim=(0, .43), ylim=(0, .20), title=f"{title}\nn = {n:,}")
        ax.set_xticks([0, .1, .2, .3, .4])
    fig.suptitle("Crisis triage: automation, error, and calibration transfer", fontsize=17, x=.06, ha="left")
    fig.subplots_adjust(left=.065, right=.98, bottom=.27, top=.79, wspace=.30)
    fig.text(.06, .14, "Action: deprioritize a post. Error: a deprioritized post has a human priority label. Points are observed rates.", fontsize=11)
    fig.text(.06, .095, "The source certificate does not formally transfer to 2019. The two 2019 panels use different roles and denominators.", fontsize=10)
    fig.text(.06, .05, "No paired estimate of recalibration benefit. Per-budget delta = 0.05; no event-level guarantee. Review-all has undefined selected error.", fontsize=10)
    save(fig, out, "risk_and_transfer")


def warmup_plot(series, out, title, caption, name="calibration_size"):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.4))
    for index, (label, records, utility_key, runs_key) in enumerate(series):
        rows = sorted((int(k), v) for k, v in records.items() if v[runs_key] == 100)
        xs = [x for x, _ in rows]
        kwargs = {"label": label, "color": COLORS[index], "marker": MARKERS[index], "linewidth": 1.8, "markersize": 5}
        axes[0].plot(xs, [v["certification_frequency"] for _, v in rows], **kwargs)
        axes[1].plot(xs, [v[utility_key]["median"] for _, v in rows], **kwargs)
        axes[1].fill_between(xs, [v[utility_key]["p05"] for _, v in rows], [v[utility_key]["p95"] for _, v in rows], color=COLORS[index], alpha=.12)
    for ax, ylabel in zip(axes, ("Runs passing calibration", "Median automation on warm-up evaluation")):
        axes_style(ax, "Requested calibration labels (log scale)", ylabel)
        ax.set_xscale("log")
        ax.set_xticks(xs, [f"{x:,}" for x in xs])
        ax.minorticks_off()
        ax.set_ylim(-.025, 1.025 if ax is axes[0] else max(.25, ax.get_ylim()[1]))
        ax.yaxis.set_major_formatter(PercentFormatter(1))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.53, .885), ncol=len(series), frameon=False)
    fig.suptitle(title, fontsize=17, x=.07, ha="left")
    fig.subplots_adjust(left=.075, right=.98, bottom=.27, top=.76, wspace=.25)
    fig.text(.07, .14, "100 recorded runs per plotted tier; medians include review-all. Shading: descriptive 5th–95th percentiles, not confidence intervals.", fontsize=10)
    fig.text(.07, .09, caption, fontsize=10)
    fig.text(.07, .045, "Full-pool rows are single observations and are excluded from the curves. Reused warm-up pools do not constitute independent replications.", fontsize=10)
    save(fig, out, name)


def sentiment_risk(data, out):
    locked = data["evaluations"]["LOCKED_TEST"]
    fig, (ax, classes) = plt.subplots(1, 2, figsize=(13, 6.6), gridspec_kw={"width_ratios": [1.1, 1]})
    for i, (alpha, row) in enumerate(locked["controllers"].items()):
        c = row["counts"]
        if not c["selected"]:
            assert alpha == "0.025" and c["harmful"] == 0
            continue
        x, y = c["selected"] / c["n"], c["harmful"] / c["selected"]
        ax.scatter(x, y, s=65, color=COLORS[i], marker=MARKERS[i], zorder=4)
        ax.annotate(f"{100 * float(alpha):g}% budget", (x, y), xytext=(8, -15), textcoords="offset points", fontsize=9)
    for key, row in locked["baselines"].items():
        c = row["counts"]
        if c["selected"]:
            ax.scatter(c["selected"] / c["n"], c["harmful"] / c["selected"], color="#667085", marker="x", s=50)
    rate_axes(ax)
    ax.set(xlim=(-.015, 1.05), ylim=(0, .35), title="Official TEST · n = 12,284")
    ax.text(.04, .94, "× Raw confidence cutoffs and accept-all", transform=ax.transAxes, va="top", fontsize=9, color="#667085")
    ax.text(.04, .85, "2.5% budget: REVIEW_ALL\nSelected error is undefined", transform=ax.transAxes, va="top", fontsize=10)
    names = ["negative", "neutral", "positive"]
    slices = locked["controllers"]["0.05"]["predicted_class"]
    values = [slices[n]["selected"] / slices[n]["n"] for n in names]
    classes.barh(names, values, color=COLORS[0], height=.50, zorder=3)
    classes.invert_yaxis()
    for i, name in enumerate(names):
        c = slices[name]
        classes.text(values[i] + .009, i, f"{c['selected']:,} / {c['n']:,} accepted\n{c['harmful']} errors", va="center", fontsize=10)
    axes_style(classes, "Accepted within predicted class", "")
    classes.xaxis.set_major_formatter(PercentFormatter(1))
    classes.set(xlim=(0, .35), title="5% budget · unequal class selection")
    fig.suptitle("Sentiment classification: risk tolerance and selective coverage", fontsize=17, x=.06, ha="left")
    fig.subplots_adjust(left=.075, right=.975, bottom=.28, top=.80, wspace=.32)
    fig.text(.06, .16, "Error: accepted sentiment differs from the human reference. At the 15% budget, observed TEST error is 810 / 5,333 = 15.1884%.", fontsize=10)
    fig.text(.06, .11, "Source calibration does not guarantee risk on a shifted TEST population. The observed excess is preserved, without post-TEST adaptation.", fontsize=10)
    fig.text(.06, .06, "Only one predicted-neutral post is accepted at 5%. These class slices are descriptive; delta = 0.05 per budget gives no class-level guarantee.", fontsize=10)
    save(fig, out, "risk_and_class_selection")


def study_map(studies, out):
    cards = [
        {"study": "GoEmotions", "application": "Emotion tagging", "action": "Accept an emotion tag", "error": "Tag absent from the\nagreed-label reference", "population": "Own group-preserving split\n10,853 locked comments", "question": "How much tagging remains useful\nunder strict error budgets?", "tests": 35, "warmup_records": 2804},
        {"study": "HumAID", "application": "Crisis triage", "action": "Deprioritize a crisis post", "error": "Selected post has a\nhuman priority label", "population": "2018 source → 2019 target\nDistinct evaluation roles", "question": "How do label requirements and\ncalibration change across years?", "tests": 16, "warmup_records": 1202},
        {"study": "TweetEval Sentiment", "application": "Sentiment classification", "action": "Accept a sentiment label", "error": "Label disagrees with the\nhuman sentiment reference", "population": "Source calibration → official TEST\n12,284 locked posts", "question": "Who gets automated when\nerror tolerance changes?", "tests": 35, "warmup_records": 2804},
    ]
    for card, (name, replay) in zip(cards, studies.items()):
        counts = replay["scope"] if name == "goemotions" else replay
        assert card["tests"] == counts.get("final_candidate_tests", counts.get("final_candidate_tests_replayed"))
        assert card["warmup_records"] == counts.get("warmup_records", counts.get("warmup_aggregate_records"))
    fig = plt.figure(figsize=(14, 7), facecolor="white")
    fig.text(.045, .92, "Risk-controlled social media analysis", fontsize=25, weight="bold")
    fig.text(.045, .86, "How much can we automate at a chosen error tolerance—and how much review remains?", fontsize=14)
    for i, card in enumerate(cards):
        x = .045 + i * .315
        fig.add_artist(FancyBboxPatch((x, .20), .29, .60, boxstyle="round,pad=0.012", facecolor="#F5F7FA", edgecolor="#DCE2EA", transform=fig.transFigure))
        fig.text(x + .014, .745, card["application"], fontsize=16, weight="bold", color=COLORS[i])
        fig.text(x + .014, .695, card["study"], fontsize=12)
        for y, label, value in [(.61, "ACTION", card["action"]), (.51, "ERROR REFERENCE", card["error"]), (.365, "EVALUATION", card["population"])]:
            fig.text(x + .014, y, label, fontsize=9, weight="bold", color="#667085")
            fig.text(x + .014, y - .033, value, fontsize=11, va="top", linespacing=1.5)
        fig.text(x + .014, .245, f"{card['tests']} final tests · {card['warmup_records']:,} warm-up records", fontsize=10)
    fig.text(.045, .12, "86 final candidate tests replayed · 6,810 warm-up aggregate records", fontsize=14, weight="bold")
    fig.text(.045, .07, "Reproduction inventory, not pooled performance. Distinct actions, references, and populations; no shared leaderboard.", fontsize=11)
    save(fig, out, "study_map")
    write_data(out, "study_map_data.json", {"cards": cards, "evidence_manifest_sha256": {k: v["evidence_manifest_sha256"] for k, v in studies.items()}, "total_final_tests": 86, "total_warmup_records": 6810, "scope": "reproduction inventory; no pooled performance"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": "#243247", "axes.labelcolor": "#243247", "xtick.color": "#243247", "ytick.color": "#243247", "svg.fonttype": "none", "svg.hashsalt": "social-media-studies-v020"})
    studies = {name: fn(args.source_root / "experiments" / name / "evidence") for name, fn in [("goemotions", emotion_replay), ("humaid", crisis_replay), ("tweeteval-sentiment", sentiment_replay)]}
    crisis, sentiment = studies["humaid"], studies["tweeteval-sentiment"]
    hum_dir = args.output / "experiments/humaid/report/figures"
    sent_dir = args.output / "experiments/tweeteval-sentiment/report/figures"
    crisis_risk(crisis, hum_dir)
    warmup_plot([(label, crisis["warmup"][period]["aggregates"], key, "runs") for label, period, key in [("2018 source · 5%", "source_2018", "evaluation_auto_deprioritization_rate"), ("2019 target · 5%", "target_2019", "evaluation_automation_rate")]], hum_dir, "Crisis triage: calibration labels and available automation", "Source n = 4,774 full-pool milestone is one run. Target full pool: n = 3,075. The evaluation populations differ.")
    sentiment_risk(sentiment, sent_dir)
    warmup_plot([(f"{100 * float(alpha):g}% budget", rows, "evaluation_automation", "replicates") for alpha, rows in sentiment["warmup"]["aggregation"].items()], sent_dir, "Sentiment classification: calibration labels and available automation", "At 2.5%, the single full-pool warm-up run passes; final calibration returns REVIEW_ALL. Full pool: n = 7,142.")
    for directory, name, replay in [(hum_dir, "humaid", crisis), (sent_dir, "tweeteval-sentiment", sentiment)]:
        write_data(directory, "plot_data.json", {"study": name, "verified_replay": replay, "display": {"full_pool_excluded_from_curves": True, "bands": "descriptive p05-p95, including review-all", "zero_selected_error": "undefined; omitted from risk scatter"}})
    study_map(studies, args.output / "docs/figures")
    print("PASS: verified public evidence; five figures (SVG/PNG) and three numerical/provenance records.")


if __name__ == "__main__":
    main()
