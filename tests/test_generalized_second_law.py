import pytest

from itb.constraints.base import ConstraintClass
from itb.constraints.generalized_second_law import GeneralizedSecondLaw
from itb.theory import Theory


def test_class_b_information():
    c = GeneralizedSecondLaw()
    assert c.constraint_class is ConstraintClass.B_INFORMATION
    assert "Bekenstein" in c.citation


def test_satisfied_at_positive_g_R2():
    c = GeneralizedSecondLaw(c_GSL=0.5)
    r = c.evaluate(Theory(coefficients={"g_R2": 0.2}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.7)


def test_satisfied_at_zero_g_R2():
    c = GeneralizedSecondLaw(c_GSL=0.5)
    r = c.evaluate(Theory(coefficients={"g_R2": 0.0}))
    assert r.satisfied is True
    assert r.margin == pytest.approx(0.5)


def test_satisfied_at_small_negative_g_R2():
    """g_R2 = -0.3 is still inside the GSL bound at c_GSL=0.5."""
    c = GeneralizedSecondLaw(c_GSL=0.5)
    r = c.evaluate(Theory(coefficients={"g_R2": -0.3}))
    assert r.satisfied is True


def test_violated_at_large_negative_g_R2():
    c = GeneralizedSecondLaw(c_GSL=0.5)
    r = c.evaluate(Theory(coefficients={"g_R2": -0.8}))
    assert r.satisfied is False


def test_all_frameworks_pass_gsl():
    """All four toy frameworks have g_R2 >= 0 → trivially pass GSL."""
    from itb.frameworks.asymptotic_safety import AsymptoticSafety
    from itb.frameworks.cdt import CausalDynamicalTriangulation
    from itb.frameworks.lqg_induced import LQGInduced
    from itb.frameworks.pure_gr import PureGR
    from itb.frameworks.string_tree_eft import StringTreeEFT

    c = GeneralizedSecondLaw(c_GSL=0.5)
    for fw_cls in (PureGR, StringTreeEFT, AsymptoticSafety,
                   LQGInduced, CausalDynamicalTriangulation):
        theory = fw_cls().encode()
        assert c.evaluate(theory).satisfied is True, fw_cls.__name__
