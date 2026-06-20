"""Tests for the v2.102 source-native cubic GW adapter."""

from experiments.gw_cubic_source_native_adapter import (
    diagnose_gw_cubic_source_native_adapter,
    evaluate_gw_cubic_source_native_packet,
    liu_yunes_paper_summary_source_native_candidate,
    public_o2_bbh_gr_posterior_candidate,
    synthetic_ready_gw_cubic_source_native_packet,
)


def test_synthetic_source_native_packet_is_ready_but_nonclaiming():
    result = evaluate_gw_cubic_source_native_packet(
        synthetic_ready_gw_cubic_source_native_packet()
    )

    assert result["native_adapter_ready"] is True
    assert result["claim_ready"] is False
    assert result["adapter_blockers"] == []
    assert "synthetic_fixture_not_real_source" in result["claim_blockers"]
    assert "g8_joint_component_missing" in result["claim_blockers"]


def test_liu_yunes_summary_preserves_alpha_intervals_but_lacks_exports():
    result = evaluate_gw_cubic_source_native_packet(
        liu_yunes_paper_summary_source_native_candidate()
    )

    assert result["native_adapter_ready"] is False
    assert result["constraints_summary"]["all_source_parameters_numeric"] is True
    assert "source_native_likelihood_export_missing" in result["adapter_blockers"]
    assert "source_parameter_covariance_missing" in result["adapter_blockers"]
    assert "systematics_not_closed" in result["adapter_blockers"]
    assert "shared_eft_domain_not_bounded" in result["adapter_blockers"]


def test_public_o2_gr_posterior_is_not_alpha_bar_evidence():
    result = evaluate_gw_cubic_source_native_packet(
        public_o2_bbh_gr_posterior_candidate()
    )

    assert result["native_adapter_ready"] is False
    assert "source_model_not_cubic_parity_preserving_eft" in result[
        "adapter_blockers"
    ]
    assert "source_parameters_missing_alpha_bar_basis" in result[
        "adapter_blockers"
    ]
    assert "source_parameter_constraints_incomplete" in result["adapter_blockers"]


def test_diagnosis_selects_alpha_likelihood_reproduction_as_next_build():
    result = diagnose_gw_cubic_source_native_adapter()

    assert result["version"] == "v2.102"
    assert result["route_status"] == (
        "source_native_cubic_gw_adapter_ready_no_real_likelihood_export"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "reproduce_gw170608_alpha_bar_likelihood_from_public_data"
    )


def test_only_synthetic_packet_satisfies_source_native_shape():
    result = diagnose_gw_cubic_source_native_adapter()

    assert result["native_adapter_ready_sample_packets"] == [
        "synthetic_ready_gw_cubic_source_native_packet"
    ]
    assert result["claim_ready_sample_packets"] == []
    assert result["blocker_counts"]["g8_joint_component_missing"] == 3


def test_g8_claim_blocker_prevents_claim_even_when_alpha_packet_is_ready():
    packet = synthetic_ready_gw_cubic_source_native_packet()
    packet["synthetic_fixture"] = False
    packet["source_url"] = "https://arxiv.org/abs/2407.08929"
    packet["engine_axis_strategy"] = {
        "status": "explicit_engine_projection",
        "target_axis": "gw_cubic_alpha",
        "source_to_engine_jacobian": [[1.0, 0.0], [0.0, 1.0]],
    }
    packet["framework_projection_strategy"] = "framework_alpha_response_defined"

    result = evaluate_gw_cubic_source_native_packet(packet)

    assert result["native_adapter_ready"] is True
    assert result["engine_projection_summary"]["engine_projection_ready"] is True
    assert result["adapter_blockers"] == []
    assert result["claim_ready"] is False
    assert result["claim_blockers"] == ["g8_joint_component_missing"]


def test_required_fields_include_likelihood_covariance_and_projection_strategy():
    result = diagnose_gw_cubic_source_native_adapter()
    fields = result["required_source_native_packet_fields"]

    assert "posterior_or_likelihood_export" in fields
    assert "source_parameter_covariance" in fields
    assert "engine_axis_strategy" in fields
    assert "framework_projection_strategy" in fields
    assert result["source_parameters"] == ["alpha_bar_1", "alpha_bar_2"]
