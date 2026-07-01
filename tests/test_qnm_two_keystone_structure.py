"""Tests for the two-keystone structure swing (v2.401)."""

from experiments.qnm_two_keystone_structure import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_two_keystones_are_matter_and_curvature():
    assert set(_RES["keystone_pair"]) == {"g_4", "g_R2"}
    load = _RES["constraint_load"]
    assert load["g_4"]["fraction"] > 0.5
    assert load["g_R2"]["fraction"] > 0.5


def test_g4_is_top():
    assert _RES["constraint_load"]["g_4"]["count"] >= _RES["constraint_load"]["g_R2"]["count"]


def test_no_third_keystone_and_free_pair():
    # third-ranked coupling is below 50%
    assert _RES["ranked"][2][1] < _RES["n_total_constraints"] / 2
    assert set(_RES["free_pair"]) == {"g_8", "g_C"}


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "two-keystone" in f
    assert "matter-gravity locking" in f
    assert "no third" in f or "no second hidden degeneracy" in f
    sc = _RES["honest_scope"].lower()
    assert "basis-dependent" in sc
    assert "no more degeneracy is visible without a finer basis" in sc or "not 'the basis is complete'" in sc
