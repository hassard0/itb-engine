"""Tests for the v2.144 supersymmetric R4 shape projection."""

from experiments.supersymmetric_r4_shape_projection import (
    diagnose_supersymmetric_r4_shape_projection,
    kallosh_bresciani_shape_packet,
    kallosh_rederivation_packet,
    source_evidence,
)


def test_source_evidence_tracks_kallosh_and_bresciani_primary_sources():
    evidence = source_evidence()

    assert evidence["kallosh_lee_rube_2008"]["url"] == (
        "https://arxiv.org/abs/0811.3417"
    )
    assert evidence["bresciani_levati_paradisi_2025"]["url"] == (
        "https://arxiv.org/abs/2504.12855"
    )
    assert "November20.tex:M_UV_3-loop" in (
        evidence["kallosh_lee_rube_2008"]["equation_refs"]
    )
    assert "letter.tex:eq:amplitude" in (
        evidence["bresciani_levati_paradisi_2025"]["equation_refs"]
    )


def test_shape_packet_sets_kplus_unit_and_kminus_zero():
    packet = kallosh_bresciani_shape_packet()
    coefficients = packet["monomial_coefficients"]

    assert coefficients["angle12^4_square34^4"] == 1.0
    assert coefficients["angle14^4_square23^4"] == 1.0
    assert coefficients["angle34^4_square12^4"] == 1.0
    assert coefficients["angle12^4_angle34^4"] == 0.0
    assert coefficients["square12^4_square34^4"] == 0.0
    assert packet["normalization"][
        "absolute_string_alpha_prime_normalization_backed"
    ] is False


def test_rederivation_packet_is_source_backed_but_scope_limited():
    packet = kallosh_rederivation_packet()

    assert packet["source_backed_derivation"] is True
    assert packet["helicity_components"] == {
        "K_plus": 1.0,
        "K_minus_real": 0.0,
        "K_minus_imag": 0.0,
    }
    assert "not the absolute type-II string" in packet["source_k_formula"]["scope"]


def test_diagnosis_projects_to_even_bresciani_r4_shape():
    result = diagnose_supersymmetric_r4_shape_projection()
    projection = result["projector_evaluation"]["derived_bresciani_projection"]

    assert result["version"] == "v2.144"
    assert result["projector_evaluation"]["ready_for_k_factor_projection"] is True
    assert result["rederivation_evaluation"]["ready_for_k_factor_projection"] is True
    assert projection["helicity_coordinates"] == {
        "c_plus": 1.0,
        "c_minus": {"real": 0.0, "imag": 0.0},
    }
    assert projection["inverted_coefficients"] == {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.5,
        "g_R4_c3": 0.0,
    }
    assert projection["positivity_summary"]["passed"] is True


def test_diagnosis_records_no_claim_until_absolute_normalization_is_done():
    result = diagnose_supersymmetric_r4_shape_projection()

    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert "absolute_type_II_string_alpha_prime_R4_coefficient" in (
        result["remaining_normalization_gaps"]
    )
    assert result["route_status"] == (
        "supersymmetric_r4_shape_projected_string_normalization_open"
    )
    assert result["selected_next_build_action"] == (
        "normalize_supersymmetric_r4_shape_to_string_alpha_prime_units"
    )
