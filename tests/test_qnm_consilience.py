"""Tests for the consilience / convergent-backbone capstone (v2.446)."""

from experiments.qnm_consilience import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_seven_areas_all_satisfied():
    theoretical = {a: s for a, s in _RES["area_summary"].items() if a != "observational_data"}
    assert len(theoretical) == 7
    for a, s in _RES["area_summary"].items():
        assert s["all_satisfied"] is True, a


def test_rigorous_core_spans_three_areas():
    areas = _RES["rigorous_core_areas"]
    assert len(areas) == 3
    for a in ("analyticity_unitarity", "causality", "holography_cft"):
        assert a in areas


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "consilience" in f
    assert "seven independent" in f or "seven distinct" in f or "seven" in f
    assert "spans three of the seven" in f or "three of the seven" in f
    sc = _RES["honest_scope"].lower()
    assert "not a theorem about independence" in sc or "not a proof" in sc
    assert "interconnection" in sc or "correlated" in sc  # some pairs linked
    assert "epistemic" in sc
