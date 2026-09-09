"""Behavioral checks for the extracted interface and its scientific boundaries."""

import copy
import math
import unittest
from decimal import Decimal, localcontext
from unittest.mock import patch

import numpy as np

from uncertainty_risk_control import selected_risk as method
from uncertainty_risk_control import synthetic
from uncertainty_risk_control._reference import selected_risk_v1 as reference
from uncertainty_risk_control.provenance import reference_integrity


def decimal_binomial_cdf(harmful, selected, alpha):
    """Direct high-precision PMF sum, independent of SciPy and the recurrence."""
    with localcontext() as context:
        context.prec = 70
        probability = Decimal.from_float(alpha)
        return float(sum(Decimal(math.comb(selected, k)) * probability**k * (1 - probability)**(selected - k) for k in range(harmful + 1)))


class NumericalTests(unittest.TestCase):
    def test_core_source_integrity(self):
        self.assertEqual(reference_integrity()["status"], "PASS")

    def test_four_budgets_against_decimal_oracle(self):
        for alpha in (0.05, 0.10, 0.15, 0.20):
            for selected in (0, 1, 10, 59, 208, 500):
                for harmful in sorted({0, min(1, selected), min(5, selected), int(selected * alpha), selected}):
                    with self.subTest(alpha=alpha, selected=selected, harmful=harmful):
                        self.assertAlmostEqual(method.exact_binomial_lower_tail_scipy(harmful, selected, alpha), decimal_binomial_cdf(harmful, selected, alpha), delta=1e-12)

    def test_upper_bound_endpoints_and_known_zero_error_formula(self):
        self.assertIsNone(method.clopper_pearson_upper(0, 0))
        self.assertEqual(method.clopper_pearson_upper(5, 5), 1.0)
        self.assertAlmostEqual(method.clopper_pearson_upper(0, 59), 1 - 0.05**(1 / 59), delta=1e-12)

    def test_rejection_equality_is_inclusive(self):
        delta = method.exact_binomial_lower_tail_scipy(0, 59)
        self.assertTrue(method.certifies(0, 59, delta=delta))
        self.assertFalse(method.certifies(0, 59, delta=math.nextafter(delta, 0)))

    def test_invalid_counts_and_probabilities_fail_even_with_zero_selection(self):
        for harmful, selected in ((True, 59), (0.0, 59), (-1, 0), (1, 0), (0, -1)):
            with self.subTest(counts=(harmful, selected)), self.assertRaises((ValueError, TypeError)):
                method.certifies(harmful, selected)
        for invalid in (0, 1, -0.1, float("nan"), float("inf"), True, "0.05"):
            with self.subTest(value=invalid):
                with self.assertRaises((ValueError, TypeError)):
                    method.certifies(0, 0, alpha=invalid)
                with self.assertRaises((ValueError, TypeError)):
                    method.clopper_pearson_upper(0, 0, delta=invalid)

    def test_numpy_integer_counts_supported(self):
        self.assertTrue(method.certifies(np.int64(0), np.int64(59)))


