"""Tests for the lqg-repair result (v2.330)."""

from experiments.qnm_repair_lqg import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_lqg_infeasible_but_close():
    assert _RES["lqg_feasible"] is False
    assert _RES["repair_distance"] < 0.3


def test_biggest_repair_is_the_cubic():
    assert _RES["biggest_change"] == "g_R3"
    assert _RES["deltas_from_lqg"]["g_R3"] < -0.05


def test_repair_keeps_parity():
    # the parity coupling stays nonzero and near the data window
    rep = _RES["repaired_coefficients"]
    assert rep["g_R2_parity"] > 0.04
    assert abs(_RES["deltas_from_lqg"]["g_R2_parity"]) < 0.03   # parity barely changed


def test_repaired_point_is_feasible():
    assert _RES["consistency_checks"]["repaired_lqg_is_feasible"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "right feature" in f
    assert "wrong one" in f
    assert "trims" in f and "parity" in f
    sc = _RES["honest_scope"].lower()
    assert "approximate projection" in sc
    assert "toy basis" in sc
