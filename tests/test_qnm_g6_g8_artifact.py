"""Tests for the g_6=g_8 center-artifact swing (v2.392)."""

from experiments.qnm_g6_g8_artifact import run

_RES = run(n_walk=9000, seed=0)   # smaller; the wide range of g_8/g_6 is robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_ratio_ranges_widely():
    r = _RES["family_g8_over_g6"]
    assert r["std"] > 0.15
    assert r["max"] / r["min"] > 2.0
    assert r["min"] < 1.0 < r["max"]      # 1.0 interior -> equality not forced


def test_not_pinned():
    assert _RES["fraction_near_equal_0p9_1p1"] < 0.6


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "artifact" in f
    assert "not a consistency prediction" in f or "not forced" in f
    assert "v2.381" in f          # ties to g_8 dark
    sc = _RES["honest_scope"].lower()
    assert "refutation is robust" in sc or "negative result" in sc
    assert "sampled-family" in sc or "sampler" in sc
