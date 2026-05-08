import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.dispersion_tower import (
    DispersionTowerCauchySchwarz,
    ScalarPositivityG8,
)
from itb.theory import Theory


def test_g8_positivity():
    c = ScalarPositivityG8()
    assert c.evaluate(Theory(coefficients={"g_8": 0.3})).satisfied is True
    assert c.evaluate(Theory(coefficients={"g_8": -0.1})).satisfied is False


def test_cauchy_schwarz_satisfied_when_g6_below_geometric_mean():
    c = DispersionTowerCauchySchwarz()
    # g_4 = 1, g_8 = 1, g_6 = 0.5: g_6^2 = 0.25 <= 1.0 ✓
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 0.5, "g_8": 1.0}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.75)


def test_cauchy_schwarz_violated_when_g6_too_large():
    c = DispersionTowerCauchySchwarz()
    # g_4 = 1, g_8 = 0.5, g_6 = 1: g_6^2 = 1 > 0.5 ✗
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_8": 0.5}))
    assert r.satisfied is False


def test_metadata_class_a():
    assert DispersionTowerCauchySchwarz().constraint_class is ConstraintClass.A_AMPLITUDE
    assert "Caron-Huot" in DispersionTowerCauchySchwarz().citation


def test_gradient_components():
    c = DispersionTowerCauchySchwarz()
    g = c.gradient(Theory(coefficients={"g_4": 0.5, "g_6": 0.3, "g_8": 0.7}))
    assert g["g_4"] == pytest.approx(0.7)
    assert g["g_6"] == pytest.approx(-0.6)
    assert g["g_8"] == pytest.approx(0.5)


def test_engine_with_full_tower():
    """Use g_4, g_6, g_8 positivity + Cauchy-Schwarz; only theories satisfying
    every step in the dispersion tower survive."""
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4,
        ScalarPositivityG6,
    )
    from itb.engine import check

    constraints = [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarPositivityG8(),
        DispersionTowerCauchySchwarz(),
    ]
    feasible = Theory(coefficients={"g_4": 1.0, "g_6": 0.5, "g_8": 1.0})
    assert check(feasible, constraints).feasible is True

    # g_6 too large: violates Cauchy-Schwarz
    infeasible = Theory(coefficients={"g_4": 1.0, "g_6": 1.5, "g_8": 1.0})
    assert check(infeasible, constraints).feasible is False
