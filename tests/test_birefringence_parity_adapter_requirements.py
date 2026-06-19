"""Regression tests for v2.56 birefringence parity adapter requirements."""

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from birefringence_parity_adapter_requirements import (  # noqa: E402
    diagnose_birefringence_parity_adapter_requirements,
)


def test_birefringence_adapter_keeps_route_alive_but_nonclaimable():
    result = diagnose_birefringence_parity_adapter_requirements()

    assert result["route"] == "cosmic_birefringence"
    assert result["route_status"] == "parity_adapter_required_not_satisfied"
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert (
        result["evidence_freshness_snapshot"]["route_status"]
        == "alive_but_not_claimable"
    )
    assert result["evidence_freshness_snapshot"]["positive_sign_dataset_count"] == 5


def test_current_beta_mapping_is_explicitly_toy_not_source_backed():
    result = diagnose_birefringence_parity_adapter_requirements()
    mapping = result["engine_current_mapping"]

    assert mapping["formula"] == "beta_pred_deg = KAPPA_BETA * g_R2_parity"
    assert mapping["kappa_beta_deg_per_unit_g_R2_parity"] == pytest.approx(3.4)
    assert mapping["mapping_status"] == "toy_order_of_magnitude_not_source_backed"
    lo, hi = mapping["preferred_g_R2_parity_band_2sigma"]
    assert lo > 0.0
    assert lo < 0.1 < hi


def test_adapter_requirements_cover_operator_map_systematics_and_circularity():
    result = diagnose_birefringence_parity_adapter_requirements()
    requirement_ids = {row["id"] for row in result["adapter_requirements"]}

    assert {
        "source_backed_operator_identity",
        "beta_to_engine_axis_normalization",
        "em_vs_gravitational_parity_separation",
        "frequency_and_redshift_transfer_model",
        "public_likelihood_or_covariance",
        "absolute_angle_calibration_closure",
        "foreground_systematics_closure",
        "five_sigma_or_preregistered_subclaim",
        "non_circular_framework_predictions",
        "excluding_discriminator_math",
    } <= requirement_ids
    assert "non_circular_framework_predictions" in result["open_adapter_requirements"]


def test_current_guard_blocks_toy_axis_mapping_and_open_systematics():
    result = diagnose_birefringence_parity_adapter_requirements()
    blockers = set(result["current_guard"]["blockers"])

    assert result["current_guard"]["ready_for_promotion"] is False
    assert "axis_mapping_not_source_backed" in blockers
    assert "systematics_not_closed" in blockers
    assert "discriminator_math_not_excluding" in blockers
    assert "external_measurement_evidence_not_ready" in blockers


def test_claim_blockers_include_birefringence_specific_promotion_blockers():
    result = diagnose_birefringence_parity_adapter_requirements()
    blockers = set(result["claim_blockers"])

    assert "operator_identity_not_source_backed" in blockers
    assert "beta_axis_normalization_toy" in blockers
    assert "em_gravity_parity_map_not_separated" in blockers
    assert "data_driven_eft_reuses_birefringence" in blockers
    assert "no_5sigma_single_dataset_detection" in blockers
