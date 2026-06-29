"""Tests for the Kerr strong-field observables (v2.239)."""

import math

from experiments.qnm_kerr_strong_field import efficiency, photon_radius, r_isco, run


def test_schwarzschild_limit():
    assert abs(r_isco(0.0, True) - 6.0) < 1e-9
    assert abs(efficiency(0.0, True) - (1 - math.sqrt(8 / 9))) < 1e-9
    assert abs(photon_radius(0.0, True) - 3.0) < 1e-9


def test_prograde_retrograde_split():
    # spin pulls prograde orbits inward and pushes retrograde outward
    assert r_isco(0.9, True) < 6.0 < r_isco(0.9, False)
    assert photon_radius(0.9, True) < 3.0 < photon_radius(0.9, False)


def test_extremal_efficiency_amplified():
    res = run()
    e = res["extremal_a1"]
    # extremal prograde efficiency -> 1 - 1/sqrt3 ~ 0.4226 (the AGN/quasar engine)
    assert abs(e["efficiency_prograde_limit"] - (1 - 1 / math.sqrt(3))) < 1e-9
    assert abs(e["isco_retrograde"] - 9.0) < 1e-6
    assert abs(e["photon_retrograde"] - 4.0) < 1e-6


def test_efficiency_monotonic_in_spin_prograde():
    effs = [efficiency(a, True) for a in (0.0, 0.5, 0.9, 0.99)]
    assert all(effs[i + 1] > effs[i] for i in range(len(effs) - 1))


def test_honest_scope_exact_kerr():
    res = run()
    assert res["schwarzschild_limit_reproduced"] is True
    sc = res["honest_scope"].lower()
    assert "exact kerr" in sc or "not a bump" in sc
    assert "extremal" in sc
    assert "g_R4_c3" in res["honest_scope"]
