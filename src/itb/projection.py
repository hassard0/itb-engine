"""Per-framework feasibility projection.

Given a framework's predicted Wilson coefficients (which may or may not
satisfy the full constraint set) and a constraint set, find the
*nearest* feasible point in coefficient space. The shift from the
framework's encoded values to this nearest feasible point tells us:

  (a) how much the framework's toy values need to move to be consistent,
  (b) which coefficients shift most (the 'most-broken' coefficients),
  (c) which constraints were binding at the nearest feasible point.

Method: scipy.optimize.minimize over the L2 distance from the
framework's encoded values, subject to all constraints satisfied (margin
>= 0). If no feasible point exists in the search range, returns the
closest-to-feasible point and identifies the violating constraints.

This is a *Bayesian-style projection*: framework values as prior,
constraints as hard likelihood, projection result as posterior peak."""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from itb.constraints.base import Constraint
from itb.engine import check
from itb.frameworks.base import Framework
from itb.theory import Theory


@dataclass
class FrameworkProjection:
    framework_name: str
    original_coefficients: dict[str, float]
    projected_coefficients: dict[str, float]
    shift_distance: float           # L2 distance moved
    coefficient_shifts: dict[str, float]
    feasible: bool
    binding_constraints: list[str]


def project_framework_to_feasible(
    framework: Framework,
    constraints: list[Constraint],
    max_iters: int = 500,
    binding_tolerance: float = 1e-3,
) -> FrameworkProjection:
    original = framework.encode().coefficients
    keys = sorted(original.keys())
    x0 = np.array([original[k] for k in keys], dtype=float)

    def to_theory(x):
        return Theory(coefficients={k: float(v) for k, v in zip(keys, x)})

    def distance_from_original(x):
        return float(np.sum((x - x0) ** 2))

    def make_constraint_fn(idx):
        def fn(x):
            return constraints[idx].evaluate(to_theory(x)).margin
        return fn

    scipy_constraints = [
        {"type": "ineq", "fun": make_constraint_fn(i)}
        for i in range(len(constraints))
    ]
    res = minimize(
        distance_from_original,
        x0,
        constraints=scipy_constraints,
        method="SLSQP",
        options={"maxiter": max_iters, "ftol": 1e-9},
    )
    final = to_theory(res.x)
    final_report = check(final, constraints)
    binding = [
        r.constraint_name
        for r in final_report.results
        if abs(r.margin) < binding_tolerance
    ]
    shifts = {k: float(v - original[k]) for k, v in final.coefficients.items()}
    return FrameworkProjection(
        framework_name=framework.name,
        original_coefficients=dict(original),
        projected_coefficients=dict(final.coefficients),
        shift_distance=float(np.sqrt(distance_from_original(res.x))),
        coefficient_shifts=shifts,
        feasible=final_report.feasible,
        binding_constraints=binding,
    )


def render_projection_report(projections: list[FrameworkProjection]) -> str:
    lines: list[str] = []
    lines.append("# Per-framework feasibility projection")
    lines.append("")
    lines.append("For each framework, the L2-nearest feasible point in 7D Wilson-")
    lines.append("coefficient space and the per-coefficient shift from the framework's")
    lines.append("encoded toy values. Larger shifts = more 'off' from the engine-")
    lines.append("allowed region.")
    lines.append("")
    lines.append("| framework | feasible | shift distance | binding count |")
    lines.append("|---|---|---|---|")
    for p in projections:
        lines.append(
            f"| {p.framework_name} | {p.feasible} | "
            f"{p.shift_distance:.4f} | {len(p.binding_constraints)} |"
        )
    lines.append("")
    lines.append("## Per-framework coefficient shifts")
    lines.append("")
    for p in projections:
        lines.append(f"### {p.framework_name}")
        lines.append("")
        lines.append("| coef | original | projected | shift |")
        lines.append("|---|---|---|---|")
        for k in sorted(p.original_coefficients.keys()):
            orig = p.original_coefficients[k]
            proj = p.projected_coefficients.get(k, 0.0)
            shift = p.coefficient_shifts.get(k, 0.0)
            lines.append(f"| {k} | {orig:.4f} | {proj:.4f} | {shift:+.4f} |")
        lines.append("")
        if p.binding_constraints:
            lines.append(f"**Binding at projection:** {', '.join(p.binding_constraints[:5])}")
        lines.append("")
    return "\n".join(lines)
