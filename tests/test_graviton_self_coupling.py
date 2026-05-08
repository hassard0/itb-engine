import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.graviton_self_coupling import (
    CubicCurvaturePositivity,
    CubicGravitonMatterBound,
)
from itb.theory import Theory


def test_positivity_class_a():
    c = CubicCurvaturePositivity()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Caron-Huot" in c.citation


def test_positivity_satisfied_when_g_R3_nonneg():
    c = CubicCurvaturePositivity()
    assert c.evaluate(Theory(coefficients={"g_R3": 0.1})).satisfied is True
    assert c.evaluate(Theory(coefficients={"g_R3": 0.0})).satisfied is True


def test_positivity_violated_when_g_R3_negative():
    c = CubicCurvaturePositivity()
    assert c.evaluate(Theory(coefficients={"g_R3": -0.1})).satisfied is False


def test_cubic_matter_bound_class_a():
    c = CubicGravitonMatterBound()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE


def test_cubic_matter_bound_satisfied_when_g_R3_below_g4_squared():
    c = CubicGravitonMatterBound(kappa=1.0)
    # g_4 = 0.5, g_R3 = 0.2: 0.25 >= 0.2 ✓
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_R3": 0.2}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.05)


def test_cubic_matter_bound_violated_when_graviton_too_strong():
    c = CubicGravitonMatterBound(kappa=1.0)
    # g_4 = 0.3, g_R3 = 0.2: 0.09 < 0.2 ✗
    r = c.evaluate(Theory(coefficients={"g_4": 0.3, "g_R3": 0.2}))
    assert r.satisfied is False


def test_cubic_matter_bound_with_strict_kappa():
    """Tighter kappa narrows the allowed region."""
    c_loose = CubicGravitonMatterBound(kappa=2.0)
    c_strict = CubicGravitonMatterBound(kappa=0.5)
    theory = Theory(coefficients={"g_4": 0.5, "g_R3": 0.2})
    # loose: 2 * 0.25 = 0.5 >= 0.2 ✓
    assert c_loose.evaluate(theory).satisfied is True
    # strict: 0.5 * 0.25 = 0.125 < 0.2 ✗
    assert c_strict.evaluate(theory).satisfied is False


def test_gradient_components_for_cubic_matter_bound():
    c = CubicGravitonMatterBound(kappa=1.0)
    g = c.gradient(Theory(coefficients={"g_4": 0.5, "g_R3": 0.2}))
    assert g["g_4"] == pytest.approx(2.0 * 0.5)  # 2 * kappa * g_4 = 1.0
    assert g["g_R3"] == pytest.approx(-1.0)
