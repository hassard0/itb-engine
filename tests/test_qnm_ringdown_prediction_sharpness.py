"""Tests for the ringdown prediction-sharpness result (v2.337)."""

from experiments.qnm_ringdown_prediction_sharpness import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_gR4_range_is_wide():
    assert _RES["gR4_range_width"] > 0.3
    assert _RES["gR4_relative_spread"] > 1.0   # >100% relative spread


def test_floor_is_moment_tower():
    assert abs(_RES["gR4_feasible_range"][0] - _RES["moment_tower_floor"]) < 0.02


def test_ringdown_looser_than_parity():
    assert _RES["gR4_relative_spread"] > 3 * _RES["parity_relative_spread"]


def test_ceiling_is_theory_constraint():
    assert _RES["ceiling_constraint"] == "complexity_cutoff"
    assert _RES["consistency_checks"]["gR4_ceiling_is_a_theory_constraint_not_data"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "firm floor" in f and "loose magnitude" in f
    assert "no data" in f
    assert "parity" in f and "sharp" in f
    sc = _RES["honest_scope"].lower()
    assert "contrast" in sc
    assert "toy basis" in sc
