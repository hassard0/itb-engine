"""Tests for the Hulse-Taylor quadrupole orbital decay (v2.278)."""

from experiments.qnm_hulse_taylor_quadrupole import (
    HT,
    MSUN,
    f_eccentricity,
    pdot_gw,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_eccentricity_factor_circular_limit_and_monotonic():
    assert abs(f_eccentricity(0.0) - 1.0) < 1e-12
    assert f_eccentricity(0.2) < f_eccentricity(0.5) < f_eccentricity(0.8)
    # HT e=0.617 enhances emission ~11.85x
    assert 11.0 < f_eccentricity(0.6171) < 13.0


def test_predicted_pdot_matches_hulse_taylor():
    res = run()
    # the famous ~ -2.40e-12 reproduction, agreement < 1%
    assert -2.45e-12 < res["predicted_Pdot"] < -2.35e-12
    assert abs(res["predicted_over_observed"] - 1.0) < 0.01


def test_pdot_scales_with_period():
    # tighter (shorter-period) orbit radiates faster: |dP/dt| larger
    m1, m2 = HT["m1_msun"] * MSUN, HT["m2_msun"] * MSUN
    p_short = pdot_gw(m1, m2, 0.5 * HT["P_s"], HT["e"])
    p_long = pdot_gw(m1, m2, HT["P_s"], HT["e"])
    assert abs(p_short) > abs(p_long)


def test_merger_time_few_hundred_Myr():
    res = run()
    assert 1e8 < res["merger_time_eccentric_yr"] < 1e9   # ~300 Myr
    assert res["merger_time_eccentric_yr"] < res["merger_time_circular_yr"]  # eccentricity shortens it


def test_honest_scope_flags_corrections():
    res = run()
    sc = res["honest_scope"].lower()
    assert "galactic-acceleration" in sc or "kinematic" in sc
    assert "circular-orbit" in sc or "order-correct" in sc
    assert "not an engine constraint refit" in sc
