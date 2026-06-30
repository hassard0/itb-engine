"""Tests for the engine-preferred-framework construction (v2.312)."""

import numpy as np

from experiments.qnm_engine_preferred_framework import run, KEYS, margins, build_stack


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_pure_gr_feasible_but_marginal():
    res = run()
    pg = res["pure_gr"]
    assert pg["feasible"] is True
    assert abs(pg["min_margin"]) < 1e-9
    # the majority of constraints saturate at the origin (the apex of the cone)
    assert pg["n_saturated_at_origin"] > res["n_constraints"] / 2


def test_preferred_framework_is_nonzero_and_strictly_feasible():
    res = run()
    pf = res["engine_preferred_framework"]
    vec = np.array([pf["couplings"][k] for k in KEYS])
    assert not np.allclose(vec, 0.0, atol=1e-6)        # nonzero (not pure GR)
    assert pf["worst_case_margin"] > 1e-9              # strictly interior
    # re-verify strict feasibility against the engine
    assert all(m > 0 for m in margins(vec, build_stack()))


def test_preferred_more_robust_than_pure_gr_and_distinct():
    res = run()
    pf = res["engine_preferred_framework"]
    assert pf["more_robust_than_pure_gr"] is True
    assert pf["distinct_from_community_frameworks"] is True


def test_no_community_higher_derivative_framework_feasible():
    res = run()
    for r in res["frameworks"]:
        if r["framework"] == "pure_gr":
            assert r["feasible"] is True
        else:
            assert r["feasible"] is False
            assert r["min_margin"] < 0.0


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "preferred framework" in f
    assert "trimmed curvature" in f or "trimmed" in f
    sc = res["honest_scope"].lower()
    assert "sign-based" in sc
    assert "empty interior" in sc          # the corrected-error disclosure
    assert "toy basis" in sc
