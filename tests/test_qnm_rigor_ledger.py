"""Tests for the rigor-ledger consolidation capstone (v2.415)."""

from experiments.qnm_rigor_ledger import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_structural_claims_are_rigorous():
    assert _RES["n_structural_rigorous"] >= 8
    for e in _RES["rigor_ledger"]:
        if e["tier"] in ("rigorous", "rigorous_implied"):
            assert e["established_by"]


def test_matter_sources_gravity_floor():
    assert _RES["matter_sources_gravity_floor"] > 0.05


def test_parity_is_the_residual_toy():
    parity = [e for e in _RES["rigor_ledger"] if "parity MAGNITUDE" in e["claim"]][0]
    assert "toy" in parity["tier"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "is the engine a toy" in f
    assert "matter-gravity content is source-exact" in f or "matter-gravity physics" in f
    sc = _RES["honest_scope"].lower()
    assert "consolidation" in sc
    assert "encoding-dependent" in sc or "framework encodings" in sc
