"""Tests for the first-principles ringdown resolvability calculation (v2.219)."""

from experiments.qnm_ringdown_resolvability import (
    OMEGA_I,
    OMEGA_R,
    critical_snr,
    ringdown_fisher,
    run,
)


def test_l2n0_resolvability_coefficients_order_unity():
    f = ringdown_fisher(OMEGA_R, OMEGA_I)
    assert abs(f["Q"] - 2.10) < 0.01
    # both O(1), consistent with the published BCW ringdown Fisher analysis
    assert 0.3 < f["R_f"] < 1.0
    assert 1.0 < f["R_tau"] < 4.0


def test_R_f_is_function_of_Q_only():
    # scale-invariance: same Q (rescale omega and 1/tau together) -> identical coefficients
    a = ringdown_fisher(OMEGA_R, OMEGA_I)
    b = ringdown_fisher(3 * OMEGA_R, 3 * OMEGA_I)
    assert abs(a["R_f"] - b["R_f"]) < 1e-3
    assert abs(a["R_tau"] - b["R_tau"]) < 1e-3


def test_critical_snr_scales_inverse_with_delta():
    R_f = ringdown_fisher(OMEGA_R, OMEGA_I)["R_f"]
    assert abs(critical_snr(0.01, R_f) - 2 * critical_snr(0.02, R_f)) < 1e-9
    assert critical_snr(0.1, R_f, n_sigma=5.0) > 0


def test_run_validates_and_reports_reach():
    res = run()
    assert res["Q_scale_invariance_validated"] is True
    a = res["r4_isospectrality_application"]
    # axial R4 fractional shift per eta_2 ~ 8.5; reach tightens with SNR
    assert abs(a["axial_R4_delta_f_per_eta2"] - 8.52) < 0.1
    reach = a["eta2_reach_5sigma"]
    assert reach["rho=8"] > reach["rho=30"] > reach["rho=100"]


def test_honest_scope_and_negatives_preserved():
    res = run()
    sc = res["honest_scope"].lower()
    assert "white noise" in sc and "single mode" in sc
    assert "g_R4_c3" in res["honest_scope"]
    assert "un-sourceable" in sc or "polar" in sc
