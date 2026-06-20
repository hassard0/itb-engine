"""Tests for the v2.175 Bresciani R4 axis dictionary."""

from copy import deepcopy

import pytest

from experiments.bresciani_k_monomial_projector import bresciani_monomial_families
from experiments.bresciani_r4_axis_dictionary import (
    bresciani_r4_axis_dictionary,
    bresciani_r4_axis_mapping_sidecar,
    diagnose_bresciani_r4_axis_dictionary,
    evaluate_bresciani_r4_axis_dictionary,
    project_bresciani_components_to_engine_axes,
)
from experiments.r4_shape_likelihood_packet_manifest import TARGET_AXES


def test_dictionary_covers_manifest_axes_and_monomial_families():
    dictionary = bresciani_r4_axis_dictionary()

    assert set(dictionary["target_axes"]) == set(TARGET_AXES)
    assert dictionary["monomial_family_dictionary"] == bresciani_monomial_families()
    assert dictionary["source"]["primary_source_url"] == (
        "https://arxiv.org/abs/2504.12855"
    )
    assert dictionary["operator_projection_matrix"]["status"] == (
        "maps_to_bresciani_r4_axes"
    )


def test_engine_unit_projection_matches_shape_policy_axes():
    projected = project_bresciani_components_to_engine_axes(
        overall_r4_factor=8.0,
        k_plus=1.0,
        k_minus_real=0.0,
        k_minus_imag=0.0,
    )

    assert projected["coefficients"] == {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.5,
        "g_R4_c3": 0.0,
    }
    assert projected["derived"] == {
        "g_R4_plus": 1.0,
        "g_R4_minus_abs": 0.0,
    }
    assert projected["positivity_summary"]["passed"] is True


def test_mixed_helicity_projection_uses_bresciani_inverse():
    projected = project_bresciani_components_to_engine_axes(
        overall_r4_factor=8.0,
        k_plus=0.3,
        k_minus_real=0.1,
        k_minus_imag=0.05,
    )

    assert projected["coefficients"] == {
        "g_R4_c1": 0.2,
        "g_R4_c2": 0.1,
        "g_R4_c3": 0.05,
    }
    assert projected["derived"]["g_R4_plus"] == 0.3
    assert projected["derived"]["g_R4_minus_abs"] == pytest.approx(
        0.111803398875,
        abs=1e-12,
    )
    assert projected["positivity_summary"]["passed"] is True


def test_evaluation_is_axis_mapping_ready_but_nonclaiming():
    dictionary = bresciani_r4_axis_dictionary()
    result = evaluate_bresciani_r4_axis_dictionary(dictionary)

    assert result["ready_for_r4_shape_packet_axis_mapping"] is True
    assert result["ready_for_likelihood_packet"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["blockers"] == []
    assert "public_covariance_over_engine_r4_axes_missing" in (
        result["downstream_likelihood_blockers"]
    )


def test_manifest_sidecar_matches_packet_axis_contract():
    sidecar = bresciani_r4_axis_mapping_sidecar()

    assert sidecar["status"] == "maps_to_bresciani_r4_axes"
    assert set(sidecar["mapped_axes"]) == set(TARGET_AXES)
    assert sidecar["axis_normalization_declared"] is True
    assert sidecar["uses_numeric_lambda_r4_scale"] is False
    assert sidecar["claim_controls"]["claim_use_allowed"] is False
    assert sidecar["claim_controls"]["framework_claim_allowed"] is False


def test_malformed_dictionary_missing_axis_or_formula_is_rejected():
    dictionary = deepcopy(bresciani_r4_axis_dictionary())
    dictionary["target_axes"].remove("g_R4_minus_abs")
    dictionary["source_to_engine_relations"]["engine_axis_equations"].pop(
        "g_R4_c3"
    )
    dictionary["claim_controls"]["framework_claim_allowed"] = True

    result = evaluate_bresciani_r4_axis_dictionary(dictionary)

    assert result["ready_for_r4_shape_packet_axis_mapping"] is False
    assert "target_axes_incomplete" in result["blockers"]
    assert "engine_axis_equations_incomplete" in result["blockers"]
    assert "framework_claim_not_disabled" in result["blockers"]


def test_diagnosis_selects_public_gw_reanalysis_fixture_next():
    result = diagnose_bresciani_r4_axis_dictionary()

    assert result["version"] == "v2.175"
    assert result["ready_for_r4_shape_packet_axis_mapping"] is True
    assert result["ready_for_likelihood_packet"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "bresciani_r4_axis_dictionary_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "build_public_gw_reanalysis_fixture_for_r4_waveform_model"
    )
