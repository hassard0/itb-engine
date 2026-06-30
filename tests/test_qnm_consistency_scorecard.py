"""Tests for the consistency scorecard + coherence audit (v2.315)."""

from experiments.qnm_consistency_scorecard import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_scorecard_ranks_preferred_first():
    res = run()
    sc = res["scorecard"]
    assert sc[0]["theory"] == "engine_preferred"
    assert sc[0]["min_margin"] > 0
    # ranked descending by min_margin
    margins = [r["min_margin"] for r in sc]
    assert margins == sorted(margins, reverse=True)


def test_only_preferred_and_pure_gr_feasible():
    res = run()
    for r in res["scorecard"]:
        if r["theory"] in ("engine_preferred", "pure_gr"):
            assert r["feasible"] is True
        else:
            assert r["feasible"] is False


def test_all_community_bound_by_repulsive_force():
    res = run()
    community = [r for r in res["scorecard"] if r["theory"] not in ("engine_preferred", "pure_gr")]
    assert len(community) == 4
    for r in community:
        assert r["binding_constraint"] == "repulsive_force_conjecture"
        assert r["binding_family"] == "C_UNIVERSALITY"


def test_universality_decisive_and_preferred_trimmed():
    res = run()
    assert res["consistency_checks"]["universality_family_is_decisive_throughout"] is True
    assert res["consistency_checks"]["preferred_curvature_gR3_trimmed_below_all_community"] is True


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "universality" in f and "decisive" in f
    assert "repulsive_force" in f or "repulsive-force" in f
    sc = res["honest_scope"].lower()
    assert "literal check() output" in sc
    assert "toy basis" in sc
