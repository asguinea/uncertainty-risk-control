# A small selected-risk walkthrough

From the repository root:

```sh
uv sync --locked
uv run --locked python examples/selected_risk_walkthrough.py
```

This contrived example fixes the threshold order `0.1, 0.2, 0.3` in advance. Scores equal to a threshold are accepted. With alpha and delta both 0.05, the first candidate selects 59 observations with zero mistakes and passes. The second selects 100 with 10 mistakes and fails. The procedure stops, returns threshold 0.1, and never tests threshold 0.3, even though the toy data beyond it contain many zero-error observations.

The script projects just that executed prefix into selected/mistake counts, replays it, and checks that the resulting controller is identical. A second example uses only 58 zero-mistake observations and returns review-all. The boundary of 59 is a numerical fixture for these particular alpha/delta values, not a recommended calibration dataset size. Calibration size and the number selected by a candidate are different quantities.

Expected key output:

```text
Result: CERTIFIED; threshold=0.1; selected=59; mistakes=0
  threshold 0.1: 0/59 mistakes; p=0.048495; PASS
  threshold 0.2: 10/100 mistakes; p=0.988528; FAIL — stop
With 58 selected observations and zero mistakes: REVIEW_ALL.
```

These hand-constructed observations explain control flow; they estimate no real population and establish no benchmark result. The [separate synthetic runner](../docs/reproduction.md) demonstrates independent development and calibration draws from a stated synthetic population. For an application, candidate design must remain independent of calibration, and the [sampling assumptions](../docs/method.md#assumptions-and-interpretation) must be justified outside the API.
