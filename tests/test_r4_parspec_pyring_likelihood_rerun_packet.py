"""Tests for the v2.208 pyRing EFT likelihood-rerun packet."""

from __future__ import annotations

import json

from experiments.r4_parspec_pyring_likelihood_rerun_packet import (
    COORDINATE_SCOPE,
    DEFAULT_OUT,
    PYRING_PAPER_COMMIT_SHA,
    REQUIRED_OUTPUT_ARTIFACTS,
    diagnose_r4_parspec_pyring_likelihood_rerun_packet,
    evaluate_pyring_likelihood_rerun_packet,
    malformed_pyring_likelihood_rerun_packet,
    pyring_likelihood_rerun_packet,
)
from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH_HEAD_SHA,
    PYRING_SOURCE_DIRECTIONS,
)


def test_source_manifest_pins_pyring_and_public_analysis_sources() -> None:
    packet = pyring_likelihood_rerun_packet()
    source = packet["source_manifest"]

    assert source["pyring_branch"] == "EFT_QNMs"
    assert source["pyring_branch_probe_head_sha"] == PYRING_BRANCH_HEAD_SHA
    assert source["pyring_execution_commit_sha"] == PYRING_PAPER_COMMIT_SHA
    assert source["pyring_execution_commit_url"].endswith(PYRING_PAPER_COMMIT_SHA)
    assert source["pyring_repo_url"].endswith("/pyring")
    assert source["pyring_eft_ringdown_analysis_url"].endswith("2411.17893")
    assert source["normalization_policy_id"] == (
        "pyring_runtime_to_parspec_high_spin_normalization_policy_v1"
    )


def test_event_manifest_uses_public_gwosc_topology_and_strain_records() -> None:
    packet = pyring_likelihood_rerun_packet()
    events = packet["event_manifest"]

    assert events["source_events"] == ["GW150914", "GW200129"]
    assert events["detector_topology_by_event"]["GW150914"] == ["H1", "L1"]
    assert events["detector_topology_by_event"]["GW200129"] == ["H1", "L1", "V1"]

    gw150914_rows = events["public_strain_by_event"]["GW150914"][
        "strain_records_32s_4khz_hdf5"
    ]
    gw200129_rows = events["public_strain_by_event"]["GW200129"][
        "strain_records_32s_4khz_hdf5"
    ]
    assert {row["detector"] for row in gw150914_rows} == {"H1", "L1"}
    assert {row["detector"] for row in gw200129_rows} == {"H1", "L1", "V1"}
    assert all(row["duration"] == 32 for row in gw150914_rows + gw200129_rows)
    assert all(row["sample_rate_hz"] == 4096 for row in gw150914_rows + gw200129_rows)
    assert all(
        row["download_url"].endswith(".hdf5") for row in gw150914_rows + gw200129_rows
    )


def test_runtime_coordinate_policy_keeps_branch_columns_nonclaiming() -> None:
    packet = pyring_likelihood_rerun_packet()
    policy = packet["runtime_coordinate_policy"]

    assert policy["coordinate_scope"] == COORDINATE_SCOPE
    assert tuple(policy["source_directions"]) == PYRING_SOURCE_DIRECTIONS
    assert policy["paper_reported_theories"] == ["quartic_1", "quartic_2"]
    assert policy["branch_extension_control_theories"] == ["quartic_3"]
    assert policy["paper_prior_policy"]["ell_km"] == [-740.0, 740.0]
    assert policy["paper_runtime_settings"]["template"] == "Kerr"
    assert policy["paper_runtime_settings"]["analysis_segment_seconds"] == 0.2
    assert policy["columns_are_branch_splitting_directions"] is True
    assert policy["columns_are_independent_operator_axes"] is False
    assert policy["columns_are_bresciani_axes"] is False


