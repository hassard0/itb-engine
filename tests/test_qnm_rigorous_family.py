"""Tests for the rigorous-family geometry cycle (v2.419)."""

from experiments.qnm_rigorous_family import run

_RES = run(n_walk=15000)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_rigorous_family_is_looser():
    assert _RES["spread_geomean_stddev"]["looser_x"] > 3.0


def test_rigor_does_not_force_candidate_features():
    rc = _RES["rigorous_core_ranges"]
    assert rc["g_R2"][0] < 0.02          # rigor allows zero curvature
    assert rc["g_R2_parity"][0] < 0.02   # rigor allows zero parity
    ff = _RES["full_stack_ranges"]
    assert ff["g_R2"][0] > 0.02          # data forces nonzero curvature
    assert ff["g_R2_parity"][0] > 0.02   # data forces nonzero parity


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "family" in f and "not the candidate" in f
    assert "rigor determines the rules" in f
    sc = _RES["honest_scope"].lower()
    assert "honest complement" in sc or "not a weakening" in sc
    assert "walk" in sc
