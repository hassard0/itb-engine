import pytest

from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.intersection_search import IntersectionResult, search_intersection


def test_finds_feasible_point_when_exists():
    """Three simple positivity constraints; the origin or any first-quadrant
    point with g_6 ≥ g_4^2 is feasible."""
    res = search_intersection(
        constraints=[
            ScalarPositivityG4(),
            ScalarPositivityG6(),
            ScalarConvexityG6vsG4(),
        ],
        initial_guess={"g_4": 0.5, "g_6": 0.5, "g_R2": 0.0},
    )
    assert isinstance(res, IntersectionResult)
    assert res.feasible is True


def test_records_violated_constraints_when_infeasible():
    """Constraint set that's definitionally inconsistent."""
    from itb.constraints.base import (
        Constraint,
        ConstraintClass,
        ConstraintResult,
    )
    from itb.theory import Theory

    class AlwaysAtLeastOne(Constraint):
        name = "always_at_least_one"
        citation = "test"
        constraint_class = ConstraintClass.A_AMPLITUDE

        def evaluate(self, theory: Theory) -> ConstraintResult:
            v = theory.coefficients.get("g_4", 0.0)
            return ConstraintResult(
                constraint_name=self.name, satisfied=v >= 1, margin=v - 1,
                signed_distance_margin=v - 1,
            )

    class AlwaysAtMostNegOne(Constraint):
        name = "always_at_most_neg_one"
        citation = "test"
        constraint_class = ConstraintClass.A_AMPLITUDE

        def evaluate(self, theory: Theory) -> ConstraintResult:
            v = theory.coefficients.get("g_4", 0.0)
            return ConstraintResult(
                constraint_name=self.name, satisfied=v <= -1, margin=-1 - v,
                signed_distance_margin=-1 - v,
            )

    res = search_intersection(
        constraints=[AlwaysAtLeastOne(), AlwaysAtMostNegOne()],
        initial_guess={"g_4": 0.0},
    )
    assert res.feasible is False
    assert len(res.constraints_violated) >= 1


def test_intersection_result_has_coefficients():
    res = search_intersection(
        constraints=[ScalarPositivityG4()],
        initial_guess={"g_4": 0.5},
    )
    assert "g_4" in res.coefficients


def test_origin_is_feasible_for_positivity_only():
    """All-zero is the simplest feasible point for positivity bounds."""
    res = search_intersection(
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
        initial_guess={"g_4": 0.1, "g_6": 0.1},
    )
    assert res.feasible is True
    # Either at origin or any non-negative point
    assert res.coefficients["g_4"] >= -1e-6
    assert res.coefficients["g_6"] >= -1e-6
