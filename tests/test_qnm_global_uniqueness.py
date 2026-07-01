"""Tests for the global-uniqueness swing (v2.406)."""

from experiments.qnm_global_uniqueness import run

_RES = run(n_starts=24, n_steps=300, seed=1)   # fewer starts; single-island result is stable


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_most_starts_reach_and_cluster():
    assert _RES["n_reached_feasibility"] > 0.8 * _RES["n_starts"]
    assert _RES["endpoints_unimodal_single_island"] is True
    d = _RES["endpoint_distance_to_constructed"]
    assert d["max"] < 0.5                 # no distant second region


def test_single_handedness():
    assert _RES["all_positive_handedness"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "globally unique" in f
    assert "single connected feasible island" in f or "one island" in f
    assert "z2 mirror" in f
    sc = _RES["honest_scope"].lower()
    assert "heuristic" in sc
    assert "cannot prove" in sc or "not a theorem" in sc
    assert "box" in sc
