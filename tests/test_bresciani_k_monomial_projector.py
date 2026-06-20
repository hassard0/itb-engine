"""Tests for the v2.143 Bresciani K monomial projector."""

from experiments.bresciani_k_monomial_projector import (
    bresciani_monomial_families,
    diagnose_bresciani_k_monomial_projector,
    malformed_monomial_packet,
    project_bresciani_k_components,
    synthetic_monomial_packet,
)


def test_monomial_families_cover_bresciani_channels():
    families = bresciani_monomial_families()

    assert len(families["K_plus"]) == 3
    assert len(families["K_minus"]) == 3
    assert len(families["K_minus_conjugate"]) == 3
    assert "angle12^4_angle34^4" in families["K_minus"]


def test_synthetic_packet_projects_components_but_is_not_ready():
    result = project_bresciani_k_components(synthetic_monomial_packet())

    assert result["projected_components"]["K_plus"] == {"real": 0.3, "imag": 0.0}
    assert result["projected_components"]["K_minus"] == {
        "real": 0.1,
        "imag": 0.05,
    }
    assert result["ready_for_k_factor_projection"] is False
    assert result["blockers"] == ["source_backed_derivation_missing"]


def test_source_backed_shape_control_reaches_projection_ready():
    result = project_bresciani_k_components(
        synthetic_monomial_packet(source_backed=True)
    )

    assert result["ready_for_k_factor_projection"] is True
    assert result["blockers"] == []
    assert result["derived_bresciani_projection"]["inverted_coefficients"] == {
        "g_R4_c1": 0.2,
        "g_R4_c2": 0.1,
        "g_R4_c3": 0.05,
    }
    assert result["derived_bresciani_projection"]["positivity_summary"]["passed"] is True


def test_malformed_packet_rejects_family_asymmetry_and_conjugacy_failure():
    result = project_bresciani_k_components(malformed_monomial_packet())

    assert result["ready_for_k_factor_projection"] is False
    assert "K_minus_coefficients_not_family_symmetric" in result["blockers"]
    assert "K_minus_conjugate_coefficients_not_family_symmetric" in result["blockers"]
    assert "K_minus_conjugate_inconsistent" in result["blockers"]


def test_diagnosis_records_only_shape_control_ready_no_claims():
    result = diagnose_bresciani_k_monomial_projector()

    assert result["version"] == "v2.143"
    assert result["ready_k_factor_projection_packets"] == [
        "source_backed_shape_control"
    ]
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "bresciani_k_monomial_projector_ready_no_source_formula"
    )
    assert result["selected_next_build_action"] == (
        "fill_projector_with_source_backed_k_monomial_coefficients"
    )
