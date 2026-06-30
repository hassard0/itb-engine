"""Tests for the region-connectivity result (v2.332)."""

from experiments.qnm_region_connectivity import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_targets_feasible_and_path_connected():
    for r in _RES["connectivity"]:
        assert r["target_feasible"] is True
        assert r["feasible_path_found"] is True


def test_straight_line_fails_somewhere_nonconvex():
    # repaired_lqg's straight line should fail (non-convex), proving connectivity is non-trivial
    lqg = next(r for r in _RES["connectivity"] if r["target"] == "repaired_lqg")
    assert lqg["straight_line_feasible"] is False
    assert lqg["feasible_path_found"] is True


def test_region_is_one_connected_family():
    assert _RES["consistency_checks"]["region_is_connected_one_family"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "connected" in f
    assert "continuous family" in f
    assert "non-convex" in f
    sc = _RES["honest_scope"].lower()
    assert "only prove connection, never disconnection" in sc or "never disconnection" in sc
    assert "toy basis" in sc
