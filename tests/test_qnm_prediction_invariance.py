"""Tests for the prediction-invariance result (v2.334)."""

from experiments.qnm_prediction_invariance import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_predictions_modest_spread():
    b = _RES["predictions_across_family"]["beta_deg"]
    assert b["rel_spread"] < 0.25
    assert 0.15 <= b["mean"] <= 0.27       # the family beta band


def test_parity_stiffer_than_matter():
    # parity relative spread is smaller than the widest matter spread
    assert _RES["parity_relative_spread"] <= max(_RES["matter_relative_spreads"].values())


def test_matter_freedom_wider_than_predictions():
    b_rel = _RES["predictions_across_family"]["beta_deg"]["rel_spread"]
    assert max(_RES["matter_relative_spreads"].values()) > b_rel


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "pinned" in f and "parity" in f
    assert "observationally hidden" in f
    assert "predictively sharp" in f or "sharp despite" in f
    sc = _RES["honest_scope"].lower()
    assert "by construction" in sc
    assert "toy basis" in sc
