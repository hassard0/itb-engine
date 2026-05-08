"""Theory fingerprint: vectorize each candidate framework by a tuple of
diagnostic numbers (Wilson coefficient values, observable predictions,
fragility, n_binding) and compute pairwise distances.

Frameworks with similar fingerprints are observably similar — predictions
match, robustness matches, etc. Frameworks with different fingerprints
encode genuinely distinct physics, and an experiment that distinguishes their
observables would be the most informative experiment to run."""

from dataclasses import dataclass

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.frameworks.base import Framework
from itb.observables import Observable
from itb.perturbation import smallest_violating_perturbation
from itb.theory import Theory


@dataclass
class Fingerprint:
    framework_name: str
    coefficients: dict[str, float]
    feasible: bool
    fragility_distance: float
    n_binding: int
    observable_values: dict[str, np.ndarray]


def fingerprint_framework(
    framework: Framework,
    constraints: list[Constraint],
    observables: dict[str, Observable] | None = None,
) -> Fingerprint:
    theory = framework.encode()
    report = check(theory, constraints)
    n_binding = sum(1 for r in report.results if abs(r.margin) < 1e-3)
    fragility = smallest_violating_perturbation(theory, constraints).distance
    obs_values: dict[str, np.ndarray] = {}
    if observables is not None:
        for name, obs in observables.items():
            obs_values[name] = obs.predict(theory)
    return Fingerprint(
        framework_name=framework.name,
        coefficients=dict(theory.coefficients),
        feasible=report.feasible,
        fragility_distance=fragility,
        n_binding=n_binding,
        observable_values=obs_values,
    )


def fingerprint_distance(a: Fingerprint, b: Fingerprint) -> float:
    """Euclidean distance combining normalized coefficient and observable diffs."""
    keys = sorted(set(a.coefficients) | set(b.coefficients))
    coeff_diff = np.array([a.coefficients.get(k, 0.0) - b.coefficients.get(k, 0.0) for k in keys])
    parts = [float(np.linalg.norm(coeff_diff))]
    common_obs = set(a.observable_values) & set(b.observable_values)
    for name in sorted(common_obs):
        diff = a.observable_values[name] - b.observable_values[name]
        parts.append(float(np.linalg.norm(diff)))
    return float(np.linalg.norm(parts))


def fingerprint_matrix(
    fingerprints: list[Fingerprint],
) -> np.ndarray:
    n = len(fingerprints)
    m = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            m[i, j] = fingerprint_distance(fingerprints[i], fingerprints[j])
    return m