def test_minimum_rerun_config_grid_has_event_direction_cross_product() -> None:
    packet = pyring_likelihood_rerun_packet()
    configs = packet["minimum_rerun_config_grid"]

    assert len(configs) == 2 * len(PYRING_SOURCE_DIRECTIONS)
    assert {
        (row["paper_event"], row["eft_direction"]) for row in configs
    } == {
        (event, direction)
        for event in ("GW150914", "GW200129")
        for direction in PYRING_SOURCE_DIRECTIONS
    }
    assert all(row["coordinate_scope"] == COORDINATE_SCOPE for row in configs)
    assert all(
        row["pyring_execution_commit_sha"] == PYRING_PAPER_COMMIT_SHA
        for row in configs
    )
    assert all(row["pyring_template"] == "Kerr" for row in configs)
    assert {
        row["eft_direction"]
        for row in configs
        if row["branch_extension_control"]
    } == {"quartic_3_minus", "quartic_3_plus"}
    assert all(row["modes"] == ["220", "221"] for row in configs)
    assert all(row["sampler_status"] == "not_executed_in_this_packet" for row in configs)


def test_output_contract_requires_reproducible_likelihood_exports() -> None:
    packet = pyring_likelihood_rerun_packet()
    contract = packet["output_contract"]

    assert set(REQUIRED_OUTPUT_ARTIFACTS).issubset(contract["required_artifacts"])
    assert contract["accepts_samples_or_grid"] is True
    assert contract["requires_output_hashes"] is True
    assert contract["requires_config_hash"] is True
    assert contract["requires_environment_lock"] is True
    assert contract["requires_nonclaiming_coordinate_label"] is True
    assert contract["requires_systematics_statement"] is True
    assert contract["documented_pyring_outputs"]["posterior_samples"] == (
        "Nested_sampler/posterior.dat"
    )
    assert "not a documented pyRing CLI mode" in contract["log_likelihood_grid_status"]


def test_evaluation_marks_spec_ready_but_likelihood_execution_missing() -> None:
    evaluation = evaluate_pyring_likelihood_rerun_packet()

    assert evaluation["rerun_packet_spec_ready"] is True
    assert evaluation["runtime_likelihood_export_ready"] is False
    assert evaluation["ready_for_bresciani_claim"] is False
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["claimable_framework_exclusions_now"] == []
    assert evaluation["route_status"] == (
        "pyring_likelihood_rerun_packet_spec_ready_execution_missing"
    )
    assert "runtime_likelihood_export_missing" in (
        evaluation["remaining_execution_blockers"]
    )
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in (
        evaluation["remaining_execution_blockers"]
    )


def test_malformed_control_rejects_promoted_branch_coordinate_claim() -> None:
    evaluation = evaluate_pyring_likelihood_rerun_packet(
        malformed_pyring_likelihood_rerun_packet()
    )

    assert evaluation["rerun_packet_spec_ready"] is False
    assert "pyring_execution_source_not_pinned" in evaluation["blockers"]
    assert "runtime_coordinates_promoted_to_operator_axes" in evaluation["blockers"]
    assert "runtime_coordinates_promoted_to_bresciani_axes" in evaluation["blockers"]
    assert "required_output_artifacts_missing" in evaluation["blockers"]
    assert "output_hashes_missing" in evaluation["blockers"]
    assert "framework_claim_not_disabled" in evaluation["blockers"]


def test_diagnosis_links_v2207_and_selects_config_exporter_next() -> None:
    result = diagnose_r4_parspec_pyring_likelihood_rerun_packet()

    assert result["version"] == "v2.208"
    assert result["v2207_route_status"] == "source_route_graph_ready_sensitivity_missing"
    assert result["rerun_packet_spec_ready"] is True
    assert result["runtime_likelihood_export_ready"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "pyring_likelihood_rerun_packet_spec_ready_execution_missing"
    )
    assert result["selected_next_build_action"] == (
        "export_executable_pyring_runtime_configs_and_run_sampler"
    )


def test_committed_artifact_matches_rerun_packet_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.208"
    assert artifact["route_status"] == (
        "pyring_likelihood_rerun_packet_spec_ready_execution_missing"
    )
    assert artifact["runtime_likelihood_export_ready"] is False
    assert artifact["ready_for_framework_claim"] is False
