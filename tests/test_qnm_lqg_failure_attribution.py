"""Tests for the lqg CP-even failure attribution and the g_R2 box (v2.311)."""

from experiments.qnm_lqg_failure_attribution import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_gR3_is_the_outlier_cubic():
    res = run()
    g = res["gR3_by_framework"]
    assert g["lqg_induced"] == 0.3
    peers = [v for n, v in g.items() if n != "lqg_induced"]
    assert g["lqg_induced"] >= 2.0 * max(peers) - 1e-9


def test_graviton_positivity_attributed_to_gR3_only():
    res = run()
    assert res["per_failure_attribution"]["graviton_forward_positivity"] == ["g_R3"]


def test_reducing_gR3_clears_four_failures():
    res = run()
    assert len(res["failures_cleared_by_reducing_gR3"]) == 4
    assert "graviton_forward_positivity" in res["failures_cleared_by_reducing_gR3"]
    assert set(res["residual_failures_after_gR3"]) == {"repulsive_force_conjecture", "bnossw_monogamy"}


def test_gR2_box_is_empty():
    res = run()
    b = res["gR2_box"]
    assert b["interval_empty"] is True
    assert b["any_feasible_value"] is False
    # the repulsive/monogamy ceiling lies strictly below the anomaly floor
    assert b["repulsive_monogamy_ceiling_gR2"] < b["anomaly_floor_gR2"]
    assert b["gap"] > 0.0


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "cubic curvature" in f
    assert "box" in f and "empty" in f
    sc = res["honest_scope"].lower()
    assert "engine's literal verdict" in sc
    assert "toy basis" in sc
