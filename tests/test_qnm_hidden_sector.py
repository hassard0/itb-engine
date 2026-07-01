"""Tests for the hidden-sector swing (v2.404)."""

from experiments.qnm_hidden_sector import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_g8_and_gR3parity_dark():
    up = _RES["unpinned_couplings"]
    assert up["g_8"]["dark"] is True
    assert up["g_R3_parity"]["dark"] is True


def test_gC_only_negligible_gw_data():
    dc = _RES["unpinned_couplings"]["g_C"]["data_constraints"]
    assert all("gw_" in c for c in dc)   # only GW dispersion, negligible


def test_hidden_sector_three_dim():
    assert len(_RES["unpinned_couplings"]) == 3
    assert _RES["n_fully_dark"] >= 2


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "hidden sector" in f
    assert "lower-dimensional than its parameter space" in f
    assert "corrects a qualitative aside in v2.403" in f or "does not exist in the engine" in f
    sc = _RES["honest_scope"].lower()
    assert "channel set" in sc or "channel-set-relative" in sc
    assert "not a theorem that no observable exists" in sc or "richer theory could have" in sc
