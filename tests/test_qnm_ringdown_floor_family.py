"""Tests for the ringdown-floor center->family extension (v2.349)."""

from experiments.qnm_ringdown_floor_family import run, floor_of, CONSTRUCTED

_RES = run()   # default seed/n_walk -> deterministic


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_floor_is_moment_tower():
    # g_R3^2 / g_R2 at the constructed center = 0.09^2 / 0.193 ~ 0.042
    assert abs(_RES["constructed_floor"] - 0.0420) < 0.002
    assert abs(floor_of(CONSTRUCTED) - 0.09 ** 2 / 0.193) < 1e-9


def test_floor_varies_and_min_is_family_minimum():
    assert _RES["family_floor_max"] > _RES["family_floor_min"]
    assert _RES["family_floor_min"] <= _RES["constructed_floor"] + 1e-9


def test_verdict_floor_not_guaranteed_family_wide():
    # with the default seed g_R3 reaches ~0, so the floor collapses on part of the family
    assert _RES["gR3_can_vanish_in_family"] is True
    assert _RES["floor_guaranteed_family_wide"] is False
    assert _RES["family_gR3_min"] < 0.02


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "ringdown" in f
    assert "center" in f and "family" in f
    sc = _RES["honest_scope"].lower()
    assert "rank-1" in sc
    assert "toy basis" in sc
    assert "sampler-dependent" in sc
