"""Tests for entanglement-amplified ringdown floor (v2.301)."""

import math

from experiments.qnm_entanglement_amplified_ringdown import (
    entanglement_bound,
    gR4_floor,
    positivity_bound,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_frameworks_have_unit_amplification():
    # mildly-asymmetric frameworks are positivity-floored -> entanglement adds no amplification
    res = run()
    for r in res["framework_floors"]:
        assert r["binding_sector"] == "positivity"
        assert abs(r["amplification"] - 1.0) < 1e-9


def test_asymmetric_point_amplifies():
    res = run()
    a = res["asymmetric_test_point"]
    assert a["entanglement_bound"] < a["positivity_bound"]   # entanglement binds
    assert a["gR4_floor"] > a["gR4_floor_positivity_only"]   # higher floor
    assert a["amplification"] > 1.0
    # amplification = (2/3) AM/GM
    assert abs(a["amplification"] - (2 / 3) * a["AM_over_GM"]) < 1e-9


def test_floor_formula():
    # g_R4 floor = g_R3^2 / g_R2_max
    assert abs(gR4_floor(0.3, 1.36) - 0.09 / 1.36) < 1e-9


def test_bounds_are_harmonic_and_geometric():
    assert abs(entanglement_bound(0.5, 0.5) - 1.5 * 0.5) < 1e-9   # (3/2) harmonic mean at g4=g6
    assert abs(positivity_bound(0.5, 0.5) - 0.5) < 1e-9           # geometric mean at g4=g6


def test_honest_scope_flags_coupling_level_and_dark_parity():
    res = run()
    sc = res["honest_scope"].lower()
    assert "prefactor-robust" in sc
    assert "dark-parity" in sc or "v2.209" in sc
    assert "coupling-level" in sc
