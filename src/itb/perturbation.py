"""Negative-result mode: given a feasible theory, find the smallest
perturbation in coefficient space that violates feasibility.

Output: the most-fragile constraint (the one closest to violation) and the
Euclidean distance to it. For a feasible theory, this answers "how far is
this theory from being ruled out, and which physical principle would rule
it out first?" — the most useful diagnostic short of an experiment.

For a constraint with constant unit gradient, the distance to its boundary
is exactly its signed-distance margin. We exploit this: the smallest
violating perturbation is the constraint with the smallest positive
signed_distance_margin, and the perturbed point is obtained by Newton-stepping
to that constraint's boundary."""

from dataclasses import dataclass

from itb.constraints.base import Constraint
from itb.engine import check
from itb.mapper import trace_boundary_along_axis
from itb.theory import Theory


@dataclass
class PerturbationResult:
    distance: float
    binding_constraint: str
    perturbed_theory: Theory


def smallest_violating_perturbation(
    theory: Theory,
    constraints: list[Constraint],
) -> PerturbationResult:
    report = check(theory, constraints)
    if not report.feasible:
        return PerturbationResult(
            distance=0.0,
            binding_constraint=report.binding or "",
            perturbed_theory=theory,
        )
    best: tuple[float, Constraint] | None = None
    for c, r in zip(constraints, report.results):
        if best is None or r.signed_distance_margin < best[0]:
            best = (r.signed_distance_margin, c)
    assert best is not None
    distance, binding_c = best
    perturbed_coeffs = trace_boundary_along_axis(
        constraint=binding_c,
        start=dict(theory.coefficients),
    )
    perturbed_theory = Theory(
        coefficients=perturbed_coeffs,
        name=f"{theory.name}+perturbed",
        source=f"smallest violating perturbation of {theory.name}",
    )
    return PerturbationResult(
        distance=distance,
        binding_constraint=binding_c.name,
        perturbed_theory=perturbed_theory,
    )
