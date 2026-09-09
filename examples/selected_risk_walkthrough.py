"""Contrived numerical illustration, not a benchmark or an estimated population."""

from uncertainty_risk_control import calibrate_fixed_sequence, minimum_selected_for_harmful
from uncertainty_risk_control.count_replay import project_counts, replay_count_prefix


def main():
    # Fixed in advance for this illustration; never learn an order from calibration.
    sequence = [{"threshold": 0.1}, {"threshold": 0.2}, {"threshold": 0.3}]
    scores = [0.1] * 59 + [0.2] * 41 + [0.3] * 900
    mistakes = [0] * 59 + [1] * 10 + [0] * 31 + [0] * 900
    result = calibrate_fixed_sequence(sequence, scores, mistakes, alpha=0.05, delta=0.05)
    print("Synthetic illustration: fixed order 0.1, 0.2, 0.3; alpha = delta = 0.05")
    print(f"Result: {result.state}; threshold={result.threshold}; selected={result.selected}; mistakes={result.harmful}")

    # Export only the prefix that the row-based procedure actually executed.
    tested = len(sequence) if result.stopped_at_index is None else result.stopped_at_index + 1
    counts = project_counts(sequence, scores, mistakes, tested_count=tested)
    repeated = replay_count_prefix(sequence, counts, n=len(scores), alpha=0.05, delta=0.05)
    assert repeated["controller"] == result
    for step in repeated["tests"]:
        state = "PASS" if step["passes"] else "FAIL — stop"
        print(f"  threshold {step['threshold']:.1f}: {step['harmful']}/{step['selected']} mistakes; p={step['p_value']:.6f}; {state}")
    print("Threshold 0.3 is never tested, even though it includes many additional zero-error observations.")
    print("This is why candidate order must be fixed before calibration.")

    sparse = calibrate_fixed_sequence(sequence, [0.1] * 58, [0] * 58, alpha=0.05, delta=0.05)
    assert sparse.state == "REVIEW_ALL"
    boundary = minimum_selected_for_harmful(0, alpha=0.05, delta=0.05)
    print(f"With 58 selected observations and zero mistakes: {sparse.state}.")
    print(f"The first passing zero-mistake count here is {boundary}; this is a numerical boundary, not a dataset sample-size recommendation.")
    print("Review-all has undefined conditional error; it is not perfect accuracy.")


if __name__ == "__main__":
    main()
