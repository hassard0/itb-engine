"""Tests for the v2.92 external evidence packet contract."""

from experiments.external_evidence_packet_contract import (
    COMMON_CLAIM_GATES,
    diagnose_external_evidence_packet_contract,
    external_evidence_contract_rows,
)
from experiments.g8_adapter_acceptance_harness import (
    REQUIRED_G8_ADAPTER_FIELDS,
    REQUIRED_SYSTEMATICS_COMPONENTS,
)


def test_external_contract_carries_forward_no_current_promotion_ready_route():
    result = diagnose_external_evidence_packet_contract()

    assert result["version"] == "v2.92"
    assert result["route_status"] == "external_evidence_contract_ready_no_packet"
    assert result["frontier_claim_ready_routes"] == []
    assert result["frontier_promotion_ready_routes"] == []
    assert result["claim_ready_without_external_packet_routes"] == []
    assert result["claimable_discriminator_now"] is False


def test_g8_ingestion_contract_includes_v2_79_adapter_fields_and_systematics():
    rows = {row["route"]: row for row in external_evidence_contract_rows()}
    row = rows["future_public_g8_measurement_ingestion"]

    for field in REQUIRED_G8_ADAPTER_FIELDS:
        assert field in row["minimum_required_fields"]
    for component in REQUIRED_SYSTEMATICS_COMPONENTS:
        assert component in (
            diagnose_external_evidence_packet_contract()[
                "systematics_components_required_for_g8"
            ]
        )
    assert row["acceptance_gate"] == "experiments.g8_adapter_acceptance_harness"
    assert "synthetic_fixture_not_real_source" in (
        row["route_specific_rejection_tests"]
    )


def test_all_rows_reject_missing_public_likelihood_and_synthetic_fixtures():
    for row in external_evidence_contract_rows():
        rejection_tests = set(row["route_specific_rejection_tests"])

        assert row["claim_ready_without_external_packet"] is False
        assert "synthetic_fixture_not_real_source" in rejection_tests
        assert "missing_public_likelihood_or_covariance" in rejection_tests
        assert "missing_framework_exclusion_math" in rejection_tests


def test_native_tower_contract_requires_framework_owned_spectrum():
    rows = {row["route"]: row for row in external_evidence_contract_rows()}
    row = rows["framework_specific_native_tower_search"]
    fields = set(row["minimum_required_fields"])
    rejection_tests = set(row["route_specific_rejection_tests"])

    assert "framework_id" in fields
    assert "native_tower_spectrum" in fields
    assert "ownership_metadata" in fields
    assert "native_tower_spectrum_missing" in rejection_tests
    assert "ownership_metadata_missing" in rejection_tests


def test_gw_parity_contract_requires_operator_normalization_bridge():
    rows = {row["route"]: row for row in external_evidence_contract_rows()}
    row = rows["gw_parity_operator_normalization_search"]
    fields = set(row["minimum_required_fields"])
    rejection_tests = set(row["route_specific_rejection_tests"])

    assert "source_backed_operator_normalization" in fields
    assert "engine_axis_target" in fields
    assert "source_backed_operator_normalization_missing" in rejection_tests
    assert "engine_axis_target_missing" in rejection_tests


def test_common_claim_gates_are_attached_to_every_contract_row():
    expected = set(COMMON_CLAIM_GATES)

    for row in external_evidence_contract_rows():
        assert set(row["common_claim_gates"]) == expected
