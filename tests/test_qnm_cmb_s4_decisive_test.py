"""Tests for the CMB-S4 decisive-test swing (v2.395)."""

from experiments.qnm_cmb_s4_decisive_test import run

_RES = run(n_walk=8000, seed=0)   # smaller; the >10-sigma region-wide exclusion is robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_excluded_by_cmb_s4():
    assert _RES["constructed_satisfies_cmb_s4"] is False
    assert _RES["constructed_tension_sigma"] > 10.0


def test_whole_region_excluded():
    thr = _RES["cmb_s4_forecast"]["threshold_sigma"]
    assert _RES["min_region_tension_sigma"] > thr
    assert _RES["min_region_tension_sigma"] > 5.0     # decisive, not marginal
    assert _RES["feasible_g4_range"][0] > 0.2         # matter dominance -> large g_4


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "make-or-break" in f
    assert "falsifies" in f
    assert "matter dominance" in f
    assert "non-gravitational observable" in f
    sc = _RES["honest_scope"].lower()
    assert "toy identification" in sc or "toy dual role" in sc or "toy-basis" in sc
    assert "forecast" in sc
