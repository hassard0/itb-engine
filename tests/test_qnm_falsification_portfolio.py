"""Tests for the falsification portfolio (v2.421)."""

from experiments.qnm_falsification_portfolio import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_portfolio_structure():
    port = _RES["portfolio"]
    assert len(port) == 5
    for e in port:
        assert e["observable"] and e["prediction_tier"] and e["role"]


def test_two_independent_parity_channels():
    parity_channels = [e for e in _RES["portfolio"] if "parity" in e["measures"]]
    assert len(parity_channels) >= 2   # CMB photon + GW graviton


def test_rigorous_backbone_present():
    assert any(e["prediction_tier"].startswith("RIGOROUS") for e in _RES["portfolio"])


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "two independent" in f
    assert "not hostage to one measurement" in f or "redundant probes" in f
    sc = _RES["honest_scope"].lower()
    assert "consolidation" in sc
    assert "magnitudes" in sc and "toy" in sc
