"""Tests for the repulsive-force-conjecture edge anatomy (v2.284)."""

from experiments.qnm_repulsive_force_edge import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_decomposition_matches_engine_margin():
    res = run()
    for r in res["framework_anatomy"]:
        assert r["matches_engine"] is True
        # margin = matter - linear - quadratic
        assert abs(r["rfc_margin"] - (r["matter_product"] - r["curv_linear_WGC"]
                                      - r["curv_quadratic_RFC"])) < 1e-12


def test_string_and_cdt_sit_on_linear_wgc_boundary():
    res = run()
    assert set(res["on_linear_wgc_boundary"]) == {"string_tree_eft", "cdt"}
    for name in ("string_tree_eft", "cdt"):
        r = next(x for x in res["framework_anatomy"] if x["framework"] == name)
        assert abs(r["linear_wgc_margin"]) < 1e-9     # exactly on the WGC line
        assert r["rfc_margin"] < 0                     # but the quadratic RFC term tips it over


def test_as_and_lqg_below_linear_wgc():
    res = run()
    assert set(res["below_linear_wgc"]) == {"asymptotic_safety", "lqg_induced"}
    for name in ("asymptotic_safety", "lqg_induced"):
        r = next(x for x in res["framework_anatomy"] if x["framework"] == name)
        assert r["linear_wgc_margin"] < 0              # below even the original WGC


def test_pure_gr_trivially_saturates():
    res = run()
    pg = next(x for x in res["framework_anatomy"] if x["framework"] == "pure_gr")
    assert abs(pg["rfc_margin"]) < 1e-12


def test_honest_scope_flags_encoding_not_physics():
    res = run()
    sc = res["honest_scope"].lower()
    assert "encoding" in sc
    assert "not a claim that string theory saturates the physical wgc" in sc
    assert "not a new constraint" in sc
