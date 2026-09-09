"""A reproducible illustration with separate development and calibration draws."""

from dataclasses import asdict

import numpy as np

from .selected_risk import (
    _integer,
    _probability,
    build_threshold_family,
    calibrate_fixed_sequence,
    order_thresholds_from_development,
)


def run(config: dict[str, object]) -> dict[str, object]:
    expected = {"schema_version", "seed", "development_n", "calibration_n", "alpha", "delta"}
    if set(config) != expected or _integer(config["schema_version"], "schema_version") != 1:
        raise ValueError("require exactly the documented synthetic schema version 1 fields")
    seed = _integer(config["seed"], "seed")
    sizes = [_integer(config[name], name) for name in ("development_n", "calibration_n")]
    if seed < 0 or any(n <= 0 for n in sizes):
        raise ValueError("seed must be nonnegative and sample sizes positive")
    alpha = _probability(config["alpha"], "alpha")
    delta = _probability(config["delta"], "delta")
    development_rng, calibration_rng = [np.random.default_rng(child) for child in np.random.SeedSequence(seed).spawn(2)]

    def draw(rng, count):
        scores = rng.uniform(size=count)
        outcomes = rng.binomial(1, 0.005 + 0.12 * scores**2)
        return scores, outcomes

    development_scores, development_outcomes = draw(development_rng, sizes[0])
    family = build_threshold_family(development_scores)
    frozen_sequence = order_thresholds_from_development(family, development_scores, development_outcomes)
    calibration_scores, calibration_outcomes = draw(calibration_rng, sizes[1])
    result = calibrate_fixed_sequence(frozen_sequence, calibration_scores, calibration_outcomes, alpha, delta)
    return {
        "kind": "synthetic_illustration",
        "config": config,
        "population": "score ~ Uniform(0,1); mistake | score ~ Bernoulli(0.005 + 0.12 * score**2)",
        "role_generation": "separate SeedSequence child streams for development and calibration",
        "frozen_sequence": frozen_sequence,
        "calibration": asdict(result),
        "selected_fraction": result.selected / sizes[1],
        "empirical_selected_error": result.harmful / result.selected if result.selected else None,
    }
