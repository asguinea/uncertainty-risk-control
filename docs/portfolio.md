# Portfolio and article drafts

These drafts accompany the local v0.2.0 candidate. They have not been posted to a website, EyeTrustAI page, Substack or Medium. Link the [repository](https://github.com/asguinea/risk-controlled-social-media-analysis) while discussing work in progress; once v0.2.0 is published, replace that with the verified immutable release link and finalized citation metadata. The existing [v0.1.0 release](https://github.com/asguinea/risk-controlled-social-media-analysis/releases/tag/v0.1.0) supports GoEmotions only.

## Personal portfolio card

**Risk-controlled social media analysis**

Research on uncertainty quantification for emotion tagging, sentiment classification and crisis triage. I investigate how explicit error budgets change automation, human review and calibration-label requirements using GoEmotions, HumAID and TweetEval Sentiment. The research includes frozen-evidence calibration replay and reproducible aggregate figures, including low-utility and unsuccessful outcomes. Developed in connection with EyeTrustAI, which I own.

## Suggested article sequence

| Article | Main evidence and suggested figure |
| --- | --- |
| **How much social media analysis can we automate under an error budget?** | Introduce the actions and human references with the [study map](figures/study_map.png), then use the [three-study research note](social-media-research.md). |
| **A calibrated emotion tagger can still leave almost everything for review** | GoEmotions' strict budgets and annotation agreement; [risk/automation](../experiments/goemotions/report/figures/risk_automation.png) and [sample size](../experiments/goemotions/report/figures/calibration_size.png). |
| **Does a crisis-triage threshold travel to the next year?** | HumAID source transfer and local calibration on separate roles; [risk and transfer](../experiments/humaid/report/figures/risk_and_transfer.png) and [sample size](../experiments/humaid/report/figures/calibration_size.png). |
| **Who gets automated by a selective sentiment classifier?** | TweetEval review-all, class selection and the observed result above 15%; [risk and classes](../experiments/tweeteval-sentiment/report/figures/risk_and_class_selection.png) and [sample size](../experiments/tweeteval-sentiment/report/figures/calibration_size.png). |

## Opening paragraph

A social media classifier can label every post. The harder question is how much work it can handle when errors among its automatic decisions must stay below a chosen tolerance. I investigated this across emotion tagging, crisis-post deprioritization and sentiment classification. Stricter budgets can leave almost everything for review; more calibration labels do not always deliver useful automation; and calibration on one population does not automatically protect another. The accompanying research repository lets readers replay frozen final-calibration evidence and regenerate aggregate reports while keeping unsuccessful results and uncertainty about the human references visible.

## EyeTrustAI research-page description

EyeTrustAI's validation research informed these studies of uncertainty quantification for social media analysis. Alejandro Sanchez Guinea, EyeTrustAI's owner, maintains the personal research repository. It makes selected protocols, implementations and aggregate benchmark evidence reproducible. A planned product-validation companion will map immutable research releases to particular EyeTrustAI versions and requirements, identifying shared evidence and ownership. These benchmark results alone do not establish product readiness or independent external validation.

## Reuse and precision

SVGs accompany each PNG. Preserve the full captions and population labels from the [GoEmotions](../experiments/goemotions/report/figures/README.md), [HumAID](../experiments/humaid/report/figures/README.md), and [TweetEval](../experiments/tweeteval-sentiment/report/figures/README.md) guides. Credit the original analysis and cite applicable datasets, models and statistical methods from the [notices](../THIRD_PARTY_NOTICES.md).

Use “replays frozen final-calibration evidence and regenerates aggregate reports.” State delta 0.05 separately per budget and retain the sampling assumptions. Describe human references explicitly. Report HumAID target roles separately; retain TweetEval's review-all and 15.1884% observation. Full-pool warm-up points are single runs. The 86 final tests and 6,810 aggregate records measure reproduction scope, not a combined performance result.

The [contribution statement](contributions.md) identifies prior work and shared EyeTrustAI ownership. The [reproduction guide](reproduction.md) states the missing historical training, inference and warm-up prefix workflows.
