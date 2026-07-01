"""Tests for the c-a modulus swing (v2.399)."""

from experiments.qnm_c_minus_a_modulus import run

_RES = run(n_walk=9000, seed=0)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_ac_spans_wedge_and_a_eq_c_interior():
    ac = _RES["feasible_a_over_c"]
    wedge = _RES["HM_wedge"]
    assert abs(ac["min"] - wedge[0]) < 0.03
    assert abs(ac["max"] - wedge[1]) < 0.07
    assert ac["min"] < 1.0 < ac["max"]     # a=c interior


def test_c_minus_a_is_free_modulus():
    ac = _RES["feasible_a_over_c"]
    assert ac["max"] / ac["min"] > 3.0     # a/c ranges over the full wedge


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "assumption, not a consistency prediction" in f or "a=c is an assumption" in f
    assert "free modulus" in f
    assert "v2.392" in f            # sibling of g_6=g_8
    sc = _RES["honest_scope"].lower()
    assert "measure-dependent" in sc
    assert "not robustly 'prefer c>a'" in sc or "parametrization artifact" in sc
