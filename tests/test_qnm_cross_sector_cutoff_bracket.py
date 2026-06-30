"""Tests for the cross-sector cutoff bracket (v2.296)."""

import math

from experiments.qnm_cross_sector_cutoff_bracket import ABC, W_plus, bracket_hankel_psd, run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_W_plus_formula():
    # C W^2 - B W + A = 0 at W_+ : verify the root
    A, B, C = 0.01, 0.05, 0.04
    Wp = W_plus(A, B, C)
    assert abs(C * Wp**2 - B * Wp + A) < 1e-9


def test_W_plus_is_a_valid_bracket():
    # {W m_k - c_k} has a PSD 2x2 Hankel exactly at W_+
    res = run()
    for r in res["framework_bracket"]:
        assert r["hankel_psd_at_Wplus"] is True


def test_W_plus_sharpens_trivial_bound():
    res = run()
    for r in res["framework_bracket"]:
        assert r["W_plus"] >= r["trivial_max_ratio"] - 1e-9


def test_lqg_has_largest_relative_curvature_coupling():
    res = run()
    by = {r["framework"]: r["W_plus"] for r in res["framework_bracket"]}
    assert by["lqg_induced"] == max(by.values())
    assert by["lqg_induced"] > 0.7


def test_bracket_predicate_at_forced_minimum_A_zero():
    # at g_R4 = g_R3^2/g_R2 the curvature Hankel saturates: A = 0, so W_+ = B/C
    A, B, C = ABC(0.5, 0.4, 0.4, 0.2, 0.15, 0.15**2 / 0.2)
    assert abs(A) < 1e-12
    assert abs(W_plus(A, B, C) - B / C) < 1e-9


def test_three_handle_map_complete():
    res = run()
    m = res["three_handle_map"]
    assert "nothing new" in m["w_ge_0"].lower()
    assert "monoton" in m["w_monotone"].lower()
    assert "relative curvature coupling" in m["w_le_W"].lower()


def test_honest_scope_flags_relative_not_scale():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not directly the eft cutoff" in sc or "not a scale in gev" in sc
    assert "not a theorem" in sc
