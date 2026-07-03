"""Tests for the dark-energy thawing-line consistency relation + DESI tension (v2.454)."""

from experiments.qnm_dark_energy_thawing_line import run, wa_thawing

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_thawing_relation():
    assert abs(wa_thawing(-0.9) - (-0.15)) < 1e-9
    assert abs(wa_thawing(-1.0)) < 1e-12   # w0 = -1 => wa = 0


def test_desi_tension():
    d = _RES["desi_central"]
    assert d["early_w"] < -1.0                       # phantom past
    assert _RES["desi_wa_steepness_factor"] > 2      # DESI wa steeper than thawing line


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "most vulnerable front" in f
    assert "canonical thawing" in f
    assert "w >= -1" in f or "phantom" in f
    sc = _RES["honest_scope"].lower()
    assert "representative" in sc
    assert "tension in trend" in sc or "trend-tension" in sc or "not a falsification" in sc
    assert "cpl" in sc
