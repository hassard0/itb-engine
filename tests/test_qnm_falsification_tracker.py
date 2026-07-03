"""Tests for the falsification tracker (v2.449)."""

from experiments.qnm_falsification_tracker import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_every_prediction_has_kill_condition():
    for t in _RES["tracker"]:
        assert len(t["kill_condition"]) > 0
        assert "prediction" in t and "current_status" in t


def test_gR2_over_determination_present():
    ids = {t["id"] for t in _RES["tracker"]}
    assert "gR2_over_determination" in ids
    assert "primordial_null" in ids


def test_none_excluded():
    for t in _RES["tracker"]:
        st = t["current_status"].lower()
        assert "ruled out" not in st and "candidate excluded" not in st


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "dual of the consilience" in f
    assert "over-determination" in f
    assert "birefringence" in f
    sc = _RES["honest_scope"].lower()
    assert "consolidation" in sc
    assert "hint" in sc
    assert "plateau-class" in sc or "plateau class" in sc
