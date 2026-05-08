"""All-constraint intersection search.

Given a list of constraints, search for a theory in coefficient space that
satisfies all of them simultaneously. If such a theory exists, return it
plus the constraint margins at that point. If not, return the closest-to-
feasible point and the constraints that violate hardest.

This is the engine's sharpest answer to its own question: "Given everything
encoded, what is the actual UV-completion-allowed point in theory space?"

Method: scipy.optimize.minimize with the worst-case (most-negative) margin
as the maximization target. If the optimizer drives the worst-case margin
to ≥ 0, we have a feasible point. If it stalls at margin < 0, we have a
provable lower bound on incompatibility."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from itb.constraints.base import Constraint
from itb.engine import check
from itb.theory import Theory


@dataclass
class IntersectionResult:
    feasible: bool
    coefficients: dict[str, float]
    worst_case_margin: float
    constraints_violated: list[str]
    constraints_binding: list[str]
    optimizer_status: str


def search_intersection(
    constraints: list[Constraint],
    initial_guess: dict[str, float],
    max_iters: int = 500,
    binding_tolerance: float = 1e-3,
) -> IntersectionResult:
    keys = list(initial_guess.keys())
    x0 = np.array([initial_guess[k] for k in keys], dtype=float)

    def to_theory(x):
        return Theory(coefficients={k: float(v) for k, v in zip(keys, x)})

    def worst_case_margin(x):
        theory = to_theory(x)
        margins = [c.evaluate(theory).margin for c in constraints]
        return min(margins) if margins else 0.0

    # Maximize worst-case margin (= minimize its negation).
    res = minimize(
        lambda x: -worst_case_margin(x),
        x0,
        method="Nelder-Mead",
        options={"maxiter": max_iters, "xatol": 1e-6, "fatol": 1e-8},
    )
    final = to_theory(res.x)
    final_report = check(final, constraints)
    violated = [r.constraint_name for r in final_report.results if not r.satisfied]
    binding = [
        r.constraint_name for r in final_report.results
        if abs(r.margin) < binding_tolerance
    ]
    return IntersectionResult(
        feasible=final_report.feasible,
        coefficients=final.coefficients,
        worst_case_margin=-float(res.fun),
        constraints_violated=violated,
        constraints_binding=binding,
        optimizer_status=res.message,
    )
