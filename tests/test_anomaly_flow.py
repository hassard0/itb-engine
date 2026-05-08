import pytest

from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow,
    tHooftAnomalyMatching,
)
from itb.constraints.base import ConstraintClass
from itb.theory import Theory


def test_inflow_class_c():
    c = GeneralizedAnomalyInflow()
    assert c.constraint_class is ConstraintClass.C_UNIVERSALITY


def test_inflow_satisfied_for_parity_conserving():
    """Pure GR / string / AS have all parity = 0; inflow trivially holds."""
    c = GeneralizedAnomalyInflow(rho=0.05)
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_R2": 0.2, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
    }))
    assert r.satisfied is True


def test_inflow_satisfied_for_lqg_at_default():
    """LQG g_R2_parity=0.08, g_R3_parity=0.04, g_4=0.6, g_R2=0.3
       lhs = 0.0064 + 0.0032 = 0.0096
       rhs = rho * 0.6 * 0.3 = 0.18 rho
       For rho = 0.06: 0.0108 > 0.0096 ✓"""
    c = GeneralizedAnomalyInflow(rho=0.06)
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.6, "g_R2": 0.3, "g_R2_parity": 0.08, "g_R3_parity": 0.04,
    }))
    assert r.satisfied is True


def test_inflow_violated_when_parity_too_large():
    c = GeneralizedAnomalyInflow(rho=0.05)
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_R2": 0.2, "g_R2_parity": 0.5, "g_R3_parity": 0.3,
    }))
    assert r.satisfied is False


def test_t_hooft_class_c():
    assert tHooftAnomalyMatching().constraint_class is ConstraintClass.C_UNIVERSALITY


def test_t_hooft_trivial_for_parity_conserving():
    c = tHooftAnomalyMatching()
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_6": 0.4, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
    }))
    assert r.satisfied is True


def test_t_hooft_violated_when_only_cubic_parity_present():
    """If g_R2_parity = 0 but g_R3_parity ≠ 0, anomaly matching fails."""
    c = tHooftAnomalyMatching()
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_6": 0.4, "g_R2_parity": 0.0, "g_R3_parity": 0.05,
    }))
    assert r.satisfied is False


def test_t_hooft_satisfied_for_lqg_default():
    """LQG: g_R2_parity = 0.08, g_R3_parity = 0.04, g_4 + g_6 = 1.05
       Predicted max |g_R3_parity| = 0.5 * 0.08 * 1.05 + 0.02 = 0.062
       Actual = 0.04 < 0.062 ✓"""
    c = tHooftAnomalyMatching(rho_match=0.5, slack=0.02)
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.6, "g_6": 0.45, "g_R2_parity": 0.08, "g_R3_parity": 0.04,
    }))
    assert r.satisfied is True


def test_t_hooft_violated_when_cubic_too_large_relative():
    c = tHooftAnomalyMatching(rho_match=0.5, slack=0.02)
    # g_R3_parity = 0.5 (way more than predicted ratio)
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.6, "g_6": 0.45, "g_R2_parity": 0.08, "g_R3_parity": 0.5,
    }))
    assert r.satisfied is False
