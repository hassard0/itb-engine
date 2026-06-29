"""Tests for the double pulsar PSR J0737-3039 GR test (v2.279)."""

import math

from experiments.qnm_double_pulsar import (
    DP,
    mass_from_omega_dot,
    omega_dot,
    run,
    shapiro_r_us,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_omega_dot_inverts_to_total_mass():
    # omega_dot(M) and mass_from_omega_dot are inverses; the measured omega_dot gives M ~ 2.587
    M = 2.58708
    om = omega_dot(M, DP["P_b_s"], DP["e"])
    assert abs(mass_from_omega_dot(om, DP["P_b_s"], DP["e"]) - M) < 1e-9
    res = run()
    assert abs(res["derived_total_mass_msun"] - DP["M_total_msun"]) / DP["M_total_msun"] < 0.01


def test_mass_ratio_recovers_individual_masses():
    res = run()
    assert abs(res["derived_m_A_msun"] - DP["m_A_msun"]) / DP["m_A_msun"] < 0.01
    assert abs(res["derived_m_B_msun"] - DP["m_B_msun"]) / DP["m_B_msun"] < 0.01


def test_predicted_pk_parameters_match_measured():
    res = run()
    c = res["pk_comparisons"]
    assert c["gamma_ms"]["frac_diff"] < 0.02
    assert c["Pdot_b"]["frac_diff"] < 0.02
    assert c["shapiro_r_us"]["frac_diff"] < 0.02


def test_shapiro_range_formula():
    # r = T_sun m_B (in microseconds)
    assert abs(shapiro_r_us(1.2489) - 4.925490947e-6 * 1.2489 * 1e6) < 1e-9


def test_honest_scope_flags_structural_demonstration():
    res = run()
    sc = res["honest_scope"].lower()
    assert "structural demonstration" in sc or "not the full timing fit" in sc
    assert "cited not re-derived" in sc
    assert "not an engine constraint refit" in sc
    assert "0.05%" in res["shapiro_shape_test"]
