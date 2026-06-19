"""Regression tests for the v2.52 non-tower promotion guard."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from nontower_promotion_guard_audit import (  # noqa: E402
    diagnose_nontower_promotion_guard_audit,
)
from itb.nontower import (  # noqa: E402
    ExternalMeasurementEvidence,
    evaluate_nontower_promotion_guard,
    validate_external_measurement_evidence,
)


def test_external_measurement_evidence_ready_path():
    evidence = ExternalMeasurementEvidence(
        axis="g_8",
        route="fixture",
        source_url="https://doi.org/10.0000/test",
        source_type="validated_measurement",
        measurement_kind="external_numeric_measurement",
        numerical_value=0.4,
        uncertainty=0.02,
        axis_mapping_kind="source_backed_direct",
        systematics_status="closed",
    )

    validation = validate_external_measurement_evidence(evidence)
    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=True,
    )

    assert validation["ready_for_discriminator_claim"] is True
    assert validation["blockers"] == []
    assert guard["ready_for_promotion"] is True
    assert guard["blockers"] == []


def test_external_measurement_guard_blocks_internal_proxy():
    evidence = ExternalMeasurementEvidence(
        axis="g_C",
        route="complexity_proxy",
        source_url="https://arxiv.org/abs/1509.07876",
        source_type="primary_literature",
        measurement_kind="holographic_proxy_toy_normalization",
        numerical_value=None,
        uncertainty=None,
        axis_mapping_kind="toy_or_structural_proxy",
        systematics_status="unresolved",
        metadata={"internal_cut_only": True},
    )

    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=False,
    )

    assert guard["ready_for_promotion"] is False
    assert guard["blockers"] == [
        "axis_mapping_not_source_backed",
        "discriminator_math_not_excluding",
        "external_measurement_evidence_not_ready",
        "internal_cut_not_external_measurement",
        "measurement_kind_not_external_numeric",
        "missing_external_numeric_measurement",
        "systematics_not_closed",
    ]


def test_nontower_guard_audit_blocks_all_current_routes():
    result = diagnose_nontower_promotion_guard_audit()

    assert result["scenario_count"] == 8
    assert result["claimable_discriminator_now"] is False
    assert result["current_claim_ready_routes"] == []
    assert result["status_counts"] == {
        "non_tower_discriminator_claim_ready": 1,
        "non_tower_promotion_guard_blocked": 7,
    }
    assert result["synthetic_claim_ready_routes"] == [
        "synthetic:ready_external_measurement"
    ]


def test_nontower_guard_blocks_birefringence_hint_until_mapping_and_systematics_close():
    result = diagnose_nontower_promotion_guard_audit()
    rows = {row["label"]: row for row in result["scenarios"]}
    row = rows["birefringence:act_dr6_hint"]

    assert row["frontier_status"] == "non_tower_promotion_guard_blocked"
    assert row["guard"]["blockers"] == [
        "axis_mapping_not_source_backed",
        "discriminator_math_not_excluding",
        "external_measurement_evidence_not_ready",
        "systematics_not_closed",
    ]
    assert row["guard"]["validation"]["numerical_value_present"] is True
    assert row["guard"]["validation"]["uncertainty_valid"] is True
