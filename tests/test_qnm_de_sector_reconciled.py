"""Tests for the dark-energy-sector self-correction (v2.457)."""

from experiments.qnm_de_sector_reconciled import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_r2_inflaton_negligible_today():
    assert _RES["r2_correction_relative_today"] < 1e-50
    assert _RES["inflaton_to_de_scale_ratio"] > 1e20


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "over-unification" in f
    assert "bounds" in f and "does not be" in f
    assert "over-determination" in f and ("weaker" in f or "tempered" in f or "not one dynamical field" in f)
    assert "stand for their own sectors" in f  # individual predictions still hold
    sc = _RES["honest_scope"].lower()
    assert "physics-reasoning" in sc or "not a new engine computation" in sc
    assert "tempers" in sc and "not refute" in sc or "does not refute" in sc
    assert "conjecture-tier" in sc
