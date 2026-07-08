"""Tests for the executed scale-clean UV test / Regge fingerprint match (v2.466)."""

import math
from experiments.qnm_regge_fingerprint_match import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_flat_regge_zeta_ratios():
    fr = _RES["flat_regge_fingerprint"]
    z2, z3, z4 = math.pi**2/6, 1.2020569, math.pi**4/90
    assert abs(fr["matter_low_zeta2_zeta4_over_zeta3sq"] - z2*z4/z3**2) < 1e-3


def test_both_string_like_decreasing():
    fr = _RES["flat_regge_fingerprint"]
    cf = _RES["candidate_fingerprint"]
    assert fr["matter_low_zeta2_zeta4_over_zeta3sq"] > 1 and fr["matter_high_zeta3_zeta5_over_zeta4sq"] > 1
    assert cf["matter_low"] > 1 and cf["matter_high"] >= 1 - 1e-9
    # decreasing toward 1 with rung
    assert fr["matter_high_zeta3_zeta5_over_zeta4sq"] < fr["matter_low_zeta2_zeta4_over_zeta3sq"]


def test_low_ratio_moderate_match():
    assert _RES["fractional_diff"]["low"] < 0.15


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "first executed" in f
    assert "regge-tower" in f and "consistent" in f
    assert "zeta-value ratios" in f
    sc = _RES["honest_scope"].lower()
    assert "proof of concept" in sc and "toy" in sc
    assert "not the exact string" in sc or "not the definitive virasoro" in sc or "not the exact virasoro" in sc
    assert "shape" in sc  # shape robust, value approximate
