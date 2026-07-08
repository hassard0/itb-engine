"""Tests for the swampland pattern (v2.473)."""

from experiments.qnm_swampland_pattern import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_axion_wgc_violation():
    assert _RES["S_needed_DE_axion"] > 100
    assert _RES["axion_wgc_violation_factor"] > 100


def test_violations_are_aggressive_and_map_to_observables():
    m = _RES["swampland_membership"]
    assert set(_RES["violated"]) == {"TCC", "axion_WGC"}
    for k in _RES["violated"]:
        assert m[k]["class"] == "aggressive"
        assert "observable" in m[k]
    # all structural ones are satisfied
    structural = [k for k, v in m.items() if v["class"] == "structural"]
    assert all(m[k]["status"] == "SATISFIES" for k in structural)
    assert len(structural) == 5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "pattern" in f
    assert "aggressive" in f and "observable" in f
    assert "litebird" in f and "desi" in f
    sc = _RES["honest_scope"].lower()
    assert "class-level" in sc
    assert "contested" in sc
    assert "interpretation, not a" in sc or "not a theorem" in sc
