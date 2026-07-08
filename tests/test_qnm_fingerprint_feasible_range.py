"""Tests for the fingerprint feasible-range capstone (v2.478)."""

from experiments.qnm_fingerprint_feasible_range import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_range_wide_and_contains_strings():
    lo, hi = _RES["feasible_double_ratio_range"]
    assert abs(lo - 1.0) < 0.02          # tower floor
    assert hi > 3.0                       # wide
    # string values within the range
    for v in _RES["string_values"].values():
        assert lo - 1e-6 <= v <= hi
    assert lo - 1e-6 <= _RES["constructed_point"] <= hi


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "not sharply predict" in f or "does not sharply predict" in f
    assert "consistent" in f
    assert "over-read" in f
    assert "supersedes" in f
    sc = _RES["honest_scope"].lower()
    assert "deflation" in sc
    assert "consistency, not prediction" in sc or "consistency not prediction" in sc
    assert "diagnostic" in sc
