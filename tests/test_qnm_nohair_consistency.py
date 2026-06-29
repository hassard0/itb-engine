"""Tests for the black-hole-spectroscopy no-hair consistency test (v2.226)."""

from experiments.qnm_nohair_consistency import (
    gr_nohair_ratios,
    r4_nohair_violation,
    run,
)


def test_gr_ratios_match_berti():
    res = run()
    assert res["gr_ratios_validated"] is True
    assert res["max_ratio_rel_err"] < 5e-3
    r = gr_nohair_ratios()
    # the no-hair fingerprint: solver reproduces the tabulated GR ratios
    assert abs(r["330"]["solver"] - 1.604) < 0.01
    assert abs(r["440"]["solver"] - 2.166) < 0.01


def test_r4_violates_nohair_consistency():
    v = r4_nohair_violation()
    # R4 shifts both the frequency and damping ratios away from their GR values
    assert abs(v["r4_freq_ratio_violation_per_gamma"]) > 1.0
    assert abs(v["r4_damp_ratio_violation_per_gamma"]) > 100.0


def test_damping_channel_dominates_nohair():
    v = r4_nohair_violation()
    # the damping no-hair channel inherits dtq_1=171.35 -> ~130x more sensitive
    assert v["damp_over_freq_sensitivity"] > 100
    assert v["rho_crit_1sigma_damp_channel_per_gamma"] < v["rho_crit_1sigma_freq_channel_per_gamma"]


def test_honest_scope_cross_l_not_computed():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not computed" in sc
    assert "v2.212" in res["honest_scope"]
    assert "source-backed" in sc
    assert "g_R4_c3" in res["honest_scope"]
