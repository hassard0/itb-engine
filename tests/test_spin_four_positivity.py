import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.spin_four_positivity import SpinFourPositivity
from itb.theory import Theory


def test_class_a_amplitude():
    c = SpinFourPositivity()
    assert c.constraint_class is ConstraintClass.A_AMPLITUDE


def test_satisfied_when_cubic_curvature_dominates():
    c = SpinFourPositivity(gamma=0.3, delta=0.5)
    # g_R3=0.3, g_8=0.4 (γ=0.3 → +0.12), g_4=0.5, g_R2=0.2 (δ=0.5 → -0.05)
    # margin = 0.3 + 0.12 - 0.05 = 0.37 ✓
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_R2": 0.2, "g_8": 0.4, "g_R3": 0.3,
    }))
    assert r.satisfied is True


def test_violated_when_matter_graviton_coupling_dominates():
    c = SpinFourPositivity(gamma=0.3, delta=2.0)
    # delta=2 makes the negative term dominant: g_R3 + 0.3*0.4 - 2*0.2*0.5 =
    # 0.3 + 0.12 - 0.2 = 0.22 still positive... need stronger delta:
    c2 = SpinFourPositivity(gamma=0.3, delta=10.0)
    r = c2.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_R2": 0.5, "g_8": 0.0, "g_R3": 0.0,
    }))
    # margin = 0 + 0 - 10*0.5*0.5 = -2.5
    assert r.satisfied is False


def test_string_eft_passes_default():
    """String EFT: g_R3=0.15, g_8=0.4, g_4=0.5, g_R2=0.2.
       margin = 0.15 + 0.3*0.4 - 0.5*0.2*0.5 = 0.15 + 0.12 - 0.05 = 0.22 ✓"""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = SpinFourPositivity()
    r = c.evaluate(StringTreeEFT().encode())
    assert r.satisfied is True


def test_lqg_induced_passes_default():
    """LQG: g_R3=0.30, g_8=0.40, g_4=0.6, g_R2=0.3.
       margin = 0.3 + 0.12 - 0.5*0.3*0.6 = 0.3 + 0.12 - 0.09 = 0.33 ✓"""
    from itb.frameworks.lqg_induced import LQGInduced
    c = SpinFourPositivity()
    r = c.evaluate(LQGInduced().encode())
    assert r.satisfied is True
