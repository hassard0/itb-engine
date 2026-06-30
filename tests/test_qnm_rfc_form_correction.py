"""Tests for the RFC-form correction (v2.316)."""

from experiments.qnm_rfc_form_correction import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_default_form_is_the_deprecated_matter_product():
    res = run()
    assert res["default_rfc_form"] == "matter_product"


def test_matter_product_excludes_all_community():
    res = run()
    for r in res["scores_matter_product"]:
        if r["framework"] != "pure_gr":
            assert r["feasible"] is False


def test_convex_hull_frees_three_community_frameworks():
    res = run()
    assert res["newly_feasible_under_convex_hull"] == ["asymptotic_safety", "cdt", "string_tree_eft"]
    cy = {r["framework"]: r for r in res["scores_convex_hull"]}
    for f in ["string_tree_eft", "asymptotic_safety", "cdt"]:
        assert cy[f]["feasible"] is True
        assert cy[f]["min_margin"] > 0


def test_lqg_infeasible_under_both_and_not_via_rfc():
    res = run()
    by = {r["framework"]: r for r in res["scores_matter_product"]}
    cy = {r["framework"]: r for r in res["scores_convex_hull"]}
    assert by["lqg_induced"]["feasible"] is False
    assert cy["lqg_induced"]["feasible"] is False
    # under the recommended form lqg's binding constraint is NOT repulsive force
    assert cy["lqg_induced"]["binding"] != "repulsive_force_conjecture"


def test_finding_documents_artifact_and_scope():
    res = run()
    f = res["finding"].lower()
    assert "artifact" in f
    assert "convex_hull" in f
    sc = res["honest_scope"].lower()
    assert "self-correction" in sc
    assert "unaffected" in sc
    assert "toy basis" in sc
