"""Tests for the scale-clean UV-embedding double-ratio (v2.464)."""

from experiments.qnm_scale_clean_uv_test import run, double_ratio

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_double_ratio_scale_independent():
    assert _RES["x_power_of_D"] == 0     # (1+3) - 2*2 = 0, alpha' cancels


def test_candidate_D_moment_tower():
    assert _RES["candidate_D_at_floor"] >= 1.0 - 1e-9
    # D grows with g_R4 above the floor
    assert double_ratio(0.193, 0.09, 0.08) > double_ratio(0.193, 0.09, 0.05)


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "scale-independent" in f
    assert "alpha' cancel" in f or "x cancel" in f
    assert "wall" in f
    sc = _RES["honest_scope"].lower()
    assert "does not compute d_string" in sc or "not compute d_string" in sc
    assert "basis-dependent" in sc or "field-redefinition" in sc  # R^3,R^4 ambiguity
    assert "floor" in sc  # candidate D=1 is a floor/Chebyshev feature
