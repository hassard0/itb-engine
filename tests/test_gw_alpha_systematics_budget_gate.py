"""Tests for the v2.118 alpha systematics-budget gate."""

from experiments.gw_alpha_systematics_budget_gate import (
    component_evidence,
    diagnose_gw_alpha_systematics_budget_gate,
    evaluate_alpha_systematics_budget,
    load_json,
    packet_with_partial_systematics_budget,
    public_data_reproducibility_evidence,
    sampler_convergence_evidence,
)
from experiments.gw_cubic_source_native_adapter import (
    REQUIRED_SYSTEMATICS_COMPONENTS,
    evaluate_gw_cubic_source_native_packet,
)
from experiments.gw_marginal_alpha_packet_export import DEFAULT_MARGINAL_RESULT_PATH
from experiments.gw_alpha_engine_projection_packet import (
    load_v2_116_packet,
    packet_with_explicit_alpha_engine_projection,
)


def test_sampler_convergence_evidence_bounds_deterministic_grid():
    marginal = load_json(DEFAULT_MARGINAL_RESULT_PATH)
    evidence = sampler_convergence_evidence(marginal)

    assert evidence["status"] == "bounded"
    assert evidence["alpha_grid_points"] == 441
    assert evidence["nuisance_points_per_detector"] == [81, 81]
    assert evidence["deterministic_ready"] is True


def test_public_data_reproducibility_is_bounded_by_loader_artifact():
    evidence = public_data_reproducibility_evidence()

    assert evidence["status"] == "bounded"
    assert evidence["required_detectors"] == ["H1", "L1"]
    assert evidence["cache_rehydration_supported"] is True


def test_component_evidence_covers_required_systematics_components():
    evidence = component_evidence(load_json(DEFAULT_MARGINAL_RESULT_PATH))

    assert list(evidence) == list(REQUIRED_SYSTEMATICS_COMPONENTS)
    assert evidence["sampler_convergence"]["status"] == "bounded"
    assert evidence["public_data_reproducibility"]["status"] == "bounded"
    assert evidence["waveform_systematics"]["status"] == "open"
    assert evidence["detector_calibration"]["status"] == "open"


def test_partial_budget_packet_narrows_systematics_without_closing_claim():
    base_packet = packet_with_explicit_alpha_engine_projection(load_v2_116_packet())
    packet = packet_with_partial_systematics_budget(
        base_packet,
        load_json(DEFAULT_MARGINAL_RESULT_PATH),
    )
    result = evaluate_gw_cubic_source_native_packet(packet)

    assert packet["systematics_budget"]["components"]["sampler_convergence"] == (
        "bounded"
    )
    assert packet["systematics_budget"]["components"][
        "public_data_reproducibility"
    ] == "bounded"
    assert packet["systematics_budget"]["components"]["waveform_systematics"] == "open"
    assert result["engine_projection_summary"]["engine_projection_ready"] is True
    assert result["adapter_blockers"] == ["systematics_not_closed"]
    assert result["claim_ready"] is False


def test_systematics_evaluation_reports_bounded_and_open_components():
    base_packet = packet_with_explicit_alpha_engine_projection(load_v2_116_packet())
    packet = packet_with_partial_systematics_budget(
        base_packet,
        load_json(DEFAULT_MARGINAL_RESULT_PATH),
    )
    result = evaluate_alpha_systematics_budget(packet)

    assert result["partial_systematics_budget_ready"] is True
    assert result["bounded_components"] == [
        "sampler_convergence",
        "public_data_reproducibility",
    ]
    assert "waveform_systematics" in result["open_components"]
    assert "g8_joint_component_missing" in result["remaining_nonclaiming_reasons"]


def test_diagnosis_selects_remaining_systematics_next():
    result = diagnose_gw_alpha_systematics_budget_gate()

    assert result["version"] == "v2.118"
    assert result["route_status"] == (
        "alpha_systematics_budget_partially_bounded_nonclaiming"
    )
    assert result["claimable_discriminator_now"] is False
    assert result["selected_next_build_action"] == (
        "bound_waveform_calibration_prior_and_eft_systematics"
    )
