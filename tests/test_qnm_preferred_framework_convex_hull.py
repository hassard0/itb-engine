"""Tests for the corrected preferred-framework picture under convex_hull (v2.317)."""

from experiments.qnm_preferred_framework_convex_hull import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_scorecard_community_ranking():
    res = run()
    sc = res["scorecard"]
    # ranked descending by geometric margin
    g = [r["geom_margin"] for r in sc]
    assert g == sorted(g, reverse=True)
    # asymptotic_safety is the most robust community framework; lqg the only infeasible
    feasible_community = [r["theory"] for r in sc if r["feasible"] and r["theory"] != "pure_gr"]
    assert feasible_community[0] == "asymptotic_safety"
    assert [r["theory"] for r in sc if not r["feasible"]] == ["lqg_induced"]


def test_constructed_center_beats_all_community():
    res = run()
    pf = res["constructed_preferred_framework"]["geom_margin"]
    community_best = max(r["geom_margin"] for r in res["scorecard"]
                         if r["feasible"] and r["theory"] != "pure_gr")
    assert pf > community_best + 1e-9


def test_corrected_preferred_has_parity_and_parity_helps():
    res = run()
    pt = res["parity_test"]
    assert abs(pt["g_R2_parity"]) > 0.02            # mild parity violation
    # forcing parity to zero strictly reduces the achievable robustness
    assert pt["parity_free_geom_margin"] > pt["parity_zero_geom_margin"] + 1e-3


def test_finding_states_survives_and_reversal():
    res = run()
    f = res["finding"].lower()
    assert "core survives" in f or "still prefers a distinct" in f
    assert "parity reversal" in f or "parity-violating" in f
    sc = res["honest_scope"].lower()
    assert "convex_hull" in sc
    assert "toy basis" in sc
