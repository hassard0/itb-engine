"""Tests for the axion-universality consequence (v2.435)."""

from experiments.qnm_axion_universality import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_heterotic_curvature_consistency():
    hc = _RES["heterotic_curvature_consistency"]
    assert hc["g_R2_positive_gauss_bonnet"]
    assert hc["g_R3_positive"]
    assert hc["candidate_plus_tower_feasible"]
    assert hc["parity_positive_handedness_matches_CMB_beta"]


def test_universality_consequence_present():
    uc = _RES["universality_consequence"]
    assert "universal" in uc["claim"].lower() and "determined" in uc["claim"].lower()
    assert "predicts" in uc["implication_1"].lower()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "universal" in f
    assert "predicts cosmic birefringence" in f
    assert "parameter" in f
    sc = _RES["honest_scope"].lower()
    assert "physics argument" in sc
    assert "model-independent" in sc and "contingent" in sc
    assert "magnitude" in sc and "string scale" in sc
