"""Tests for the method-as-proposal / carved g_R4 prediction (v2.297)."""

from experiments.qnm_method_as_proposal import carved_gR4_range, gr4_substack, run
from experiments.stack import frameworks


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_admitted_frameworks_get_finite_bands():
    res = run()
    assert set(res["admitted"]) == {"string_tree_eft", "asymptotic_safety", "cdt"}
    for r in res["framework_gR4_bands"]:
        if r["framework"] in res["admitted"]:
            assert r["band_width"] is not None and r["band_width"] > 0


def test_band_floor_is_the_mandate():
    res = run()
    for r in res["framework_gR4_bands"]:
        if r.get("has_curvature") and r["g_R4_carved_min"] is not None:
            assert abs(r["g_R4_carved_min"] - r["g_R4_floor_mandate"]) < 0.01


def test_carving_rejects_lqg():
    res = run()
    assert res["rejected"] == ["lqg_induced"]
    lqg = next(r for r in res["framework_gR4_bands"] if r["framework"] == "lqg_induced")
    assert lqg["g_R4_carved_min"] is None      # empty band -> rejected


def test_carved_range_direct():
    # string gets a finite band, lqg does not
    st = gr4_substack()
    fw = {f.name: dict(f.encode().coefficients) for f in frameworks()}
    lo, hi = carved_gR4_range(fw["string_tree_eft"], st)
    assert lo is not None and hi is not None and hi > lo
    assert carved_gR4_range(fw["lqg_induced"], st) == (None, None)


def test_honest_scope_flags_o1_and_dark_parity():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not the full 38-constraint" in sc
    assert "dark-parity" in sc or "parity-odd" in sc
    assert "methodological proposal, not a theorem" in sc
