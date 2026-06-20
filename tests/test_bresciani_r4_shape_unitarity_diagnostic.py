"""Tests for the v2.158 Bresciani R4 shape-unitarity diagnostic."""

from copy import deepcopy

from experiments.bresciani_r4_shape_unitarity_diagnostic import (
    bresciani_shape_diagnostic_requirements,
    compute_bresciani_shape_diagnostics,
    diagnose_bresciani_r4_shape_unitarity_diagnostic,
    evaluate_bresciani_r4_shape_unitarity_diagnostic,
)
from experiments.r4_symbolic_lambda_query_attachment import (
    query_r4_symbolic_lambda_surface,
)


def test_shape_diagnostic_requirements_track_query_and_blocker_inputs():
    requirements = bresciani_shape_diagnostic_requirements()

    assert "registered_r4_query_row" in requirements
    assert "numeric_shape_coefficients_available" in requirements
    assert "symbolic_lambda_sidecar_attached" in requirements
    assert "claim_blocker_ledger_preserved" in requirements


def test_compute_shape_diagnostics_for_registered_string_row():
    row = query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    )
    result = compute_bresciani_shape_diagnostics(row)

    assert result["coefficients"] == {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.5,
        "g_R4_c3": 0.0,
    }
    assert result["derived"] == {
        "g_R4_plus": 1.0,
        "g_R4_minus_abs": 0.0,
    }
    assert result["positivity"]["residual_4_c1_c2_minus_c3_squared"] == 1.0
    assert result["positivity"]["passed"] is True
    assert result["shape_ratio_summary"]["g_R4_minus_abs_over_g_R4_plus"] == 0.0
    assert result["shape_ratio_summary"]["same_helicity_dominant"] is True
    assert result["shape_ratio_summary"]["source_family"] == (
        "supersymmetric_same_helicity_R4_shape"
    )
    assert result["unitarity_shape_family"]["uses_absolute_lambda_scale"] is False


def test_evaluation_is_internal_ready_but_nonclaiming():
    result = evaluate_bresciani_r4_shape_unitarity_diagnostic()

    assert result["query_key"] == "string_tree_eft:gravity_R4_Riemann4"
    assert result["ready_for_internal_shape_unitarity_diagnostic"] is True
    assert result["ready_for_measurement_likelihood_claim"] is False
    assert result["ready_for_numeric_wilson_export"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["diagnostic_blockers"] == []
    assert "measurement_likelihood_missing_or_incomplete" in result["claim_blockers"]
    assert "symbolic_lambda_policy_nonclaiming" in result["claim_blockers"]


def test_evaluation_blocks_if_symbolic_sidecar_or_ledger_missing():
    row = deepcopy(query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    ))
    row["symbolic_lambda_r4_sidecar"] = None
    row["claim_blockers"] = []

    result = evaluate_bresciani_r4_shape_unitarity_diagnostic(row)

    assert result["ready_for_internal_shape_unitarity_diagnostic"] is False
    assert "symbolic_lambda_sidecar_missing" in result["diagnostic_blockers"]
    assert "claim_blocker_ledger_missing" in result["diagnostic_blockers"]
    assert result["ready_for_framework_claim"] is False


def test_diagnosis_records_ready_nonclaiming_diagnostic_and_next_likelihood_search():
    result = diagnose_bresciani_r4_shape_unitarity_diagnostic()

    assert result["version"] == "v2.158"
    assert result["ready_for_internal_shape_unitarity_diagnostic"] is True
    assert result["ready_for_measurement_likelihood_claim"] is False
    assert result["ready_for_numeric_wilson_export"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "bresciani_r4_shape_unitarity_diagnostic_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "search_public_r4_shape_likelihood_packet"
    )
