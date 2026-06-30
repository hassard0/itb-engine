"""Tests for the parity-hierarchy / distance-conjecture bound (v2.326)."""

from experiments.qnm_parity_hierarchy_bound import run, hierarchy

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_parity_violation_stretches_hierarchy():
    assert _RES["min_odd_hierarchy"] > _RES["max_even_hierarchy"]
    # exact arithmetic check
    assert abs(hierarchy({"g_4": 0.5, "g_6": 0.4}) - 1.25) < 1e-9


def test_both_bounds_lower_bound_parity():
    assert _RES["distance_conjecture_parity_lower_bound"] > 0
    assert _RES["data_parity_lower_bound"] > 0
    # data tighter than the distance-conjecture bound
    assert _RES["data_parity_lower_bound"] > _RES["distance_conjecture_parity_lower_bound"]


def test_lqg_largest_hierarchy_near_limit():
    h = {r["theory"]: r["hierarchy"] for r in _RES["hierarchies"]}
    assert h["lqg_induced"] == max(v for v in h.values())
    assert h["lqg_induced"] >= 0.6 * _RES["implied_R_max"]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "distance conjecture" in f
    assert "hierarchy" in f
    assert "both" in f and "push the parity coupling up" in f
    sc = _RES["honest_scope"].lower()
    assert "exact arithmetic" in sc
    assert "toy basis" in sc
