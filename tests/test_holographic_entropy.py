import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.holographic_entropy import (
    BNOSSWMonogamy,
    HolographicSubadditivity,
)
from itb.theory import Theory


def test_subadditivity_class_b():
    c = HolographicSubadditivity()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "SA" in c.citation or "subadditivity" in c.citation.lower()


def test_subadditivity_satisfied_when_matter_dominates():
    c = HolographicSubadditivity()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_6": 0.4, "g_R2": 0.2}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.7)


def test_subadditivity_violated_when_g_R2_too_large():
    c = HolographicSubadditivity()
    r = c.evaluate(Theory(coefficients={"g_4": 0.1, "g_6": 0.1, "g_R2": 0.5}))
    assert r.satisfied is False


def test_mmi_class_b():
    c = BNOSSWMonogamy()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "BNOSSW" in c.citation or "Bao" in c.citation


def test_mmi_satisfied_for_symmetric_matter_sector():
    c = BNOSSWMonogamy()
    # g_4 = g_6 = 1: harmonic = 0.5; g_R2 = 0.3 ≤ 0.5 ✓
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.3}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.2)


def test_mmi_tighter_than_bekenstein_in_asymmetric_sector():
    """MMI bound is tighter than Bekenstein-tight when matter is asymmetric.

    g_4 = 2, g_6 = 0.5, g_R2 = 0.5:
      Bekenstein: g_R2^2 = 0.25 ≤ 0.5 * 2 * 0.5 = 0.5 ✓
      MMI: harmonic = (2 * 0.5)/2.5 = 0.4; 0.4 - 0.5 = -0.1 ✗ (violated)
    """
    from itb.constraints.bekenstein_tight import BekensteinTight
    theory = Theory(coefficients={"g_4": 2.0, "g_6": 0.5, "g_R2": 0.5})
    assert BekensteinTight().evaluate(theory).satisfied is True
    assert BNOSSWMonogamy().evaluate(theory).satisfied is False


def test_mmi_violated_when_g4_plus_g6_negative_and_gR2_positive():
    """MMI requires positive matter coefficients to support holographic
    correlations. Negative matter + positive graviton mediation = inconsistent."""
    c = BNOSSWMonogamy()
    r = c.evaluate(Theory(coefficients={"g_4": -1.0, "g_6": -1.0, "g_R2": 0.5}))
    assert r.satisfied is False


def test_mmi_trivially_satisfied_at_origin():
    """Pure GR limit (no matter, no graviton-mediated coupling) trivially
    satisfies MMI — there are no correlations to monogamize."""
    c = BNOSSWMonogamy()
    r = c.evaluate(Theory(coefficients={"g_4": 0.0, "g_6": 0.0, "g_R2": 0.0}))
    assert r.satisfied is True


def test_mmi_gradient_components():
    c = BNOSSWMonogamy()
    g = c.gradient(Theory(coefficients={"g_4": 1.0, "g_6": 1.0, "g_R2": 0.3}))
    # at g_4 = g_6 = 1, denom = 2, partials = g_6^2/4 = 0.25 each
    assert g["g_4"] == pytest.approx(0.25)
    assert g["g_6"] == pytest.approx(0.25)
    assert g["g_R2"] == pytest.approx(-1.0)


def test_existing_frameworks_against_new_constraints():
    """Do our 4 frameworks pass SA and MMI?"""
    from itb.constraints.bekenstein_tight import BekensteinTight
    from itb.frameworks.asymptotic_safety import AsymptoticSafety
    from itb.frameworks.lqg_induced import LQGInduced
    from itb.frameworks.pure_gr import PureGR
    from itb.frameworks.string_tree_eft import StringTreeEFT

    sa = HolographicSubadditivity()
    mmi = BNOSSWMonogamy()

    # All 4 frameworks should pass SA (matter coefficients dominate)
    for fw_cls in (PureGR, StringTreeEFT, AsymptoticSafety, LQGInduced):
        theory = fw_cls().encode()
        if fw_cls is PureGR:
            # 0 + 0 - 0 = 0 ≥ 0 ✓ (boundary)
            assert sa.evaluate(theory).satisfied is True
        else:
            assert sa.evaluate(theory).satisfied is True, fw_cls.__name__

    # MMI is tighter — check what we get for each
    # string-EFT: g_4=0.5, g_6=0.4, g_R2=0.2 → harmonic = 0.2/0.9 ≈ 0.222 vs 0.2 → margin ≈ 0.022 ✓
    assert mmi.evaluate(StringTreeEFT().encode()).satisfied is True
    # AS: g_4=0.4, g_6=0.3, g_R2=0.15 → harmonic = 0.12/0.7 ≈ 0.171 vs 0.15 → margin ≈ 0.021 ✓
    assert mmi.evaluate(AsymptoticSafety().encode()).satisfied is True
    # LQG: g_4=0.6, g_6=0.45, g_R2=0.3 → harmonic = 0.27/1.05 ≈ 0.257 vs 0.3 → margin ≈ -0.043 ✗
    # LQG-induced VIOLATES MMI! That's a real result.
    assert mmi.evaluate(LQGInduced().encode()).satisfied is False
