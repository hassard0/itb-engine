"""Tests for the third-assumption (parity cubic) swing (v2.403)."""

from experiments.qnm_third_assumption_parity_cubic import run

_RES = run(n_scan=201)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_gR3parity_zero_interior():
    lo, hi = _RES["feasible_gR3parity_range"]
    assert lo < 0.0 < hi                 # 0 interior -> not forced
    assert hi - lo > 0.02                # a genuine free window


def test_anomaly_closed_value_feasible():
    assert _RES["anomaly_closed_feasible"] is True
    assert _RES["anomaly_closed_value"] > 0.0


def test_bounded_by_anomaly_inflow():
    assert any("anomaly" in c for c in _RES["upper_edge_binding"])


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "third" in f and "assumption" in f
    assert "a=c" in f and "g_6=g_8" in f
    assert "second, cubic-order parity observable" in f or "second parity observable" in f or "second, cubic-order parity" in f
    sc = _RES["honest_scope"].lower()
    assert "toy" in sc
    assert "interior" in sc
