"""Tests for the photon-sphere ringdown<->shadow multi-messenger consistency (v2.230)."""

import math

from experiments.qnm_shadow_multimessenger import (
    overtone_ladder,
    photon_sphere_shadow,
    run,
)


def test_shadow_radius_first_principles():
    ps = photon_sphere_shadow()
    assert abs(ps["b_c_shadow_radius"] - 3 * math.sqrt(3)) < 1e-12
    # Omega_c = 1/b_c exactly
    assert abs(ps["Omega_c_times_b_c"] - 1.0) < 1e-12


def test_ringdown_shadow_consistency_converges():
    res = run()
    assert res["consistency_converges_to_1"] is True
    # at high l the GW ringdown frequency matches the shadow light-crossing rate
    assert res["best_ringdown_shadow_ratio"] > 0.98


def test_overtone_ladder_equally_spaced_at_minus_lambda():
    ps = photon_sphere_shadow()
    lad = overtone_ladder(ps)
    # the imaginary parts are equally spaced with spacing ~ -lambda = -Omega_c
    assert lad["max_rel_err"] < 0.02
    for s in lad["spacings"]:
        assert abs(s - (-ps["lambda"])) / ps["lambda"] < 0.02


def test_honest_scope_geodesic_multimessenger():
    res = run()
    sc = res["honest_scope"].lower()
    assert "eikonal" in sc and "schwarzschild-only" in sc
    assert "cross-channel" in res["finding"].lower()
    assert "g_R4_c3" in res["honest_scope"]
