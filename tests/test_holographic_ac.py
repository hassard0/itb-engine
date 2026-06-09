"""Tests for the holographic a/c <-> eta/s unification (v1.72)."""
import pytest

from itb.holographic_ac import (
    LAMBDA_CAUSALITY_MAX, LAMBDA_CAUSALITY_MIN, AC_FLOOR, AC_CEIL,
    ac_ratio, c_minus_a_over_c, eta_over_s_kss, gC_from_gR2,
    lambda_GB, unification_residual,
)


def test_lambda_zero_is_einstein():
    """lambda=0: a=c (a/c=1), eta/s=1 (KSS saturated)."""
    assert ac_ratio(0.0) == pytest.approx(1.0)
    assert eta_over_s_kss(0.0) == pytest.approx(1.0)
    assert c_minus_a_over_c(0.0) == pytest.approx(0.0)


def test_unification_linear_order():
    """1 - 4pi(eta/s) = (c-a)/c holds to LINEAR order: tight at small lambda,
    with O(lambda^2) corrections that grow toward the causal boundary."""
    # small-lambda regime: identity is tight
    for lam in (-0.03, 0.0, 0.02, 0.03):
        assert abs(unification_residual(lam)) < 0.01
    # exact forms differ by a factor (1-2 lambda): residual grows at large |lambda|
    assert abs(unification_residual(-0.19)) > 0.1     # O(lambda^2) is real
    # the exact multiplicative relation IS exact everywhere:
    for lam in (-0.19, -0.05, 0.05, 0.09):
        lhs = 1.0 - eta_over_s_kss(lam)               # = 4 lambda
        rhs = c_minus_a_over_c(lam) * (1.0 - 2.0 * lam)
        assert lhs == pytest.approx(rhs)


def test_positive_lambda_lowers_both():
    """lambda>0 (c>a): a/c<1 AND eta/s<1 (both below their Einstein values)."""
    lam = 0.08
    assert ac_ratio(lam) < 1.0
    assert eta_over_s_kss(lam) < 1.0


def test_causality_strictly_inside_HM():
    """The GB causality window maps strictly inside the HM wedge [1/3, 31/18]."""
    ac_at_caus_max = ac_ratio(LAMBDA_CAUSALITY_MAX)   # ~0.561
    ac_at_caus_min = ac_ratio(LAMBDA_CAUSALITY_MIN)   # ~1.560
    assert AC_FLOOR < ac_at_caus_max < ac_at_caus_min < AC_CEIL
    # HM floor needs lambda beyond causality
    assert 1.0 / 8.0 > LAMBDA_CAUSALITY_MAX


def test_gC_consistency():
    """g_C = g_R2 / (a/c); with lambda>0, g_C > g_R2 (c>a)."""
    gR2 = 0.3
    gC = gC_from_gR2(gR2)
    assert gC > gR2
    assert gC == pytest.approx(gR2 / ac_ratio(lambda_GB(gR2)))


def test_gR2_zero_vacuous():
    assert gC_from_gR2(0.0) == 0.0
