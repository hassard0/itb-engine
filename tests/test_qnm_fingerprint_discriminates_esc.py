"""Tests for the fingerprint-discriminates-ESC result (v2.474)."""

from experiments.qnm_fingerprint_discriminates_esc import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_branches_differ_and_candidate_favors_regge():
    assert abs(_RES["regge_low_double_ratio"] - _RES["kk_low_double_ratio"]) > 0.1
    assert _RES["frac_diff"]["regge"] < _RES["frac_diff"]["kk"]
    assert _RES["frac_diff"]["regge"] < 0.15
    assert _RES["frac_diff"]["kk"] > 0.2
    assert "string" in _RES["favors"].lower()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "discriminates" in f
    assert "v2.438" in f
    assert "heterotic-string" in f or "string (regge)" in f
    sc = _RES["honest_scope"].lower()
    assert "proof-of-concept" in sc or "flat-residue" in sc
    assert "low rung" in sc  # high rung floor-contaminated
    assert "chebyshev" in sc
