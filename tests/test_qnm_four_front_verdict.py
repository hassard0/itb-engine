"""Tests for the four-front unified verdict (v2.442)."""

from experiments.qnm_four_front_verdict import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_four_experiments_three_keystones():
    assert len(_RES["fronts"]) == 4
    assert len(_RES["independent_keystones"]) == 3


def test_gR2_over_determined():
    assert set(_RES["gR2_experiments"]) == {"DESI_dark_energy_w", "LiteBIRD_tensors"}


def test_one_of_eight_patterns():
    assert _RES["n_sign_patterns"] == 8


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "over-determined" in f
    assert "litebird" in f and "desi" in f
    assert "falsified" in f
    sc = _RES["honest_scope"].lower()
    assert "structural" in sc
    assert "sign" in sc
    assert "plateau-class" in sc or "plateau class" in sc
