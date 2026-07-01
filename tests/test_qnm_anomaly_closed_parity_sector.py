"""Tests for the closed anomaly-system parity determination (v2.371)."""

from experiments.qnm_anomaly_closed_parity_sector import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_closed_system_satisfies_both_equalities():
    assert _RES["consistency_checks"]["closed_system_satisfies_inflow_equality"] is True
    assert _RES["consistency_checks"]["closed_system_satisfies_thooft_equality"] is True


def test_predicts_full_parity_odd_sector_nonzero_cubic():
    assert _RES["predicted_g_R2_parity"] > 0.04
    assert _RES["predicted_g_R3_parity"] > 0.01     # nonzero cubic, reversing the bound-form center
    assert _RES["closed_system_feasible"] is True


def test_honest_tension_complete_fits_worse():
    # the complete (both-matched) system fits birefringence worse than saturation-only
    assert _RES["sigma_closed"] > _RES["sigma_saturation_only_v2370"]
    assert _RES["sigma_closed"] < 2.0               # still within 2 sigma (a soft preference)


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "close" in f and "parity-odd sector" in f
    assert "not data-driven" in f or "determined" in f
    assert "tension" in f
    sc = _RES["honest_scope"].lower()
    assert "exact equalit" in sc
    assert "toy" in sc
    assert "v2.329" in sc
