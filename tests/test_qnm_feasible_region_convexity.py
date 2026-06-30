"""Tests for the feasible-region convexity structural test (v2.304)."""

from experiments.qnm_feasible_region_convexity import run, avg, feasible
from itb.constraints.swampland_variants import RepulsiveForceConjecture


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_endpoints_feasible_midpoint_infeasible():
    res = run()
    t = res["repulsive_force_test"]
    assert t["A_margin"] >= 0.0       # A satisfies the bound
    assert t["B_margin"] >= 0.0       # B satisfies the bound
    assert t["midpoint_margin"] < 0.0  # the average does NOT
    assert t["non_convex"] is True


def test_counterexample_reproducible_against_engine():
    # rebuild the counterexample independently against the real constraint
    rfc = RepulsiveForceConjecture(gamma=1.0)
    A = {"g_4": 1.0, "g_6": 0.3, "g_R2": 0.22}
    B = {"g_4": 0.2, "g_6": 0.06, "g_R2": 0.01}
    fa, _ = feasible(A, rfc)
    fb, _ = feasible(B, rfc)
    fm, mm = feasible(avg(A, B), rfc)
    assert fa and fb            # both endpoints satisfy
    assert not fm and mm < 0.0  # midpoint violates -> non-convex


def test_second_order_cones_are_convex():
    res = run()
    assert res["soc_convexity"]["moment_tower_convex"] is True
    assert res["soc_convexity"]["matter_dispersion_convex"] is True


def test_finding_states_nonconvex_and_dividing_line():
    res = run()
    f = res["finding"].lower()
    assert "non-convex" in f
    assert "bilinear" in f
    assert "second-order" in f or "second order" in f


def test_honest_scope_flags():
    res = run()
    sc = res["honest_scope"].lower()
    assert "prefactor-robust" in sc
    assert "reproducible" in sc
    assert "toy basis" in sc
