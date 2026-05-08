from itb.completeness import check_boundedness, BoundednessReport
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)


def _three_constraints():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_returns_boundedness_report():
    report = check_boundedness(
        constraints=_three_constraints(),
        params=["g_4", "g_6"],
        starting_box=2.0,
        max_box=8.0,
        steps_per_axis=11,
    )
    assert isinstance(report, BoundednessReport)


def test_unbounded_for_three_constraints():
    """g_4 >= 0, g_6 >= 0, g_6 >= g_4^2 — region extends to infinity in g_4 and g_6."""
    report = check_boundedness(
        constraints=_three_constraints(),
        params=["g_4", "g_6"],
        starting_box=2.0,
        max_box=8.0,
        steps_per_axis=11,
    )
    assert report.bounded is False
    assert "g_4" in report.unbounded_directions or "g_6" in report.unbounded_directions


def test_bounded_when_upper_bounds_exist():
    """Add a synthetic upper-bound constraint to make the region bounded."""
    from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
    from itb.theory import Theory

    class UpperBound(Constraint):
        name = "upper_bound"
        citation = "synthetic"
        constraint_class = ConstraintClass.A_AMPLITUDE

        def evaluate(self, theory: Theory) -> ConstraintResult:
            g4 = theory.coefficients.get("g_4", 0.0)
            g6 = theory.coefficients.get("g_6", 0.0)
            margin = 1.0 - max(g4, g6)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=margin >= 0,
                margin=margin,
                signed_distance_margin=margin,
            )

    report = check_boundedness(
        constraints=_three_constraints() + [UpperBound()],
        params=["g_4", "g_6"],
        starting_box=2.0,
        max_box=8.0,
        steps_per_axis=11,
    )
    assert report.bounded is True


def test_records_box_size_at_termination():
    report = check_boundedness(
        constraints=_three_constraints(),
        params=["g_4", "g_6"],
        starting_box=2.0,
        max_box=8.0,
        steps_per_axis=7,
    )
    assert report.final_box_size == 8.0
