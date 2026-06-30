"""Tests for the CMB curvature-tower spectroscopy attempt (v2.308) -- a refuted hypothesis."""

from experiments.qnm_curvature_tower_cmb_spectroscopy import run, observables4, running


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_b0c0_reproduces_starobinsky_including_running():
    o = observables4(1.0, 0.0, 0.0, 55.0)
    assert abs(o["n_s"] - (1.0 - 2.0 / 55.0)) < 0.004
    al = running(1.0, 0.0, 0.0, 55.0)
    assert abs(al - (-2.0 / 55.0 ** 2)) < 5e-5


def test_running_insensitive_to_both_operators():
    res = run()
    sw = res["swings"]
    # both higher operators move the running by < 0.3 Planck-running-sigma
    assert sw["quartic_alpha_swing"] / 0.0067 < 0.3
    assert sw["cubic_alpha_swing"] / 0.0067 < 0.3


def test_cubic_and_quartic_both_move_ns_degeneracy():
    res = run()
    sw = res["swings"]
    # both move n_s by > 1 sigma -> they are degenerate in n_s (no spectroscopy)
    assert sw["quartic_ns_swing"] / 0.0042 > 1.0
    assert sw["cubic_ns_swing"] / 0.0042 > 1.0


def test_moment_floor_quartic_is_negligible():
    res = run()
    mt = res["moment_tower_forced"]
    assert mt["ns_shift_from_floor_quartic"] < 0.1 * 0.0042
    assert mt["running_deviation_from_starobinsky"] < 0.0067


def test_hypothesis_refuted_and_scope_flags():
    res = run()
    assert "REFUTED" in res["spectroscopy_hypothesis"]
    f = res["finding"].lower()
    assert "refuted" in f
    assert "degenerate" in f
    sc = res["honest_scope"].lower()
    assert "refuted hypothesis" in sc
    assert "toy basis" in sc
