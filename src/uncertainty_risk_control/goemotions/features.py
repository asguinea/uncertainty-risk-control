"""Original 97 probability-derived meta-risk features; no fitted model weights."""

from __future__ import annotations

import numpy as np


def sigmoid(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    positive = values >= 0
    result = np.empty_like(values)
    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exponential = np.exp(values[~positive])
    result[~positive] = exponential / (1.0 + exponential)
    return result


def feature_names() -> list[str]:
    return (
        [f"probability_{index:02d}" for index in range(28)]
        + ["p_top1", "p_top2", "p_top3", "margin_1_2", "margin_1_3"]
        + [
            "probability_sum",
            "probability_mean",
            "probability_max",
            "count_ge_0_5",
            "count_ge_0_25",
            "count_ge_0_10",
        ]
        + ["binary_entropy_mean", "binary_entropy_max"]
        + [f"top_label_one_hot_{index:02d}" for index in range(28)]
        + [f"top_label_confidence_interaction_{index:02d}" for index in range(28)]
    )


def feature_vector(probabilities: list[float]) -> list[float]:
    values = np.asarray(probabilities, dtype=np.float64)
    if values.shape != (28,) or not np.all(np.isfinite(values)) or np.any((values < 0) | (values > 1)):
        raise ValueError("invalid frozen probability vector")
    ranked = np.sort(values)[::-1]
    top = int(np.argmax(values))
    epsilon = 1e-12
    clipped = np.clip(values, epsilon, 1.0 - epsilon)
    entropy = -(clipped * np.log(clipped) + (1.0 - clipped) * np.log(1.0 - clipped))
    one_hot = np.zeros(28, dtype=np.float64)
    one_hot[top] = 1.0
    interaction = one_hot * ranked[0]
    features = np.concatenate(
        [
            values,
            np.asarray([ranked[0], ranked[1], ranked[2], ranked[0] - ranked[1], ranked[0] - ranked[2]]),
            np.asarray(
                [
                    values.sum(),
                    values.mean(),
                    values.max(),
                    np.sum(values >= 0.5),
                    np.sum(values >= 0.25),
                    np.sum(values >= 0.10),
                ]
            ),
            np.asarray([entropy.mean(), entropy.max()]),
            one_hot,
            interaction,
        ]
    )
    if len(features) != len(feature_names()) or len(features) != 97:
        raise AssertionError("meta-risk feature schema changed")
    return [float(value) for value in features]
