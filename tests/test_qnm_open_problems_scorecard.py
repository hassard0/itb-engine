"""Tests for the open-problems scorecard (v2.471)."""

from experiments.qnm_open_problems_scorecard import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_four_tiers_present():
    sc = _RES["scorecard"]
    assert set(sc["explains_structural"]) == {"dark_energy", "cosmic_birefringence", "baryon_asymmetry", "inflation"}
    assert "dark_matter" in sc["compatible_axiverse_available_not_predicted"]
    assert set(sc["does_not_address"]) >= {"neutrino_masses", "CC_magnitude", "hierarchy_problem"}


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "quartet" in f
    assert "not a theory of everything" in f
    assert "axiverse" in f and "not predict" in f
    sc = _RES["honest_scope"].lower()
    assert "accounting" in sc
    assert "available-not-predicted" in sc or "not a prediction" in sc
    assert "class-level" in sc
