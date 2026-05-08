import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.parity_violation import (
    LIGOBirefringenceBound,
    LeftHandedGravitonPositivity,
    ParityViolatingPositivity,
    RightHandedGravitonPositivity,
)
from itb.theory import Theory


def test_parity_positivity_class_a():
    assert ParityViolatingPositivity().constraint_class is ConstraintClass.A_AMPLITUDE


def test_parity_positivity_satisfied_when_combined_below_matter():
    c = ParityViolatingPositivity(kappa=1.0)
    # g_R2^2 + g_R2_parity^2 = 0.04 + 0.01 = 0.05; g_4*g_6 = 0.2 ✓
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_6": 0.4, "g_R2": 0.2, "g_R2_parity": 0.1,
    }))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.15)


def test_parity_positivity_violated_when_parity_too_large():
    c = ParityViolatingPositivity(kappa=1.0)
    # 0.04 + 0.49 = 0.53 > 0.2 ✗
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_6": 0.4, "g_R2": 0.2, "g_R2_parity": 0.7,
    }))
    assert r.satisfied is False


def test_left_handed_satisfied_when_handedness_aligned():
    c = LeftHandedGravitonPositivity(kappa=1.0)
    # b_left = g_R2 + g_R2_parity = 0.2 + 0.1 = 0.3; b_left^2 = 0.09 < 0.2 ✓
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_6": 0.4, "g_R2": 0.2, "g_R2_parity": 0.1,
    }))
    assert r.satisfied is True


def test_right_handed_can_be_satisfied_when_left_is_not():
    """Asymmetric parity content: a theory with g_R2_parity opposite in
    sign to g_R2 favors one helicity over the other."""
    # b_left = 0.5; b_right = -0.1; b_left^2 = 0.25 > 0.2 ✗
    # b_right^2 = 0.01 < 0.2 ✓
    theory = Theory(coefficients={
        "g_4": 0.5, "g_6": 0.4, "g_R2": 0.2, "g_R2_parity": 0.3,
    })
    assert LeftHandedGravitonPositivity(kappa=1.0).evaluate(theory).satisfied is False
    assert RightHandedGravitonPositivity(kappa=1.0).evaluate(theory).satisfied is True


def test_ligo_birefringence_bound_class_b():
    c = LIGOBirefringenceBound()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "LIGO" in c.citation


def test_ligo_birefringence_satisfied_at_zero_parity():
    c = LIGOBirefringenceBound(bound=0.1)
    r = c.evaluate(Theory(coefficients={"g_R2_parity": 0.0}))
    assert r.satisfied is True


def test_ligo_birefringence_violated_at_large_parity():
    c = LIGOBirefringenceBound(bound=0.1)
    r = c.evaluate(Theory(coefficients={"g_R2_parity": 0.5}))
    assert r.satisfied is False


def test_ligo_birefringence_symmetric_in_sign():
    """|g_R2_parity| bound — both signs equally restricted."""
    c = LIGOBirefringenceBound(bound=0.1)
    pos = c.evaluate(Theory(coefficients={"g_R2_parity": 0.05}))
    neg = c.evaluate(Theory(coefficients={"g_R2_parity": -0.05}))
    assert pos.satisfied == neg.satisfied
    assert pos.margin == pytest.approx(neg.margin)
