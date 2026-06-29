"""Tests for the Dvali species scale (v2.264)."""

import math

from experiments.qnm_inflation_tensor_qg import M_PL_GEV
from experiments.qnm_species_scale import (
    min_bh_entropy,
    run,
    species_for_cutoff,
    species_scale_gev,
)


def test_species_scale_closed_form():
    for n in (1.0, 118.0, 1e6, 1e32):
        assert abs(species_scale_gev(n) - M_PL_GEV / math.sqrt(n)) < 1e-6 * species_scale_gev(n)


def test_smallest_bh_entropy_equals_N():
    # the defining property: a BH at the species scale carries entropy exactly N
    for n in (1.0, 118.0, 1e3, 1e6, 1e32):
        assert abs(min_bh_entropy(n) - n) < 1e-6 * max(n, 1.0)
    res = run()
    for row in res["species_grid"]:
        assert row["min_bh_entropy_equals_N"] is True


def test_loglog_slope_is_minus_half():
    res = run()
    assert res["slope_is_minus_half"] is True
    assert abs(res["loglog_slope_lambda_vs_N"] + 0.5) < 1e-9


def test_add_reproduces_famous_species_count():
    # lowering the cutoff to a TeV needs ~1e31 (reduced) / ~1e32 (full M_Pl) species
    res = run()
    a = res["add_tev_cutoff"]
    assert 1e30 < a["N_for_TeV_reduced_Mpl"] < 1e31
    assert 1e32 < a["N_for_TeV_full_Mpl"] < 1e33
    # inverse consistency: species_for_cutoff and species_scale_gev are inverses
    n = species_for_cutoff(1e3)
    assert abs(species_scale_gev(n) - 1e3) < 1e-6 * 1e3


def test_sm_cutoff_about_an_order_below_planck():
    res = run()
    sm = next(r for r in res["species_grid"] if r["N"] == 118.0)
    assert 0.05 < sm["lambda_sp_over_Mpl"] < 0.15   # ~ 0.09 M_Pl


def test_honest_scope_flags_prefactor_and_convention():
    res = run()
    sc = res["honest_scope"].lower()
    assert "prefactor" in sc and "convention" in sc
    assert "order-of-magnitude" in sc
    assert "exponent" in sc
