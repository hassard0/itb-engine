"""Tests for the v2.139 four-dimensional R4 projection workbench."""

from experiments.four_dimensional_r4_projection_derivation_workbench import (
    bresciani_helicity_matching_contract,
    derive_bresciani_from_source_projection,
    diagnose_four_dimensional_r4_projection_derivation_workbench,
    source_component_status,
    string_contact_matching_ansatz,
    synthetic_unit_projection_example,
)


def test_matching_contract_tracks_bresciani_helicity_channels():
    contract = bresciani_helicity_matching_contract()
    channels = contract["target_channels"]

    assert contract["spin"] == 2
    assert channels["same_helicity_to_same_helicity"]["source_symbol"] == "c_plus"
    assert channels["helicity_flip_complex_channel"]["source_symbol"] == "c_minus"
    assert contract["coordinate_inversion"]["g_R4_c3"] == "Im(c_minus)"


def test_string_contact_ansatz_defines_source_components():
    ansatz = string_contact_matching_ansatz()

    assert ansatz["matching_equations"]["c_plus"] == (
        "overall_R4_factor * K_plus / 8"
    )
    assert "K_minus_projection_on_helicity_flip_channel" in (
        ansatz["required_source_components"]
    )
    assert len(ansatz["source_urls"]) == 3


def test_projection_derivation_inverts_to_bresciani_axes():
    result = derive_bresciani_from_source_projection(
        overall_r4_factor=8.0,
        k_plus=0.3,
        k_minus_real=0.1,
        k_minus_imag=0.05,
    )

    assert result["helicity_coordinates"]["c_plus"] == 0.3
    assert result["helicity_coordinates"]["c_minus"]["real"] == 0.1
    assert result["inverted_coefficients"]["g_R4_c1"] == 0.2
    assert result["inverted_coefficients"]["g_R4_c2"] == 0.1
    assert result["inverted_coefficients"]["g_R4_c3"] == 0.05
    assert result["positivity_summary"]["passed"] is True


def test_synthetic_unit_projection_example_is_not_source_backed():
    example = synthetic_unit_projection_example()

    assert example["source_backed"] is False
    assert example["derived"]["positivity_summary"]["passed"] is True


def test_source_component_status_keeps_derivation_blocked():
    statuses = source_component_status()
    blockers = {row["blocker"] for row in statuses}

    assert all(row["status"] == "missing" for row in statuses)
    assert "source_K_plus_projection_missing" in blockers
    assert "source_K_minus_projection_missing" in blockers


def test_diagnosis_records_workbench_ready_but_no_source_components():
    result = diagnose_four_dimensional_r4_projection_derivation_workbench()

    assert result["version"] == "v2.139"
    assert result["workbench_algebra_ready"] is True
    assert result["source_projection_components_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "four_dimensional_r4_projection_workbench_ready_no_source_components"
    )
    assert result["selected_next_build_action"] == (
        "solve_source_k_factor_helicity_decomposition"
    )
