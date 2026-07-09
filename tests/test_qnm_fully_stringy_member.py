"""Tests for the nearly-fully-stringy member (v2.481)."""

from experiments.qnm_fully_stringy_member import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_exact_curvature_close():
    assert _RES["matter_mismatch"] < 1e-4
    assert _RES["curvature_mismatch"] < 0.02
    assert _RES["feasible_margin"] > -1e-3
    # curvature g_R3/g_R2 capped below the 0.90 target
    assert _RES["curvature_ratios"][0] < 0.90


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "nearly-fully-stringy" in f
    assert "both" in f and "exactly" in f
    sc = _RES["honest_scope"].lower()
    assert "existence, not uniqueness" in sc or "existence-not-uniqueness" in sc
    assert "closed" in sc and ("virasoro" in sc or "wrong target" in sc)
    assert "overstate" in sc or "not a genuine string-inconsistency" in sc or "not a real obstruction" in sc
