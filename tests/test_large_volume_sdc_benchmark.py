"""Regression tests for v2.37 large-volume SDC benchmark audit."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from large_volume_sdc_benchmark import diagnose_large_volume_sdc_benchmark  # noqa: E402


def test_large_volume_benchmark_is_schema_ready_and_math_excluding_only():
    result = diagnose_large_volume_sdc_benchmark()
    candidate = result["candidate"]

    assert result["benchmark_status"]["schema_ready"] is True
    assert result["benchmark_status"]["math_excluding_if_delta1_assumed"] is True
    assert result["benchmark_status"]["framework_claim_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert candidate["claimable_now"] is False
    assert "delta_moduli_equals_one_is_benchmark_not_framework_prediction" in (
        candidate["scope_blockers"]
    )


def test_large_volume_benchmark_conservative_lambda_exceeds_threshold():
    result = diagnose_large_volume_sdc_benchmark()
    candidate = result["candidate"]
    spectrum = candidate["evidence"]["spectrum"]
    summary = spectrum["metadata"]["lambda_summary"]

    assert summary["lambda_sdc_min"] > candidate["critical_phi_tower"]
    assert spectrum["phi_tower_mean"] == pytest.approx(summary["lambda_sdc_mean"])
    assert candidate["two_sigma_phi_interval"][0] > candidate["critical_phi_tower"]
    assert candidate["conservative_delta_moduli_required_for_exclusion"] < 1.0


def test_large_volume_benchmark_records_uncertainty_and_scope_guardrails():
    result = diagnose_large_volume_sdc_benchmark()
    candidate = result["candidate"]
    summary = candidate["evidence"]["spectrum"]["metadata"]["lambda_summary"]

    assert candidate["framework_tower_verdict"] == "tower_excluded_by_predictive_spectrum"
    assert candidate["tower_claimable_by_math"] is True
    assert "not a statistical measurement uncertainty" in summary["angular_variation_note"]
    assert "one-Planck displacement" in result["literature_guardrail"]["claim"]
