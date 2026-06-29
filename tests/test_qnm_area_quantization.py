"""Tests for QNM asymptotics / area quantization / Barbero-Immirzi (v2.274)."""

import math

from experiments.qnm_area_quantization import (
    LN3,
    area_quantum,
    barbero_immirzi_dreyer,
    omega_asymptotic_real,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_asymptotic_qnm_real_matches_famous_value():
    # Re(omega_inf) = ln3/(8 pi M); M=1 gives the famous 0.04371
    assert abs(omega_asymptotic_real(1.0) - LN3 / (8 * math.pi)) < 1e-15
    assert abs(omega_asymptotic_real(1.0) - 0.04371) < 1e-4


def test_area_quantum_is_universal_4ln3():
    # dA = 32 pi M Re(omega_inf) -> 4 ln3, independent of M
    for M in (0.3, 1.0, 7.0, 100.0):
        assert abs(area_quantum(M) - 4 * LN3) < 1e-9


def test_entropy_quantum_three_microstates():
    dS = area_quantum(1.0) / 4.0
    assert abs(dS - LN3) < 1e-12
    assert abs(math.exp(dS) - 3.0) < 1e-9   # exactly 3 microstates per area quantum


def test_discrete_spectrum_reproduces_bekenstein_hawking():
    res = run()
    for lvl in res["area_spectrum_levels"]:
        assert lvl["S_equals_A_over_4"] is True
        assert abs(lvl["entropy"] - lvl["area"] / 4.0) < 1e-12


def test_barbero_immirzi_tension_is_real():
    g = barbero_immirzi_dreyer()
    assert abs(g - LN3 / (2 * math.pi * math.sqrt(2))) < 1e-15
    res = run()
    # Dreyer's value disagrees with the standard LQG counting value by ~2x
    assert res["tension_ratio"] > 1.5
    assert res["barbero_immirzi_dreyer"] < res["barbero_immirzi_standard_lqg"]


def test_honest_scope_flags_input_and_unresolved_tension():
    res = run()
    sc = res["honest_scope"].lower()
    assert "source-backed" in sc
    assert "cannot reach" in sc or "low-overtone" in sc   # WKB can't reach n->inf
    assert "conjecture" in sc
    assert "not resolved" in sc or "reported, not resolved" in sc
