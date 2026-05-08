import pytest

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.importance import constraint_importance, ImportanceReport


def _three_constraints():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_returns_one_score_per_constraint():
    report = constraint_importance(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    assert isinstance(report, ImportanceReport)
    assert len(report.scores) == 3
    names = [s.constraint_name for s in report.scores]
    assert "scalar_positivity_g4" in names
    assert "scalar_positivity_g6" in names
    assert "scalar_convexity_g6_vs_g4" in names


def test_score_is_nonnegative():
    report = constraint_importance(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=7,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=7,
        constraints=_three_constraints(),
    )
    for s in report.scores:
        assert s.allowed_region_growth >= 0


def test_removing_a_constraint_grows_the_region():
    report = constraint_importance(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    # At least one constraint must be doing work — otherwise the constraint
    # set is trivially redundant on this domain
    assert any(s.allowed_region_growth > 0 for s in report.scores)


def test_baseline_allowed_count_recorded():
    report = constraint_importance(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=7,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=7,
        constraints=_three_constraints(),
    )
    # The baseline (all constraints in) allowed count should be a non-negative
    # integer no larger than the total grid size.
    assert 0 <= report.baseline_allowed_count <= 7 * 7


def test_convexity_constraint_does_real_work():
    """In our toy with all three constraints, removing the convexity
    constraint should grow the allowed region (the parabolic boundary
    disappears, leaving only the first-quadrant condition)."""
    report = constraint_importance(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=21,
        constraints=_three_constraints(),
    )
    convex_score = next(s for s in report.scores
                        if s.constraint_name == "scalar_convexity_g6_vs_g4")
    assert convex_score.allowed_region_growth > 0
