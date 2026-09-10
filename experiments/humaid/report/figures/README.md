# HumAID figures

[Risk and transfer: SVG](risk_and_transfer.svg) · [PNG](risk_and_transfer.png)

[Calibration size: SVG](calibration_size.svg) · [PNG](calibration_size.png)

[Verified numerical inputs and provenance](plot_data.json)

## Risk and calibration transfer

Each point shows automatically deprioritized posts / all evaluated posts on the horizontal axis, and priority-labeled posts / automatically deprioritized posts on the vertical axis. The three panels retain distinct populations: 2018 source locked (9,559), 2019 source-policy transfer on warm-up evaluation (3,075), and 2019 locally calibrated locked evaluation (6,159). Source budgets are 2.5%, 5%, 10%; the target series uses 5%. The raw 0.5 scorer cutoff is a descriptive baseline.

No curve connects these populations. The source certificate does not formally transfer. Comparing the two target panels does not estimate a paired or causal recalibration benefit. Review-all has undefined selected error and is omitted. Deprioritize-all has much larger selected error and is omitted for legibility; its counts remain in the [complete tables](../results.md) and JSON. The points are observed rates, not confidence limits. Delta is 0.05 for each budget; there is no guarantee for every event.

## Calibration sample size

The source and target 5% series show calibration passing frequency and median automation on their respective warm-up evaluation roles. Each plotted requested tier (50, 100, 200, 500, 1,000, 2,000) has 100 recorded runs. Medians and 5th–95th percentile shading include zero automation from review-all. Bands are descriptive, not confidence intervals, and the reused pools are not independent replications.

Full-pool rows (source 4,774; target 3,075) are single runs and are excluded from the repeated-run curves. In particular, the source's combined 90%-passing/10%-automation milestone at 4,774 is a single full-pool observation. At source n = 2,000 only 5/100 runs pass and median automation is zero. Values are study-specific label requirements.

## Regeneration and attribution

From the repository root run `uv run --locked --group figures python scripts/plot_social_media_studies.py --output results/social-media`. The [generator](../../../../scripts/plot_social_media_studies.py) replays the public bundle before plotting. The output mirrors these paths beneath the requested directory. JSON retains the complete verified replay, generator SHA-256 and environment. No source text, labels per row, model weights or recalibration are involved.

These are original analytical figures based on the HumAID study. Credit Alejandro Sanchez Guinea / EyeTrustAI and cite [HumAID and its terms](../../../../THIRD_PARTY_NOTICES.md#humaid). Human priority labels are the reference, not verified incident truth. Preserve population labels and these qualifications when reusing figures.
