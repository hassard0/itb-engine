"""Tests for the hierarchical curvature-tower carving (v2.303)."""

import math

from experiments.qnm_curvature_tower_hierarchical_carving import cemz_bound, cubic_bound, run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_cemz_geometric_mean_form():
    # |g_R3| <= 0.8 sqrt(g_4 g_R2)
    assert abs(cemz_bound(0.5, 0.2) - 0.8 * math.sqrt(0.1)) < 1e-9
    # cubic positivity g_R3 <= g_4^2
    assert abs(cubic_bound(0.5) - 0.25) < 1e-9


def test_causality_vs_unitarity_split():
    res = run()
    assert set(res["causality_bound_frameworks"]) == {"lqg_induced", "cdt"}
    assert set(res["unitarity_bound_frameworks"]) == {"string_tree_eft", "asymptotic_safety"}


def test_all_frameworks_satisfy_both_cubic_bounds():
    res = run()
    for r in res["framework_cubic_bounds"]:
        assert r["g_R3"] <= min(r["cemz_bound"], r["cubic_bound"]) + 1e-9
        assert r["g_R3_satisfies_both"] is True


def test_crossover_at_gR2_equals_g4_cubed_over_kappa_sq():
    # CEMZ tighter than cubic when g_R2 < g_4^3 / kappa_cemz^2
    res = run()
    for r in res["framework_cubic_bounds"]:
        if r["g_R2"] < r["crossover_gR2"]:
            assert r["cemz_bound"] < r["cubic_bound"]    # causality binds
        else:
            assert r["cemz_bound"] >= r["cubic_bound"]   # unitarity binds


def test_hierarchy_three_distinct_principles():
    res = run()
    h = res["hierarchical_carving"]
    assert len(h) == 3
    assert "four principles" in h["g_R2_Ricci2"].lower()
    assert "causality" in h["g_R3_Ricci3"].lower()
    assert "moment tower" in h["g_R4_Riemann4"].lower()


def test_honest_scope_flags_structural_robust():
    res = run()
    sc = res["honest_scope"].lower()
    assert "prefactor-robust" in sc
    assert "required higher-spin tower" in sc
    assert "organizing statement, not a new bound" in sc
