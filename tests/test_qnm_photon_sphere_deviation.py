"""Tests for the photon-sphere deviation cross-channel sensitivity (v2.231)."""

from experiments.qnm_photon_sphere_deviation import geodesics, run, sensitivities


def test_locking_identity_universal():
    # d ln(Omega_c) = -d ln(b_c) for every deformation profile (Omega_c b_c = 1 identically)
    res = run()
    assert res["locking_identity_universal"] is True
    for r in res["sensitivities_per_profile"]:
        assert abs(r["locking_residual"]) < 1e-6


def test_coefficients_are_profile_specific():
    # the identity is universal but the magnitudes depend on the deformation profile k
    s2, s3, s4 = sensitivities(2), sensitivities(3), sensitivities(4)
    assert abs(s2["d_ln_b_c"]) > abs(s3["d_ln_b_c"]) > abs(s4["d_ln_b_c"])


def test_damping_is_independent_of_shadow():
    res = run()
    assert res["damping_independent"] is True
    for r in res["sensitivities_per_profile"]:
        # the Lyapunov (damping) response is not locked to the shadow response
        assert abs(r["damping_minus_neg_b_c"]) > 1e-3


def test_undeformed_recovers_schwarzschild():
    g = geodesics(0.0, 3)
    assert abs(g["r_ph"] - 3.0) < 1e-9
    assert abs(g["Omega_c"] * g["b_c"] - 1.0) < 1e-9


def test_honest_scope_null_test_framing():
    res = run()
    sc = res["honest_scope"].lower()
    assert "eikonal" in sc and "illustrative" in sc
    assert "null test" in res["finding"].lower()
    assert "g_R4_c3" in res["honest_scope"]
