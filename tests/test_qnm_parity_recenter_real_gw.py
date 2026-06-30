"""Tests for the parity re-centering under the real GW bound (v2.348)."""

from experiments.qnm_parity_recenter_real_gw import run, RECENTER_PARITY, GW_REAL


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_original_feasible_then_killed_by_gw():
    res = run()
    assert res["original_violations_standard"] == []
    # tightening the GW bound makes the original infeasible, and ONLY the GW bound kills it
    assert res["original_violations_real_gw"] == ["ligo_birefringence_bound"]


def test_recentered_survives_full_tightened_stack():
    res = run()
    assert res["recentered_violations_real_gw"] == []
    assert RECENTER_PARITY < GW_REAL          # inside the real bound
    assert RECENTER_PARITY > res["recentered_parity_window"][0]  # above the CMB floor


def test_only_parity_changed():
    res = run()
    assert res["changed_couplings"] == ["g_R2_parity"]


def test_prediction_window_sharpened():
    res = run()
    assert res["recentered_window_width"] < res["original_window_width"]
    # roughly an order of magnitude tighter
    assert res["original_window_width"] / res["recentered_window_width"] > 5.0


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "survives" in f
    assert "self-correcting" in f
    assert "sharpen" in f
    sc = res["honest_scope"].lower()
    assert "toy basis" in sc
    assert "v2.329" in sc or "cmb hint being real" in sc
