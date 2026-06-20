"""Tests for the v2.180 source-backed R4 PN/IMR derivation."""

import numpy as np
import pytest

from experiments.r4_source_backed_pn_imr_derivation import (
    BERNARD_SOURCE_URL,
    LIU_YUNES_SOURCE_URL,
    evaluate_r4_source_backed_pn_imr_derivation,
    malformed_r4_source_backed_pn_imr_derivation,
    quartic_curvature_pn_dictionary,
    r4_pn_power_law_terms,
    source_backed_r4_pn_imr_response_derivation,
    diagnose_r4_source_backed_pn_imr_derivation,
)


def test_quartic_dictionary_records_source_backed_5pn_and_7pn_rules():
    dictionary = quartic_curvature_pn_dictionary()
    row = dictionary["quartic_no_scalar_no_derivatives"]

    assert dictionary["source_reference"] == BERNARD_SOURCE_URL
    assert row["curvature_order_p"] == 4
    assert row["extra_degrees_of_freedom"] is False
    assert row["derivatives_of_riemann"] is False
    assert row["tidal_pn_order"] == 5.0
    assert row["direct_bulk_pn_order"] == 7.0


def test_pn_power_law_terms_match_frequency_domain_rules():
    grid = np.array([0.1, 0.2, 0.3])
    terms = r4_pn_power_law_terms(grid)

    assert terms["phase_delta_psi"]["tidal_5pn"] == pytest.approx(
        list(grid**5)
    )
    assert terms["phase_delta_psi"]["direct_bulk_7pn"] == pytest.approx(
        list(grid**9)
    )
    assert terms["relative_amplitude_delta_a_over_a_newt"]["tidal_5pn"] == (
        pytest.approx(list(grid**10))
    )
    assert terms["relative_amplitude_delta_a_over_a_newt"][
        "direct_bulk_7pn"
    ] == pytest.approx(list(grid**14))


def test_source_backed_derivation_has_rank_three_bresciani_channel_basis():
    derivation = source_backed_r4_pn_imr_response_derivation()
    rank = derivation["channel_rank_probe"]

    assert derivation["source_backed_waveform_derivation"] is True
    assert derivation["axis_mapping"]["status"] == "maps_to_bresciani_r4_axes"
    assert rank["source_channels"] == ["K_plus", "Re_K_minus", "Im_K_minus"]
    assert rank["channel_kernel_rank"] == 3
    assert rank["flattened_vector_length"] > 1000
    assert set(derivation["source_evidence"]) == {
        "bernard_giri_lehner_sturani_2025",
        "bresciani_levati_paradisi_2025",
        "liu_yunes_2024",
    }
    assert derivation["source_evidence"]["liu_yunes_2024"]["url"] == (
        LIU_YUNES_SOURCE_URL
    )


def test_evaluation_ready_to_replace_ansatz_but_not_claiming():
    derivation = source_backed_r4_pn_imr_response_derivation()
    result = evaluate_r4_source_backed_pn_imr_derivation(derivation)

    assert result["response_derivation_ready"] is True
    assert result["ready_to_replace_v2_177_ansatz_kernel_basis"] is True
    assert result["ready_to_wire_into_v2_179_hdf5_projection"] is True
    assert result["ready_for_framework_claim"] is False
    assert result["derivation_blockers"] == []
    assert result["removed_v2_179_blocker"] == (
        "r4_response_kernels_are_ansatz_not_source_backed"
    )
    assert "source_backed_r4_pn_or_imr_waveform_derivation" not in (
        result["remaining_real_reanalysis_blockers"]
    )
    assert "nuisance_marginalized_covariance_not_exported" in (
        result["remaining_real_reanalysis_blockers"]
    )


def test_malformed_derivation_rejects_source_pn_rank_and_claim_toggle():
    result = evaluate_r4_source_backed_pn_imr_derivation(
        malformed_r4_source_backed_pn_imr_derivation()
    )

    assert result["response_derivation_ready"] is False
    assert "response_not_marked_source_backed" in result["derivation_blockers"]
    assert "direct_bulk_pn_order_not_7pn" in result["derivation_blockers"]
    assert "phase_delta_psi_direct_bulk_7pn_power_law_mismatch" in (
        result["derivation_blockers"]
    )
    assert "engine_axis_channel_weights_changed" in result["derivation_blockers"]
    assert "claim_use_not_disabled" in result["derivation_blockers"]
    assert "source_backed_r4_pn_or_imr_waveform_derivation" in (
        result["remaining_real_reanalysis_blockers"]
    )


def test_diagnosis_selects_wiring_kernels_into_gwosc_projection_next():
    result = diagnose_r4_source_backed_pn_imr_derivation()

    assert result["version"] == "v2.180"
    assert result["response_derivation_ready"] is True
    assert result["ready_real_public_r4_reanalysis_packets_now"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "r4_source_backed_pn_imr_derivation_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "wire_source_backed_r4_pn_kernels_into_gwosc_hdf5_projection"
    )
