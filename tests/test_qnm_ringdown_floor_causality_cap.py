"""Tests for the causality cap on the ringdown floor (v2.351)."""

from experiments.qnm_ringdown_floor_causality_cap import run

_RES = run()   # default seed/n_walk -> deterministic


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_cap_coefficient_is_kappa_squared():
    assert abs(_RES["cap_coefficient_kappa_squared"] - _RES["cemz_kappa"] ** 2) < 1e-9


def test_constructed_floor_below_cap():
    assert _RES["constructed_floor"] <= _RES["constructed_cap"]
    # the constructed center is well below its causality cap (headroom, v2.339)
    assert _RES["constructed_saturation"] < 0.5


def test_family_brackets_floor_zero_to_cap():
    # lower bracket (v2.349): floor reaches ~0; upper bracket (here): never exceeds the cap
    assert _RES["family_floor_min"] < 0.01
    assert _RES["family_respects_cap"] is True
    assert 0.0 <= _RES["family_max_saturation_of_cap"] <= 1.0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "causality" in f and "cap" in f
    assert "bracket" in f
    assert "v2.349" in f
    sc = _RES["honest_scope"].lower()
    assert "exact algebra" in sc
    assert "rank-1" in sc
    assert "toy basis" in sc
