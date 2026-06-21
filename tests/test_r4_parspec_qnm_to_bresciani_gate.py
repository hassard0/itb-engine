"""Tests for the v2.200 qNM-to-Bresciani gate."""

import json
from pathlib import Path

from experiments.bresciani_r4_axis_dictionary import PROJECTION_AXES
from experiments.r4_lalsuite_waveform_response_contract import RESPONSE_AXES
from experiments.r4_parspec_qeft_source_asset_audit import QEFT_POWER
from experiments.r4_parspec_qnm_deformation_jacobian import (
    qeft_qnm_coefficient_vector,
)
from experiments.r4_parspec_qnm_to_bresciani_gate import (
    ENGINE_AXES,
    QNM_AXES,
    current_qeft_qnm_ray_packet,
    diagnose_r4_parspec_qnm_to_bresciani_gate,
    evaluate_qnm_to_bresciani_packet,
    malformed_qnm_to_bresciani_packet,
    matrix_rank,
    qnm_to_bresciani_gate_contract,
    synthetic_ready_qnm_to_bresciani_packet,
)


def test_matrix_rank_detects_full_rank_and_ray_cases():
    assert matrix_rank([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]) == 2
    assert matrix_rank([[1.0], [2.0], [3.0], [4.0]]) == 1
    assert matrix_rank([[1.0, 2.0], [2.0, 4.0]]) == 1


def test_contract_requires_engine_rows_and_qnm_columns():
    contract = qnm_to_bresciani_gate_contract()
    minimum = contract["minimum_sensitivity_matrix"]

    assert contract["qnm_axes"] == list(QNM_AXES)
    assert contract["target_engine_axes"] == list(ENGINE_AXES)
    assert minimum["rows"] == list(ENGINE_AXES)
    assert minimum["columns"] == list(QNM_AXES)
    assert minimum["required_rank"] == len(ENGINE_AXES)
    assert "sensitivity_matrix" in contract["required_packet_fields"]


def test_axis_invariants_match_existing_engine_and_bresciani_contracts():
    assert ENGINE_AXES == PROJECTION_AXES == RESPONSE_AXES
    assert ENGINE_AXES == ("g_R4_c1", "g_R4_c2", "g_R4_c3")
    assert QNM_AXES == (
        "delta_omega_qeft_0",
        "delta_tau_qeft_0",
        "delta_omega_qeft_1",
        "delta_tau_qeft_1",
    )
    assert QEFT_POWER == 6
    assert qeft_qnm_coefficient_vector() == {
        "delta_omega_qeft_0": -0.2114,
        "delta_tau_qeft_0": -0.607,
        "delta_omega_qeft_1": -1.5263,
        "delta_tau_qeft_1": 171.35,
    }


def test_synthetic_ready_packet_passes_operator_and_attachment_gate_only():
    packet = synthetic_ready_qnm_to_bresciani_packet()
    matrix = packet["sensitivity_matrix"]["matrix"]

    assert len(matrix) == len(ENGINE_AXES)
    assert all(len(row) == len(QNM_AXES) for row in matrix)

    result = evaluate_qnm_to_bresciani_packet(
        packet
    )

    assert result["sensitivity_matrix_rank"] == 3
    assert result["operator_map_ready"] is True
    assert result["likelihood_attachment_ready"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["map_blockers"] == []
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_current_qeft_ray_is_not_a_three_axis_bresciani_map():
    result = evaluate_qnm_to_bresciani_packet(current_qeft_qnm_ray_packet())

    assert result["operator_map_ready"] is False
    assert result["likelihood_attachment_ready"] is False
    assert result["sensitivity_matrix_rank"] == 1
    assert "source_maps_only_one_qeft_ray" in result["map_blockers"]
    assert "sensitivity_matrix_not_four_qnm_columns" in result["map_blockers"]
    assert "sensitivity_matrix_not_three_engine_rows" in result["map_blockers"]
    assert "sensitivity_matrix_rank_deficient" in result["map_blockers"]
    assert "bresciani_coordinate_orientation_missing" in result["map_blockers"]


def test_current_packet_preserves_absolute_gamma_rows_but_no_public_likelihood():
    packet = current_qeft_qnm_ray_packet()
    rows = packet["source_event_absolute_gamma_rows"]
    result = evaluate_qnm_to_bresciani_packet(packet)

    assert [row["label"] for row in rows] == ["GW150914", "GW200129"]
    assert rows[0]["absolute_gamma_central"] > 0.0
    assert rows[1]["absolute_gamma_central"] > rows[0]["absolute_gamma_central"]
    assert (
        "public_parspec_qeft_likelihood_or_posterior_samples_missing"
        in result["all_blockers"]
    )
    assert "claim_grade_systematics_export_missing" in result["all_blockers"]


def test_diagnosis_records_gate_progress_without_promoting_map_claim():
    result = diagnose_r4_parspec_qnm_to_bresciani_gate()

    assert result["version"] == "v2.200"
    assert result["operator_map_gate_ready"] is True
    assert result["current_operator_map_ready"] is False
    assert result["current_likelihood_attachment_ready"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["resolved_v2199_subpiece"] == (
        "qnm_to_bresciani_sensitivity_gate_defined"
    )
    assert result["route_status"] == (
        "parspec_qnm_to_bresciani_gate_ready_map_missing"
    )
    assert (
        "qnm_deformation_to_bresciani_engine_r4_map_missing"
        in result["remaining_claim_blockers"]
    )


def test_malformed_packet_rejects_bad_sources_shape_and_claim_flag():
    result = evaluate_qnm_to_bresciani_packet(
        malformed_qnm_to_bresciani_packet()
    )

    assert result["operator_map_ready"] is False
    assert "parspec_source_url_missing" in result["all_blockers"]
    assert "bresciani_source_url_missing" in result["all_blockers"]
    assert "sensitivity_matrix_not_three_engine_rows" in result["all_blockers"]
    assert "sensitivity_matrix_shape_mismatch" in result["all_blockers"]
    assert "claim_use_not_disabled" in result["all_blockers"]


def test_committed_artifact_records_current_qeft_ray_blockers():
    path = Path("experiments/results/v2.200/r4_parspec_qnm_to_bresciani_gate.json")
    result = json.loads(path.read_text(encoding="utf-8"))
    current = result["current_qeft_qnm_ray_evaluation"]

    assert result["version"] == "v2.200"
    assert result["operator_map_gate_ready"] is True
    assert current["operator_map_ready"] is False
    assert "source_maps_only_one_qeft_ray" in current["map_blockers"]
    assert result["claimable_framework_exclusions_now"] == []
