"""Tests for the holographic eta/s bug-fix (v2.462)."""

from experiments.qnm_holographic_etas_fix import run


_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_two_modules_agree():
    assert abs(_RES["eta_over_s_candidate"] - _RES["eta_over_s_candidate_holographic_ac_module"]) < 1e-9


def test_candidate_kss_violating_and_correct_value():
    assert 0 < _RES["eta_over_s_candidate"] < 1.0
    assert abs(_RES["eta_over_s_candidate"] - 0.833) < 0.02       # ~0.81-0.83, not the old 0.665
    assert abs(_RES["eta_over_s_candidate"] - _RES["old_wrong_value_1_minus_8L"]) > 0.1


def test_brigante_floor():
    assert abs(_RES["eta_over_s_largest_gR2"] - 16.0 / 25.0) < 0.02


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "factor-of-2 error" in f
    assert "1 - 4 lambda" in f
    assert "16/25" in f
    sc = _RES["honest_scope"].lower()
    assert "what-if" in sc
    assert "observable" in sc and "not a" in sc  # observable not constraint
    assert "ordering" in sc
