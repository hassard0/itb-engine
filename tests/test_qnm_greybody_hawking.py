"""Tests for black-hole greybody factors and the Hawking spectrum (v2.273)."""

import math

from experiments.qnm_greybody_hawking import (
    B_C,
    greybody_wkb,
    hawking_flux,
    rw_peak,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_greybody_is_half_at_barrier_peak():
    V_max, V2 = rw_peak(2, 2)
    omega_c = math.sqrt(V_max)
    assert abs(greybody_wkb(omega_c, V_max, V2) - 0.5) < 1e-12


def test_greybody_monotonic_0_to_1():
    V_max, V2 = rw_peak(2, 2)
    omega_c = math.sqrt(V_max)
    assert greybody_wkb(0.05, V_max, V2) < 1e-2          # barrier reflects soft quanta
    assert greybody_wkb(2.0 * omega_c, V_max, V2) > 0.99  # transmits above the barrier
    vals = [greybody_wkb(w, V_max, V2) for w in (0.05, 0.15, 0.3, omega_c, 0.6, 1.0)]
    assert all(vals[i + 1] >= vals[i] for i in range(len(vals) - 1))


def test_eikonal_peak_is_photon_sphere():
    # for large L the barrier peak frequency * b_c / (L+1/2) -> 1 (photon-sphere orbit)
    res = run()
    last = res["eikonal_scan"][-1]
    assert abs(last["wc_bc_over_l"] - 1.0) < 0.02
    # capture cross-section is the geometric 27 pi M^2 = pi b_c^2
    assert abs(res["capture_cross_section_high_freq"] - 27.0 * math.pi) < 1e-9
    assert abs(B_C - 3.0 * math.sqrt(3.0)) < 1e-12


def test_greybody_suppresses_low_frequency_hawking_flux():
    res = run()
    for s in res["hawking_spectrum"]:
        assert s["greybody_flux"] <= s["blackbody_flux"]
    # explicit: at low omega the greybody flux is far below the blackbody
    V_max, V2 = rw_peak(2, 2)
    g = greybody_wkb(0.1, V_max, V2)
    assert hawking_flux(0.1, g) < hawking_flux(0.1, 1.0)


def test_honest_scope_flags_wkb_low_freq_invalidity():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not accurate at low frequency" in sc or "wkb-limited" in sc
    assert "area theorem" in sc
    assert "not an engine constraint refit" in sc
