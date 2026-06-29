"""Tests for the cosmological constant problem reconstruction (v2.259)."""

from experiments.qnm_cosmological_constant_problem import overshoot, run


def test_planck_overshoot_is_1e122():
    o = overshoot(1.22e28)
    assert 1e122 < o < 1e123


def test_overshoot_scales_as_cutoff_fourth():
    # rho_vac ~ M^4
    assert abs(overshoot(2e8) / overshoot(1e8) - 16.0) < 1e-6


def test_even_low_cutoff_overshoots_hugely():
    res = run()
    rows = {r["cutoff"]: r for r in res["vacuum_energy_overshoot"]}
    # even the electron-mass cutoff overshoots by ~1e33
    assert rows["electron mass"]["overshoot_ratio"] > 1e30


def test_de_sitter_quintessence_link():
    res = run()
    ds = res["de_sitter_conjecture"]
    assert "quintessence" in ds["implication"].lower()
    assert "v2.255" in ds["links"]


def test_honest_scope_naive_scaling():
    res = run()
    sc = res["honest_scope"].lower()
    assert "naive" in sc and "controversial" in sc
    assert "susy" in sc
    assert "g_R4_c3" in res["honest_scope"]
