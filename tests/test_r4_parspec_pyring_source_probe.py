"""Tests for the v2.201 public pyRing EFT QNM source probe."""

from __future__ import annotations

import json

from experiments.r4_parspec_pyring_source_probe import (
    DEFAULT_OUT,
    PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT,
    PYRING_BRANCH_HEAD_SHA,
    PYRING_QNM_PROBE_AXES,
    PYRING_SOURCE_DIRECTIONS,
    diagnose_r4_parspec_pyring_source_probe,
    evaluate_pyring_quartic_source_probe,
    malformed_pyring_quartic_snapshot,
    pyring_quartic_table_manifest,
    pyring_spin_zero_qnm_direction_matrix,
)
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES, QNM_AXES


def test_public_pyring_quartic_manifest_is_pinned() -> None:
    manifest = pyring_quartic_table_manifest()

    assert manifest["branch_head_sha"] == PYRING_BRANCH_HEAD_SHA
    assert len(manifest["tables"]) == 6
    assert [row["source_direction"] for row in manifest["tables"]] == list(
        PYRING_SOURCE_DIRECTIONS
    )
    assert all(
        row["raw_url"].startswith("https://git.ligo.org/")
        for row in manifest["tables"]
    )
    assert all(len(row["sha256"]) == 64 for row in manifest["tables"])
    assert all(
        len(row["git_lfs_pointer_blob_sha1"]) == 40
        for row in manifest["tables"]
    )
    assert {row["data_rows"] for row in manifest["tables"]} == {3}
    assert {row["columns"] for row in manifest["tables"]} == {29}


def test_spin_zero_qnm_direction_matrix_has_full_probe_rank() -> None:
    matrix = pyring_spin_zero_qnm_direction_matrix()

    assert matrix["rows"] == list(PYRING_QNM_PROBE_AXES)
    assert matrix["columns"] == list(PYRING_SOURCE_DIRECTIONS)
    assert len(matrix["matrix"]) == 4
    assert all(len(row) == 6 for row in matrix["matrix"])
    assert matrix["rank"] == 4
    assert matrix["required_rank_for_probe_axes"] == 4


def test_known_zero_and_branch_antisymmetry_are_preserved() -> None:
    snapshot = PUBLIC_PYRING_QUARTIC_TABLE_SNAPSHOT

    assert snapshot["quartic_2_plus"]["spin_zero_220_221_vector"] == [
        0.0,
        0.0,
        0.0,
        0.0,
    ]
    q3_minus = snapshot["quartic_3_minus"]["spin_zero_220_221_vector"]
    q3_plus = snapshot["quartic_3_plus"]["spin_zero_220_221_vector"]
    assert q3_plus == [-value for value in q3_minus]


def test_evaluation_closes_source_subpiece_but_not_claim_gate() -> None:
    evaluation = evaluate_pyring_quartic_source_probe()

    assert evaluation["public_pyring_quartic_table_intake_ready"] is True
    assert evaluation["independent_branch_qnm_columns_ready"] is True
    assert evaluation["independent_qnm_source_directions_ready"] is False
    assert evaluation["operator_theory_count"] == 3
    assert evaluation["branch_column_count"] == 6
    assert evaluation["qnm_to_bresciani_sensitivity_ready"] is False
    assert evaluation["public_likelihood_ready"] is False
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["source_intake_blockers"] == []
    assert "public_pyring_quartic_qnm_table_intake_ready" in evaluation[
        "resolved_v2200_subpieces"
    ]
    assert "spin_zero_quartic_branch_qnm_coefficients_ranked" in evaluation[
        "resolved_v2200_subpieces"
    ]
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in evaluation[
        "remaining_claim_blockers"
    ]
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in evaluation[
        "remaining_claim_blockers"
    ]
    assert "pyring_plus_minus_branches_not_independent_operator_axes" in evaluation[
        "remaining_claim_blockers"
    ]


def test_malformed_snapshot_fails_rank_gate() -> None:
    malformed = evaluate_pyring_quartic_source_probe(
        malformed_pyring_quartic_snapshot()
    )

    assert malformed["public_pyring_quartic_table_intake_ready"] is False
    assert malformed["independent_branch_qnm_columns_ready"] is False
    assert malformed["independent_qnm_source_directions_ready"] is False
    assert "pyring_quartic_spin_zero_direction_rank_deficient" in malformed[
        "source_intake_blockers"
    ]
    assert malformed["resolved_v2200_subpieces"] == []


def test_diagnosis_preserves_engine_and_parspec_axis_boundaries() -> None:
    result = diagnose_r4_parspec_pyring_source_probe()

    assert result["version"] == "v2.201"
    assert tuple(result["engine_target_axes"]) == ENGINE_AXES
    assert tuple(result["parspec_qnm_axes"]) == QNM_AXES
    assert tuple(result["pyring_probe_axes"]) == PYRING_QNM_PROBE_AXES
    assert result["spin_zero_qnm_direction_matrix"]["rank"] == 4
    assert result["independent_branch_qnm_columns_ready"] is True
    assert result["independent_qnm_source_directions_ready"] is False
    assert result["qnm_to_bresciani_sensitivity_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False


def test_committed_artifact_matches_probe_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.201"
    assert artifact["route_status"] == (
        "pyring_quartic_qnm_tables_ready_bresciani_map_missing"
    )
    assert artifact["public_pyring_quartic_table_intake_ready"] is True
    assert artifact["independent_branch_qnm_columns_ready"] is True
    assert artifact["independent_qnm_source_directions_ready"] is False
    assert artifact["ready_for_framework_claim"] is False
