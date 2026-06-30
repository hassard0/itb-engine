"""Tests for the parity-prefactor robustness audit (v2.344)."""

import math

from experiments.qnm_parity_prefactor_robustness import run, anomaly_upper, PROD, CONSTRUCTED_PARITY


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_window_nonempty_and_positive_across_band():
    res = run()
    for r in res["scan"]:
        assert r["window_nonempty"] is True, r["anomaly_rho"]
        assert r["joint_window"][0] > 0.0


def test_constructed_excluded_at_band_bottom_only():
    res = run()
    bottom = res["scan"][0]
    assert abs(bottom["anomaly_rho"] - 0.03) < 1e-9
    assert bottom["constructed_0p06_survives"] is False
    # everything at/above the survival threshold passes
    for r in res["scan"]:
        if r["anomaly_rho"] >= res["threshold_rho_constructed_survives"] + 1e-9:
            assert r["constructed_0p06_survives"] is True


def test_thresholds_closed_form():
    res = run()
    # constructed survives iff rho >= 0.06^2 / (g4 gR2)
    assert abs(res["threshold_rho_constructed_survives"] - CONSTRUCTED_PARITY ** 2 / PROD) < 1e-3
    # window opens iff rho >= bire_lo^2 / (g4 gR2); bire_lo = 0.0471
    assert abs(res["threshold_rho_window_opens"] - 0.0471 ** 2 / PROD) < 1e-3
    # the survival threshold lies INSIDE the declared band (this is the fragility)
    lo, hi = res["declared_anomaly_rho_band"]
    assert lo < res["threshold_rho_constructed_survives"] < hi


def test_anomaly_upper_matches_engine_at_default():
    # closed form at default rho 0.06
    assert abs(anomaly_upper(0.06) - math.sqrt(0.06 * PROD)) < 1e-12
    res = run()
    assert res["consistency_checks"]["closed_form_matches_engine_constraint"] is True


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "robust" in f and "prefactor" in f
    assert "0.0353" in f or "0.035" in f
    sc = res["honest_scope"].lower()
    assert "toy basis" in sc
    assert "v2.329" in sc or "birefringence data being real" in sc
