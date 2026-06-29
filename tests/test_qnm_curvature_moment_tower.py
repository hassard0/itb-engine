"""Tests for the curvature dispersion tower as a Stieltjes moment sequence (v2.261)."""

import numpy as np

from experiments.qnm_curvature_moment_tower import hankel, is_psd, moments, run


def test_moment_sequence_all_hankel_psd():
    res = run()
    assert res["all_hankel_psd"] is True
    for t in res["hankel_tower"]:
        assert t["hankel_psd"] is True
        assert t["shifted_stieltjes_psd"] is True


def test_2x2_minor_is_v234_bound():
    res = run()
    assert res["minor_matches_v234"] is True
    # det[[g_R2,g_R3],[g_R3,g_R4]] = g_R2 g_R4 - g_R3^2 (v2.234)
    c = res["curvature_couplings"]
    assert abs(res["hankel_2x2_minor"] - (c["g_R2"] * c["g_R4"] - c["g_R3"] ** 2)) < 1e-9


def test_hankel_of_positive_density_is_psd():
    # H = sum_i w_i v_i v_i^T is manifestly PSD for w_i >= 0
    m = moments([0.4, 0.6], [1.5, 3.0], 6)
    assert is_psd(hankel(m, 2)) is True


def test_swampland_counterexample_not_a_moment_sequence():
    res = run()
    assert res["swampland_counterexample_violates_hankel"] is True
    # a sequence with a negative Hankel eigenvalue has no positive spectral representation
    m = moments([0.5, 0.5], [1.0, 2.0], 4)
    m_bad = m.copy()
    m_bad[2] = (m[1] ** 2 / m[0]) * 0.5
    assert not is_psd(hankel(m_bad, 1))


def test_honest_scope_structural_not_operator_exact():
    res = run()
    sc = res["honest_scope"].lower()
    assert "representative" in sc and "moment map" in sc
    assert "not a new bound" in sc
    assert "g_R4_c3" in res["honest_scope"]
