"""Tests for the anomaly de-toying capstone (v2.414)."""

from experiments.qnm_anomaly_detoy import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_sources_gravity_is_rigorous():
    f = _RES["gR2_floor_given_matter"]
    assert f["rigorous_plus_implied_core"] > 0.05           # rigorous core forces g_R2 > 0 given matter
    assert f["anomaly_moves_floor_x"] < 1.15                # the toy anomaly barely moves the floor


def test_low_gR2_excluded_by_cross_sector_positivity():
    ex = _RES["rigorous_excluders_of_low_gR2"]
    assert "cross_sector_efthedron" in ex
    assert "graviton_forward_positivity" in ex


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "matter-sources-gravity is rigorous" in f
    assert "toy artifact" in f
    assert "parity" in f and "residual" in f
    sc = _RES["honest_scope"].lower()
    assert "single matter-fixed ray" in sc or "on that ray" in sc
    assert "did not remove" in sc or "removable-in-principle" in sc
    assert "physics judgement" in sc or "physics-judgement" in sc