class SequenceTests(unittest.TestCase):
    def test_valid_inputs_exactly_match_frozen_core_for_each_budget(self):
        rng = np.random.default_rng(9102)
        for alpha in (0.05, 0.10, 0.15, 0.20):
            for risk in (0.0, 0.03, 0.12, 0.30):
                scores = rng.uniform(size=800)
                outcomes = rng.binomial(1, risk, size=800)
                sequence = [{"threshold": threshold} for threshold in (0.3, 0.6, 0.5, 1.0)]
                with self.subTest(alpha=alpha, risk=risk):
                    self.assertEqual(method.calibrate_fixed_sequence(sequence, scores, outcomes, alpha), reference.calibrate_fixed_sequence(sequence, scores, outcomes, alpha))

    def test_threshold_ties_included_and_selected_count_ties_use_higher_threshold(self):
        result = method.calibrate_fixed_sequence([{"threshold": 0.1}, {"threshold": 0.3}, {"threshold": 0.2}], [0.1] * 59, [0] * 59)
        self.assertEqual(result.selected, 59)
        self.assertEqual(result.threshold, 0.3)
        self.assertEqual(len(result.certified_thresholds), 3)
        self.assertIsNone(result.stopped_at_index)

    def test_nonmonotone_sequence_preserved_and_tail_not_tested(self):
        sequence = [{"threshold": x} for x in (0.1, 0.3, 0.2)]
        scores, outcomes = [0.1] * 59 + [0.3] * 41, [0] * 59 + [1] * 41
        # The third candidate would pass, but the second must stop the procedure.
        with patch.object(reference, "exact_binomial_lower_tail_scipy", wraps=reference.exact_binomial_lower_tail_scipy) as calls:
            result = method.calibrate_fixed_sequence(sequence, scores, outcomes)
            self.assertEqual(calls.call_count, 2)
        self.assertEqual(result.stopped_at_index, 1)
        self.assertEqual(result.threshold, 0.1)

    def test_empty_calibration_and_empty_sequence_review_all(self):
        for sequence, scores, outcomes in (([{"threshold": 0.5}], [], []), ([], [0.1] * 59, [0] * 59), ([{"threshold": 0.0}], [0.1] * 59, [0] * 59)):
            result = method.calibrate_fixed_sequence(sequence, scores, outcomes)
            self.assertEqual(result.state, "REVIEW_ALL")
            self.assertIsNone(result.threshold)
            self.assertIsNone(result.cp_upper)
            self.assertEqual(result.certified_thresholds, ())

    def test_development_design_is_unchanged_by_calibration(self):
        scores = [i / 100 for i in range(1, 101)]
        family = method.build_threshold_family(scores)
        sequence = method.order_thresholds_from_development(family, scores, [0] * 70 + [1] * 30)
        self.assertEqual(sequence, reference.order_thresholds_from_development(family, scores, [0] * 70 + [1] * 30))
        saved = copy.deepcopy(sequence)
        with patch.object(reference, "order_thresholds_from_development", side_effect=AssertionError("calibration tried to redesign the sequence")):
            method.calibrate_fixed_sequence(sequence, [0.1] * 100, [0] * 100)
            method.calibrate_fixed_sequence(sequence, [0.1] * 100, [1] * 100)
        self.assertEqual(sequence, saved)

    def test_invalid_vectors_and_thresholds_are_rejected_before_casting(self):
        for scores, outcomes in (([0.1], [256]), ([0.1], [0.5]), ([0.1], [-1]), ([0.1], [float("nan")]), ([float("inf")], [0]), ([-0.1], [0]), ([1.1], [0]), ([[0.1]], [[0]]), ([0.1, 0.2], [0]), (["0.1"], [0])):
            with self.subTest(scores=scores, outcomes=outcomes), self.assertRaises(ValueError):
                method.calibrate_fixed_sequence([{"threshold": 0.5}], scores, outcomes)
        for threshold in (float("nan"), float("inf"), -1, 2, True, "0.1"):
            with self.subTest(threshold=threshold), self.assertRaises((TypeError, ValueError)):
                method.calibrate_fixed_sequence([{"threshold": threshold}], [0.1], [0])


class SyntheticTests(unittest.TestCase):
    config = dict(schema_version=1, seed=1729, development_n=300, calibration_n=500, alpha=0.05, delta=0.05)

    def test_repeatable_and_calibration_size_does_not_change_design(self):
        first = synthetic.run(self.config)
        self.assertEqual(first, synthetic.run(self.config))
        self.assertEqual(first["frozen_sequence"], synthetic.run({**self.config, "calibration_n": 1000})["frozen_sequence"])

    def test_config_rejects_unknown_fields_and_invalid_sizes(self):
        for change in ({"calbration_n": 100}, {"seed": -1}, {"development_n": 0}, {"calibration_n": True}, {"alpha": 0}):
            with self.subTest(change=change), self.assertRaises((TypeError, ValueError)):
                synthetic.run({**self.config, **change})


if __name__ == "__main__":
    unittest.main()
