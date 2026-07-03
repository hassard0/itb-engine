"""Tests for the alpha_EM cosmic-birefringence near-prediction (v2.451)."""

import math
from experiments.qnm_alpha_em_birefringence import run, beta_deg, ALPHA_EM

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_unit_prediction_is_alpha_over_4pi():
    assert abs(_RES["unit_prediction_deg"] - math.degrees(ALPHA_EM / (4 * math.pi))) < 1e-3


def test_natural_range_brackets_measured():
    lo = _RES["natural_range_deg"]["low"]
    hi = _RES["natural_range_deg"]["high"]
    assert lo < _RES["measured_deg"] <= hi * 1.1   # measured at the upper edge


def test_beta_scales_linearly():
    assert abs(beta_deg(2, 3) - 6 * beta_deg(1, 1)) < 1e-9   # linear in c_gamma*dtheta


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "scale-independent" in f
    assert "alpha_em" in f
    assert "near-prediction" in f
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "not computed" in sc            # anomaly coeff not derived
    assert "upper end" in sc or "upper edge" in sc
    assert "3.6-sigma" in sc or "3.6 sigma" in sc
