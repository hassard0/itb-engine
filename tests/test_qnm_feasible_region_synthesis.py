"""Tests for the engine feasible-region synthesis capstone (v2.288)."""

from experiments.qnm_feasible_region_synthesis import run


def test_all_checks_pass():
    res = run()
    assert res["all_pass"] is True
    assert res["checks_passed"] == res["checks_total"] == 7
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_arc_has_seven_cycles():
    res = run()
    cycles = [a["cycle"] for a in res["arc"]]
    assert cycles == ["v2.281", "v2.282", "v2.283", "v2.284", "v2.285", "v2.286", "v2.287"]


def test_robust_vs_canonical_split_recorded():
    res = run()
    # the robust conclusions and the canonical-only ones are both present and distinct
    assert len(res["robust_conclusions"]) >= 2
    assert len(res["canonical_only_conclusions"]) >= 2
    robust_text = " ".join(res["robust_conclusions"]).lower()
    canon_text = " ".join(res["canonical_only_conclusions"]).lower()
    assert "not just general relativity" in robust_text
    assert "prefactor" in canon_text


def test_witness_robust_but_positivity_verdict_not():
    res = run()
    assert res["consistency_checks"]["witness_robust_to_positivity_prefactors"] is True
    assert res["consistency_checks"]["lqg_positivity_verdict_is_prefactor_dependent"] is True


def test_only_pure_gr_feasible():
    res = run()
    feas = res["framework_feasibility"]
    assert feas["pure_gr"] is True
    assert not any(v for k, v in feas.items() if k != "pure_gr")


def test_honest_scope_preserves_demotion():
    res = run()
    sc = res["honest_scope"].lower()
    assert "preserves the v2.287 demotion" in sc
    assert "adds no new constraint" in sc
