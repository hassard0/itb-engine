"""Tests for the dark-energy equation-of-state readout (v2.424, CC3)."""

from experiments.qnm_cc_equation_of_state import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_static_vs_quintessence():
    assert _RES["w_static_true_CC"] == -1.0
    assert _RES["w_dS_conjecture_slope_c0p8"] > -1.0
    assert _RES["w_mild_quintessence_slope0p25"] > -1.0


def test_full_dS_slope_disfavored():
    # a full O(1) dS-conjecture slope pushes w far above -1, in tension with observations
    assert _RES["w_dS_conjecture_slope_c0p8"] > -0.9


def test_candidate_predicts_w_geq_minus1():
    band = _RES["candidate_predicted_w_band"]
    assert band[0] >= -1.0 - 1e-9
    assert band[1] > -1.0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "equation of state" in f
    assert "desi" in f and "euclid" in f
    assert "third" in f  # third falsification front
    sc = _RES["honest_scope"].lower()
    assert "illustrative" in sc or "order-of-magnitude" in sc
    assert "conjectural" in sc
