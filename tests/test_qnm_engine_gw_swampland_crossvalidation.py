"""Tests for the engine GW + swampland cross-validation (v2.281)."""

from experiments.qnm_engine_gw_swampland_crossvalidation import (
    GW_SWAMPLAND_SECTOR,
    run,
    species_scale_form_matches_v264,
)
from itb.constraints.gw_speed import CGW_BOUND


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_species_scale_form_matches_v264():
    # engine Lambda = M_Pl/N^{1/(d-2)} -> d=4 -> M_Pl/sqrt(N), the v2.264 derivation
    assert species_scale_form_matches_v264() is True


def test_engine_gw_speed_bound_is_source_value():
    assert abs(CGW_BOUND - 5e-16) < 1e-18


def test_four_frameworks_pass_and_lqg_fails_forward_positivity():
    res = run()
    assert len(res["frameworks_passing_full_sector"]) == 4
    assert "lqg_induced" in res["frameworks_failing_sector"]
    # the specific constraint lqg fails is the forward-limit graviton positivity (the v2.262 physics)
    assert "graviton_forward_positivity" in res["frameworks_failing_sector"]["lqg_induced"]
    for fw in ("pure_gr", "string_tree_eft", "asymptotic_safety", "cdt"):
        assert fw in res["frameworks_passing_full_sector"]


def test_cross_validation_table_all_agree():
    res = run()
    assert all(c["agrees"] for c in res["cross_validation"])
    physics = {c["physics"] for c in res["cross_validation"]}
    assert "species scale" in physics and "graviton mass" in physics


def test_sector_constraints_resolve_in_engine():
    # the named sector constraints actually exist in the engine results (no silent name typos)
    res = run()
    seen = set()
    for r in res["framework_sector_results"]:
        seen.update(r["sector"].keys())
    # at least the core reconstructed-physics constraints are present
    for name in ("species_scale_bound", "gw_speed_bound", "ligo_graviton_mass_bound",
                 "graviton_forward_positivity"):
        assert name in seen and name in GW_SWAMPLAND_SECTOR


def test_honest_scope_flags_consistency_not_new_constraint():
    res = run()
    sc = res["honest_scope"].lower()
    assert "does not add a new constraint" in sc or "not add a new constraint" in sc
    assert "engine's own verdict" in sc
    assert "v2.262" in res["honest_scope"]
