"""Tests for the g_R4 (Riemann^4) axis scoping (v2.234)."""

from experiments.qnm_gr4_axis_scoping import forced_gr4_min, gr4_constraint_spec, run


def test_gr4_constraint_types_present():
    spec = {s["name"] for s in gr4_constraint_spec()}
    # the curvature dispersion tower + positivity are the load-bearing ones
    assert "curvature_dispersion_tower" in spec
    assert "gr4_positivity" in spec


def test_positivity_forces_minimum_gr4():
    rows = {r["framework"]: r for r in forced_gr4_min()}
    # frameworks with curvature corrections are forced to carry a nonzero Riemann^4
    assert rows["string_tree_eft"]["ringdown_operator_mandated"] is True
    assert abs(rows["string_tree_eft"]["g_R4_min_forced"] - 0.1125) < 1e-4
    # pure GR (no curvature couplings) is not forced
    assert rows["pure_gr"]["ringdown_operator_mandated"] is False


def test_count_mandated():
    res = run()
    assert res["n_frameworks_mandating_gr4"] == 4


def test_read_only_and_honest_scope():
    res = run()
    sc = res["honest_scope"].lower()
    assert "read-only" in sc
    assert "does not modify the committed" in sc
    assert "un-sourceable" in sc
    assert "g_R4_c3" in res["honest_scope"]
