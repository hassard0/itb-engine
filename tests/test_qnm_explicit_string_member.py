"""Tests for the explicit string-spectrum member (v2.480)."""

from experiments.qnm_explicit_string_member import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_superstring_member_exists_feasible():
    m = _RES["members"]["superstring"]
    assert m["mismatch"] < 1e-3
    assert m["feasible_margin"] > -1e-3
    # ratios match the zeta(k+1) targets
    for r, t in zip(m["ratios"], m["target_ratios"]):
        assert abs(r - t) < 5e-3


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "string-realizable" in f
    assert "explicit" in f and "feasible" in f
    assert "zeta(k+1)" in f
    sc = _RES["honest_scope"].lower()
    assert "existence, not uniqueness" in sc or "existence-not-uniqueness" in sc
    assert "ratio" in sc
    assert "admits" in sc or "not 'consistency selects" in sc or "not select" in sc
