"""Tests for the v2.126 alpha-to-G8 joint component audit."""

from experiments.gw_alpha_g8_joint_component_audit import (
    DEFAULT_ALPHA_PACKET_PATH,
    alpha_packet_join_status,
    diagnose_gw_alpha_g8_joint_component_audit,
    g8_candidate_join_rows,
    g8_joint_component_audit,
    load_json,
)


def _alpha_result():
    return load_json(DEFAULT_ALPHA_PACKET_PATH)


def test_alpha_packet_is_ready_for_g8_join_but_not_claim_ready():
    status = alpha_packet_join_status(_alpha_result())

    assert status["alpha_packet_native_adapter_ready"] is True
    assert status["alpha_packet_claim_ready"] is False
    assert status["adapter_blockers"] == []
    assert status["claim_blockers"] == ["g8_joint_component_missing"]
    assert status["ready_for_g8_join"] is True


def test_current_g8_candidates_do_not_supply_join_component():
    rows = g8_candidate_join_rows()

    assert len(rows) >= 7
    assert all(row["join_ready_now"] is False for row in rows)
    assert any(row["g8_axis_candidate"] for row in rows)
    assert any(
        "joint_likelihood_or_covariance" in row["required_missing_for_alpha_join"]
        for row in rows
    )
    assert any(
        "external_numeric_measurement" in row["required_missing_for_alpha_join"]
        for row in rows
        if row["g8_axis_candidate"]
    )


def test_joint_component_audit_reports_no_current_g8_join():
    audit = g8_joint_component_audit(_alpha_result())

    assert audit["alpha_status"]["ready_for_g8_join"] is True
    assert audit["g8_joint_component_supplied"] is False
    assert audit["join_ready_candidate_count"] == 0
    assert audit["g8_axis_candidate_count"] > 0
    assert audit["blocker_counts"]["joint_likelihood_or_covariance"] > 0


def test_diagnosis_selects_external_g8_measurement_packet_spec():
    result = diagnose_gw_alpha_g8_joint_component_audit()

    assert result["version"] == "v2.126"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "alpha_ready_g8_joint_component_missing_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "external_spin4_or_detector_g8_measurement_packet_spec"
    )
