"""Tests for the bold heterotic UV-identification (v2.434)."""

from experiments.qnm_heterotic_identification import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_R2_required_given_R3_and_parity():
    # given the candidate's R3+parity, R2=0 is excluded by source-exact bounds
    assert _RES["consistency_checks"]["R2_rigorously_required_given_R3_and_parity"] is True


def test_type_II_is_distinct():
    assert len(_RES["type_II_R4only_full_stack_violations"]) > 0


def test_decision_is_heterotic():
    assert "HETEROTIC" in _RES["decision"].upper()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "heterotic" in f and "type ii" in f
    assert "axion" in f
    sc = _RES["honest_scope"].lower()
    assert "structural identification" in sc
    assert "not a heterotic compactification computation" in sc or "not a compactification" in sc
    assert "disfavored" in sc  # type II disfavored not excluded
