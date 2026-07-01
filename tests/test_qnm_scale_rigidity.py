"""Tests for the scale-rigidity swing (v2.390)."""

from experiments.qnm_scale_rigidity import run

_RES = run(n_scan=201)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_bounded_scale_window():
    lo, hi = _RES["scale_window"]
    assert 0.1 < lo < 1.0
    assert 1.0 <= hi < 2.0
    assert _RES["window_factor"] < 6.0     # order-few, not a cone


def test_binding_constraints():
    assert any("cubic_graviton_matter" in c for c in _RES["lower_edge_binding"])
    assert any("anomaly" in c for c in _RES["upper_edge_binding"])


def test_constructed_near_upper_edge():
    assert _RES["constructed_position_in_window"] > 0.7   # near the strong-coupling ceiling


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "scale-rigid" in f
    assert "not a" in f and "cone" in f
    assert "no data" in f or "before any measurement" in f
    sc = _RES["honest_scope"].lower()
    assert "uniform rescaling" in sc
    assert "toy" in sc
    assert "bounded scale window" in sc or "bounded-window" in sc
