"""Tests for the cross-sector moment principle (v2.293)."""

from experiments.qnm_cross_sector_moment_principle import (
    cross_sector_ratios,
    passes_curvature_tower,
    passes_matter_tower,
    relative_spread,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_real_frameworks_in_tight_band():
    res = run()
    for r in res["framework_cross_sector"]:
        if r.get("has_both_sectors"):
            assert r["relative_spread"] < res["band_threshold"]
            assert r["monotone"] is True


def test_decoupled_passes_both_towers_but_fails_cross_sector():
    # the headline: a point both separate moment towers accept, the cross-sector principle rejects
    res = run()
    d = res["decoupled_counterexample"]
    assert d["passes_matter_tower"] is True
    assert d["passes_curvature_tower"] is True
    assert d["relative_spread"] > res["band_threshold"]
    assert res["consistency_checks"]["cross_sector_is_strictly_stronger"] is True


def test_ratio_and_spread_helpers():
    r = cross_sector_ratios(0.5, 0.4, 0.4, 0.2, 0.15, 0.1125)
    assert abs(r[0] - 0.4) < 1e-9 and abs(r[2] - 0.28125) < 1e-9
    assert relative_spread([0.4, 0.4, 0.4]) == 0.0          # identical ratios -> perfectly consistent
    assert relative_spread([0.4, 0.4, 5.0]) > 1.0           # wild ratio -> large spread


def test_tower_predicates():
    assert passes_matter_tower(0.5, 0.4, 0.4) is True       # 0.16 <= 0.20
    assert passes_curvature_tower(0.2, 0.15, 2.0) is True   # 0.0225 <= 0.40
    assert passes_matter_tower(0.1, 0.9, 0.1) is False


def test_honest_scope_flags_novel_unproven():
    res = run()
    sc = res["honest_scope"].lower()
    assert "novel, unproven" in sc
    assert "hypothesis" in sc
    assert "calibrated" in sc
    assert "not 'proven bound'" in sc
