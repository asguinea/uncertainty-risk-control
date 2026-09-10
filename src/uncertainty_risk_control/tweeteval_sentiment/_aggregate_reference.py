"""Preserved historical quantiles, milestones and aggregation loop; no runner.

See provenance/tweeteval_sentiment_extraction.json.
"""
import numpy as np
BUDGETS = (0.025, 0.05, 0.1, 0.15)
TIERS = (50, 100, 200, 500, 1000, 2000, 4000, 7142)

def q(values):
    a = np.asarray(values, dtype=float)
    if len(a) == 0:
        return {'min': None, 'p05': None, 'median': None, 'p95': None, 'max': None}
    return {'min': float(np.min(a)), 'p05': float(np.quantile(a, 0.05)), 'median': float(np.median(a)), 'p95': float(np.quantile(a, 0.95)), 'max': float(np.max(a))}

def milestone(aggregate, key, predicate):
    for tier in TIERS:
        item = aggregate[str(tier)]
        if predicate(item):
            return tier
    return None

def aggregate(runs):
    aggregation = {}
    milestones = {}
    full = {}
    for budget in BUDGETS:
        key = str(budget)
        aggregation[key] = {}
        for tier in TIERS:
            values = runs[key][str(tier)]
            nonzero = [x for x in values if x['evaluation']['selected'] > 0]
            aggregation[key][str(tier)] = {'requested_n': tier, 'realized_n': q([x['realized_n'] for x in values]), 'replicates': len(values), 'certification_frequency': sum((x['calibration']['certified'] for x in values)) / len(values), 'review_all_frequency': sum((x['calibration']['review_all'] for x in values)) / len(values), 'evaluation_automation': q([x['evaluation']['automation'] for x in values]), 'evaluation_selected_error_nonzero': q([x['evaluation']['selected_error'] for x in nonzero]), 'threshold_nonzero': q([x['calibration']['threshold'] for x in values if x['calibration']['threshold'] is not None])}
        a = aggregation[key]
        milestones[key] = {'any_certification': milestone(a, 'certification_frequency', lambda x: x['certification_frequency'] > 0), 'certification_50': milestone(a, 'certification_frequency', lambda x: x['certification_frequency'] >= 0.5), 'certification_80': milestone(a, 'certification_frequency', lambda x: x['certification_frequency'] >= 0.8), 'certification_90': milestone(a, 'certification_frequency', lambda x: x['certification_frequency'] >= 0.9)}
        for target in (0.1, 0.25, 0.5, 0.75):
            milestones[key][f'median_automation_{target}'] = milestone(a, 'automation', lambda x, t=target: (x['evaluation_automation']['median'] or 0) >= t)
        for target in (0.1, 0.25, 0.5):
            milestones[key][f'combined_90_certification_automation_{target}'] = milestone(a, 'combined', lambda x, t=target: x['certification_frequency'] >= 0.9 and (x['evaluation_automation']['median'] or 0) >= t)
        full[key] = runs[key]['7142'][0]
    return {'aggregation': aggregation, 'milestones': milestones, 'full': full}
