"""Tests for the rigorous-core prefactor-robustness audit (v2.427)."""

from experiments.qnm_rigorous_prefactor_audit import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_lqg_exclusion_alpha_independent():
    tab = _RES["alpha_table"]
    # excluded at every alpha
    assert all(tab[a]["lqg_excluded"] for a in tab)
    # at low alpha, cross_sector drops out of the kill-set yet LQG stays excluded
    assert tab["0.5"]["cross_sector_in_lqg_killset"] is False
    assert tab["0.5"]["lqg_excluded"] is True


def test_matter_floor_stable_to_tighter():
    tab = _RES["alpha_table"]
    assert tab["0.5"]["gR2_floor"] > 0.05
    assert tab["1.1"]["gR2_floor"] <= tab["2.0"]["gR2_floor"]   # floor only tightens with alpha


def test_candidate_O1_robust():
    tab = _RES["alpha_table"]
    assert tab["1.1"]["candidate_feasible"] is True
    assert tab["2.0"]["candidate_feasible"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "alpha-independent" in f
    assert "source-exact in form" in f
    sc = _RES["honest_scope"].lower()
    assert "one simplified prefactor" in sc or "one prefactor" in sc
    assert "not an exhaustive" in sc or "load-bearing" in sc
