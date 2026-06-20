"""Tests for the v2.137 strict R4 source-provenance guard."""

from experiments.gravity_r4_source_provenance_guard import (
    diagnose_gravity_r4_source_provenance_guard,
    evaluate_r4_source_provenance_packet,
    source_backed_control_packet,
    source_provenance_summary,
    v2136_symbolic_fixture_packet,
)


def test_strict_guard_rejects_v2136_nested_synthetic_fixture():
    result = evaluate_r4_source_provenance_packet(v2136_symbolic_fixture_packet())

    assert result["base_ready_for_framework_projection"] is True
    assert result["ready_for_source_backed_framework_projection"] is False
    assert "synthetic_fixture_not_real_source" in result["strict_projection_blockers"]
    assert "source_provenance_missing_or_incomplete" in (
        result["strict_projection_blockers"]
    )
    assert result["source_provenance_summary"]["truthy_synthetic_fixture_paths"] == [
        "$.ownership_metadata.synthetic_fixture"
    ]


def test_source_backed_control_passes_strict_projection_but_not_claim():
    result = evaluate_r4_source_provenance_packet(source_backed_control_packet())

    assert result["base_ready_for_framework_projection"] is True
    assert result["ready_for_source_backed_framework_projection"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["strict_projection_blockers"] == []
    assert result["strict_claim_blockers"] == [
        "discriminator_math_not_excluding",
        "measurement_likelihood_missing_or_incomplete",
    ]


def test_source_provenance_requires_packet_source_url_to_be_listed():
    packet = source_backed_control_packet()
    packet["source_provenance"]["primary_source_urls"] = [
        "https://doi.org/10.1016/0550-3213(86)90429-3"
    ]

    summary = source_provenance_summary(packet)
    result = evaluate_r4_source_provenance_packet(packet)

    assert summary["source_url_is_listed"] is False
    assert "source_url_not_listed_in_source_provenance" in (
        result["strict_projection_blockers"]
    )


def test_source_provenance_rejects_non_primary_urls():
    packet = source_backed_control_packet()
    packet["source_provenance"]["primary_source_urls"] = [
        "https://example.com/not-primary"
    ]

    result = evaluate_r4_source_provenance_packet(packet)

    assert "source_provenance_url_not_primary_allowed" in (
        result["strict_projection_blockers"]
    )


def test_diagnosis_records_fixture_block_and_no_claims():
    result = diagnose_gravity_r4_source_provenance_guard()

    assert result["version"] == "v2.137"
    assert result["source_backed_ready_projection_packets"] == [
        "source_backed_control"
    ]
    assert result["fixture_blocked_packets"] == [
        "v2.136_symbolic_fixture_replay"
    ]
    assert result["claimable_framework_exclusions_now"] == []
    assert result["blocker_counts"]["synthetic_fixture_not_real_source"] == 1
    assert result["route_status"] == (
        "r4_source_provenance_guard_blocks_nested_fixture"
    )
