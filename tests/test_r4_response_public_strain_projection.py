"""Tests for the v2.178 R4 response public-strain projection harness."""

import numpy as np

from experiments.r4_response_public_strain_projection import (
    RESPONSE_AXES,
    diagnose_r4_response_public_strain_projection,
    evaluate_r4_response_public_strain_projection,
    malformed_r4_projected_public_strain_fixture_packet,
    network_r4_response_projection,
    project_detector_r4_response,
    r4_projected_public_strain_fixture_packet,
    r4_response_template_summary,
)


def test_r4_response_templates_are_orthonormal_for_projection_segment():
    summary = r4_response_template_summary()

    assert summary["template_kind"] == (
        "r4_response_contract_time_domain_projection_fixture"
    )
    assert summary["axes"] == list(RESPONSE_AXES)
    assert summary["orthonormal_within_tolerance"] is True
    for axis in RESPONSE_AXES:
        assert summary["template_norms"][axis] == 1.0


def test_detector_projection_returns_finite_h1_l1_coefficients():
    rows = [project_detector_r4_response("H1"), project_detector_r4_response("L1")]

    assert [row["detector"] for row in rows] == ["H1", "L1"]
    for row in rows:
        assert row["projection_ready"] is True
        assert row["synthetic_strain_fixture"] is True
        assert row["conditioning"]["conditioned_rms"] == 1.0
        for axis in RESPONSE_AXES:
            assert np.isfinite(row["projection"][axis])


def test_network_projection_builds_positive_covariance_seed():
    rows = [project_detector_r4_response("H1"), project_detector_r4_response("L1")]
    network = network_r4_response_projection(rows)

    assert network["axes"] == list(RESPONSE_AXES)
    assert set(network["central_values"]) == set(RESPONSE_AXES)
    assert len(network["covariance"]) == 3
    assert all(network["covariance"][idx][idx] > 0.0 for idx in range(3))
    assert network["synthetic_strain_fixture"] is True


def test_projected_fixture_packet_ingests_and_scores():
    packet = r4_projected_public_strain_fixture_packet()
    result = evaluate_r4_response_public_strain_projection(packet)

    assert result["projection_harness_engine_ready"] is True
    assert result["fixture_packet_evaluation"]["fixture_packet_engine_ready"] is True
    assert result["shape_score"]["score_available"] is True
    assert result["ready_for_framework_claim"] is False
    assert "synthetic_control_not_claim_evidence" in result["claim_blockers"]


def test_malformed_projected_packet_rejects_bad_template_and_covariance():
    result = evaluate_r4_response_public_strain_projection(
        malformed_r4_projected_public_strain_fixture_packet()
    )

    assert result["projection_harness_engine_ready"] is False
    assert "r4_response_templates_not_orthonormal" in result["projection_blockers"]
    assert "projection_detectors_not_h1_l1" in result["projection_blockers"]
    assert "projected_fixture_packet_not_engine_ready" in result["projection_blockers"]


def test_diagnosis_selects_real_gwosc_hdf5_projection_next():
    result = diagnose_r4_response_public_strain_projection()

    assert result["version"] == "v2.178"
    assert result["projection_harness_engine_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_response_public_strain_projection_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "replace_synthetic_strain_rows_with_gwosc_hdf5_r4_projection"
    )
