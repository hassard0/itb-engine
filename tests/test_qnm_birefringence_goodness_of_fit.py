"""Tests for the birefringence goodness-of-fit (v2.360)."""

from experiments.qnm_birefringence_goodness_of_fit import run

_RES = run()   # default n_walk/seed -> deterministic


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_no_structural_underprediction():
    # the theory's best beta reaches within 1 sigma of the central value -> the criticism is refuted
    assert abs(_RES["best_fit_residual_sigma"]) < 1.0
    lo, hi = _RES["measured_1sigma_band"]
    assert lo <= _RES["beta_max_predictable"] <= hi


def test_center_is_conservative():
    # the constructed center underpredicts relative to the theory's feasibility ceiling
    assert _RES["beta_constructed_center"] < _RES["beta_max_predictable"]


def test_range_overlaps_and_leans_low():
    rng = _RES["theory_beta_range"]
    assert rng[0] < rng[1]
    # the theory's ceiling leans below the measured central value (a mild low lean, not a tension)
    assert _RES["beta_max_predictable"] < _RES["measured_beta"][0]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "refuted" in f
    assert "underpredict" in f
    assert "mild" in f and "lean" in f
    sc = _RES["honest_scope"].lower()
    assert "search, not a proof" in sc or "not a proof" in sc
    assert "v2.329" in sc
    assert "toy basis" in sc
