"""Tests for the ringdown<->engine operator-sector bridge (v2.233)."""

from experiments.qnm_engine_operator_sector_bridge import (
    curvature_invariants,
    run,
    tidal_components,
)


def test_kretschmann_matches_closed_form():
    for r in (3.0, 5.0, 10.0):
        ci = curvature_invariants(r)
        assert abs(ci["K_numeric"] - ci["K_closed_form"]) < 1e-12
        assert abs(ci["K_numeric"] - 48.0 / r**6) < 1e-12


def test_schwarzschild_is_ricci_flat():
    # the orthonormal tidal tensor is trace-free -> Ricci = 0 (vacuum)
    for r in (3.0, 5.0, 10.0):
        c = tidal_components(r)
        assert abs(c["R_0101"] + c["R_0202"] + c["R_0303"]) < 1e-12


def test_operator_sector_classification():
    res = run()
    sec = res["operator_sector_classification"]
    # Ricci-scalar operators (in the engine) are ringdown-blind on Schwarzschild
    assert sec["g_R2_R_squared"]["ringdown_active"] is False
    assert sec["g_R3_R_cubed"]["ringdown_active"] is False
    # the ringdown-active operator is Riemann^4 (dim-8), NOT in the engine basis
    assert sec["Riemann4_quartic_dim8_R4"]["ringdown_active"] is True
    assert sec["Riemann4_quartic_dim8_R4"]["in_engine_basis"] is False
    # g_8 is matter, not curvature
    assert sec["g_8_matter_s4_moment"]["ringdown_active"] is False


def test_all_checks_pass_and_scope_honest():
    res = run()
    assert res["all_K_match"] is True and res["all_ricci_flat"] is True
    sc = res["honest_scope"].lower()
    assert "structural clarification" in sc
    assert "un-sourceable" in sc
    assert "g_R4_c3" in res["honest_scope"]
