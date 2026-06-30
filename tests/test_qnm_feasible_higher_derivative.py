"""Tests for the feasible higher-derivative theory / curvature ceiling (v2.285)."""

from experiments.qnm_feasible_higher_derivative import WITNESS, candidate_for_gR2, run
from experiments.stack import build_stack
from itb.engine import check
from itb.theory import Theory


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_witness_is_feasible_with_nonzero_curvature():
    # the headline: a higher-derivative theory the engine accepts
    rep = check(Theory(coefficients=dict(WITNESS), name="w"), build_stack())
    assert rep.feasible is True
    assert WITNESS["g_R2"] > 0 and WITNESS["g_R3"] > 0


def test_curvature_ceiling_respects_analytic_bound():
    # the demonstrated ceiling is finite and below the hard anomaly-vs-repulsive bound 0.2
    res = run()
    assert res["curvature_ceiling"] is not None
    assert 0.0 < res["curvature_ceiling"] <= res["analytic_ceiling"] + 0.01


def test_above_ceiling_is_infeasible():
    # the analytic algebra forbids g_R2 > 0.2 for any completion -> our completion fails well before
    res = run()
    high = check(candidate_for_gR2(0.30), build_stack())
    assert high.feasible is False


def test_toy_frameworks_below_repulsive_floor():
    res = run()
    for t in res["toy_framework_matter_vs_floor"]:
        if t["framework"] != "pure_gr":
            assert t["above_floor"] is False
            assert t["matter_product"] < t["repulsive_floor"]


def test_honest_scope_flags_completion_family_and_hard_bound():
    res = run()
    sc = res["honest_scope"].lower()
    assert "hand-constructed" in sc
    assert "provably cannot exceed" in sc or "hard ceiling" in sc
    assert "not a validated physical lagrangian" in sc
