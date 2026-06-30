"""Tests for the wedge robustness / realism sweep (v2.287)."""

from experiments.qnm_wedge_robustness import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_gR2_ceiling_is_prefactor_invariant():
    # the anomaly/repulsive g_R2 wall does not move under the positivity prefactors
    res = run()
    lo, hi = res["gR2_ceiling_range"]
    assert (hi - lo) <= 0.02


def test_x_ceiling_is_prefactor_sensitive_and_straddles_frameworks():
    # the positivity x ceiling moves a lot, bracketing both the string/cdt (~0.7) and lqg (1.0) ratios
    res = run()
    lo, hi = res["x_ceiling_range"]
    assert (hi - lo) >= 0.3
    assert lo < 0.75       # at tight prefactors, string's x=0.75 falls outside
    assert hi > 1.0        # at loose prefactors, lqg's x=1.0 falls inside


def test_wedge_exists_for_every_prefactor():
    res = run()
    for s in res["prefactor_samples"]:
        assert s["x_ceiling"] > 0
        assert s["gR2_ceiling"] > 0


def test_canonical_reproduces_v286():
    res = run()
    assert abs(res["canonical"]["x_ceiling"] - 0.8) < 1e-9


def test_honest_scope_demotes_v286_verdict():
    res = run()
    sc = res["honest_scope"].lower()
    assert "demotion" in sc or "non-robust" in sc
    assert "canonical-only" in sc or "canonical verdict" in sc.replace("canonical-only", "x")
    assert "preserved, not papered over" in sc
