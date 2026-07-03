"""Tests for the neutral-BH-entropy / causality<->second-law sign agreement (v2.445)."""

from experiments.qnm_neutral_bh_entropy import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_gC_negative_excluded_by_causality():
    scan = _RES["gC_sign_scan"]
    assert scan["-0.193"]["feasible"] is False
    assert any("hofman" in v.lower() for v in scan["-0.193"]["violations"])
    assert scan["+0.193"]["feasible"] is True


def test_entropy_shift_positive():
    assert _RES["neutral_Schwarzschild_delta_S_sign"] == "positive"


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "second law" in f
    assert "causality" in f and "agree" in f
    assert "schwarzschild" in f
    sc = _RES["honest_scope"].lower()
    assert "sign-level" in sc
    assert "planck-suppressed" in sc
    assert "independent of the a=c" in sc
