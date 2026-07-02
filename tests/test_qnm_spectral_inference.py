"""Tests for the spectral-inference cycle (v2.438)."""

from experiments.qnm_spectral_inference import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_candidate_interior_multi_state():
    assert _RES["candidate_saturation"] < 0.95   # interior => tower
    assert _RES["candidate_saturation"] > 0.0


def test_all_viable_interior():
    st = _RES["saturation_table"]
    for n in ("string_tree_eft", "asymptotic_safety", "cdt"):
        assert st[n] is not None and st[n] < 0.95


def test_rankings_differ():
    assert _RES["closest_by_saturation"] != _RES["closest_by_distance"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "multi-state" in f and "tower" in f
    assert "cannot see the tower's type" in f or "not the tower's type" in f or "not its type" in f
    sc = _RES["honest_scope"].lower()
    assert "chebyshev-center artifact" in sc or "artifact" in sc
    assert "interior" in sc
