"""Engine: evaluate a theory against a set of constraints; return feasibility,
the most-binding constraint when infeasible, and per-constraint results.

A `tolerance` parameter relaxes the strict satisfaction test: a constraint is
treated as satisfied if its margin is >= -tolerance. Default tolerance is a
small positive number to avoid spurious infeasibility from floating-point
noise on boundary points."""

from dataclasses import dataclass

from itb.constraints.base import Constraint, ConstraintResult
from itb.theory import Theory


DEFAULT_TOLERANCE = 1e-9


@dataclass
class EngineReport:
    theory_name: str
    feasible: bool
    results: list[ConstraintResult]
    binding: str | None = None
    binding_class: str | None = None
    tolerance: float = DEFAULT_TOLERANCE


def check(
    theory: Theory,
    constraints: list[Constraint],
    tolerance: float = DEFAULT_TOLERANCE,
) -> EngineReport:
    raw_results = [c.evaluate(theory) for c in constraints]
    results: list[ConstraintResult] = []
    for r in raw_results:
        satisfied = r.margin >= -tolerance
        results.append(
            ConstraintResult(
                constraint_name=r.constraint_name,
                satisfied=satisfied,
                margin=r.margin,
                signed_distance_margin=r.signed_distance_margin,
                details=dict(r.details),
            )
        )
    feasible = all(r.satisfied for r in results)
    binding_name: str | None = None
    binding_cls: str | None = None
    if not feasible:
        violated = [(c, r) for c, r in zip(constraints, results) if not r.satisfied]
        c, r = min(violated, key=lambda cr: cr[1].signed_distance_margin)
        binding_name = r.constraint_name
        binding_cls = c.constraint_class.value
    return EngineReport(
        theory_name=theory.name,
        feasible=feasible,
        results=results,
        binding=binding_name,
        binding_class=binding_cls,
        tolerance=tolerance,
    )
