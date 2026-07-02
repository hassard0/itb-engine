"""Tests for the two-layer structure of solving QG (v2.439)."""

from experiments.qnm_two_layers import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_engine_presupposes_graviton():
    assert _RES["einstein_hilbert_carved"] is False
    # only higher-derivative couplings; no Einstein/dim-2/Newton coupling
    for k in _RES["engine_coupling_keys"]:
        assert k not in ("g_R", "g_EH", "G_N", "g_2")
    assert "g_R2" in _RES["engine_coupling_keys"]


def test_two_layers_defined():
    L = _RES["two_layers"]
    assert "quantum" in L["layer_1_is_gravity_quantum"]["question"].lower()
    assert "presupposed" in L["layer_1_is_gravity_quantum"]["status_in_program"].lower()
    assert "bmv" in L["layer_1_is_gravity_quantum"]["decisive_test"].lower()
    assert "which" in L["layer_2_which_QG_EFT"]["question"].lower()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "two layers" in f
    assert "presupposes" in f and "bmv" in f
    assert "observationally separate" in f
    sc = _RES["honest_scope"].lower()
    assert "foundational framing" in sc
    assert "debated" in sc  # BMV reasoning contested
