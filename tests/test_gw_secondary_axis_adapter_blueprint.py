"""Tests for the v2.100 public-GW secondary-axis adapter blueprint."""

from experiments.gw_secondary_axis_adapter_blueprint import (
    bernard_dictionary_only_adapter_candidate,
    diagnose_gw_secondary_axis_adapter_blueprint,
    evaluate_gw_secondary_axis_adapter,
    liu_yunes_gw170608_paper_summary_adapter_candidate,
    synthetic_ready_gw_secondary_axis_adapter,
)


def test_synthetic_ready_secondary_axis_adapter_is_nonclaiming_acceptance_fixture():
    result = evaluate_gw_secondary_axis_adapter(
        synthetic_ready_gw_secondary_axis_adapter()
    )

    assert result["adapter_ready"] is True
    assert result["claim_ready"] is False
    assert result["adapter_blockers"] == []
    assert result["claim_blockers"] == ["synthetic_fixture_not_real_source"]
    assert result["engine_axis_target"] == "g_C"


def test_liu_yunes_summary_supplies_numeric_alpha_constraints_but_lacks_mapping():
    result = evaluate_gw_secondary_axis_adapter(
        liu_yunes_gw170608_paper_summary_adapter_candidate()
    )

    assert result["adapter_ready"] is False
    assert result["constraints_summary"]["all_parameters_have_numeric_constraints"] is True
    assert "source_to_engine_jacobian_missing" in result["adapter_blockers"]
    assert "engine_axis_likelihood_export_missing" in result["adapter_blockers"]
    assert "systematics_not_closed" in result["adapter_blockers"]
    assert "shared_eft_domain_not_bounded" in result["adapter_blockers"]


def test_dictionary_only_candidate_is_not_an_event_likelihood_packet():
    result = evaluate_gw_secondary_axis_adapter(
        bernard_dictionary_only_adapter_candidate()
    )

    assert result["adapter_ready"] is False
    assert "source_parameter_constraints_incomplete" in result["adapter_blockers"]
    assert "source_to_engine_jacobian_missing" in result["adapter_blockers"]
    assert "engine_axis_likelihood_export_missing" in result["adapter_blockers"]


def test_diagnosis_selects_jacobian_derivation_as_next_build_action():
    result = diagnose_gw_secondary_axis_adapter_blueprint()

    assert result["version"] == "v2.100"
    assert result["route_status"] == (
        "gw_secondary_axis_adapter_blueprint_ready_no_real_jacobian"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "derive_source_to_engine_jacobian_for_alpha_bar_to_g_C_or_g_R2"
    )


def test_diagnosis_accepts_only_synthetic_adapter_fixture():
    result = diagnose_gw_secondary_axis_adapter_blueprint()

    assert result["adapter_ready_sample_packets"] == [
        "synthetic_ready_gw_secondary_axis_adapter"
    ]
    assert result["claim_ready_sample_packets"] == []
    assert result["blocker_counts"]["synthetic_fixture_not_real_source"] == 1
    assert result["blocker_counts"]["source_to_engine_jacobian_missing"] == 2


def test_valid_axes_are_g_c_and_g_r2():
    result = diagnose_gw_secondary_axis_adapter_blueprint()

    assert result["valid_engine_secondary_axes"] == ["g_C", "g_R2"]
