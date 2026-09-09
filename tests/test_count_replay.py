import unittest
from unittest.mock import patch

import numpy as np

from uncertainty_risk_control import count_replay
from uncertainty_risk_control.selected_risk import calibrate_fixed_sequence


class CountReplayTests(unittest.TestCase):
    def test_replay_matches_row_engine_for_all_budgets_and_nonmonotone_orders(self):
        rng = np.random.default_rng(8935)
        for alpha in (0.05, 0.1, 0.15, 0.2):
            for risk in (0.0, 0.03, 0.12, 0.3):
                sequence = [{"threshold": x} for x in (0.2, 0.5, 0.3, 0.8, 1.0)]
                scores, outcomes = rng.uniform(size=900), rng.binomial(1, risk, size=900)
                expected = calibrate_fixed_sequence(sequence, scores, outcomes, alpha)
                tested = expected.stopped_at_index + 1 if expected.stopped_at_index is not None else len(sequence)
                counts = count_replay.project_counts(sequence, scores, outcomes, tested_count=tested)
                actual = count_replay.replay_count_prefix(sequence, counts, n=900, alpha=alpha)
                with self.subTest(alpha=alpha, risk=risk):
                    self.assertEqual(actual["controller"], expected)
                    self.assertEqual(len(actual["tests"]), tested)

    def test_missing_first_failure_and_extra_tail_are_rejected(self):
        sequence = [{"threshold": x} for x in (0.1, 0.2, 0.3)]
        scores, outcomes = [0.1] * 59 + [0.2] * 41, [0] * 59 + [1] * 41
        valid = count_replay.project_counts(sequence, scores, outcomes, tested_count=2)
        self.assertFalse(count_replay.replay_count_prefix(sequence, valid, n=100)["tests"][-1]["passes"])
        for invalid in (valid[:1], count_replay.project_counts(sequence, scores, outcomes, tested_count=3)):
            with self.assertRaises(ValueError):
                count_replay.replay_count_prefix(sequence, invalid, n=100)

    def test_only_supplied_historical_tests_are_evaluated(self):
        sequence = [{"threshold": x} for x in (0.1, 0.2, 0.3)]
        counts = count_replay.project_counts(sequence, [0.1] * 58, [0] * 58, tested_count=1)
        with patch.object(count_replay, "exact_binomial_lower_tail_scipy", wraps=count_replay.exact_binomial_lower_tail_scipy) as calls:
            result = count_replay.replay_count_prefix(sequence, counts, n=58)
            self.assertEqual(calls.call_count, 1)
        self.assertEqual(result["controller"].state, "REVIEW_ALL")

    def test_inclusive_ties_and_zero_selection(self):
        sequence = [{"threshold": x} for x in (0.1, 0.3, 0.2)]
        counts = count_replay.project_counts(sequence, [0.1] * 59, [0] * 59, tested_count=3)
        result = count_replay.replay_count_prefix(sequence, counts, n=59)
        self.assertEqual(result["controller"].threshold, 0.3)
        counts = count_replay.project_counts(sequence, [], [], tested_count=1)
        result = count_replay.replay_count_prefix(sequence, counts, n=0)
        self.assertIsNone(result["controller"].cp_upper)
        self.assertEqual(result["tests"][0]["p_value"], 1.0)

    def test_misalignment_invalid_counts_and_impossible_nested_counts(self):
        sequence = [{"threshold": 0.1}, {"threshold": 0.2}]
        valid = count_replay.project_counts(sequence, [0.1] * 100, [0] * 100, tested_count=2)
        for change in ({"index": 2}, {"threshold": 0.11}, {"selected": 101}, {"harmful": -1}, {"extra": "unrequested"}):
            broken = [{**valid[0], **change}, valid[1]]
            with self.subTest(change=change), self.assertRaises((ValueError, TypeError)):
                count_replay.replay_count_prefix(sequence, broken, n=100)
        impossible = [valid[0], {**valid[1], "selected": 99}]
        with self.assertRaisesRegex(ValueError, "nested"):
            count_replay.replay_count_prefix(sequence, impossible, n=100)


if __name__ == "__main__":
    unittest.main()
