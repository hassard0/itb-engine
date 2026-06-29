"""Tests for the vacuum-birefringence parity-violation probe (v2.252)."""

from experiments.qnm_vacuum_birefringence import rotation_angle, run, xi_bound


def test_grb_excludes_dim5_parity_violation():
    res = run()
    grb = next(r for r in res["xi_bounds"] if "0.1-1 MeV" in r["label"])
    # Planck-suppressed energy-dependent parity violation tightly excluded
    assert grb["xi_bound"] < 1e-15


def test_higher_energy_band_is_tighter():
    # the E^2 dependence makes a wider/higher band a much stronger bound
    b_low = xi_bound(1e5, 1e6, 3.3 * 3.086e25)
    b_high = xi_bound(1e5, 1e7, 3.3 * 3.086e25)
    assert b_high < b_low / 50


def test_rotation_scales_as_energy_squared():
    a = rotation_angle(1e-17, 1e6, 1e25)
    b = rotation_angle(1e-17, 2e6, 1e25)
    assert abs(b / a - 4.0) < 1e-9      # ~E^2


def test_cosmic_birefringence_is_energy_independent_contrast():
    res = run()
    cb = res["cosmic_birefringence_contrast"]
    assert "ENERGY-INDEPENDENT" in cb["character"]
    assert cb["beta_deg"] == 0.34
    assert "hint" in cb["status"].lower()


def test_honest_scope_order_of_magnitude_hint():
    res = run()
    sc = res["honest_scope"].lower()
    assert "order-of-magnitude" in sc and "depolarization" in sc
    assert "hint" in sc and "not a discovery" in sc
    assert "g_R4_c3" in res["honest_scope"]
