"""Sensitivity propagation: turn binary feasibility into a probability by
sampling Wilson coefficients from a Gaussian-power-counting prior and
counting fraction of samples that satisfy all constraints.

In an EFT, dimensionless Wilson coefficients are O(1) up to power-counting
uncertainty. Treating them as Gaussian-distributed around their nominal value
with a power-counting std σ gives a probability distribution on feasibility:

    P_feasible(theta) = (1/N) * sum_i [check(theta + σ * eps_i, constraints).feasible]

This connects the engine to Bayesian model evidence: P_feasible is proportional
to the marginal likelihood of the theory under a power-counting prior and a
hard-constraint likelihood. A theory near a constraint boundary gets
fractional P_feasible, which is the right Bayesian thing to compute."""

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class SensitivityResult:
    nominal_feasible: bool
    p_feasible: float
    n_samples: int
    margin_mean: float
    margin_std: float


def feasibility_probability(
    nominal: dict[str, float],
    constraints: list[Constraint],
    sigma: float = 0.1,
    n_samples: int = 200,
    rng_seed: int | None = 0,
    perturbed_keys: Iterable[str] | None = None,
) -> SensitivityResult:
    rng = np.random.default_rng(rng_seed)
    keys = list(perturbed_keys) if perturbed_keys is not None else list(nominal.keys())
    nominal_theory = Theory(coefficients=dict(nominal))
    nominal_report = check(nominal_theory, constraints)
    n_feasible = 0
    margins: list[float] = []
    for _ in range(n_samples):
        coeffs = dict(nominal)
        for k in keys:
            coeffs[k] = float(coeffs.get(k, 0.0) + rng.normal(0.0, sigma))
        report = check(Theory(coefficients=coeffs), constraints)
        if report.feasible:
            n_feasible += 1
        # use the most-binding margin as a scalar summary
        worst = min(r.margin for r in report.results) if report.results else 0.0
        margins.append(worst)
    return SensitivityResult(
        nominal_feasible=nominal_report.feasible,
        p_feasible=n_feasible / n_samples,
        n_samples=n_samples,
        margin_mean=float(np.mean(margins)),
        margin_std=float(np.std(margins)),
    )


def sensitivity_grid_2d(
    x_param: str,
    x_range: tuple[float, float],
    x_steps: int,
    y_param: str,
    y_range: tuple[float, float],
    y_steps: int,
    constraints: list[Constraint],
    sigma: float = 0.1,
    n_samples: int = 80,
    rng_seed: int | None = 0,
    fixed_coefficients: dict[str, float] | None = None,
) -> dict:
    fixed = dict(fixed_coefficients or {})
    x_values = np.linspace(x_range[0], x_range[1], x_steps)
    y_values = np.linspace(y_range[0], y_range[1], y_steps)
    p_grid = np.zeros((x_steps, y_steps), dtype=float)
    for i, x in enumerate(x_values):
        for j, y in enumerate(y_values):
            coefficients = dict(fixed)
            coefficients[x_param] = float(x)
            coefficients[y_param] = float(y)
            res = feasibility_probability(
                nominal=coefficients,
                constraints=constraints,
                sigma=sigma,
                n_samples=n_samples,
                rng_seed=rng_seed,
                perturbed_keys=(x_param, y_param),
            )
            p_grid[i, j] = res.p_feasible
    return {
        "x_param": x_param,
        "x_values": x_values,
        "y_param": y_param,
        "y_values": y_values,
        "p_grid": p_grid,
    }
