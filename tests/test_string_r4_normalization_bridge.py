"""Tests for the v2.145 string R4 normalization bridge."""

from experiments.string_r4_normalization_bridge import (
    RUSSO_TREE_R4_CONTACT_SCALAR,
    ZETA_3,
    diagnose_string_r4_normalization_bridge,
    evaluate_string_r4_normalization_bridge,
    normalization_bridge_requirements,
    source_backed_unit_shape_control_packet,
    source_fixed_partial_packet,
    synthetic_unit_bridge_packet,
)


def test_requirements_track_contact_k_bridge_and_engine_units():
    fields = {row["field"] for row in normalization_bridge_requirements()}

    assert fields == {
        "source_contact_scalar",
        "k_convention_bridge",
        "engine_lambda_r4_unit_conversion",
    }


def test_russo_contact_scalar_is_two_zeta_three():
    assert RUSSO_TREE_R4_CONTACT_SCALAR == 2.0 * ZETA_3
    assert round(RUSSO_TREE_R4_CONTACT_SCALAR, 12) == 2.404113806319


def test_source_fixed_partial_packet_is_rejected_until_bridges_exist():
    result = evaluate_string_r4_normalization_bridge(source_fixed_partial_packet())

    assert result["source_contact_scalar"] == round(RUSSO_TREE_R4_CONTACT_SCALAR, 12)
    assert result["ready_for_engine_normalized_r4_projection"] is False
    assert "k_convention_bridge_missing_or_not_source_backed" in result["blockers"]
    assert "engine_lambda_r4_unit_conversion_missing_or_not_source_backed" in (
        result["blockers"]
    )


def test_synthetic_unit_bridge_still_rejected():
    result = evaluate_string_r4_normalization_bridge(synthetic_unit_bridge_packet())

    assert result["candidate_projection"] is None
    assert result["ready_for_engine_normalized_r4_projection"] is False
    assert "source_backed_normalization_missing" in result["blockers"]


def test_source_backed_unit_shape_control_computes_expected_projection():
    result = evaluate_string_r4_normalization_bridge(
        source_backed_unit_shape_control_packet()
    )
    projection = result["candidate_projection"]

    assert result["ready_for_engine_normalized_r4_projection"] is True
    assert result["blockers"] == []
    assert projection["helicity_coordinates"] == {
        "c_plus": round(RUSSO_TREE_R4_CONTACT_SCALAR / 8.0, 12),
        "c_minus": {"real": 0.0, "imag": 0.0},
    }
    assert projection["inverted_coefficients"] == {
        "g_R4_c1": round(RUSSO_TREE_R4_CONTACT_SCALAR / 16.0, 12),
        "g_R4_c2": round(RUSSO_TREE_R4_CONTACT_SCALAR / 16.0, 12),
        "g_R4_c3": 0.0,
    }


def test_diagnosis_records_bridge_missing_no_claims():
    result = diagnose_string_r4_normalization_bridge()

    assert result["version"] == "v2.145"
    assert result["ready_normalization_packets"] == []
    assert result["ready_control_packets"] == [
        "source_backed_unit_shape_control"
    ]
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "string_r4_normalization_equation_ready_bridge_missing"
    )
    assert result["selected_next_build_action"] == (
        "source_k_convention_bridge_or_define_engine_lambda_r4_unit"
    )
    assert "k_convention_bridge_missing_or_not_source_backed" in (
        result["current_blockers"]
    )
