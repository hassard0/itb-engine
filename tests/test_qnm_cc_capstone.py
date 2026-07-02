"""Tests for the CC-arc capstone (v2.425)."""

from experiments.qnm_cc_capstone import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_profile_three_pillars():
    prof = _RES["dark_energy_profile"]
    assert prof["admits_dark_energy"]["g_Lambda_dS_window"][1] > 0.05     # admits DE
    assert prof["selects_de_sitter"]["ads_branch"] is None                 # selects dS
    band = prof["equation_of_state"]["w_band"]
    assert band[0] >= -1.0 - 1e-9 and band[1] > -1.0                       # w >~ -1


def test_sector_conjectural_tiered():
    assert "sourced_proxy" in _RES["cc_sector_rigor_tier"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "dark-energy profile" in f
    assert "inflation-to-dark-energy" in f or "inflation->dark-energy" in f or "keystone scalaron" in f
    sc = _RES["honest_scope"].lower()
    assert "consolidation" in sc
    assert "cc magnitude problem" in sc or "not the cc magnitude" in sc
    assert "conjectural" in sc
