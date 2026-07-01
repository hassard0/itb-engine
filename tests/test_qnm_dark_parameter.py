"""Tests for the dark-parameter swing (v2.381)."""

from experiments.qnm_dark_parameter import run

_RES = run(n_walk=10000, seed=0)   # smaller walk; g_8's darkness is structural and stable


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_g8_is_uniquely_dark():
    assert _RES["dark_couplings"] == ["g_8"]
    assert _RES["coupling_observability"]["g_8"]["max_abs_corr"] < 0.25


def test_other_couplings_observable():
    obs = _RES["coupling_observability"]
    for k in ("g_4", "g_6", "g_R2", "g_R3", "g_R2_parity"):
        assert obs[k]["status"] != "DARK"


def test_observable_couplings_map_to_channels():
    obs = _RES["coupling_observability"]
    assert obs["g_R2"]["correlations"]["screening"] > 0.8
    assert obs["g_R3"]["correlations"]["ringdown"] > 0.8
    assert obs["g_R2_parity"]["correlations"]["parity"] > 0.8


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "dark" in f
    assert "string-like matter" in f
    assert "hidden" in f or "cannot touch" in f
    sc = _RES["honest_scope"].lower()
    assert "structural" in sc
    assert "toy" in sc
