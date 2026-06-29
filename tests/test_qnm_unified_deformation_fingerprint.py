"""Tests for the unified deformation fingerprint (v2.238)."""

import math

from experiments.qnm_unified_deformation_fingerprint import observables, run


def test_gr_baselines_reproduced():
    b = observables(0.0)
    assert abs(b["shadow_b_c"] - 3 * math.sqrt(3)) < 1e-4
    assert abs(b["ringdown_freq_Omega_c"] - 1 / (3 * math.sqrt(3))) < 1e-4
    assert abs(b["isco_radius"] - 6.0) < 1e-4
    assert abs(b["accretion_efficiency"] - (1 - math.sqrt(8 / 9))) < 1e-4


def test_shadow_ringdown_frequency_locked():
    res = run()
    # Omega_c = 1/b_c -> equal and opposite fractional shifts (the v2.231 locking identity)
    assert abs(res["shadow_ringdown_locking_residual"]) < 1e-6


def test_coherent_em_gw_signature():
    res = run()
    f = res["fractional_sensitivity_d_ln_d_eps"]
    # one eps/r^3 deformation: shadow & ISCO shrink, efficiency & frequencies rise
    assert f["shadow_b_c"] < 0
    assert f["isco_radius"] < 0
    assert f["accretion_efficiency"] > 0
    assert f["merger_freq_Omega_isco"] > 0
    assert f["ringdown_freq_Omega_c"] > 0


def test_all_six_channels_present():
    res = run()
    assert len(res["gr_baseline"]) == 6
    assert set(res["channel"].values()) == {"EM", "GW", "geom"}


def test_honest_scope_synthesis():
    res = run()
    sc = res["honest_scope"].lower()
    assert "synthesis" in sc and "illustrative" in sc
    assert "g_R4_c3" in res["honest_scope"]
