"""Tests for the matter moment-tower extension (v2.426, MT)."""

from experiments.qnm_matter_tower import run
from experiments.stack import build_stack, rigor_of, rigorous_core_stack


_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_tower_opt_in():
    default = {c.name for c in build_stack(rfc_form="convex_hull", include_data=True)}
    mt = {c.name for c in build_stack(rfc_form="convex_hull", include_data=True, include_matter_tower=True)}
    assert "matter_tower_g8_squared_bound" not in default
    assert "matter_tower_g8_squared_bound" in mt
    assert "scalar_positivity_g10" in mt


def test_new_constraints_are_rigorous():
    assert rigor_of("matter_tower_g8_squared_bound") == "rigorous"
    assert rigor_of("scalar_positivity_g10") == "rigorous"
    core = rigorous_core_stack(rfc_form="convex_hull", include_data=True, include_matter_tower=True)
    assert any(c.name == "matter_tower_g8_squared_bound" for c in core)


def test_predicts_g10_floor():
    # g_8^2 / g_6 = 0.16/0.4 = 0.4
    assert abs(_RES["predicted_g10_floor"] - 0.4) < 1e-6
    win = _RES["g10_window_full_stack"]
    assert abs(win[0] - 0.4) < 0.02       # rigorous Hankel floor
    assert win[1] > win[0]                 # bounded window


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "moment tower" in f
    assert "rigorous" in f and "zero toy" in f
    sc = _RES["honest_scope"].lower()
    assert "source-exact in form" in sc
    assert "lower bound" in sc or "not a determination" in sc
