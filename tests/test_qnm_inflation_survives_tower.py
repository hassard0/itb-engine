"""Tests for the inflation-survives-tower cycle (v2.441)."""

from experiments.qnm_inflation_survives_tower import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_ns_r_in_windows():
    assert abs(_RES["n_s"] - 0.9649) < 0.006
    assert 0.001 < _RES["r"] < 0.01


def test_tower_stays_above_H_both_branches():
    for label, b in _RES["branches"].items():
        assert b["tower_stays_above_H"] is True, label
        assert b["tower_over_H_at_end"] > 10, label
        assert b["field_range_margin"] > 1.5, label


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "survives its own swampland tower" in f
    assert "fourth" in f
    assert "litebird" in f
    sc = _RES["honest_scope"].lower()
    assert "conjecture" in sc
    assert "plateau class" in sc or "plateau-class" in sc  # not uniquely the candidate
    assert "order-of-magnitude" in sc
