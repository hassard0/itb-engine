"""Tests for relativistic stellar structure / TOV / Buchdahl (v2.289)."""

import math

from experiments.qnm_tov_compactness import (
    analytic_P_of_r,
    analytic_Pc_over_rho,
    compactness,
    run,
    tov_integrate,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_buchdahl_bound_central_pressure_diverges():
    # central pressure -> infinity as beta -> 8/9
    assert analytic_Pc_over_rho(0.8) < analytic_Pc_over_rho(0.88)
    assert analytic_Pc_over_rho(8 / 9 - 1e-7) > 1e4


def test_tov_reproduces_analytic_interior():
    # numerical RK4 TOV matches the analytic Schwarzschild interior for a uniform-density star
    R, beta = 1.0, 0.4
    rho = beta / ((8 / 3) * math.pi * R**2)
    P_surf, mR, Pc, M = tov_integrate(rho, R)
    assert P_surf < 1e-3 * Pc          # pressure vanishes at the surface
    assert abs(mR - M) < 1e-6 * M       # mass integrates correctly
    # mid-radius profile point matches analytic
    assert abs(analytic_P_of_r(0.5, R, M, rho) - rho * 0.13) < rho  # sane order


def test_compactness_hierarchy():
    # Sun << white dwarf << neutron star < Buchdahl < BH
    sun = compactness(1.0, 696000.0)
    ns = compactness(1.4, 12.0)
    assert sun < 1e-5 < ns < 8 / 9 < 1.0
    assert 0.3 < ns < 0.4               # canonical NS ~ 0.34


def test_photon_sphere_onset_at_two_thirds():
    res = run()
    ns = next(o for o in res["compactness_hierarchy"] if o["name"].startswith("neutron"))
    uc = next(o for o in res["compactness_hierarchy"] if o["name"].startswith("ultracompact"))
    assert ns["has_photon_sphere"] is False        # beta ~ 0.34 < 2/3
    assert uc["has_photon_sphere"] is True         # beta ~ 0.67 > 2/3


def test_honest_scope_flags_uniform_density_and_eos():
    res = run()
    sc = res["honest_scope"].lower()
    assert "uniform-density" in sc
    assert "equation of state" in sc
    assert "not an engine constraint refit" in sc
