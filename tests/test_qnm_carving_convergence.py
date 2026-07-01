"""Tests for the carving-convergence swing (v2.407)."""

from experiments.qnm_carving_convergence import run

_RES = run(n_pts=3000, n_orders=120)   # smaller; the taper is robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_region_saturates_small():
    assert 0.0 < _RES["final_feasible_fraction_local_box"] < 0.05


def test_marginal_shrinkage_tapers_order_of_magnitude():
    assert _RES["marginal_drop_last_third"] < _RES["marginal_drop_first_third"]
    assert _RES["taper_ratio"] > 5.0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "converges" in f
    assert "near-saturated" in f
    assert "converged answer" in f or "converged property" in f
    sc = _RES["honest_scope"].lower()
    assert "local box" in sc
    assert "order-averaged" in sc
    assert "current constraint" in sc or "current kind" in sc or "same kind" in sc
