"""Tests for the helicity-resolved curvature moment tower (v2.298)."""

from experiments.qnm_helicity_resolved_tower import helicity_floors, run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_parity_conserving_reduces_to_v292():
    # g_*_parity = 0 -> both helicity floors equal g_R3^2/g_R2, g_R4_parity = 0
    f = helicity_floors(0.2, 0.15, 0.0, 0.0)
    assert abs(f["floor_L"] - f["floor_R"]) < 1e-12
    assert abs(f["g_R4_parity_forced"]) < 1e-12
    assert abs(f["g_R4_forced"] - 0.15**2 / 0.2) < 1e-12


def test_parity_violating_forces_nonzero_g_R4_parity():
    # lqg's parity couplings force a nonzero parity-odd quartic
    f = helicity_floors(0.3, 0.3, 0.08, 0.04)
    assert f["floor_L"] != f["floor_R"]
    assert abs(f["g_R4_parity_forced"]) > 1e-9
    # cross-check: g_R4 = (L+R)/2, g_R4_p = (L-R)/2
    assert abs(f["g_R4_forced"] - 0.5 * (f["floor_L"] + f["floor_R"])) < 1e-12
    assert abs(f["g_R4_parity_forced"] - 0.5 * (f["floor_L"] - f["floor_R"])) < 1e-12


def test_only_lqg_parity_violating_and_splits():
    res = run()
    pv = [r for r in res["framework_helicity"] if r.get("has_curvature") and r["parity_violating"]]
    assert [r["framework"] for r in pv] == ["lqg_induced"]
    assert pv[0]["ringdown_splits"] is True
    assert abs(pv[0]["g_R4_parity_forced"]) > 1e-9


def test_parity_conserving_frameworks_no_split():
    res = run()
    for r in res["framework_helicity"]:
        if r.get("has_curvature") and not r["parity_violating"]:
            assert r["ringdown_splits"] is False
            assert abs(r["g_R4_parity_forced"]) < 1e-9


def test_honest_scope_flags_floor_not_full_determination():
    res = run()
    sc = res["honest_scope"].lower()
    assert "mandate floor" in sc
    assert "does not resolve the v2.209 sourcing gap" in sc
    assert "structural" in sc
