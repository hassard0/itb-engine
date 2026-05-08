import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.distance_conjecture import DistanceConjecture
from itb.theory import Theory


def test_class_c_universality():
    c = DistanceConjecture()
    assert c.constraint_class is ConstraintClass.C_UNIVERSALITY


def test_trivial_for_pure_gr():
    """All zeros → no aspect ratio."""
    c = DistanceConjecture()
    r = c.evaluate(Theory(coefficients={"g_4": 0.0, "g_6": 0.0, "g_R2": 0.0}))
    assert r.satisfied is True


def test_satisfied_for_balanced_coefficients():
    c = DistanceConjecture(R_max=20.0)
    # ratio = 0.5 / 0.1 = 5 ≤ 20 ✓
    r = c.evaluate(Theory(coefficients={"g_4": 0.5, "g_R2": 0.1}))
    assert r.satisfied is True


def test_violated_for_pathologically_anisotropic():
    c = DistanceConjecture(R_max=10.0)
    # ratio = 1.0 / 0.001 = 1000 > 10 ✗
    r = c.evaluate(Theory(coefficients={"g_4": 1.0, "g_R2": 0.001}))
    assert r.satisfied is False


def test_string_eft_passes_default():
    from itb.frameworks.string_tree_eft import StringTreeEFT
    c = DistanceConjecture(R_max=20.0)
    r = c.evaluate(StringTreeEFT().encode())
    # max/min = 0.5/0.15 = 3.33 ≤ 20 ✓
    assert r.satisfied is True


def test_lqg_induced_passes_default_but_close():
    """LQG has g_R3_parity = 0.04 as smallest, g_4 = 0.6 as largest.
       ratio ≈ 15 < 20 ✓ but with margin only 5."""
    from itb.frameworks.lqg_induced import LQGInduced
    c = DistanceConjecture(R_max=20.0)
    r = c.evaluate(LQGInduced().encode())
    assert r.satisfied is True
    assert r.margin < 10  # closer to boundary than other frameworks


def test_lqg_violates_strict_bound():
    """If we tighten R_max to 10, LQG fails."""
    from itb.frameworks.lqg_induced import LQGInduced
    c = DistanceConjecture(R_max=10.0)
    assert c.evaluate(LQGInduced().encode()).satisfied is False
