"""Tests for the v2.192 ParSpec source-event alignment manifest."""

import json
from pathlib import Path

from experiments.r4_parspec_source_event_alignment_manifest import (
    diagnose_r4_parspec_source_event_alignment_manifest,
    evaluate_parspec_event_set_alignment_manifest,
    parspec_source_event_records,
    parspec_source_event_strain_records,
    summarize_source_event_manifest,
)


def test_source_event_records_use_gwosc_canonical_versions_and_dois():
    records = {row["paper_event"]: row for row in parspec_source_event_records()}

    assert records["GW150914"]["gwosc_event_name"] == "GW150914"
    assert records["GW150914"]["event_version"] == "GW150914-v3"
    assert records["GW150914"]["catalog"] == "GWTC-1-confident"
    assert records["GW150914"]["doi"] == "https://doi.org/10.7935/82H3-HH23"
    assert records["GW150914"]["detectors"] == ["H1", "L1"]

    assert records["GW200129"]["gwosc_event_name"] == "GW200129_065458"
    assert records["GW200129"]["event_version"] == "GW200129_065458-v1"
    assert records["GW200129"]["catalog"] == "GWTC-3-confident"
    assert records["GW200129"]["doi"] == "https://doi.org/10.7935/b024-1886"
    assert records["GW200129"]["detectors"] == ["H1", "L1", "V1"]


def test_strain_records_cover_minimal_h1_l1_and_gw200129_v1():
    events = parspec_source_event_records()
    summary = summarize_source_event_manifest(
        events,
        parspec_source_event_strain_records(),
    )

    assert summary["source_event_public_strain_urls_ready"] is True
    assert summary["missing_source_events"] == []
    assert summary["minimal_h1_l1_records_missing"] == []
    assert summary["malformed_records"] == []
    assert summary["gw200129_requires_v1_policy"] is True
    assert summary["gwosc_event_names"] == {
        "GW150914": "GW150914",
        "GW200129": "GW200129_065458",
    }


def test_32_second_records_have_event_inside_segment_and_sample_counts():
    events = parspec_source_event_records()
    summary = summarize_source_event_manifest(
        events,
        parspec_source_event_strain_records(),
    )
    rows = [
        row
        for row in summary["strain_records"]
        if row["duration"] == 32 and row["detector"] in {"H1", "L1"}
    ]

    assert rows
    assert all(row["expected_sample_count"] == 32 * 4096 for row in rows)
    assert all(row["event_inside_segment"] is True for row in rows)
    assert all(row["download_url"].endswith(".hdf5") for row in rows)
    assert any(
        row["paper_event"] == "GW200129"
        and row["gwosc_event_name"] == "GW200129_065458"
        for row in rows
    )


def test_manifest_ready_but_event_set_alignment_not_run():
    result = diagnose_r4_parspec_source_event_alignment_manifest()

    assert result["event_set_manifest_ready"] is True
    assert result["event_set_alignment_ready"] is False
    assert result["route_status"] == (
        "parspec_source_event_gwosc_manifest_ready_alignment_not_run"
    )
    blockers = result["evaluation"]["alignment_blockers"]
    assert "current_engine_event_set_not_parspec_source_events" in blockers
    assert "gw200129_v1_detector_topology_policy_missing" in blockers
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in blockers
    assert result["ready_for_framework_claim"] is False


def test_event_alignment_evaluator_accepts_event_set_after_rerun_but_keeps_claim_blockers():
    manifest = diagnose_r4_parspec_source_event_alignment_manifest()
    result = evaluate_parspec_event_set_alignment_manifest(
        manifest,
        current_engine_events=("GW150914", "GW200129"),
    )

    assert result["event_set_manifest_ready"] is True
    assert result["event_set_alignment_ready"] is False
    assert "current_engine_event_set_not_parspec_source_events" not in (
        result["alignment_blockers"]
    )
    assert "gw200129_v1_detector_topology_policy_missing" in (
        result["alignment_blockers"]
    )
    assert "operator_basis_map_missing" in result["alignment_blockers"]


def test_committed_artifact_records_source_event_manifest():
    path = Path(
        "experiments/results/v2.192/"
        "r4_parspec_source_event_alignment_manifest.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.192"
    assert result["source_event_manifest_summary"][
        "source_event_public_strain_urls_ready"
    ] is True
    assert result["source_event_manifest_summary"]["gw200129_requires_v1_policy"] is True
    assert result["event_set_alignment_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
