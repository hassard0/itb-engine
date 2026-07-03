"""Tests for the complete scale-independent inflation prediction set (v2.453)."""

from experiments.qnm_inflation_consistency_set import run, predict

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_single_field_tensor_consistency():
    p = predict(0.9649)
    assert abs(p["n_t"] + p["r"] / 8.0) < 1e-12   # n_t = -r/8


def test_values_at_measured_ns():
    pr = _RES["predictions_at_measured_ns"]
    assert 0.002 < pr["r"] < 0.006
    assert pr["n_t"] < 0 and pr["alpha_s"] < 0     # both negative
    assert 40 < pr["N"] < 70


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "complete" in f and "scale-independent" in f
    assert "n_t" in f and "alpha_s" in f
    sc = _RES["honest_scope"].lower()
    assert "plateau-class" in sc
    assert "unmeasurable" in sc          # n_t, alpha_s too small
    assert "leading order" in sc
