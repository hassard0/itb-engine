"""Tests for the v2.193 ParSpec source-event H1/L1 likelihood rerun."""

import json
from pathlib import Path

from experiments.r4_lalsuite_waveform_likelihood_posterior import AXES, GRID_OFFSETS
from experiments.r4_parspec_same_event_h1l1_likelihood import (
    CLAIM_GRADE_REMAINING_BLOCKERS,
    diagnose_r4_parspec_same_event_h1l1_likelihood,
    evaluate_source_event_h1l1_likelihoods,
    source_event_h1l1_32s_records,
)
from experiments.r4_parspec_source_event_alignment_manifest import (
    diagnose_r4_parspec_source_event_alignment_manifest,
)


def _synthetic_network() -> dict:
    center = {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.49,
        "g_R4_c3": -0.01,
        "delta_g_R4_c1": 0.0,
        "delta_g_R4_c2": 0.0,
        "delta_g_R4_c3": 0.0,
        "log_marginal_likelihood": 0.0,
        "profile_log_likelihood": 0.0,
    }
    return {
        "detectors": ["H1", "L1"],
        "grid_points": len(GRID_OFFSETS) ** len(AXES),
        "posterior": {
            "posterior_normalized": True,
            "posterior_positive_semidefinite": True,
            "maximum_posterior_grid_point": center,
            "posterior_mean": {axis: center[axis] for axis in AXES},
        },
        "best_marginal_grid_point": center,
        "best_profile_grid_point": center,
    }


def _synthetic_event_likelihood(event: str) -> dict:
    return {
        "paper_event": event,
        "gwosc_event_name": (
            "GW150914" if event == "GW150914" else "GW200129_065458"
        ),
        "event_version": (
            "GW150914-v3" if event == "GW150914" else "GW200129_065458-v1"
        ),
        "detectors": ["H1", "L1"],
        "network_likelihood": _synthetic_network(),
        "h1l1_likelihood_ready": True,
    }


def test_source_event_h1l1_records_select_32s_h1_l1_only():
    manifest = diagnose_r4_parspec_source_event_alignment_manifest()
    records = source_event_h1l1_32s_records(manifest)

    assert sorted(records) == ["GW150914", "GW200129"]
    for event, rows in records.items():
        assert [row["detector"] for row in rows] == ["H1", "L1"]
        assert all(row["duration"] == 32 for row in rows)
        assert all(row["download_url"].endswith(".hdf5") for row in rows)
        assert all("event_gps" in row for row in rows)
        if event == "GW200129":
            assert all(row["gwosc_event_name"] == "GW200129_065458" for row in rows)
            assert all(row["event_gps"] == 1264316116.4 for row in rows)


def test_evaluator_accepts_synthetic_h1l1_source_event_likelihoods_nonclaiming():
    result = evaluate_source_event_h1l1_likelihoods(
        [
            _synthetic_event_likelihood("GW150914"),
            _synthetic_event_likelihood("GW200129"),
        ],
        status={"available": True, "has_imrphenomd": True},
    )

    assert result["h1l1_same_event_likelihood_ready"] is True
    assert result["event_set_alignment_ready"] is False
    assert result["h1l1_likelihood_blockers"] == []
    assert result["route_status"] == (
        "parspec_source_events_h1l1_likelihood_ready_v1_policy_missing"
    )
    assert set(CLAIM_GRADE_REMAINING_BLOCKERS).issubset(
        set(result["claim_blockers"])
    )
    assert result["ready_for_framework_claim"] is False


def test_evaluator_rejects_missing_lalsuite_and_bad_event_set():
    result = evaluate_source_event_h1l1_likelihoods(
        [_synthetic_event_likelihood("GW150914")],
        status={"available": False, "has_imrphenomd": False},
    )

    assert result["h1l1_same_event_likelihood_ready"] is False
    assert "lalsuite_not_installed" in result["h1l1_likelihood_blockers"]
    assert "lalsuite_imrphenomd_unavailable" in result["h1l1_likelihood_blockers"]
    assert "source_event_likelihoods_not_exact_parspec_events" in (
        result["h1l1_likelihood_blockers"]
    )


def test_local_diagnosis_is_nonclaiming_and_handles_missing_lalsuite():
    result = diagnose_r4_parspec_same_event_h1l1_likelihood()

    assert result["version"] == "v2.193"
    assert result["event_set_alignment_ready"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    if not result["lalsuite_status"]["available"]:
        assert result["h1l1_same_event_likelihood_ready"] is False
        assert "lalsuite_not_installed" in result["evaluation"][
            "h1l1_likelihood_blockers"
        ]


def test_committed_artifact_records_vulcan_h1l1_source_event_rerun():
    path = Path(
        "experiments/results/v2.193/"
        "r4_parspec_same_event_h1l1_likelihood.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.193"
    assert result["route_status"] in {
        "parspec_source_events_h1l1_likelihood_ready_v1_policy_missing",
        "parspec_source_events_h1l1_likelihood_not_ready",
    }
    assert result["event_set_alignment_ready"] is False
    assert result["ready_for_framework_claim"] is False
    if result["h1l1_same_event_likelihood_ready"]:
        assert [row["paper_event"] for row in result["event_likelihoods"]] == [
            "GW150914",
            "GW200129",
        ]
        assert all(
            row["network_likelihood"]["grid_points"]
            == len(GRID_OFFSETS) ** len(AXES)
            for row in result["event_likelihoods"]
        )
    else:
        assert result["evaluation"]["h1l1_likelihood_blockers"]


def test_committed_artifact_keeps_v1_and_parspec_likelihood_blockers():
    path = Path(
        "experiments/results/v2.193/"
        "r4_parspec_same_event_h1l1_likelihood.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))
    blockers = set(result["evaluation"]["claim_blockers"])

    assert "gw200129_v1_detector_channel_response_missing" in blockers
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in blockers
    assert "operator_basis_map_missing" in blockers
    assert result["claimable_framework_exclusions_now"] == []
