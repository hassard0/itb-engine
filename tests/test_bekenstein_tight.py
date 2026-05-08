import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.theory import Theory


def test_metadata_class_b():
    c = BekensteinTight()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "Bekenstein" in c.citation


def test_satisfied_when_g_R2_squared_below_half_g4_g6():
    c = BekensteinTight()
    # g_R2^2 = 0.04, (1/2) * g_4 * g_6 = 0.5; satisfied
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.2}))
    assert r.satisfied is True


def test_strictly_tighter_than_caron_huot_bound():
    """Bekenstein-tight should rule out points that the looser Caron-Huot
    mixed-positivity allows."""
    from itb.constraints.graviton_eft import GravitonMixedPositivity

    # Pick a point inside the Caron-Huot region (g_R2^2 < g_4*g_6) but outside
    # the Bekenstein-tight region (g_R2^2 > 0.5 * g_4 * g_6).
    # g_4 = g_6 = 1.0, g_R2 = 0.8: g_R2^2 = 0.64
    # Caron-Huot: 0.64 <= 1.0 ✓ (allowed)
    # Bekenstein-tight: 0.64 > 0.5 ✗ (forbidden)
    theory = Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.8})
    assert GravitonMixedPositivity().evaluate(theory).satisfied is True
    assert BekensteinTight().evaluate(theory).satisfied is False


def test_gradient_components():
    c = BekensteinTight()
    # margin = 0.5 * g_4 * g_6 - g_R2^2
    g = c.gradient(Theory(coefficients={"g_4": 0.7, "g_6": 0.3, "g_R2": 0.5}))
    assert g["g_4"] == pytest.approx(0.5 * 0.3)
    assert g["g_6"] == pytest.approx(0.5 * 0.7)
    assert g["g_R2"] == pytest.approx(-2.0 * 0.5)


def test_binding_class_diagnostic_now_distinguishes_classes():
    """With both class-A graviton positivity AND class-B Bekenstein in the
    set, the engine should report binding_class differently in different
    regions of theory space."""
    from itb.constraints.graviton_eft import GravitonMixedPositivity
    from itb.engine import check

    constraints = [GravitonMixedPositivity(), BekensteinTight()]
    # In a region where Bekenstein binds first
    bek_region = Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.85})
    r = check(bek_region, constraints)
    assert r.feasible is False
    assert r.binding_class == "information_theoretic"
