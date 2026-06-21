"""Tests for the v2.195 ParSpec source-event covariance export."""

import json
from pathlib import Path

from experiments.r4_lalsuite_waveform_likelihood_posterior import AXES, GRID_OFFSETS
from experiments.r4_nuisance_covariance_export import load_json
from experiments.r4_parspec_event_topology_likelihood import DEFAULT_OUT as V2194_PATH
from experiments.r4_parspec_source_event_covariance_export import (
    CLAIM_GRADE_REMAINING_BLOCKERS,
    combined_event_set_covariance,
    diagnose_r4_parspec_source_event_covariance_export,
    evaluate_source_event_covariance_export,
    malformed_source_event_covariance_export,
    source_event_covariance_rows,
)


def _v2194() -> dict:
    return load_json(V2194_PATH)


def test_source_event_covariance_rows_preserve_events_and_topology():
    rows = source_event_covariance_rows(_v2194())

    assert [row["paper_event"] for row in rows] == ["GW150914", "GW200129"]
    assert rows[0]["detectors"] == ["H1", "L1"]
    assert rows[1]["detectors"] == ["H1", "L1", "V1"]
    for row in rows:
        assert row["grid_points"] == len(GRID_OFFSETS) ** len(AXES)
        assert row["posterior_positive_semidefinite"] is True
        assert row["nuisance_grid"]["grid_is_posterior_sampler"] is False


def test_combined_event_set_covariance_is_positive_semidefinite():
    combined = combined_event_set_covariance(_v2194())

    assert combined["source_events"] == ["GW150914", "GW200129"]
    assert combined["grid_points"] == len(GRID_OFFSETS) ** len(AXES)
    assert combined["posterior_positive_semidefinite"] is True
    assert set(combined["posterior_mean"]) == set(AXES)
    assert combined["detectors_by_event"]["GW200129"] == ["H1", "L1", "V1"]


def test_diagnosis_exports_source_event_covariance_nonclaiming():
    result = diagnose_r4_parspec_source_event_covariance_export()
    evaluation = result["evaluation"]

    assert result["version"] == "v2.195"
    assert result["source_event_specific_nuisance_covariance_export_ready"] is True
    assert evaluation["source_event_specific_nuisance_covariance_export_ready"] is True
    assert evaluation["removed_v2_194_blocker"] == (
        "source_event_specific_nuisance_covariance_export_missing"
    )
    assert "source_event_specific_nuisance_covariance_export_missing" not in (
        evaluation["claim_blockers"]
    )
    assert set(CLAIM_GRADE_REMAINING_BLOCKERS).issubset(
        set(evaluation["claim_blockers"])
    )
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []


def test_malformed_export_rejects_covariance_shape_and_combined_grid():
    malformed = malformed_source_event_covariance_export()
    evaluation = evaluate_source_event_covariance_export(malformed)

    assert evaluation["source_event_specific_nuisance_covariance_export_ready"] is False
    assert "GW150914_covariance_not_psd" in evaluation["export_blockers"]
    assert "GW150914_covariance_shape_unexpected" in evaluation["export_blockers"]
    assert "combined_event_set_covariance_grid_missing" in (
        evaluation["export_blockers"]
    )


def test_committed_artifact_records_source_event_covariance_export():
    path = Path(
        "experiments/results/v2.195/"
        "r4_parspec_source_event_covariance_export.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.195"
    assert result["route_status"] == (
        "parspec_source_event_covariance_export_ready_axis_map_missing"
    )
    assert result["source_event_specific_nuisance_covariance_export_ready"] is True
    export = result["source_event_covariance_export"]
    assert [row["paper_event"] for row in export["event_covariances"]] == [
        "GW150914",
        "GW200129",
    ]
    assert export["combined_event_set_covariance"][
        "posterior_positive_semidefinite"
    ] is True


def test_committed_artifact_keeps_parspec_likelihood_and_axis_map_blockers():
    path = Path(
        "experiments/results/v2.195/"
        "r4_parspec_source_event_covariance_export.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))
    blockers = set(result["evaluation"]["claim_blockers"])

    assert "source_event_specific_nuisance_covariance_export_missing" not in blockers
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in blockers
    assert "operator_basis_map_missing" in blockers
    assert "nuisance_grid_is_coarse_not_posterior_sampler" in blockers
    assert result["claimable_framework_exclusions_now"] == []
