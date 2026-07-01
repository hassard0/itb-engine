"""Tests for the swampland field-range gap swing (v2.410)."""

from experiments.qnm_swampland_field_range_gap import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_starobinsky_super_planckian():
    assert _RES["field_range_at_N55_Mpl"] > 1.0
    for N, dphi in _RES["starobinsky_field_range_Mpl"].items():
        assert dphi > 1.0


def test_sdc_tower_below_cutoff():
    assert _RES["sdc_tower_mass_Mpl"] < _RES["species_cutoff_Mpl"]
    assert _RES["sdc_tower_mass_Mpl"] < 0.1


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "engine limitation" in f
    assert "coupling hierarchies, not field-space distances" in f or "hierarchies, not field-space" in f
    assert "swampland-coupling-complete" in f
    sc = _RES["honest_scope"].lower()
    assert "debated" in sc
    assert "imported" in sc or "not engine-computed" in sc
    assert "does not claim the candidate is ruled out" in sc or "not a definitive violation" in sc
