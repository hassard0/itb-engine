"""Tests for the superradiant Regge-plane exclusion (v2.244)."""

from experiments.qnm_superradiance_regge_exclusion import (
    M_gamma,
    excluded_alpha_window,
    omega_h,
    run,
)


def test_growth_positive_only_when_superradiant():
    a = 0.9
    om = omega_h(a)
    # unstable (Gamma>0) below threshold, stable (<=0) above
    assert M_gamma(0.5 * om, a) > 0
    assert M_gamma(1.1 * om, a) <= 0


def test_excluded_window_bounded_by_threshold():
    a, M, age = 0.9, 10.0, 1e9
    win = excluded_alpha_window(a, M, age)
    assert win is not None
    # the upper edge is below the superradiance threshold
    assert win[1] < omega_h(a) + 1e-6
    assert win[0] < win[1]


def test_exclusion_spans_ultralight_masses():
    res = run()
    mus = [m for r in res["regge_exclusion"] if r["excluded_alpha"] for m in r["excluded_mu_eV"]]
    assert max(mus) > 1e-13 and min(mus) < 1e-20


def test_heavier_holes_probe_lighter_bosons():
    res = run()
    stellar = next(r for r in res["regge_exclusion"] if "stellar" in r["label"])["excluded_mu_eV"][1]
    m87 = next(r for r in res["regge_exclusion"] if "M87" in r["label"])["excluded_mu_eV"][1]
    # the supermassive window is far below the stellar window
    assert m87 < stellar


def test_honest_scope_representative_rates():
    res = run()
    sc = res["honest_scope"].lower()
    assert "representative" in sc and "alpha^8" in sc
    assert "g_R4_c3" in res["honest_scope"]
