"""Tests for the moment-tower enforcement audit (v2.479)."""

from experiments.qnm_moment_tower_enforcement_audit import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_high_rung_not_enforced_witness():
    # explicit feasible point with matter-high ratio < 1
    assert _RES["g10_0p05_feasible"] is True
    assert _RES["matter_high_ratio_at_g10_0p05"] < 1.0
    assert _RES["stack_has_low_rung"] is True
    assert _RES["stack_has_high_rung_constraint"] is False


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "first rung" in f
    assert "v2.375" in f and "overstated" in f
    assert "v2.478" in f and "stands" in f
    sc = _RES["honest_scope"].lower()
    assert "witness" in sc
    assert "nuance" in sc and "not a refutation" in sc
