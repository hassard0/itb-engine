import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.theory import Theory


def test_metadata():
    c = GravitonMixedPositivity()
    assert c.name == "graviton_mixed_positivity"
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Caron-Huot" in c.citation


def test_satisfied_when_g_R2_squared_below_g4_g6_product():
    c = GravitonMixedPositivity()
    # g_R2^2 = 0.25, g_4 * g_6 = 1.0; satisfied with margin 0.75
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.5}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.75)


def test_violated_when_g_R2_too_large():
    c = GravitonMixedPositivity()
    # g_R2^2 = 4.0, g_4 * g_6 = 1.0; violated with margin -3.0
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 2.0}))
    assert r.satisfied is False
    assert r.margin == pytest.approx(-3.0)


def test_violated_when_g_4_negative_even_if_g_R2_zero():
    c = GravitonMixedPositivity()
    # g_R2 = 0; g_4 * g_6 = -1.0; margin = 0 - (-1) = 1, but we ALSO require
    # the underlying positivity, so this constraint is "g_R2^2 <= g_4 * g_6"
    # which fails when the product is negative.
    r = c.evaluate(Theory(coefficients={"g_4": -1.0, "g_6": 1.0, "g_R2": 0.0}))
    assert r.satisfied is False


def test_gradient_components():
    c = GravitonMixedPositivity()
    # margin = g_4 * g_6 - g_R2^2
    # d/dg_4 = g_6, d/dg_6 = g_4, d/dg_R2 = -2 g_R2
    g = c.gradient(Theory(coefficients={"g_4": 0.7, "g_6": 0.3, "g_R2": 0.5}))
    assert g["g_4"] == pytest.approx(0.3)
    assert g["g_6"] == pytest.approx(0.7)
    assert g["g_R2"] == pytest.approx(-1.0)


def test_works_with_engine_against_three_coefficient_theory():
    from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )
    from itb.engine import check

    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
        GravitonMixedPositivity(),
    ]
    feasible = Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.3})
    assert check(feasible, constraints).feasible is True

    infeasible = Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 1.5})
    assert check(infeasible, constraints).feasible is False
