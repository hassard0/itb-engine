import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.swampland import WeakGravityConjecture
from itb.theory import Theory


def test_wgc_class_c_universality():
    c = WeakGravityConjecture()
    assert c.constraint_class is ConstraintClass.C_UNIVERSALITY
    assert "Arkani-Hamed" in c.citation


def test_wgc_satisfied_when_g_R2_below_sqrt_g_4():
    c = WeakGravityConjecture(alpha=1.0)
    # sqrt(0.5) ≈ 0.707, so g_R2 = 0.3 satisfies
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_R2": 0.3}))
    assert r.satisfied is True
    assert r.margin > 0


def test_wgc_violated_when_g_R2_too_large():
    c = WeakGravityConjecture(alpha=1.0)
    # sqrt(0.25) = 0.5, g_R2 = 0.8 violates
    r = c.evaluate(Theory(coefficients={"g_4": 0.25, "g_R2": 0.8}))
    assert r.satisfied is False


def test_wgc_violated_at_negative_g_4():
    """Negative matter self-coupling makes the WGC undefined / violated."""
    c = WeakGravityConjecture()
    r = c.evaluate(Theory(coefficients={"g_4": -0.1, "g_R2": 0.0}))
    assert r.satisfied is False


def test_wgc_with_strict_alpha():
    """Tighter alpha gives stricter bound."""
    c_loose = WeakGravityConjecture(alpha=2.0)
    c_strict = WeakGravityConjecture(alpha=0.5)
    theory = Theory(coefficients={"g_4": 0.5, "g_R2": 0.6})
    # alpha=2: sqrt(0.5)*2 ≈ 1.41, g_R2=0.6 ok
    assert c_loose.evaluate(theory).satisfied is True
    # alpha=0.5: sqrt(0.5)*0.5 ≈ 0.35, g_R2=0.6 violates
    assert c_strict.evaluate(theory).satisfied is False


def test_wgc_against_string_eft():
    """Does the v0.5 toy string-EFT framework satisfy the WGC?
    string-EFT: g_4 = 0.5, g_R2 = 0.2; sqrt(0.5) ≈ 0.707, so 0.2 < 0.707 ✓"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = WeakGravityConjecture()
    theory = StringTreeEFT().encode()
    assert c.evaluate(theory).satisfied is True
