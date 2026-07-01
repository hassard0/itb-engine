"""Tests for the channel-correlation deflationary swing (v2.380)."""

from experiments.qnm_channel_correlation_structure import run

_RES = run(n_walk=10000, seed=0)   # smaller walk; the correlation structure is stable


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_screening_bh_near_identical():
    assert _RES["screening_bh_correlation"] > 0.8


def test_ringdown_orthogonal():
    assert _RES["ringdown_max_correlation_with_others"] < 0.25


def test_effective_dimension_between_two_and_four():
    d = _RES["effective_observable_dimension"]
    assert 2.0 < d < 3.5           # not four independent, not fully degenerate


def test_parity_partial_correlation():
    assert 0.3 < _RES["parity_correlation_with_g2_group"] < 0.75


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "not four independent" in f or "overstates" in f
    assert "orthogonal" in f
    assert "near-identical" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "basis-robust" in sc or "structure is basis-robust" in sc
    assert "deflation" in sc
