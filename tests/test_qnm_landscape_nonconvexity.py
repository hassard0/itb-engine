"""Tests for the landscape non-convexity swing (v2.383)."""

from experiments.qnm_landscape_nonconvexity import run

_RES = run(n_walk=6000, n_pairs=3000, seed=0)   # smaller; the non-convexity + SDC attribution are stable


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_region_is_non_convex():
    assert _RES["fraction_nonconvex_full_stack"] > 0.02


def test_sdc_is_dominant_cause():
    assert _RES["sdc_share_of_violations"] > 0.9


def test_dropping_sdc_restores_convexity():
    assert _RES["fraction_nonconvex_without_sdc"] < 0.01
    # the amplitude sector is essentially convex compared to the full stack
    assert _RES["fraction_nonconvex_without_sdc"] < _RES["fraction_nonconvex_full_stack"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "non-convex" in f
    assert "swampland distance conjecture" in f or "sdc" in f
    assert "amplitude" in f and "convex" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "aspect-ratio" in sc
    assert "near-zero" in sc or "coupling exactly zero" in sc or "approaches-zero" in sc
