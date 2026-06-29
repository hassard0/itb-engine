"""Tests for the forced per-framework higher-curvature tower (v2.262)."""

import numpy as np

from experiments.qnm_framework_curvature_tower import hankel, run


def test_every_curvature_framework_has_geometric_tower():
    res = run()
    rows = [r for r in res["framework_towers"] if r.get("has_curvature")]
    assert len(rows) >= 3
    for r in rows:
        x = r["effective_state_x"]
        t = r["minimal_tower"]
        # g_R(k+2) = g_R2 x^k : geometric with ratio x
        assert abs(t["g_R4"] - r["g_R2"] * x**2) < 1e-12
        assert abs(t["g_R5"] - r["g_R2"] * x**3) < 1e-12
        assert abs(t["g_R6"] - r["g_R2"] * x**4) < 1e-12


def test_g_r4_min_reproduces_v234_bound():
    res = run()
    for r in res["framework_towers"]:
        if r.get("has_curvature"):
            assert r["g_R4_min_matches_v234"] is True
            assert abs(r["minimal_tower"]["g_R4"] - r["g_R3"] ** 2 / r["g_R2"]) < 1e-12


def test_minimal_tower_saturates_2x2_hankel():
    # the single-effective-state tower sits exactly on the boundary: det of the 2x2 Hankel ~ 0
    res = run()
    for r in res["framework_towers"]:
        if r.get("has_curvature"):
            assert abs(r["hankel_2x2_det"]) < 1e-12
            t = r["minimal_tower"]
            H = hankel([r["g_R2"], r["g_R3"], t["g_R4"]], 1)
            assert abs(float(np.linalg.det(H))) < 1e-12


def test_lqg_is_the_marginal_framework():
    res = run()
    assert res["marginal_frameworks"] == ["lqg_induced"]
    for r in res["framework_towers"]:
        if r.get("framework") == "lqg_induced":
            assert abs(r["effective_state_x"] - 1.0) < 1e-12
            assert r["tower_regime"].startswith("marginal")
        elif r.get("has_curvature"):
            assert r["effective_state_x"] < 1.0
            assert r["tower_regime"].startswith("converging")


def test_honest_scope_flags_minimal_floor_and_representative():
    res = run()
    sc = res["honest_scope"].lower()
    assert "minimal" in sc and "lower envelope" in sc
    assert "representative" in sc
    assert "g_R4_c3" in res["honest_scope"]
