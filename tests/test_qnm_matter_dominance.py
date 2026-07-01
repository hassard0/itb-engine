"""Tests for the matter-dominance cross-sector-principle swing (v2.389)."""

from experiments.qnm_matter_dominance import run

_RES = run(n_walk=8000, seed=0)   # smaller; the ceilings + scaling are structural


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_ceilings_hold():
    for k, v in _RES["ceiling_relations_hold"].items():
        assert v is True, k


def test_ceilings_scale_with_matter():
    for coupling, c in _RES["ceiling_matter_correlations"].items():
        assert c > 0.6, coupling


def test_total_gravity_tracks_matter():
    assert _RES["total_gravitational_vs_matter_correlation"] > 0.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "matter dominance" in f
    assert "no intrinsic scale" in f
    assert "weakest force" in f
    sc = _RES["honest_scope"].lower()
    assert "not every gravitational bound is matter-controlled" in sc or "intra-sector" in sc or "intra-gravitational" in sc
    assert "toy" in sc
