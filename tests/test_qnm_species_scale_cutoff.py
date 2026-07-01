"""Tests for the species-scale UV-cutoff swing (v2.394)."""

from experiments.qnm_species_scale_cutoff import run

_RES = run(n_walk=8000, seed=0)   # smaller; the near-Planckian tight cutoff is structural


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_cutoff_near_but_sub_planckian():
    L = _RES["constructed_cutoff_over_Mpl"]
    assert 0.5 < L < 1.0
    assert abs(L - (1.0 / (1.952 ** 0.5))) < 0.02


def test_cutoff_tightly_bounded():
    fam = _RES["family_cutoff_over_Mpl"]
    assert fam["max"] - fam["min"] < 0.3
    assert fam["min"] > 0.5


def test_species_bound_not_saturated():
    assert _RES["species_bound_saturation"]["max"] < 1.0


def test_ghost_ladder_consistent():
    assert _RES["ghost_scale_over_Mpl"] > _RES["family_cutoff_over_Mpl"]["max"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "species scale" in f
    assert "near-planckian" in f
    assert "validity ladder" in f or "ghost" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "proxy" in sc or "coupling sum" in sc
