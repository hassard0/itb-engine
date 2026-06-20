"""Tests for the v2.142 K-factor rederivation route validator."""

from experiments.polarization_k_factor_rederivation_route import (
    diagnose_polarization_k_factor_rederivation_route,
    empty_rederivation_packet,
    evaluate_k_rederivation_packet,
    rederivation_stages,
    synthetic_control_packet,
)


def test_rederivation_stages_include_k_components_and_normalization():
    stages = {row["stage"]: row for row in rederivation_stages()}

    assert "state_source_k_formula" in stages
    assert "project_helicity_components" in stages
    assert "normalize_to_engine_lambda_r4" in stages
    assert "invert_and_check_positivity" in stages


def test_empty_packet_is_rejected_with_expected_blockers():
    result = evaluate_k_rederivation_packet(empty_rederivation_packet())

    assert result["ready_for_k_factor_projection"] is False
    assert "missing_required_fields" in result["blockers"]
    assert "source_urls_not_primary" in result["blockers"]
    assert "k_plus_k_minus_components_missing_or_nonnumeric" in result["blockers"]


def test_synthetic_control_has_components_but_is_not_source_backed():
    result = evaluate_k_rederivation_packet(synthetic_control_packet())

    assert result["ready_for_k_factor_projection"] is False
    assert result["k_components"] == {
        "K_plus": 0.3,
        "K_minus_real": 0.1,
        "K_minus_imag": 0.05,
    }
    assert result["derived_bresciani_projection"] is None
    assert result["blockers"] == ["source_backed_derivation_missing"]


def test_source_backed_packet_can_reach_projection_ready():
    packet = synthetic_control_packet()
    packet["label"] = "source_backed_control_shape"
    packet["source_k_formula"]["status"] = "source_backed_derivation"
    packet["source_backed_derivation"] = True

    result = evaluate_k_rederivation_packet(packet)

    assert result["ready_for_k_factor_projection"] is True
    assert result["blockers"] == []
    assert result["derived_bresciani_projection"]["inverted_coefficients"] == {
        "g_R4_c1": 0.2,
        "g_R4_c2": 0.1,
        "g_R4_c3": 0.05,
    }


def test_diagnosis_records_no_ready_packets_and_no_claims():
    result = diagnose_polarization_k_factor_rederivation_route()

    assert result["version"] == "v2.142"
    assert result["ready_k_factor_projection_packets"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "polarization_k_factor_rederivation_route_specified_no_source_packet"
    )
    assert result["selected_next_build_action"] == (
        "derive_or_ingest_source_backed_k_rederivation_packet"
    )
