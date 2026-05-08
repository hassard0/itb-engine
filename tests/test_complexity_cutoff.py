import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.complexity_cutoff import ComplexityCutoff
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


def test_class_c_universality():
    c = ComplexityCutoff()
    assert c.constraint_class is ConstraintClass.C_UNIVERSALITY
    assert "Susskind" in c.citation or "Lloyd" in c.citation


def test_pure_gr_zero_complexity():
    c = ComplexityCutoff(c_max=1.0)
    r = c.evaluate(PureGR().encode())
    assert r.satisfied is True
    assert r.details["complexity"] == 0.0


def test_complexity_grows_with_coefficients():
    c = ComplexityCutoff(c_max=10.0)
    small = c.evaluate(Theory(coefficients={"g_4": 0.1}))
    large = c.evaluate(Theory(coefficients={"g_4": 1.0}))
    assert large.details["complexity"] > small.details["complexity"]


def test_higher_dim_operator_weighted_more():
    c = ComplexityCutoff(c_max=10.0)
    g4_only = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    g8_only = c.evaluate(Theory(coefficients={"g_8": 0.5}))
    # g_8 has weight 3 vs g_4 weight 1, so same coefficient gives 3x complexity
    assert g8_only.details["complexity"] > g4_only.details["complexity"]


def test_at_default_c_max_only_lqg_fails():
    """Default c_max = 1.5. Actual framework complexities:
       Pure GR: 0
       AS:      0.16 + 0.18 + 0.0225 + 0.27 + 0.02 = 0.6525  ✓
       String:  0.25 + 0.32 + 0.04 + 0.48 + 0.045 = 1.135   ✓
       LQG:     0.36 + 0.405 + 0.09 + 0.48 + 0.18 + 0.0064 + 0.0032 = 1.5246  ✗ (just over)"""
    c = ComplexityCutoff(c_max=1.5)
    assert c.evaluate(PureGR().encode()).satisfied is True
    assert c.evaluate(AsymptoticSafety().encode()).satisfied is True
    assert c.evaluate(StringTreeEFT().encode()).satisfied is True
    assert c.evaluate(LQGInduced().encode()).satisfied is False


def test_tighter_c_max_excludes_more_frameworks():
    c = ComplexityCutoff(c_max=1.0)
    # String (1.135) also fails at this tighter cutoff
    assert c.evaluate(StringTreeEFT().encode()).satisfied is False
    assert c.evaluate(AsymptoticSafety().encode()).satisfied is True
    assert c.evaluate(LQGInduced().encode()).satisfied is False


def test_loose_c_max_admits_all():
    c = ComplexityCutoff(c_max=10.0)
    for fw_cls in (PureGR, StringTreeEFT, AsymptoticSafety, LQGInduced):
        assert c.evaluate(fw_cls().encode()).satisfied is True


def test_gradient_points_against_growing_coefficients():
    """Gradient of margin w.r.t. coefficients should be negative (since
    increasing coefficients increases complexity, decreasing margin)."""
    c = ComplexityCutoff(c_max=3.0)
    g = c.gradient(Theory(coefficients={"g_4": 0.5, "g_6": 0.4}))
    assert g["g_4"] < 0
    assert g["g_6"] < 0


def test_custom_weights():
    """Caller can override weights to emphasize different operators."""
    c = ComplexityCutoff(c_max=1.0, weights={"g_4": 10.0})
    r = c.evaluate(Theory(coefficients={"g_4": 0.4}))
    # complexity = 10 * 0.16 = 1.6 > 1.0
    assert r.satisfied is False
