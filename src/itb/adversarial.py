"""Adversarial bootstrap: find the feasible theory where the most constraints
simultaneously bind. This is the analytic-center / vertex of the allowed region —
the point at which the constraint set is *most informative*, in the sense that
small perturbations from there activate the most constraints.

For a polyhedral allowed region this is a vertex; for a smooth region it is the
analytic center. We compute it by minimizing sum-of-squared margins subject to
feasibility (all margins >= -epsilon).
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from itb.constraints.base import Constraint
from itb.theory import Theory


@dataclass
class AdversarialPoint:
    theory: Theory
    n_binding: int
    binding_names: list[str]
    objective_value: float


def adversarial_bootstrap(
    constraints: list[Constraint],
    initial_guess: dict[str, float],
    binding_tolerance: float = 1e-3,
) -> AdversarialPoint:
    keys = list(initial_guess.keys())
    x0 = np.array([initial_guess[k] for k in keys], dtype=float)

    def to_theory(x):
        return Theory(coefficients={k: float(v) for k, v in zip(keys, x)})

    def objective(x):
        theory = to_theory(x)
        return sum(c.evaluate(theory).margin ** 2 for c in constraints)

    def make_constraint(idx):
        def fn(x):
            theory = to_theory(x)
            return constraints[idx].evaluate(theory).margin
        return fn

    scipy_constraints = [
        {"type": "ineq", "fun": make_constraint(i)}
        for i in range(len(constraints))
    ]
    res = minimize(
        objective, x0,
        constraints=scipy_constraints,
        method="SLSQP",
        options={"ftol": 1e-10, "maxiter": 200},
    )
    final = to_theory(res.x)
    binding_names: list[str] = []
    for c in constraints:
        r = c.evaluate(final)
        if abs(r.margin) < binding_tolerance:
            binding_names.append(c.name)
    return AdversarialPoint(
        theory=final,
        n_binding=len(binding_names),
        binding_names=binding_names,
        objective_value=float(res.fun),
    )
