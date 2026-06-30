"""Tests for the three-channel falsifiability map (v2.356)."""

from experiments.qnm_falsifiability_map import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_three_channels_each_verified():
    chans = _RES["channels"]
    assert len(chans) == 3
    assert {c["channel"] for c in chans} == {"parity", "ringdown", "screening"}
    for c in chans:
        assert c["verified"] is True, c["channel"]
    # observationally distinct
    assert len({c["observable"] for c in chans}) == 3


def test_constructed_feasible_on_program_stack():
    assert _RES["constructed_feasible"] is True


def test_thresholds_recomputed():
    # ringdown floor = g_R3^2/g_R2 and within the causality cap
    assert abs(_RES["ringdown_floor"] - 0.09 ** 2 / 0.193) < 1e-3
    assert _RES["ringdown_floor"] <= _RES["ringdown_cap"]
    # screening: g_R2 over the unscreened cap
    assert _RES["screening_over_factor"] > 2.0
    assert _RES["submm_unscreened_cap"] < 0.193


def test_data_dependence_split():
    # two of three channels have a non-fully-data-dependent core (ringdown, screening)
    assert _RES["n_not_fully_data_dependent"] == 2


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "three" in f and "channel" in f
    assert "parity" in f and "ringdown" in f and "screening" in f
    sc = _RES["honest_scope"].lower()
    assert "synthesis" in sc
    assert "re-computed" in sc or "re-derived" in sc
    assert "toy basis" in sc
