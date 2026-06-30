"""Tests for the feasible curvature region map (v2.286)."""

from experiments.qnm_feasible_curvature_region import completion, run
from experiments.stack import build_stack
from itb.engine import check


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_region_non_empty_and_bounded_in_gR2():
    res = run()
    assert len(res["feasible_points"]) > 0
    assert res["gR2_ceiling"] is not None and res["gR2_ceiling"] <= 0.2


def test_gR3_bounded_above_by_positivity():
    res = run()
    # at every feasible g_R2, g_R3 has a finite upper bound
    for v in res["region_by_gR2"].values():
        assert v["g_R3_max"] < 0.30
    # pushing g_R3 past the ceiling binds on the forward-limit positivity (moment tower)
    assert res["binding_just_above_gR3_ceiling"] == "graviton_forward_positivity"


def test_x_ratio_ceiling_excludes_lqg():
    # region x-ceiling ~0.83 < lqg's x = 1.0, so lqg sits outside the positivity wedge
    res = run()
    assert res["region_x_ceiling"] is not None
    assert res["region_x_ceiling"] < 1.0


def test_a_point_inside_the_wedge_is_feasible():
    # g_R2=0.1, g_R3=0.06 (x=0.6, inside the ~0.83 ceiling) must be feasible
    assert check(completion(0.1, 0.06), build_stack()).feasible is True
    # g_R2=0.1, g_R3=0.12 (x=1.2, above the ceiling) must be infeasible
    assert check(completion(0.1, 0.12), build_stack()).feasible is False


def test_honest_scope_flags_completion_family_and_grid():
    res = run()
    sc = res["honest_scope"].lower()
    assert "completion family" in sc
    assert "0.02 grid" in sc
    assert "not a new constraint" in sc
