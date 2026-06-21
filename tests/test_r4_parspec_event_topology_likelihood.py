"""Tests for the v2.194 ParSpec event-topology likelihood bridge."""

import json
from pathlib import Path

from experiments.r4_lalsuite_waveform_likelihood_posterior import AXES, GRID_OFFSETS
from experiments.r4_parspec_event_topology_likelihood import (
    CLAIM_GRADE_REMAINING_BLOCKERS,
    EVENT_TOPOLOGY_DETECTORS,
    diagnose_r4_parspec_event_topology_likelihood,
    evaluate_parspec_event_topology_likelihoods,
    source_event_topology_32s_records,
)
from experiments.r4_parspec_source_event_alignment_manifest import (
    diagnose_r4_parspec_source_event_alignment_manifest,
)


def _response(detector: str) -> dict:
    return {
        "detector": detector,
        "K_plus": 0.6,
        "Re_K_minus": 0.52,
        "Im_K_minus": 0.52,
        "tensor_rms": 0.6,
        "helicity_re_rms": 0.31,
        "helicity_im_rms": 0.31,
        "detector_channel_response_calibrated": True,
    }


def _synthetic_network(detectors: list[str]) -> dict:
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
        "detectors": detectors,
        "grid_points": len(GRID_OFFSETS) ** len(AXES),
        "nuisance_points_per_detector": [81 for _ in detectors],
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
    detectors = list(EVENT_TOPOLOGY_DETECTORS[event])
    return {
        "paper_event": event,
        "gwosc_event_name": (
            "GW150914" if event == "GW150914" else "GW200129_065458"
        ),
        "event_version": (
            "GW150914-v3" if event == "GW150914" else "GW200129_065458-v1"
        ),
        "expected_detectors": detectors,
        "detectors": detectors,
        "detector_channel_responses": {
            detector: _response(detector) for detector in detectors
        },
        "network_likelihood": _synthetic_network(detectors),
        "event_detector_topology_likelihood_ready": True,
    }


def test_source_event_topology_records_include_gw200129_v1_32s():
    manifest = diagnose_r4_parspec_source_event_alignment_manifest()
    records = source_event_topology_32s_records(manifest)

    assert [row["detector"] for row in records["GW150914"]] == ["H1", "L1"]
    assert [row["detector"] for row in records["GW200129"]] == ["H1", "L1", "V1"]
    assert all(row["duration"] == 32 for row in records["GW200129"])
    v1 = [row for row in records["GW200129"] if row["detector"] == "V1"][0]
    assert v1["event_version"] == "GW200129_065458-v1"
    assert v1["event_gps"] == 1264316116.4
    assert v1["download_url"].endswith("V-V1_GWOSC_4KHZ_R1-1264316101-32.hdf5")


def test_evaluator_accepts_synthetic_event_topology_nonclaiming():
    result = evaluate_parspec_event_topology_likelihoods(
        [
            _synthetic_event_likelihood("GW150914"),
            _synthetic_event_likelihood("GW200129"),
        ],
        status={"available": True, "has_imrphenomd": True},
    )

    assert result["source_event_detector_topology_likelihood_ready"] is True
    assert result["event_set_alignment_ready"] is True
    assert result["event_topology_likelihood_blockers"] == []
    assert result["route_status"] == (
        "parspec_source_event_topology_likelihood_ready_covariance_missing"
    )
    assert result["ready_for_framework_claim"] is False
    assert "gw200129_v1_detector_channel_response_missing" not in (
        result["claim_blockers"]
    )
    assert set(CLAIM_GRADE_REMAINING_BLOCKERS).issubset(
        set(result["claim_blockers"])
    )


def test_evaluator_rejects_missing_gw200129_v1_topology():
    bad = _synthetic_event_likelihood("GW200129")
    bad["detectors"] = ["H1", "L1"]
    bad["detector_channel_responses"].pop("V1")
    result = evaluate_parspec_event_topology_likelihoods(
        [_synthetic_event_likelihood("GW150914"), bad],
        status={"available": True, "has_imrphenomd": True},
    )

    assert result["source_event_detector_topology_likelihood_ready"] is False
    assert "GW200129_detectors_not_expected_topology" in (
        result["event_topology_likelihood_blockers"]
    )
    assert "GW200129_V1_K_plus_not_positive" in (
        result["event_topology_likelihood_blockers"]
    )


def test_local_diagnosis_is_nonclaiming_and_handles_missing_lalsuite():
    result = diagnose_r4_parspec_event_topology_likelihood()

    assert result["version"] == "v2.194"
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    if not result["lalsuite_status"]["available"]:
        assert result["source_event_detector_topology_likelihood_ready"] is False
        assert "lalsuite_not_installed" in result["evaluation"][
            "event_topology_likelihood_blockers"
        ]


def test_committed_artifact_records_vulcan_event_topology_rerun():
    path = Path(
        "experiments/results/v2.194/"
        "r4_parspec_event_topology_likelihood.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.194"
    assert result["route_status"] == (
        "parspec_source_event_topology_likelihood_ready_covariance_missing"
    )
    assert result["source_event_detector_topology_likelihood_ready"] is True
    assert result["event_set_alignment_ready"] is True
    events = {row["paper_event"]: row for row in result["event_likelihoods"]}
    assert events["GW150914"]["detectors"] == ["H1", "L1"]
    assert events["GW200129"]["detectors"] == ["H1", "L1", "V1"]
    assert events["GW200129"]["network_likelihood"]["nuisance_points_per_detector"] == [
        81,
        81,
        81,
    ]
    v1 = events["GW200129"]["detector_channel_responses"]["V1"]
    assert v1["lal_detector_index"] == "LALDetectorIndexVIRGODIFF"
    assert v1["detector_channel_response_calibrated"] is True
    assert v1["K_plus"] > 0.0


def test_committed_artifact_keeps_remaining_claim_blockers_without_v1_response():
    path = Path(
        "experiments/results/v2.194/"
        "r4_parspec_event_topology_likelihood.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))
    blockers = set(result["evaluation"]["claim_blockers"])

    assert "gw200129_v1_detector_channel_response_missing" not in blockers
    assert "source_event_specific_nuisance_covariance_export_missing" in blockers
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in blockers
    assert "operator_basis_map_missing" in blockers
    assert result["claimable_framework_exclusions_now"] == []
