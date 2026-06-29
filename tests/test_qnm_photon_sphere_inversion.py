"""Tests for the two-parameter photon-sphere inversion (v2.232)."""

from experiments.qnm_photon_sphere_inversion import geodesics, jacobian, run, verify_inversion


def test_two_observables_invert_two_parameters():
    res = run()
    # the (shadow, damping) Jacobian is non-singular -> locally invertible
    assert res["invertible"] is True
    assert abs(res["det"]) > 1e-6


def test_inversion_recovers_parameters():
    jac = jacobian()
    inv = verify_inversion(0.01, -0.02, jac)
    # linear recovery of a small deformation is accurate
    assert inv["max_abs_err"] < 1e-3


def test_condition_number_finite():
    # moderate conditioning (damping responds similarly to the two profiles; shadow breaks it)
    res = run()
    assert 1.0 < res["condition_number"] < 1000.0


def test_undeformed_is_schwarzschild():
    g = geodesics(0.0, 0.0)
    assert abs(g["r_ph"] - 3.0) < 1e-9
    assert abs(g["Omega_c"] * g["b_c"] - 1.0) < 1e-9


def test_honest_scope_and_core_recon_recorded():
    res = run()
    sc = res["honest_scope"].lower()
    assert "eikonal" in sc and "illustrative" in sc
    assert "g_R4_c3" in res["honest_scope"]
    # the core-engine reconnaissance is recorded for follow-up
    assert "g_8" in res["core_engine_reconnaissance_note"]
    assert "catalog.py" in res["core_engine_reconnaissance_note"]
