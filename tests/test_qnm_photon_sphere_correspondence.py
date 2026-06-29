"""Tests for the eikonal QNM <-> photon-sphere correspondence (v2.229)."""

import math

from experiments.qnm_photon_sphere_correspondence import (
    eikonal_table,
    photon_sphere,
    run,
)


def test_photon_sphere_first_principles():
    ps = photon_sphere()
    cf = 1.0 / (3.0 * math.sqrt(3.0))
    # both the orbital frequency and the Lyapunov exponent equal 1/(3 sqrt3) for Schwarzschild
    assert abs(ps["Omega_c"] - cf) < 1e-12
    assert abs(ps["lambda"] - cf) < 1e-12
    assert ps["r_ph"] == 3.0


def test_qnm_converges_to_photon_sphere():
    res = run()
    assert res["convergence_monotone_in_l"] is True
    # at high l the WKB QNM matches the geodesic limit to ~1%
    assert res["best_rel_err_Omega_c"] < 0.02
    assert res["best_rel_err_lambda"] < 0.01


def test_correction_is_order_one_over_l():
    # the eikonal correction shrinks ~ 1/l: error at l roughly halves as l doubles
    rows = {r["l"]: r["rel_err_Omega_c"] for r in eikonal_table(0)}
    assert rows[4] < rows[2]
    assert rows[8] < rows[4]
    # not exact but the l=12 error is well below the l=2 error
    assert rows[12] < 0.1 * rows[2]


def test_honest_scope_geodesic_limit():
    res = run()
    sc = res["honest_scope"].lower()
    assert "asymptotic" in sc
    assert "schwarzschild only" in sc
    assert "g_R4_c3" in res["honest_scope"]
