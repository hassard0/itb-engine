import pytest

from itb.adversarial import adversarial_bootstrap, AdversarialPoint
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)


def _three_constraints():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_returns_adversarial_point():
    res = adversarial_bootstrap(
        constraints=_three_constraints(),
        initial_guess={"g_4": 0.5, "g_6": 0.5},
    )
    assert isinstance(res, AdversarialPoint)


def test_finds_origin_with_three_binding_constraints():
    res = adversarial_bootstrap(
        constraints=_three_constraints(),
        initial_guess={"g_4": 0.5, "g_6": 0.5},
    )
    # The origin (0, 0) satisfies all three constraints with zero margin.
    assert abs(res.theory.coefficients["g_4"]) < 1e-3
    assert abs(res.theory.coefficients["g_6"]) < 1e-3
    assert res.n_binding == 3


def test_returned_theory_is_feasible():
    res = adversarial_bootstrap(
        constraints=_three_constraints(),
        initial_guess={"g_4": 0.5, "g_6": 0.5},
    )
    for c in _three_constraints():
        result = c.evaluate(res.theory)
        # allow for small numerical violation up to the optimizer tolerance
        assert result.margin >= -1e-4


def test_two_positivity_constraints_only_also_finds_origin():
    res = adversarial_bootstrap(
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
        initial_guess={"g_4": 0.5, "g_6": 0.5},
    )
    assert abs(res.theory.coefficients["g_4"]) < 1e-3
    assert abs(res.theory.coefficients["g_6"]) < 1e-3
    assert res.n_binding == 2
