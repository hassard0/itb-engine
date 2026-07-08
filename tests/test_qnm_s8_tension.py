"""Tests for the S8-tension confrontation (v2.469)."""

from experiments.qnm_s8_tension import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_helps_s8_opposite_of_h0():
    assert _RES["candidate_helps_s8"] is True
    sc = _RES["mixed_scorecard"]
    assert sc["S8_tension"]["helps"] is True
    assert sc["H0_tension"]["helps"] is False


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "mixed" in f and "scorecard" in f
    assert "helps s8" in f or "help s8" in f
    assert "opposite sign" in f
    sc = _RES["honest_scope"].lower()
    assert "physics-reasoning" in sc or "not an engine" in sc
    assert "not a full resolution" in sc or "not a computed" in sc
    assert "direction" in sc and "magnitude" in sc   # direction robust, magnitude small
