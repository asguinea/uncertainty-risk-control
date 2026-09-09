#!/usr/bin/env python3
"""Deterministic unit tests preserved from the original selected-risk method."""

from __future__ import annotations

import unittest

from uncertainty_risk_control.selected_risk import (
    build_threshold_family,
    calibrate_fixed_sequence,
    certifies,
    exact_binomial_lower_tail_scipy,
    minimum_selected_for_harmful,
    order_thresholds_from_development,
)

from uncertainty_risk_control._reference.selected_risk_v1 import exact_binomial_lower_tail_recurrence


class ExactBinomialTests(unittest.TestCase):
    def test_named_sample_geometry(self) -> None:
        self.assertFalse(certifies(0, 58))
        self.assertTrue(certifies(0, 59))
        self.assertEqual(
            {harmful: minimum_selected_for_harmful(harmful) for harmful in range(6)},
            {0: 59, 1: 93, 2: 124, 3: 153, 4: 181, 5: 208},
        )

    def test_zero_selection_never_certifies(self) -> None:
        self.assertFalse(certifies(0, 0))
        self.assertEqual(exact_binomial_lower_tail_scipy(0, 0), 1.0)

    def test_independent_oracles_agree(self) -> None:
        for selected in (1, 10, 58, 59, 4774):
            for harmful in range(min(5, selected) + 1):
                self.assertAlmostEqual(
                    exact_binomial_lower_tail_scipy(harmful, selected),
                    exact_binomial_lower_tail_recurrence(harmful, selected),
                    delta=1e-12,
                )


class FixedSequenceTests(unittest.TestCase):
    def test_stops_at_first_non_rejection(self) -> None:
        sequence = [{"threshold": 0.1}, {"threshold": 0.2}, {"threshold": 0.3}]
        scores = [0.05] * 59 + [0.15] + [0.25] * 60
        outcomes = [0] * 59 + [1] + [0] * 60
        result = calibrate_fixed_sequence(sequence, scores, outcomes)
        self.assertEqual(result.state, "CERTIFIED")
        self.assertEqual(result.stopped_at_index, 1)
        self.assertEqual(len(result.certified_thresholds), 1)
        self.assertEqual(result.threshold, 0.1)

    def test_development_family_and_order_are_deterministic(self) -> None:
        scores = [index / 100 for index in range(1, 101)]
        outcomes = [0] * 70 + [1] * 30
        family = build_threshold_family(scores)
        first = order_thresholds_from_development(family, scores, outcomes)
        second = order_thresholds_from_development(family, scores, outcomes)
        self.assertEqual(first, second)
        self.assertTrue(all(row["development_selected"] > 0 for row in first))


if __name__ == "__main__":
    unittest.main()
