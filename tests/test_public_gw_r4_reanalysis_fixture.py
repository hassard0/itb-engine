"""Tests for the v2.176 public-GW R4 reanalysis fixture."""

from experiments.public_gw_r4_reanalysis_fixture import (
    diagnose_public_gw_r4_reanalysis_fixture,
    evaluate_public_gw_r4_reanalysis_fixture,
    gw170608_r4_reanalysis_source_package,
    linearized_r4_waveform_parameterization,
    malformed_public_gw_r4_reanalysis_packet,
    synthetic_public_gw_r4_reanalysis_packet,
)


def test_source_package_declares_public_gw170608_inputs():
    package = gw170608_r4_reanalysis_source_package()

    assert package["event"] == "GW170608"
    assert package["event_record"]["event_version"] == "GW170608-v3"
    assert package["strain_summary"]["public_strain_urls_ready"] is True
    assert package["strain_summary"]["record_count"] == 4
    assert "https://gwosc.org/api/v2/event-versions/GW170608-v3" in (
        package["source_urls"]
    )


def test_waveform_parameterization_reuses_bresciani_axis_sidecar():
    parameterization = linearized_r4_waveform_parameterization()

    assert parameterization["status"] == "fixture_parameterization_ready"
    assert parameterization["axis_mapping_sidecar"]["status"] == (
        "maps_to_bresciani_r4_axes"
    )
    assert parameterization[
        "source_to_engine_jacobian_for_overall_R4_factor_8"
    ] == [
        [0.5, 0.5, 0.0],
        [0.5, -0.5, 0.0],
        [0.0, 0.0, 1.0],
    ]
    assert (
        parameterization["response_model"]["real_waveform_code_attached"]
        is False
    )


def test_fixture_packet_ingests_through_manifest_and_shape_adapter():
    packet = synthetic_public_gw_r4_reanalysis_packet()
    result = evaluate_public_gw_r4_reanalysis_fixture(packet)

    assert result["fixture_packet_engine_ready"] is True
    assert result["manifest_evaluation"]["ready_for_engine_likelihood_packet"] is True
    assert result["ingestion_evaluation"]["adapter_ingestion_ready"] is True
    assert result["shape_score"]["score_available"] is True
    assert result["synthetic_control"] is True
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_fixture_claims_remain_blocked_until_real_waveform_reanalysis():
    result = evaluate_public_gw_r4_reanalysis_fixture(
        synthetic_public_gw_r4_reanalysis_packet()
    )

    assert result["ready_for_real_public_r4_reanalysis"] is False
    assert result["ready_for_framework_claim"] is False
    assert "r4_waveform_response_model_is_fixture" in result["claim_blockers"]
    assert "public_r4_reanalysis_samples_missing" in result["claim_blockers"]
    assert "external_adversarial_review_missing" in result["claim_blockers"]


def test_malformed_packet_rejects_bad_axis_mapping_and_covariance():
    result = evaluate_public_gw_r4_reanalysis_fixture(
        malformed_public_gw_r4_reanalysis_packet()
    )

    assert result["fixture_packet_engine_ready"] is False
    assert "manifest_packet_gate_failed" in result["fixture_blockers"]
    assert "r4_ingestion_adapter_failed" in result["fixture_blockers"]
    assert "public_strain_urls_not_ready" in result["fixture_blockers"]
    assert "axis_mapping_axes_incomplete" in (
        result["manifest_evaluation"]["blockers"]
    )


def test_diagnosis_selects_real_lalsuite_r4_reanalysis_next():
    result = diagnose_public_gw_r4_reanalysis_fixture()

    assert result["version"] == "v2.176"
    assert result["engine_ready_fixture_packets"] == [
        "gw170608_public_r4_shape_reanalysis_fixture_v1"
    ]
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "public_gw_r4_reanalysis_fixture_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "replace_fixture_response_with_lalsuite_r4_waveform_reanalysis"
    )
