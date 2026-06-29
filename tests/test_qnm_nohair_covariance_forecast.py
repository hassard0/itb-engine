"""Tests for the covariance-corrected no-hair detectability forecast (v2.227)."""

from experiments.qnm_nohair_covariance_forecast import ratio_uncertainty, run


def test_isolated_estimate_was_optimistic():
    res = run()
    # the covariance-corrected rho_crit is several times larger than the v2.226 isolated estimate
    for chan in ("freq", "damp"):
        assert res["nohair_forecast"][chan]["optimism_factor_vs_isolated"] > 5


def test_correlation_mitigates_ratio_variance():
    # correlated mode errors partially cancel in a ratio -> full < diagonal
    ru = ratio_uncertainty()
    for chan in ("freq", "damp"):
        assert ru[chan]["rho_sigma_full"] < ru[chan]["rho_sigma_diag"]
        assert ru[chan]["mode_correlation"] > 0.7
    # mitigation is strongest in the damping channel
    res = run()
    assert res["nohair_forecast"]["damp"]["correlation_mitigation"] > 0.2


def test_damping_channel_still_dominates():
    res = run()
    assert res["damp_over_freq_sensitivity_full"] > 50
    fc = res["nohair_forecast"]
    assert fc["damp"]["rho_crit_1sigma_full_per_gamma"] < fc["freq"]["rho_crit_1sigma_full_per_gamma"]


def test_honest_scope_refines_v2226():
    res = run()
    sc = res["honest_scope"].lower()
    assert "refines the v2.226" in sc
    assert "source-backed" in sc
    assert "g_R4_c3" in res["honest_scope"]
