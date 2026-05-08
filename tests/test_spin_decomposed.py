import pytest

from itb.constraints.spin_decomposed import SpinTwoPositivity, SpinZeroPositivity
from itb.theory import Theory


def test_spin_zero_satisfied_when_g_4_dominates():
    c = SpinZeroPositivity(alpha=0.5)
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_R2": 0.5}))
    # 1.0 - 0.5*0.5 = 0.75 > 0
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.75)


def test_spin_zero_violated_when_g_R2_dominates():
    c = SpinZeroPositivity(alpha=2.0)
    r = c.evaluate(Theory(coefficients={"g_4": 0.1, "g_R2": 1.0}))
    # 0.1 - 2.0*1.0 = -1.9 < 0
    assert r.satisfied is False


def test_spin_two_satisfied_in_normal_region():
    c = SpinTwoPositivity(beta=0.3)
    r = c.evaluate(Theory(coefficients={"g_6": 0.5, "g_R2": 0.4}))
    # 0.4 + 0.3*0.5 = 0.55 > 0
    assert r.satisfied is True


def test_spin_two_violated_with_negative_g_R2():
    c = SpinTwoPositivity(beta=0.3)
    r = c.evaluate(Theory(coefficients={"g_6": 0.0, "g_R2": -0.5}))
    assert r.satisfied is False


def test_combined_spin_decomposition_with_string_eft():
    from itb.engine import check
    from itb.frameworks.string_tree_eft import StringTreeEFT
    constraints = [SpinZeroPositivity(alpha=0.5), SpinTwoPositivity(beta=0.3)]
    theory = StringTreeEFT().encode()
    report = check(theory, constraints)
    assert report.feasible is True


def test_gradient_components():
    c0 = SpinZeroPositivity(alpha=0.5)
    g0 = c0.gradient(Theory(coefficients={"g_4": 0.5, "g_R2": 0.5}))
    assert g0["g_4"] == 1.0
    assert g0["g_R2"] == -0.5
    c2 = SpinTwoPositivity(beta=0.3)
    g2 = c2.gradient(Theory(coefficients={"g_6": 0.5, "g_R2": 0.5}))
    assert g2["g_R2"] == 1.0
    assert g2["g_6"] == 0.3
