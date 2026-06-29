"""Tests for the eikonal Kerr ringdown damping / Lyapunov exponent (v2.241)."""

import math

from experiments.qnm_kerr_eikonal_damping import lyapunov, run


def test_schwarzschild_lyapunov_gate():
    # a=0 -> lambda = Omega_c = 1/(3 sqrt3), the v2.229 identity
    assert abs(lyapunov(0.0, True) - 1 / (3 * math.sqrt(3))) < 1e-9
    assert abs(lyapunov(0.0, False) - 1 / (3 * math.sqrt(3))) < 1e-9


def test_prograde_damping_falls_toward_extremal():
    res = run()
    assert res["prograde_damping_falls_with_spin"] is True
    # near-extremal prograde damping heads to zero
    assert lyapunov(0.998, True) < 0.05


def test_quality_factor_rises_with_spin():
    res = run()
    assert res["quality_factor_rises_with_spin"] is True
    seq = res["spin_sequence"]
    assert seq[-1]["quality_factor_prograde"] > 5 * seq[0]["quality_factor_prograde"]


def test_honest_scope_eikonal_extremal():
    res = run()
    assert res["schwarzschild_gate_ok"] is True
    sc = res["honest_scope"].lower()
    assert "eikonal" in sc and "leaver" in sc
    assert "zero-damping" in res["finding"].lower()
    assert "g_R4_c3" in res["honest_scope"]
