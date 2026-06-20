"""Tests for the v2.129 current-source G8 sidecar scout."""

from experiments.gw_alpha_g8_sidecar_source_scout import (
    diagnose_gw_alpha_g8_sidecar_source_scout,
    primary_source_scout_rows,
)


def test_source_scout_scans_primary_and_public_rows():
    rows = primary_source_scout_rows()
    labels = {row["label"] for row in rows}

    assert len(rows) >= 7
    assert "bresciani_partial_wave_unitarity_bounds_v2_2026" in labels
    assert "cms_energy_correlator_hepdata_2024" in labels
    assert "liu_yunes_gw170608_alpha_constraints_2024" in labels
    assert all(row["packet_attempt"]["synthetic_fixture"] is False for row in rows)


def test_source_scout_finds_no_real_claim_ready_packet():
    result = diagnose_gw_alpha_g8_sidecar_source_scout()

    assert result["version"] == "v2.129"
    assert result["source_count"] == result["evaluated_packet_attempt_count"]
    assert result["acceptance_ready_source_packets"] == []
    assert result["claim_ready_source_packets"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "current_g8_sidecar_sources_scanned_no_real_packet"
    )


def test_bresciani_formalism_is_closest_but_still_blocked():
    result = diagnose_gw_alpha_g8_sidecar_source_scout()
    closest = result["closest_source_packet_attempts"][0]

    assert closest["label"] == "bresciani_partial_wave_unitarity_bounds_v2_2026"
    assert closest["claim_ready"] is False
    assert "external_numeric_measurement_missing" in closest["claim_blockers"]
    assert "public_g8_likelihood_or_covariance_missing" in (
        closest["claim_blockers"]
    )
    assert "projection_to_engine_g8_missing" in closest["claim_blockers"]


def test_public_energy_correlator_data_does_not_promote_to_g8():
    result = diagnose_gw_alpha_g8_sidecar_source_scout()
    attempts = {
        row["label"]: row
        for row in result["evaluated_source_packet_attempts_ranked"]
    }
    cms = attempts["cms_energy_correlator_hepdata_2024"]

    assert cms["claim_ready"] is False
    assert "observable_basis_not_g8_high_moment" in cms["claim_blockers"]
    assert "engine_g8_normalization_missing" in cms["claim_blockers"]
    assert "external_numeric_measurement_missing" in cms["claim_blockers"]
    assert "public_g8_likelihood_or_covariance_missing" in (
        cms["claim_blockers"]
    )


def test_next_action_targets_projection_before_claims():
    result = diagnose_gw_alpha_g8_sidecar_source_scout()

    assert result["selected_next_build_action"] == (
        "derive_bresciani_v2_partial_wave_to_engine_g8_projection_audit"
    )
    assert result["legacy_source_queue_labels"]
