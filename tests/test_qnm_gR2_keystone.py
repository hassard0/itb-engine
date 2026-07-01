"""Tests for the g_R2 keystone swing (v2.396)."""

from experiments.qnm_gR2_keystone import run

_RES = run(n_walk=7000, seed=0)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_eight_roles_all_consistent():
    assert _RES["n_roles"] == 8
    for k, v in _RES["gR2_roles"].items():
        assert v is True, k


def test_a_theorem_implied_by_anomaly():
    assert _RES["gR2_min_region"] > 0.0     # anomaly-forced g_R2>0 region-wide
    assert _RES["delta_a_estimate"] > 0.0   # Delta_a >= 0 automatic


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "keystone" in f
    assert "a-theorem is implied by the gravitational anomaly" in f or "automatically guarantees rg-flow monotonicity" in f
    assert "eight distinct consistency roles" in f
    sc = _RES["honest_scope"].lower()
    assert "toy-basis artifact" in sc
    assert "finer basis" in sc
    assert "heuristic" in sc
