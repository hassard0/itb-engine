"""Tests for the handedness-as-data-readout result (v2.364)."""

from experiments.qnm_handedness_data_readout import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_left_right_positivity_are_the_asymmetric_pair():
    asym = _RES["theoretical_asymmetric_constraints"]
    assert set(asym) == {"left_handed_graviton_positivity", "right_handed_graviton_positivity"}


def test_no_net_theoretical_handedness_preference():
    # the min theoretical margin is identical for +/- g_R2_parity (mirror-paired constraints)
    assert abs(_RES["min_theoretical_margin_plus"] - _RES["min_theoretical_margin_minus"]) < 1e-6


def test_both_signs_theoretically_feasible_only_data_breaks_tie():
    assert _RES["theo_feasible_plus"] is True
    assert _RES["theo_feasible_minus"] is True
    # birefringence: satisfied for +, violated for -
    assert _RES["birefringence_margin_plus"] > 0
    assert _RES["birefringence_margin_minus"] < 0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "data-readout" in f
    assert "mirror-paired" in f
    assert "existence" in f and "magnitude" in f and "sign" in f
    sc = _RES["honest_scope"].lower()
    assert "encoding choice" in sc or "encoding" in sc
    assert "v2.329" in sc
    assert "toy basis" in sc
