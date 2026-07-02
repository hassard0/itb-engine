"""Tests for the 2030 verdict table (v2.430)."""

from experiments.qnm_verdict_table import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_engine_anchors():
    a = _RES["engine_anchors"]
    assert a["candidate_feasible"]
    assert a["parity_off_infeasible"]
    assert a["weak_matter_infeasible"]
    assert a["parity_conserving_rival_feasible_if_beta0"]


def test_candidate_confirmed_by_one_pattern():
    assert _RES["candidate_confirmed_patterns"] == 1
    assert _RES["total_patterns"] == 8
    assert _RES["non_confirming_patterns"] >= 5


def test_rivals_distinct_and_correlation_breakers_kill():
    table = _RES["verdict_table"]
    # beta=0 + matter + dark energy -> parity-conserving rival
    rival = [r for r in table if r["parity"] == 0 and r["matter"] == 1 and r["dark_energy"] == 1][0]
    assert "RIVAL" in rival["verdict"]
    # parity without matter -> candidate killed
    breaker = [r for r in table if r["parity"] == 1 and r["matter"] == 0 and r["dark_energy"] == 1][0]
    assert "killed" in breaker["verdict"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "maximally falsifiable" in f
    assert "one of eight" in f or "1/8" in f or "exactly one" in f
    sc = _RES["honest_scope"].lower()
    assert "not a likelihood" in sc or "decision-support" in sc or "not-bayes" in sc or "decision-map" in sc
    assert "coarse" in sc
