"""Tests for the correlated make-or-break signature (v2.429)."""

from experiments.qnm_correlated_signature import run

_RES = run(n_walk=12000)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_three_fronts_required():
    assert all(_RES["all_three_required_nonzero"].values())
    for band in _RES["feasible_bands"].values():
        assert band[0] > 0.02   # each driver strictly positive


def test_fronts_positively_correlated():
    for r in _RES["front_correlations"].values():
        assert r > 0.15


def test_no_front_dispensable():
    # turning any single front off is infeasible with the rest at candidate values
    assert not any(_RES["conjunction_test_each_front_off_is_feasible"].values())


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "correlated" in f and "conjunction" in f
    assert "empirical solve" in f
    sc = _RES["honest_scope"].lower()
    assert "coupling" in sc
    assert "toy" in sc
    assert "birefringence" in sc
