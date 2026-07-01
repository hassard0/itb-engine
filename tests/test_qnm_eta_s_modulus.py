"""Tests for the eta/s modulus swing (v2.409)."""

from experiments.qnm_eta_s_modulus import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_eta_s_is_a_band_saturating_kss_at_ac():
    b = _RES["eta_over_s_in_KSS_units"]
    assert b["at_a_equals_c"] == 1.0            # KSS saturated at a=c
    assert b["band"][1] - b["band"][0] > 0.5    # a genuine band
    assert b["band"][0] < 1.0 < b["band"][1]    # a=c interior to the band


def test_kss_violation_requires_c_gt_a():
    assert _RES["kss_violation_possible"] is True
    assert _RES["eta_over_s_in_KSS_units"]["band"][0] < 1.0   # sub-KSS accessible


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "modulus-band" in f
    assert "kss" in f and "saturat" in f
    assert "v1.72" in f and "assumption in disguise" in f
    sc = _RES["honest_scope"].lower()
    assert "holographic dual" in sc
    assert "conditional on holography" in sc or "if there is no dual" in sc
    assert "looser than" in sc or "gauss-bonnet causality" in sc
