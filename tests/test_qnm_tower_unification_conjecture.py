"""Tests for the tower-unification bold-swing conjecture (v2.367)."""

from experiments.qnm_tower_unification_conjecture import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_prediction_arithmetic():
    res = run()
    # g_R4 = floor / r_matter
    assert abs(res["predicted_g_R4"] - res["moment_floor"] / res["r_matter"]) < 1e-3
    assert abs(res["predicted_over_floor"] - 1.0 / res["r_matter"]) < 1e-2


def test_prediction_is_feasible_and_above_floor():
    res = run()
    lo, hi = res["feasible_range_v2337"]
    assert lo <= res["predicted_g_R4"] <= hi
    assert res["predicted_g_R4"] > res["moment_floor"]


def test_flagged_as_conjecture_not_result():
    res = run()
    assert "CONJECTURE" in res["status"]
    assert "not engine-derived" in res["status"]
    sc = res["honest_scope"].lower()
    assert "conjecture" in sc
    assert "not derived from the engine" in sc or "not guaranteed" in sc
    assert "falsifiable" in sc


def test_finding_has_falsifier_and_swing_framing():
    res = run()
    f = res["finding"].lower()
    assert "conjecture" in f
    assert "falsifiable" in f or "falsif" in f
    assert res["falsifier"]
