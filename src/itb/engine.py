"""Engine: evaluate a theory against a set of constraints and produce a
unified report including which constraints are binding when infeasible."""

from dataclasses import dataclass

from itb.constraints.base import Constraint, ConstraintResult
from itb.theory import Theory


@dataclass
class EngineReport:
    theory_name: str
    feasible: bool
    results: list[ConstraintResult]


def check(theory: Theory, constraints: list[Constraint]) -> EngineReport:
    results = [c.evaluate(theory) for c in constraints]
    feasible = all(r.satisfied for r in results)
    return EngineReport(
        theory_name=theory.name,
        feasible=feasible,
        results=results,
    )
