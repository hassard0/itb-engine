"""Tests for the ghost-safety swing (v2.385)."""

from experiments.qnm_ghost_safety import run

_RES = run(n_walk=8000, seed=0)   # smaller; g_C<1 across the region is structural


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_ghost_above_cutoff():
    assert _RES["constructed_ghost_mass_over_cutoff"] > 1.0
    assert abs(_RES["constructed_ghost_mass_over_cutoff"] - (0.193 ** -0.5)) < 0.02


def test_whole_region_ghost_safe():
    assert _RES["region_max_g_C"] < 1.0
    assert _RES["region_min_ghost_mass_over_cutoff"] >= 1.5


def test_wgc_guarantees_it():
    assert _RES["wgc_bound_holds"] is True
    assert _RES["g4_below_one"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "ostrogradsky" in f
    assert "above the" in f and "cutoff" in f
    assert "wgc" in f or "weak gravity" in f
    assert "v2.375" in f       # tower as UV resolution
    sc = _RES["honest_scope"].lower()
    assert "o(1)" in sc
    assert "toy" in sc
    assert "eft-sense" in sc or "standard eft stance" in sc or "low-energy pathology" in sc
