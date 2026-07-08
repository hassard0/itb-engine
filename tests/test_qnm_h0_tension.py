"""Tests for the H0-tension confrontation (v2.467)."""

from experiments.qnm_h0_tension import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_candidate_does_not_resolve_h0():
    assert _RES["candidate_resolves_H0"] is False
    m = _RES["resolution_mechanisms"]
    assert m["phantom_late_DE_w_lt_minus1"]["resolves_H0"] and not m["phantom_late_DE_w_lt_minus1"]["candidate_can"]
    assert m["early_dark_energy"]["resolves_H0"] and not m["early_dark_energy"]["candidate_can"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "does not resolve the h0 tension" in f or "does not resolve the hubble tension" in f
    assert "canonical" in f and "w >= -1" in f
    assert "axiverse" in f
    sc = _RES["honest_scope"].lower()
    assert "not an engine computation" in sc or "physics-reasoning" in sc
    assert "not predicted" in sc          # axiverse available not predicted
    assert "not an independent test" in sc or "not independent" in sc or "reinforces" in sc
