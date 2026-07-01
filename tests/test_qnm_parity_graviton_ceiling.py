"""Tests for the parity graviton-ceiling swing (v2.387)."""

from experiments.qnm_parity_graviton_ceiling import run

_RES = run(n_walk=8000, seed=0)   # smaller; the order-few headroom is structural


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_ceiling_far_above_value():
    assert _RES["constructed_graviton_ceiling"] > 3 * _RES["constructed_parity_value"]
    assert _RES["constructed_headroom"] > 2.0


def test_ceiling_above_cmb_2sigma():
    assert _RES["constructed_graviton_ceiling"] > _RES["cmb_2sigma_upper"]


def test_whole_region_headroom():
    assert _RES["family_headroom"]["mean"] > 2.0
    assert _RES["fraction_below_half_ceiling"] > 0.99


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "ceiling" in f
    assert "headroom" in f
    assert "falsifiable" in f
    assert "1/4" in f or "not near its" in f
    sc = _RES["honest_scope"].lower()
    assert "kappa" in sc
    assert "toy" in sc
    assert "ordering" in sc
