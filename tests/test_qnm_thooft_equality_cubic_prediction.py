"""Tests for the conditional 't Hooft-equality cubic prediction (v2.353)."""

from experiments.qnm_thooft_equality_cubic_prediction import run, RHO_MATCH, BASE


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_ratio_is_matter_fixed():
    res = run()
    assert abs(res["matter_fixed_ratio_r"] - RHO_MATCH * (BASE["g_4"] + BASE["g_6"])) < 1e-4


def test_cubic_becomes_a_prediction():
    res = run()
    # nonzero, and equals r * g_R2_parity at the constructed point
    assert res["predicted_cubic_at_constructed"] > 0.01
    assert abs(res["predicted_cubic_at_constructed"]
               - res["matter_fixed_ratio_r"] * BASE["g_R2_parity"]) < 1e-5


def test_predicted_point_feasible_in_current_engine():
    res = run()
    assert res["predicted_feasible"] is True
    assert res["predicted_point_violations"] == []


def test_equality_tightens_quadratic():
    res = run()
    assert res["anomaly_edge_under_equality"] < res["anomaly_edge_bound_form"]
    # self-consistent cubic window is narrower than the naive one (uses the tightened quadratic edge)
    assert res["self_consistent_cubic_window"][1] <= res["predicted_cubic_window"][1] + 1e-9


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "conditional" in f
    assert "second parity-odd prediction" in f
    sc = res["honest_scope"].lower()
    assert "does not change the core engine" in sc
    assert "up to sign" in sc or "not the sign" in sc
    assert "toy basis" in sc
