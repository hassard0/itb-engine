"""Tests for the end-to-end R4 detectability forecast (v2.228)."""

from experiments.qnm_r4_end_to_end_forecast import ell_scaling, gamma_reach, run


def test_gamma_reach_scales_inverse_snr_and_sqrtN():
    # doubling SNR or quadrupling N each halve the gamma reach (1/(rho sqrt N))
    base = gamma_reach(10, 1)
    assert abs(gamma_reach(20, 1) - base / 2) < 1e-9
    assert abs(gamma_reach(10, 4) - base / 2) < 1e-9


def test_ell_scaling_is_steep_p6():
    # ell ~ (rho sqrt N)^{-1/6}: a 64x effective-SNR gain only halves ell
    assert abs(ell_scaling(64, 1) / ell_scaling(1, 1) - 0.5) < 1e-6


def test_forecast_scenarios_monotone():
    res = run()
    rows = res["scenarios"]
    # deeper effective SNR -> smaller gamma reach
    by_snr = sorted(rows, key=lambda r: r["effective_snr"])
    reaches = [r["gamma_reach_5sigma"] for r in by_snr]
    assert all(reaches[i] > reaches[i + 1] for i in range(len(reaches) - 1))


def test_leaver_foundation_documented_not_overclaimed():
    res = run()
    lf = res["leaver_solver_foundation"].lower()
    assert "5-term" in lf
    assert "deferred" in lf or "foundation laid" in lf
    assert "g_R4_c3" in res["honest_scope"]
