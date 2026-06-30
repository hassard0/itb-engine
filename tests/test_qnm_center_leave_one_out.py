"""Tests for the leave-one-out center stability / method well-posedness (v2.361)."""

from experiments.qnm_center_leave_one_out import run

_RES = run(n_ascent=1500, seed=0)   # smaller ascent for speed; qualitative checks are n-robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_margins_not_cross_comparable_caveat():
    # the genuine methodological discovery: gw_speed margin (~5e-16) << theoretical margins (~0.02)
    assert _RES["margins_incomparable"] is True
    assert _RES["gw_speed_margin"] < _RES["tightest_theoretical_margin"] / 1e6


def test_theoretical_radius_positive():
    assert _RES["theoretical_chebyshev_radius_full"] > 0.0


def test_slack_controls_do_not_move_radius():
    slack = [r for r in _RES["leave_one_out"] if r["group"] == "slack-control"]
    assert slack
    for r in slack:
        assert r["radius_increase"] < 0.02, r["constraint"]


def test_no_single_drop_explodes_prediction():
    assert _RES["max_core_radius_increase"] < 0.5
    assert _RES["max_core_radius_increase"] >= _RES["max_slack_radius_increase"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "well-posed" in f
    assert "not cross-comparable" in f or "cross-comparable" in f
    sc = _RES["honest_scope"].lower()
    assert "local search" in sc or "not a proved global optimum" in sc
    assert "toy basis" in sc
