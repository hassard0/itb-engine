"""Tests for the v2.196 ParSpec published-bound surrogate."""

import json
import math
from pathlib import Path

from experiments.r4_parspec_published_bound_surrogate import (
    HALF_NORMAL_90_Z,
    diagnose_r4_parspec_published_bound_surrogate,
    evaluate_published_bound_surrogate,
    event_aligned_published_bound_packet,
    half_normal_surrogate_from_upper_bound,
    malformed_published_bound_surrogate,
    parspec_qeft_published_bound_surrogates,
)


def test_half_normal_surrogate_recovers_published_90_bound():
    row = half_normal_surrogate_from_upper_bound("combined", 51.3)

    assert row["source_axis"] == "ell_qEFT_km"
    assert math.isclose(
        row["half_normal_sigma_km"] * HALF_NORMAL_90_Z,
        row["upper_bound_km_90"],
        rel_tol=0.0,
        abs_tol=1e-9,
    )
    assert row["is_public_likelihood_or_posterior_sample"] is False
    assert row["grid"][0]["ell_qEFT_km"] == 0.0


def test_published_bound_surrogates_preserve_source_bounds():
    surrogate = parspec_qeft_published_bound_surrogates()
    rows = {row["label"]: row for row in surrogate["surrogates"]}

    assert set(rows) == {"GW150914", "GW200129", "combined"}
    assert rows["GW150914"]["upper_bound_km_90"] == 51.7
    assert rows["GW200129"]["upper_bound_km_90"] == 54.8
    assert rows["combined"]["upper_bound_km_90"] == 51.3
    assert surrogate["machine_readable_public_likelihood_ready"] is False


def test_event_aligned_packet_removes_event_set_mismatch_but_not_likelihood():
    result = diagnose_r4_parspec_published_bound_surrogate()
    evaluation = result["evaluation"]
    packet_eval = result["event_aligned_packet_evaluation"]

    assert result["published_bound_surrogate_ready"] is True
    assert evaluation["event_set_alignment_ready"] is True
    assert "event_set_mismatch_gw170608_vs_gw150914_gw200129" not in (
        packet_eval["all_blockers"]
    )
    assert "parspec_likelihood_source_axis_mismatch" not in (
        packet_eval["all_blockers"]
    )
    assert "public_parspec_qeft_likelihood_or_posterior_samples_missing" in (
        packet_eval["all_blockers"]
    )
    assert result["ready_for_framework_claim"] is False


def test_event_aligned_packet_uses_v2195_source_events():
    packet = event_aligned_published_bound_packet()

    assert packet["event_set_policy"]["status"] == "aligned"
    assert packet["event_set_policy"]["source_events"] == ["GW150914", "GW200129"]
    assert packet["event_set_policy"]["engine_events"] == ["GW150914", "GW200129"]
    assert packet["event_set_policy"]["same_event_set"] is True
    assert packet["likelihood_reference"]["status"] == "published_bound_surrogate"


def test_malformed_surrogate_rejects_quantile_and_public_flag():
    malformed = malformed_published_bound_surrogate()
    evaluation = evaluate_published_bound_surrogate(malformed)

    assert evaluation["published_bound_surrogate_ready"] is False
    assert "published_bound_surrogate_labels_mismatch" in (
        evaluation["surrogate_blockers"]
    )
    assert "GW150914_surrogate_quantile_mismatch" in (
        evaluation["surrogate_blockers"]
    )
    assert "GW200129_public_likelihood_flag_unexpected" in (
        evaluation["surrogate_blockers"]
    )


def test_committed_artifact_records_nonclaiming_bound_surrogate():
    path = Path(
        "experiments/results/v2.196/r4_parspec_published_bound_surrogate.json"
    )
    result = json.loads(path.read_text(encoding="utf-8"))

    assert result["version"] == "v2.196"
    assert result["route_status"] == (
        "parspec_published_bound_surrogate_ready_axis_map_and_public_likelihood_missing"
    )
    assert result["published_bound_surrogate_ready"] is True
    assert result["evaluation"]["machine_readable_public_likelihood_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
