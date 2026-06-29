"""Tests for the feasible-region-edge characterization (v2.283)."""

from experiments.qnm_curvature_headroom import POSITIVITY_FAMILY, run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_only_pure_gr_feasible():
    res = run()
    feasible = [r["framework"] for r in res["framework_edge"] if r["feasible"]]
    assert feasible == ["pure_gr"]


def test_three_eft_frameworks_fail_only_repulsive_force():
    res = run()
    for name in ("string_tree_eft", "asymptotic_safety", "cdt"):
        r = next(x for x in res["framework_edge"] if x["framework"] == name)
        assert r["n_failing"] == 1
        assert r["failing_constraints"] == ["repulsive_force_conjecture"]


def test_lqg_fails_six_including_positivity_family():
    res = run()
    lqg = next(x for x in res["framework_edge"] if x["framework"] == "lqg_induced")
    assert lqg["n_failing"] == 6
    assert POSITIVITY_FAMILY.issubset(set(lqg["failing_constraints"]))
    assert POSITIVITY_FAMILY.issubset(set(res["lqg_extra_failures_vs_others"]))


def test_lqg_anomaly_vs_positivity_tension():
    # curvature off -> fails anomaly_cancellation (needs curvature); curvature on -> fails positivity
    res = run()
    assert "anomaly_cancellation" in res["lqg_fails_curvature_off"]
    assert res["consistency_checks"]["lqg_anomaly_vs_positivity_tension"] is True


def test_honest_scope_corrects_headroom_premise():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not a claim that string theory is in the swampland" in sc
    assert "honest by construction" in sc
    assert "corrects" in sc and "headroom" in sc
