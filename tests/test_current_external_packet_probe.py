"""Tests for the v2.94 current external packet probe."""

from experiments.current_external_packet_probe import (
    current_source_candidate_packets,
    diagnose_current_external_packet_probe,
)


def test_current_probe_finds_no_schema_or_claim_ready_packet():
    result = diagnose_current_external_packet_probe()

    assert result["version"] == "v2.94"
    assert result["route_status"] == (
        "current_source_probe_no_external_packet_satisfies_gate"
    )
    assert result["schema_ready_candidates"] == []
    assert result["claim_ready_candidates"] == []
    assert result["claimable_discriminator_now"] is False


def test_cms_hepdata_candidate_is_not_engine_normalized_g8():
    result = diagnose_current_external_packet_probe()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["cms_hepdata_energy_correlator_2024"]

    assert row["source_url"] == "https://www.hepdata.net/record/150737"
    assert "observable_basis_not_adapter_supported" in row["active_rejection_tests"]
    assert "wilson_coefficient_normalization_not_engine_g8" in (
        row["active_rejection_tests"]
    )
    assert row["claim_ready"] is False


def test_current_long_range_partial_wave_source_is_nonpromoting_formalism():
    result = diagnose_current_external_packet_probe()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["plestid_quilez_long_range_partial_wave_2026"]

    assert row["source_url"] == "https://arxiv.org/abs/2606.19432"
    assert "operator_identity_missing" in row["active_rejection_tests"]
    assert "missing_public_likelihood_or_covariance" in row["active_rejection_tests"]
    assert row["schema_ready"] is False


def test_quest_limit_is_not_gw_parity_engine_bridge():
    result = diagnose_current_external_packet_probe()
    rows = {row["label"]: row for row in result["rows"]}
    row = rows["quest_length_fluctuation_limits_2025"]

    assert row["route"] == "gw_parity_operator_normalization_search"
    assert "source_backed_operator_normalization_missing" in (
        row["active_rejection_tests"]
    )
    assert "engine_axis_target_missing" in row["active_rejection_tests"]
    assert row["claim_ready"] is False


def test_candidate_sources_are_primary_or_public_records():
    packets = current_source_candidate_packets()

    assert len(packets) == 4
    for packet in packets:
        assert packet["source_url"].startswith(("https://arxiv.org/", "https://www.hepdata.net/", "https://link.aps.org/doi/"))
        assert packet["source_type"] in {
            "primary_theory_formalism",
            "primary_measurement",
            "public_data_product",
        }
