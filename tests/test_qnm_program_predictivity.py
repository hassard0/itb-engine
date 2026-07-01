"""Tests for the program-predictivity method-as-proposal swing (v2.373)."""

from experiments.qnm_program_predictivity import run

_RES = run(n_samples=15000, seed=0)   # small n for suite speed; structural checks are n-robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_feasible_fraction_tiny_and_reduction_large():
    assert _RES["feasible_fraction_full"] < 1e-3
    assert _RES["predictivity_reduction_full"] > 1000


def test_consistency_dominates_data_small_factor():
    # data adds only a small multiplicative factor beyond consistency
    assert _RES["data_added_factor"] < 5.0


def test_a_priori_box_defined():
    box = _RES["a_priori_box"]
    assert box["cp_even_couplings"] == [0.0, 1.0]
    assert box["parity_coupling"] == [0.0, 0.2]


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "predictive" in f
    assert "consistency-driven" in f or "consistency, not data" in f
    assert "method-as-proposal" in f
    sc = _RES["honest_scope"].lower()
    assert "box-dependent" in sc
    assert "order of magnitude" in sc
    assert "toy basis" in sc
