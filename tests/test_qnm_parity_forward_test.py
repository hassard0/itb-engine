"""Tests for the parity forward-test capstone (v2.377)."""

from experiments.qnm_parity_forward_test import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_variants_ordered_and_below_central():
    rows = _RES["parity_determinations"]
    betas = [r["beta_pred"] for r in rows]
    assert betas == sorted(betas)                 # ordered hierarchy
    assert all(b < _RES["measured_beta"][0] for b in betas)   # all below central 0.34


def test_variant_names():
    names = {r["determination"] for r in _RES["parity_determinations"]}
    assert names == {"geometric_center", "anomaly_closed_system", "anomaly_saturated", "feasibility_ceiling"}


def test_fork_needs_better_precision():
    # resolving the saturated-vs-closed fork needs much better precision than current
    assert _RES["precision_to_resolve_anomaly_fork"] < _RES["current_precision"] / 3.0
    assert _RES["precision_to_resolve_anomaly_fork"] > 0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "internal test" in f
    assert "hierarchy" in f
    assert "anomaly" in f and "cubic" in f
    sc = _RES["honest_scope"].lower()
    assert "not a claim about any specific instrument" in sc or "not a sourced number" in sc or "not a claim about" in sc
    assert "toy" in sc
    assert "v2.329" in sc
