"""Tests for the two-tower scale comparison swing (v2.376)."""

from experiments.qnm_two_tower_scales import run

_RES = run(n_walk=10000, seed=0)   # smaller walk; the ordering/robustness verdict is stable


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_curvature_faster_at_center():
    assert _RES["constructed_r_curv_gR3_over_gR2"] < _RES["constructed_r_matter_g6_over_g4"]


def test_attack_survives_across_family():
    # curvature faster-decaying in the large majority of the family -> not a g6=g8 artifact
    assert _RES["curvature_faster_decaying_fraction"] > 0.8


def test_matter_tower_slower_on_average():
    assert _RES["family_r_matter"]["mean"] > _RES["family_r_curv"]["mean"]
    assert _RES["scale_separation_ratio_of_ratios"]["mean"] < 1.0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "both sectors" in f or "both" in f
    assert "string-like" in f
    assert "harder" in f
    assert "artifact" in f
    sc = _RES["honest_scope"].lower()
    assert "log-convex" in sc
    assert "toy basis" in sc
    assert "ordering" in sc
