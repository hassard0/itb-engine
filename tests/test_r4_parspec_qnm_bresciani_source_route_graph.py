"""Tests for the v2.207 qNM-to-Bresciani source-route graph."""

from __future__ import annotations

import json

from experiments.r4_parspec_qnm_bresciani_source_route_graph import (
    CLAIM_STAGE_REQUIREMENTS,
    DEFAULT_OUT,
    REQUIRED_SENSITIVITY_EDGES,
    diagnose_r4_parspec_qnm_bresciani_source_route_graph,
    evaluate_qnm_bresciani_source_route_graph,
    malformed_synthetic_source_route_graph,
    qnm_bresciani_source_route_graph,
    qnm_bresciani_source_routes,
)


def _routes_by_id() -> dict[str, dict]:
    return {route["route_id"]: route for route in qnm_bresciani_source_routes()}


def test_graph_records_required_sensitivity_and_claim_requirements() -> None:
    graph = qnm_bresciani_source_route_graph()
    target = graph["target_sensitivity"]

    assert tuple(target["rows"]) == ("g_R4_c1", "g_R4_c2", "g_R4_c3")
    assert tuple(target["columns"]) == (
        "delta_omega_qeft_0",
        "delta_tau_qeft_0",
        "delta_omega_qeft_1",
        "delta_tau_qeft_1",
    )
    assert tuple(target["required_edges"]) == REQUIRED_SENSITIVITY_EDGES
    assert tuple(graph["claim_stage_requirements"]) == CLAIM_STAGE_REQUIREMENTS
    assert graph["claim_controls"]["claim_use_allowed"] is False
    assert graph["claim_controls"]["synthetic_sensitivity_allowed"] is False


def test_source_registry_uses_public_primary_source_urls() -> None:
    graph = qnm_bresciani_source_route_graph()
    registry = graph["source_registry"]

    assert registry["silva_ghosh_buonanno_2023"]["url"].endswith("2205.05132")
    assert registry["maselli_cardoso_et_al_2020_parspec"]["url"].endswith(
        "1910.12893"
    )
    assert registry["parspec_eft_scale_framework_2021"]["url"].endswith(
        "2102.05939"
    )
    assert registry["cano_et_al_2021_quartic_qnm_shifts"]["url"].endswith(
        "2110.11378"
    )
    assert registry["cano_fransen_hertog_maenaut_2023"]["url"].endswith(
        "2307.07431"
    )
    assert registry["bresciani_levati_paradisi_2026"]["url"].endswith(
        "2504.12855"
    )
    assert registry["pyring_eft_qnms_branch"]["branch"] == "EFT_QNMs"
    assert registry["maenaut_2024_pyring_eft_ringdown_analysis"]["url"].endswith(
        "2411.17893"
    )


def test_parspec_qeft_route_is_rank_one_and_missing_operator_edge() -> None:
    route = _routes_by_id()["parspec_qeft_ray_plus_bresciani_dictionary"]

    assert "maselli_cardoso_et_al_2020_parspec" in route["source_ids"]
    assert "parspec_eft_scale_framework_2021" in route["source_ids"]
    assert route["local_matrix_shape"] == [4, 1]
    assert route["local_matrix_rank"] == 1
    assert route["sensitivity_ready"] is False
    assert "qnm_deformation_to_operator_coordinate_map" in route["missing_edges"]
    assert "operator_coordinate_to_bresciani_K_map" in route["missing_edges"]


def test_pyring_route_has_local_rank_but_not_bresciani_orientation() -> None:
    route = _routes_by_id()["pyring_quartic_tables_plus_bresciani_dictionary"]

    assert "cano_et_al_2021_quartic_qnm_shifts" in route["source_ids"]
    assert route["local_matrix_shape"] == [6, 4]
    assert route["local_matrix_rank"] >= 3
    assert route["sensitivity_ready"] is False
    assert "field_redefinition_policy" in route["missing_edges"]
    assert "finite_3x4_sensitivity_matrix" in route["missing_edges"]


def test_bresciani_dictionary_route_is_only_downstream_projection() -> None:
    route = _routes_by_id()["bresciani_amplitude_dictionary_only"]

    assert route["local_matrix_shape"] == [3, 3]
    assert route["local_matrix_rank"] == 3
    assert route["provided_edges"] == ["bresciani_K_to_engine_axis_projection"]
    assert "source_qnm_deformation_axis_schema" in route["missing_edges"]
    assert route["sensitivity_ready"] is False


def test_likelihood_rerun_route_is_next_build_candidate_not_claim() -> None:
    route = _routes_by_id()["pyring_eft_likelihood_rerun_route"]

    assert route["route_kind"] == "next_likelihood_build_candidate"
    assert route["sensitivity_ready"] is False
    assert "public_or_reproducible_likelihood_export" in route["missing_edges"]
    assert "operator_coordinate_to_bresciani_K_map" in route["missing_edges"]


def test_evaluation_keeps_sensitivity_and_claim_gates_closed() -> None:
    evaluation = evaluate_qnm_bresciani_source_route_graph()

    assert evaluation["source_route_graph_ready"] is True
    assert evaluation["qnm_to_bresciani_sensitivity_ready"] is False
    assert evaluation["ready_sensitivity_routes"] == []
    assert evaluation["next_likelihood_build_candidate_routes"] == [
        "pyring_eft_likelihood_rerun_route"
    ]
    assert evaluation["ready_for_framework_claim"] is False
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in (
        evaluation["remaining_claim_blockers"]
    )


def test_malformed_synthetic_route_graph_is_rejected() -> None:
    evaluation = evaluate_qnm_bresciani_source_route_graph(
        malformed_synthetic_source_route_graph()
    )

    assert evaluation["source_route_graph_ready"] is False
    assert "synthetic_qnm_to_bresciani_matrix_synthetic_route_present" in (
        evaluation["blockers"]
    )
    assert "synthetic_sensitivity_not_forbidden" in evaluation["blockers"]
    assert "qnm_bresciani_source_route_graph_not_clean" in (
        evaluation["remaining_claim_blockers"]
    )


def test_diagnosis_selects_rerun_or_primary_operator_source_next() -> None:
    result = diagnose_r4_parspec_qnm_bresciani_source_route_graph()

    assert result["version"] == "v2.207"
    assert result["qnm_to_bresciani_sensitivity_ready"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == "source_route_graph_ready_sensitivity_missing"
    assert result["selected_next_build_action"] == (
        "build_pyring_eft_likelihood_rerun_packet_or_find_primary_"
        "qnm_to_bresciani_operator_source"
    )
    assert result["v2206_public_likelihood_status"][
        "machine_readable_public_likelihood_ready"
    ] is False


def test_committed_artifact_matches_source_route_graph_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.207"
    assert artifact["route_status"] == "source_route_graph_ready_sensitivity_missing"
    assert artifact["qnm_to_bresciani_sensitivity_ready"] is False
    assert artifact["ready_for_framework_claim"] is False
