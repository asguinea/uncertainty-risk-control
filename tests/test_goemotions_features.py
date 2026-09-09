#!/usr/bin/env python3
"""Focused deterministic tests for GoEmotions D1S."""

from __future__ import annotations

import unittest

import numpy as np

from uncertainty_risk_control.goemotions.features import feature_names, feature_vector


class FeatureSchemaTests(unittest.TestCase):
    def test_feature_order_and_count_are_frozen(self) -> None:
        names = feature_names()
        self.assertEqual(len(names), 97)
        self.assertEqual(names[:2], ["probability_00", "probability_01"])
        self.assertEqual(names[28:33], ["p_top1", "p_top2", "p_top3", "margin_1_2", "margin_1_3"])
        self.assertEqual(names[-1], "top_label_confidence_interaction_27")

    def test_feature_vector_has_expected_components(self) -> None:
        probabilities = [0.1] * 28
        probabilities[7] = 0.9
        probabilities[2] = 0.7
        probabilities[4] = 0.6
        features = np.asarray(feature_vector(probabilities))
        self.assertEqual(features.shape, (97,))
        self.assertAlmostEqual(features[28], 0.9)
        self.assertAlmostEqual(features[31], 0.2)
        one_hot = features[41:69]
        interaction = features[69:97]
        self.assertEqual(int(one_hot.sum()), 1)
        self.assertEqual(one_hot[7], 1)
        self.assertAlmostEqual(interaction[7], 0.9)

    def test_feature_schema_excludes_forbidden_inputs(self) -> None:
        joined = " ".join(feature_names()).lower()
        for forbidden in ("text", "subreddit", "disagreement", "rater", "author", "thread", "timestamp"):
            self.assertNotIn(forbidden, joined)


if __name__ == "__main__":
    unittest.main()
