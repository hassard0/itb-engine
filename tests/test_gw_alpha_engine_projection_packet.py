"""Tests for the v2.117 alpha engine projection packet."""

from experiments.gw_alpha_engine_projection_packet import (
    alpha_identity_engine_projection_strategy,
    diagnose_gw_alpha_engine_projection_packet,
    evaluate_alpha_engine_projection_packet,
    load_v2_116_packet,
    packet_with_explicit_alpha_engine_projection,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


def test_identity_projection_strategy_targets_gw_cubic_alpha():
    strategy = alpha_identity_engine_projection_strategy()

    assert strategy["status"] == "explicit_engine_projection"
    assert strategy["target_axis"] == "gw_cubic_alpha"
    assert strategy["source_to_engine_jacobian"] == [[1.0, 0.0], [0.0, 1.0]]
    assert strategy["source_parameters"] == ["alpha_bar_1", "alpha_bar_2"]
    assert strategy["engine_parameters"] == ["alpha_bar_1", "alpha_bar_2"]


def test_projected_packet_has_engine_projection_but_open_systematics():
    packet = packet_with_explicit_alpha_engine_projection(load_v2_116_packet())
    result = evaluate_gw_cubic_source_native_packet(packet)

    assert result["engine_projection_summary"]["engine_projection_ready"] is True
    assert result["engine_projection_summary"]["target_axis"] == "gw_cubic_alpha"
    assert result["native_adapter_ready"] is False
    assert result["adapter_blockers"] == ["systematics_not_closed"]
    assert "engine_projection_not_ready" not in result["claim_blockers"]
    assert "g8_joint_component_missing" in result["claim_blockers"]


def test_projection_evaluation_removes_engine_projection_blocker_only():
    packet = packet_with_explicit_alpha_engine_projection(load_v2_116_packet())
    result = evaluate_alpha_engine_projection_packet(packet)

    assert result["alpha_engine_projection_ready"] is True
    assert result["target_axis"] == "gw_cubic_alpha"
    assert result["claim_ready"] is False
    assert result["removed_v2_116_blockers"] == ["engine_projection_not_ready"]
    assert "systematics_not_closed" in result[
        "remaining_claim_blockers_without_removed_projection"
    ]
    assert "g8_joint_component_missing" in result[
        "remaining_claim_blockers_without_removed_projection"
    ]


def test_diagnosis_selects_systematics_closure_next():
    result = diagnose_gw_alpha_engine_projection_packet()

    assert result["version"] == "v2.117"
    assert result["route_status"] == "alpha_engine_projection_packet_ready_nonclaiming"
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "close_alpha_packet_systematics_budget"
    )
    assert result["evaluation"]["adapter_evaluation"]["engine_projection_summary"][
        "engine_projection_ready"
    ] is True


def test_projected_packet_preserves_likelihood_and_covariance_exports():
    packet = packet_with_explicit_alpha_engine_projection(load_v2_116_packet())
    result = evaluate_gw_cubic_source_native_packet(packet)

    assert result["likelihood_summary"]["source_native_usable"] is True
    assert result["covariance_summary"]["numeric"] is True
    assert result["constraints_summary"]["all_source_parameters_numeric"] is True
