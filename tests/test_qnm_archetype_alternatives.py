"""Tests for the archetype-alternatives map (v2.420)."""

from experiments.qnm_archetype_alternatives import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_candidate_survives():
    assert _RES["archetype_table"]["A_candidate"]["full_feasible"] is True


def test_parity_conserving_is_the_live_rival():
    b = _RES["archetype_table"]["B_parity_conserving"]
    assert b["rigorous_feasible"] is True
    assert b["full_feasible"] is False
    assert b["full_violations"] == ["cosmic_birefringence_data"]


def test_extreme_archetypes_rigorously_excluded():
    assert _RES["archetype_table"]["D_curvature_heavy"]["rigorous_feasible"] is False
    assert _RES["archetype_table"]["E_matter_light"]["rigorous_feasible"] is False


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "single live rival" in f
    assert "is cosmic birefringence real" in f
    sc = _RES["honest_scope"].lower()
    assert "representative" in sc
    assert "contingent" in sc
