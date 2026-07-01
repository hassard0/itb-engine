"""Tests for the predictivity-by-constraint-class decomposition (v2.374)."""

from experiments.qnm_predictivity_by_class import run

_RES = run(n_samples=12000, seed=1)   # smaller n for suite speed; the ranking is robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_information_is_least_carving():
    o = _RES["opened_by_dropping_class"]
    B = o["B_INFORMATION"]["n_feasible"]
    assert B <= o["A_AMPLITUDE"]["n_feasible"]
    assert B <= o["C_UNIVERSALITY"]["n_feasible"]


def test_universality_and_amplitude_dominate():
    o = _RES["opened_by_dropping_class"]
    base = max(_RES["baseline_n_feasible"], 1)
    assert o["C_UNIVERSALITY"]["n_feasible"] > 3 * base
    assert o["A_AMPLITUDE"]["n_feasible"] > 3 * base


def test_ranking_present():
    r = _RES["ranking_biggest_to_smallest_carver"]
    assert len(r) == 3
    assert r[-1] == "B_INFORMATION"     # holography is the smallest carver


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "swampland" in f and "positivity" in f
    assert "holographic" in f or "information" in f
    assert "unitarity" in f
    sc = _RES["honest_scope"].lower()
    assert "ranking" in sc
    assert "toy basis" in sc
    assert "box-dependent" in sc
