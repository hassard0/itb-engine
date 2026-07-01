"""Tests for the anomaly-saturation parity prediction swing (v2.370)."""

import math

from experiments.qnm_anomaly_saturation_parity import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_saturation_value_from_even_sector():
    res = run()
    # g_R2_parity = sqrt(rho g_4 g_R2)
    assert abs(res["predicted_g_R2_parity_saturation"] - math.sqrt(res["anomaly_rho"] * 0.529 * 0.193)) < 1e-3
    # it is the upper edge of the data window (above the Chebyshev center)
    assert res["predicted_g_R2_parity_saturation"] > res["chebyshev_center_g_R2_parity"]


def test_saturation_on_engine_boundary_and_feasible():
    res = run()
    assert res["consistency_checks"]["saturation_margin_zero_on_engine_constraint"] is True
    assert res["saturation_feasible"] is True


def test_fits_data_better_than_center():
    res = run()
    assert res["sigma_saturation"] < 2.0
    assert res["sigma_saturation"] < res["sigma_center"]


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "anomaly matching" in f
    assert "theoretical" in f
    assert "sign is still data-set" in f or "sign remains data-set" in f or "not entirely data-driven" in f
    sc = res["honest_scope"].lower()
    assert "exact equality" in sc
    assert "toy" in sc
    assert "v2.329" in sc
