"""Tests for the screening-mandate third channel (v2.354)."""

from experiments.qnm_screening_mandate import run

_RES = run(n_search=4000, seed=0)   # region is empty, so any N finds nothing -> small N is conclusive


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_violates_unscreened_only_submm():
    assert _RES["constructed_g_R2"] > _RES["g_R2_max_unscreened"]
    assert _RES["constructed_over_bound_factor"] > 2.0
    # under the unscreened stack the constructed point fails ONLY the sub-mm bound
    assert _RES["constructed_violations_unscreened"] == ["submm_gravity_yukawa_bound"]


def test_screened_feasible():
    assert _RES["constructed_violations_screened"] == []


def test_unscreened_region_empty():
    assert _RES["unscreened_region_empty"] is True
    assert _RES["unscreened_feasible_point"] is None
    # analytic corroboration: unscreened feasibility would need g_4 >= ~0.59
    assert _RES["analytic_g4_min_for_unscreened"] > 0.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "mandates screening" in f or "mandate" in f
    assert "third" in f and "channel" in f
    assert "load-bearing" in f
    sc = _RES["honest_scope"].lower()
    assert "empirical" in sc
    assert "v2.329" in sc
    assert "toy basis" in sc
