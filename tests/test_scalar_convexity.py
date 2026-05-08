import numpy as np
import pytest

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.base import ConstraintClass
from itb.mapper import trace_boundary_along_axis
from itb.theory import Theory


def test_satisfied_when_g6_exceeds_g4_squared():
    c = ScalarConvexityG6vsG4()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_6": 0.5}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.5 - 0.25)


def test_violated_when_g6_below_g4_squared():
    c = ScalarConvexityG6vsG4()
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 0.5}))
    assert r.satisfied is False
    assert r.margin == pytest.approx(-0.5)


def test_boundary_when_g6_equals_g4_squared():
    c = ScalarConvexityG6vsG4()
    r = c.evaluate(Theory(coefficients={"g_4": 0.7, "g_6": 0.49}))
    assert r.satisfied is True
    assert abs(r.margin) < 1e-9


def test_gradient_has_negative_g4_component_for_positive_g4():
    c = ScalarConvexityG6vsG4()
    g = c.gradient(Theory(coefficients={"g_4": 0.5, "g_6": 0.5}))
    assert g["g_4"] == pytest.approx(-2 * 0.5)
    assert g["g_6"] == pytest.approx(1.0)


def test_signed_distance_normalized_by_gradient_norm():
    c = ScalarConvexityG6vsG4()
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 0.5}))
    # margin = -0.5, gradient = (-2, 1), |grad| = sqrt(5)
    assert r.signed_distance_margin == pytest.approx(-0.5 / np.sqrt(5))


def test_metadata():
    c = ScalarConvexityG6vsG4()
    assert c.name == "scalar_convexity_g6_vs_g4"
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE


def test_newton_tracer_converges_on_curved_boundary():
    c = ScalarConvexityG6vsG4()
    # Start strongly inside the allowed region
    point = trace_boundary_along_axis(
        constraint=c,
        start={"g_4": 0.5, "g_6": 1.0},
        max_iters=50,
        tol=1e-9,
    )
    # On the boundary g_6 = g_4^2
    assert abs(point["g_6"] - point["g_4"] ** 2) < 1e-6
