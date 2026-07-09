"""Tests for the curvature-gap physics (v2.482)."""

from experiments.qnm_curvature_gap_physics import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_cap_is_rigorous_graviton_positivity():
    cap = _RES["capping_constraint"]
    assert cap["name"] == "graviton_forward_positivity"
    assert cap["rigor"] == "rigorous"
    assert _RES["nearly_fully_stringy_point_gR3_over_gR2"] < 0.90


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "graviton_forward_positivity" in f
    assert "more gapped" in f
    assert "closed-string" in f
    assert "not a string-tension" in f or "not a string-tension" in f or "feature" in f
    sc = _RES["honest_scope"].lower()
    assert "rigorous" in sc
    assert "not proven" in sc or "plausible" in sc
    assert "point-specific" in sc or "this point" in sc or "this particular" in sc or "this configuration" in sc or "0.833 is the value at this" in sc or "value at this point" in sc
