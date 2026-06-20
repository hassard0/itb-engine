"""Tests for the v2.188 ParSpec R4 ringdown source bridge."""

import json
from pathlib import Path

from experiments.r4_lalsuite_waveform_likelihood_posterior import AXES
from experiments.r4_parspec_ringdown_source_bridge import (
    PARSPEC_QEFT_BOUND_KM_90,
    diagnose_r4_parspec_ringdown_source_bridge,
    evaluate_parspec_r4_bridge,
    malformed_parspec_r4_bridge_packet,
    parspec_quartic_eft_source,
    parspec_r4_bridge_packet,
)


def test_parspec_source_records_quartic_eft_ringdown_bound():
    source = parspec_quartic_eft_source()

    assert source["source_url"] == "https://arxiv.org/abs/2205.05132"
    assert source["source_ringdown_model_available"] is True
    assert source["quartic_eft_bound_available"] is True
    assert source["bounds_90_credible_km"]["quartic_eft_length_scale"] == (
        PARSPEC_QEFT_BOUND_KM_90
    )
    assert source["events"] == ["GW150914", "GW200129"]
    assert source["source_owned_full_imr_sampler_export_available"] is False


def test_bridge_packet_carries_v2187_frontier_and_engine_axes():
    packet = parspec_r4_bridge_packet()

    assert packet["packet_id"] == (
        "parspec_quartic_eft_ringdown_to_engine_r4_bridge_v1"
    )
    assert packet["v2_187_frontier"]["ready"] is True
    assert set(packet["engine_axes"]) == set(AXES)
    assert packet["event_bridge"]["same_event_set"] is False
    assert packet["axis_map_to_engine_r4"]["status"] == "missing"


def test_parspec_bridge_ready_but_sampler_and_claim_not_ready():
    packet = parspec_r4_bridge_packet()
    result = evaluate_parspec_r4_bridge(packet)

    assert result["source_bridge_ready"] is True
    assert result["source_owned_full_imr_sampler_ready"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "parspec_r4_ringdown_source_bridge_ready_nonclaiming"
    )
    assert "engine_r4_axes_to_parspec_qeft_length_map_missing" in (
        result["bridge_blockers"]
    )
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in (
        result["bridge_blockers"]
    )
    assert result["split_v2_187_blocker"]["now_resolved_subpiece"] == (
        "primary_parspec_quartic_eft_ringdown_source_identified"
    )


def test_malformed_packet_blocks_even_source_bridge_readiness():
    result = evaluate_parspec_r4_bridge(malformed_parspec_r4_bridge_packet())

    assert result["source_bridge_ready"] is False
    assert "parspec_primary_source_url_missing" in result["bridge_blockers"]
    assert "quartic_eft_bound_not_available" in result["bridge_blockers"]
    assert "engine_r4_axes_mismatch" in result["bridge_blockers"]
    assert "claim_use_not_disabled" in result["bridge_blockers"]


def test_diagnosis_selects_mapping_or_public_samples_next():
    result = diagnose_r4_parspec_ringdown_source_bridge()

    assert result["version"] == "v2.188"
    assert result["source_bridge_ready"] is True
    assert result["source_owned_full_imr_sampler_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["selected_next_build_action"] == (
        "map_parspec_qeft_length_likelihood_to_engine_r4_axes_or_find_public_samples"
    )


def test_committed_artifact_records_ready_nonclaiming_source_bridge():
    path = Path(
        "experiments/results/v2.188/r4_parspec_ringdown_source_bridge.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.188"
    assert result["route_status"] == (
        "parspec_r4_ringdown_source_bridge_ready_nonclaiming"
    )
    assert result["source_bridge_ready"] is True
    assert result["source_owned_full_imr_sampler_ready"] is False
    assert result["evaluation"]["parspec_bound_imported"][
        "quartic_eft_length_scale_90_credible_km"
    ] == PARSPEC_QEFT_BOUND_KM_90
    assert result["evaluation"]["split_v2_187_blocker"][
        "now_resolved_subpiece"
    ] == "primary_parspec_quartic_eft_ringdown_source_identified"
