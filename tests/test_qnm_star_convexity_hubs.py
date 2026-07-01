"""Tests for the star-convexity hub swing (v2.384)."""

from experiments.qnm_star_convexity_hubs import run

_RES = run(n_walk=8000, n_hubs=20, n_lines=1500, seed=0)   # smaller; the ordering is stable


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_good_hub_not_special():
    assert _RES["constructed_star_fraction"] > 0.9
    # constructed within noise of the safe-hub mean -> not uniquely central
    assert abs(_RES["constructed_star_fraction"] - _RES["safe_hub_mean_star_fraction"]) < 0.05


def test_star_centrality_tracks_min_coupling():
    assert _RES["corr_minCoupling_vs_starFrac"] > 0.3


def test_no_perfect_star_center():
    assert _RES["constructed_star_fraction"] < 0.999
    assert _RES["safe_hub_mean_star_fraction"] < 0.999


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "hierarchy-safety" in f
    assert "not by chebyshev" in f or "not by being the max-margin" in f or "fails honestly" in f
    assert "perfect star-center" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "v2.383" in sc
