"""Tests for higher-curvature corrections to Starobinsky inflation (v2.307)."""

from experiments.qnm_higher_curvature_inflation import run, observables


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_b0_reproduces_starobinsky():
    # the strict self-check: f(R)=R+R^2 must give n_s ~ 1-2/N, r ~ 12/N^2
    o = observables(1.0, 0.0, 55.0)
    assert o["ok"] is True
    assert abs(o["n_s"] - (1.0 - 2.0 / 55.0)) < 0.004
    assert abs(o["r"] - (12.0 / 55.0 ** 2)) < 0.004


def test_ns_far_more_sensitive_to_cubic_than_r():
    res = run()
    # n_s sweeps many Planck sigmas; r barely moves vs the BK18 limit
    assert res["n_s_swing_in_sigma"] > 5.0
    assert res["r_swing_in_BK18_units"] < 0.5


def test_r_stays_below_bk18_across_scan():
    res = run()
    assert all(s["r"] < 0.036 for s in res["cubic_scan"])


def test_cmb_carves_subwindow_tighter_than_positivity():
    res = run()
    win = res["cmb_allowed_b_window"]
    assert win is not None
    # the CMB-allowed b window is strictly inside the scanned positivity window
    scanned = [s["b"] for s in res["cubic_scan"]]
    assert win[0] >= min(scanned) - 1e-12 and win[1] <= max(scanned) + 1e-12
    assert (win[1] - win[0]) < (max(scanned) - min(scanned))   # strictly tighter


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "starobinsky" in f
    assert "n_s" in f and "cubic" in f
    sc = res["honest_scope"].lower()
    assert "schematic" in sc
    assert "self-check" in sc
    assert "toy basis" in sc
