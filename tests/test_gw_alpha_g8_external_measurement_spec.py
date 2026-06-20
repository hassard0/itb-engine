"""Tests for the v2.127 external G8 sidecar measurement spec."""

from experiments.gw_alpha_g8_external_measurement_spec import (
    diagnose_gw_alpha_g8_external_measurement_spec,
    g8_sidecar_acceptance_checks,
    g8_sidecar_packet_template,
    g8_sidecar_required_fields,
)


def test_sidecar_required_fields_cover_likelihood_projection_and_cross_covariance():
    fields = set(g8_sidecar_required_fields())

    assert {
        "source_url",
        "g8_axis_normalization",
        "covariance_or_likelihood",
        "projection_to_engine_g8",
        "cross_covariance_with_alpha",
        "systematics_budget",
        "discriminator_math",
    } <= fields


def test_sidecar_template_requires_public_engine_g8_likelihood():
    packet = g8_sidecar_packet_template()

    assert packet["g8_axis_normalization"] == "source_backed_engine_g8"
    assert packet["covariance_or_likelihood"]["status"] == "public_engine_usable"
    assert packet["covariance_or_likelihood"]["axes"] == ["g_8"]
    assert "jacobian_to_engine_g8" in packet["projection_to_engine_g8"]["requires"]
    assert "public_joint_covariance_with_alpha" in packet[
        "cross_covariance_with_alpha"
    ]["allowed_forms"]


def test_acceptance_checks_name_all_current_g8_join_blockers():
    checks = {row["check"]: row["blocker"] for row in g8_sidecar_acceptance_checks()}

    assert checks["external_numeric_measurement"] == (
        "external_numeric_measurement_missing"
    )
    assert checks["engine_g8_normalization"] == "engine_g8_normalization_missing"
    assert checks["public_likelihood"] == (
        "public_g8_likelihood_or_covariance_missing"
    )
    assert checks["framework_exclusion"] == (
        "framework_pair_exclusion_math_missing"
    )


def test_diagnosis_keeps_spec_nonclaiming_until_external_packet_exists():
    result = diagnose_gw_alpha_g8_external_measurement_spec()

    assert result["version"] == "v2.127"
    assert result["alpha_packet_ready_for_sidecar"] is True
    assert result["current_sidecar_available"] is False
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "external_g8_sidecar_packet_specified_not_satisfied"
    )
    assert result["selected_next_build_action"] == (
        "obtain_or_publish_external_g8_sidecar_packet"
    )
