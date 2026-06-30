"""Tests for the prefactor-robustness audit under convex_hull (v2.320)."""

from experiments.qnm_prefactor_robustness_convex_hull import run

_RES = run()  # one ensemble; reuse across tests (deterministic seed)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_beats_community_is_robust():
    assert _RES["fractions"]["constructed_beats_community"] >= 0.9


def test_lqg_boundary_is_robust():
    assert _RES["fractions"]["lqg_is_boundary"] >= 0.7


def test_community_feasibility_is_fragile():
    # the v2.317 community-feasibility holds in a minority of O(1) prefactor draws
    assert _RES["fractions"]["not_universal_exclusion"] < 0.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "knife's edge" in f
    assert "robust" in f and "fragile" in f
    sc = _RES["honest_scope"].lower()
    assert "realism program" in sc
    assert "house-number" in sc
    assert "toy basis" in sc
