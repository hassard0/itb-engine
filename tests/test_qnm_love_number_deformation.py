"""Tests for the deformation-induced tidal Love number (v2.236)."""

from experiments.qnm_love_number_deformation import (
    closed_form_l2,
    induced_love_proxy,
    overlap_integral,
    run,
)


def test_overlap_integral_matches_closed_form():
    for n in (6, 8, 10):
        assert abs(overlap_integral(2, n) - closed_form_l2(n)) < 1e-6


def test_gr_baseline_is_zero():
    # no deformation -> no induced response
    assert abs(induced_love_proxy(2, 8, 0.0)) < 1e-15


def test_response_linear_in_deformation():
    a = induced_love_proxy(2, 8, 0.01)
    b = induced_love_proxy(2, 8, 0.02)
    c = induced_love_proxy(2, 8, 0.04)
    assert abs(b / a - 2.0) < 1e-6
    assert abs(c / a - 4.0) < 1e-6
    res = run()
    assert res["linear_in_eps"] is True


def test_sensitivity_decreases_with_localization():
    # a more localized deformation (larger n) overlaps the tidal field less
    assert overlap_integral(2, 6) > overlap_integral(2, 8) > overlap_integral(2, 10)


def test_honest_scope_first_order():
    res = run()
    sc = res["honest_scope"].lower()
    assert "first-order" in sc and "overlap integral" in sc
    assert "illustrative" in sc
    assert "g_R4_c3" in res["honest_scope"]
