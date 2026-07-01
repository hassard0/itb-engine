"""Tests for the graviton chirality-asymmetry swing (v2.386)."""

from experiments.qnm_graviton_chirality_asymmetry import run

_RES = run(n_walk=8000, seed=0)   # smaller; the order-2 asymmetry + L-tighter are structural


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_asymmetry_and_left_tighter():
    assert _RES["constructed_LR_asymmetry"] > 1.5
    assert _RES["constructed_margins"]["left"] < _RES["constructed_margins"]["right"]


def test_family_order_two_asymmetry():
    assert _RES["family_LR_asymmetry"]["mean"] > 1.5
    assert _RES["family_LR_asymmetry"]["min"] >= 1.0


def test_left_always_tighter():
    assert _RES["family_left_tighter_fraction"] > 0.99


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "left" in f and "right" in f and "asymmetry" in f
    assert "cross-messenger" in f
    assert "handedness" in f
    sc = _RES["honest_scope"].lower()
    assert "kappa-independent" in sc or "ratio" in sc
    assert "toy" in sc
    assert "amplitude-level" in sc or "not identical to the kinematic" in sc
