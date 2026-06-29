"""Tests for the GW vs EM luminosity-distance ratio standard-siren test (v2.270)."""

from experiments.qnm_gw_em_distance_ratio import (
    extradim_ratio,
    run,
    xi_running_planck,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_gr_limits_are_exactly_unity():
    # running Planck mass Xi_0 = 1 -> ratio 1 at all z, n
    for z in (0.0, 0.1, 1.0, 5.0):
        for n in (1.0, 2.5):
            assert abs(xi_running_planck(z, 1.0, n) - 1.0) < 1e-15
    # extra dimensions D = 4 -> ratio 1 at all distance, Rc, n
    for d in (10.0, 40.0, 1000.0):
        for Rc in (50.0, 1000.0):
            assert abs(extradim_ratio(d, 4.0, Rc, 2.0) - 1.0) < 1e-15


def test_extra_dimensions_suppress_amplitude_monotonically():
    # D > 4 -> d_GW > d_EM, increasing in D
    prev = 1.0
    for D in (4.0, 4.5, 5.0, 6.0, 7.0):
        r = extradim_ratio(40.0, D, 100.0, 2.0)
        assert r >= prev
        prev = r
    assert extradim_ratio(40.0, 5.0, 100.0, 2.0) > 1.0


def test_low_distance_expansion():
    # ratio ~ 1 + (D-4)/(2n) (d/Rc)^n for Rc >> d
    d, Rc, n, D = 40.0, 5.0e5, 2.0, 5.0
    exact = extradim_ratio(d, D, Rc, n)
    approx = 1.0 + (D - 4.0) / (2 * n) * (d / Rc) ** n
    assert abs(exact - approx) < 1e-6 * (exact - 1.0)


def test_gw170817_consistent_with_gr_and_achromatic():
    res = run()
    assert res["consistency_checks"]["gw170817_consistent_with_gr"] is True
    assert res["is_achromatic"] is True
    # the published Pardo dimension bound is recorded
    assert "4.0" in res["gw170817"]["pardo_dimension_bound"]


def test_honest_scope_flags_parametrization_and_published_values():
    res = run()
    sc = res["honest_scope"].lower()
    assert "parametrization" in sc
    assert "source-backed" in sc or "published" in sc
    assert "not the full bayesian" in sc
    assert "not an engine constraint refit" in sc
