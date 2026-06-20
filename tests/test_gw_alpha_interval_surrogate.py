"""Tests for the v2.103 alpha-bar interval surrogate."""

import pytest

from experiments.gw_alpha_interval_surrogate import (
    Z_SCORE_90_CENTRAL,
    build_alpha_interval_surrogate_packet,
    diagnose_gw_alpha_interval_surrogate,
    interval_to_gaussian_surrogate,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


def test_interval_to_gaussian_surrogate_uses_central_90_z_score():
    row = {"central": 0.87, "lower_90": -0.16, "upper_90": 2.82}
    result = interval_to_gaussian_surrogate(row)

    assert result["sigma_minus_from_90"] == pytest.approx(
        (0.87 - -0.16) / Z_SCORE_90_CENTRAL
    )
    assert result["sigma_plus_from_90"] == pytest.approx(
        (2.82 - 0.87) / Z_SCORE_90_CENTRAL
    )
    assert result["sigma_average"] > 0.0
    assert result["asymmetric_interval"] is True


def test_surrogate_packet_contains_diagonal_covariance_and_alpha_parameters():
    packet = build_alpha_interval_surrogate_packet()
    covariance = packet["source_parameter_covariance"]

    assert packet["label"] == "liu_yunes_interval_gaussian_surrogate_nonclaiming"
    assert covariance["parameters"] == ["alpha_bar_1", "alpha_bar_2"]
    assert covariance["matrix"][0][0] > 0.0
    assert covariance["matrix"][1][1] > 0.0
    assert covariance["matrix"][0][1] == 0.0
    assert covariance["correlation_status"] == "unknown_forced_zero_nonclaiming"


def test_surrogate_is_rejected_by_source_native_adapter_gate():
    result = evaluate_gw_cubic_source_native_packet(
        build_alpha_interval_surrogate_packet()
    )

    assert result["native_adapter_ready"] is False
    assert result["claim_ready"] is False
    assert result["covariance_summary"]["numeric"] is True
    assert "source_native_likelihood_export_missing" in result["adapter_blockers"]
    assert "systematics_not_closed" in result["adapter_blockers"]
    assert "shared_eft_domain_not_bounded" in result["adapter_blockers"]


def test_diagnosis_records_nonclaiming_status_and_next_manifest_action():
    result = diagnose_gw_alpha_interval_surrogate()

    assert result["version"] == "v2.103"
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "alpha_interval_surrogate_built_nonclaiming_reanalysis_required"
    )
    assert result["selected_next_build_action"] == (
        "build_public_gw170608_reanalysis_run_manifest"
    )


def test_diagnosis_flags_asymmetric_marginal_intervals():
    result = diagnose_gw_alpha_interval_surrogate()

    assert result["interval_asymmetry_exceeds_gaussian_limit"] is True
    assert result["asymmetric_parameters"] == ["alpha_bar_1", "alpha_bar_2"]
    assert result["parameter_surrogates"]["alpha_bar_1"]["asymmetry_ratio"] > 1.0
    assert result["parameter_surrogates"]["alpha_bar_2"]["asymmetry_ratio"] > 1.0


def test_adapter_evaluation_embedded_in_result_is_nonclaiming():
    result = diagnose_gw_alpha_interval_surrogate()
    evaluation = result["adapter_evaluation"]

    assert evaluation["label"] == "liu_yunes_interval_gaussian_surrogate_nonclaiming"
    assert evaluation["claim_ready"] is False
    assert "g8_joint_component_missing" in evaluation["claim_blockers"]
