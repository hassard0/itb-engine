"""Tests for the UV-completion tournament / broadening (v2.436)."""

from experiments.qnm_uv_tournament import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_multiple_UV_completions_reach():
    r2 = _RES["R2_bearing_reachers"]
    assert "string_tree_eft" in r2 and "cdt" in r2 and "asymptotic_safety" in r2
    assert len(r2) >= 3


def test_only_lqg_excluded():
    assert _RES["excluded"] == ["lqg_induced"]


def test_string_closest_but_cdt_competitive():
    t = _RES["tournament"]
    assert t["string_tree_eft"]["parity_even_distance"] < t["cdt"]["parity_even_distance"]
    assert t["cdt"]["parity_even_distance"] < 0.12   # CDT a near-tie


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "not string-unique" in f or "convergence point" in f
    assert "cdt" in f and "asymptotic safety" in f
    assert "tempered" in f or "correction to the v2.434" in f
    sc = _RES["honest_scope"].lower()
    assert "encoder" in sc
    assert "tempers but does not overturn" in sc or "does not overturn" in sc
