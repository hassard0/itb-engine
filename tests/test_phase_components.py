import numpy as np

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.phase_components import phase_components, PhaseDecomposition


def _three_constraints():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_returns_decomposition():
    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    dec = phase_components(sweep)
    assert isinstance(dec, PhaseDecomposition)


def test_one_phase_for_connected_first_quadrant():
    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=21,
        constraints=_three_constraints(),
    )
    dec = phase_components(sweep)
    # The convexity wedge in the first quadrant is one connected component
    assert dec.n_components == 1
    assert dec.component_sizes[0] > 0


def test_zero_phases_when_all_excluded():
    """A constraint set that excludes everything yields zero components."""
    from itb.constraints.base import (
        Constraint,
        ConstraintClass,
        ConstraintResult,
    )
    from itb.theory import Theory

    class AlwaysFail(Constraint):
        name = "always_fail"
        citation = "test"
        constraint_class = ConstraintClass.A_AMPLITUDE

        def evaluate(self, theory: Theory) -> ConstraintResult:
            return ConstraintResult(
                constraint_name=self.name, satisfied=False, margin=-1.0,
                signed_distance_margin=-1.0,
            )

    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[AlwaysFail()],
    )
    dec = phase_components(sweep)
    assert dec.n_components == 0


def test_two_phases_when_disconnected():
    """Construct a constraint that produces two disjoint allowed islands."""
    from itb.constraints.base import (
        Constraint,
        ConstraintClass,
        ConstraintResult,
    )
    from itb.theory import Theory

    class TwoIslands(Constraint):
        """Allow only two disconnected boxes: g_4 in [-0.8, -0.4] OR [0.4, 0.8],
        with any g_6 in [-0.4, 0.4]."""
        name = "two_islands"
        citation = "test"
        constraint_class = ConstraintClass.A_AMPLITUDE

        def evaluate(self, theory: Theory) -> ConstraintResult:
            g4 = theory.coefficients.get("g_4", 0.0)
            g6 = theory.coefficients.get("g_6", 0.0)
            in_box_a = -0.8 <= g4 <= -0.4 and -0.4 <= g6 <= 0.4
            in_box_b = 0.4 <= g4 <= 0.8 and -0.4 <= g6 <= 0.4
            ok = in_box_a or in_box_b
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=ok,
                margin=1.0 if ok else -1.0,
                signed_distance_margin=1.0 if ok else -1.0,
            )

    sweep = sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=21,
        constraints=[TwoIslands()],
    )
    dec = phase_components(sweep)
    assert dec.n_components == 2
