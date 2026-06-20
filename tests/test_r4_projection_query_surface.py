"""Tests for the v2.150 R4 projection query surface."""

from experiments.r4_projection_query_surface import (
    diagnose_r4_projection_query_surface,
    query_r4_projection_surface,
    r4_projection_query_surface_rows,
)


def test_query_surface_exposes_registered_string_r4_row():
    rows = r4_projection_query_surface_rows()

    assert len(rows) == 1
    row = rows[0]
    assert row["query_key"] == "string_tree_eft:gravity_R4_Riemann4"
    assert row["projection_status"] == "internal_projection_ready_nonclaiming"
    assert row["claim_status"] == "claim_blocked"
    assert row["ready_for_internal_query"] is True
    assert row["ready_for_framework_claim"] is False


def test_query_row_contains_coefficients_and_policy_normalization():
    row = query_r4_projection_surface("string_tree_eft", "gravity_R4_Riemann4")

    assert row["coefficients"] == {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.5,
        "g_R4_c3": 0.0,
    }
    assert row["derived"] == {
        "g_R4_plus": 1.0,
        "g_R4_minus_abs": 0.0,
    }
    assert row["normalization"]["policy_id"] == "engine_r4_shape_unit_v1"
    assert row["normalization"]["claim_use_allowed"] is False


def test_query_row_lists_allowed_and_blocked_actions():
    row = query_r4_projection_surface("string_tree_eft", "gravity_R4_Riemann4")

    assert row["allowed_internal_actions"] == [
        "inspect_bresciani_coefficients",
        "run_positivity_diagnostics",
        "compare_relative_r4_shapes",
    ]
    assert "make_framework_exclusion" in row["blocked_claim_actions"]
    assert "registry_claim_path_disabled" in row["claim_blockers"]
    assert row["exposure_blockers"] == []


def test_unregistered_framework_query_is_explicitly_blocked():
    row = query_r4_projection_surface("pure_gr", "gravity_R4_Riemann4")

    assert row["projection_status"] == "adapter_not_registered"
    assert row["ready_for_internal_query"] is False
    assert row["ready_for_framework_claim"] is False
    assert row["not_found_blocker"] == "r4_adapter_not_registered"


def test_diagnosis_records_query_surface_and_no_claims():
    result = diagnose_r4_projection_query_surface()

    assert result["version"] == "v2.150"
    assert result["query_row_count"] == 1
    assert result["ready_internal_query_keys"] == [
        "string_tree_eft:gravity_R4_Riemann4"
    ]
    assert result["claim_ready_query_keys"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["lookup_examples"]["unregistered_pure_gr"]["projection_status"] == (
        "adapter_not_registered"
    )
    assert result["route_status"] == "r4_projection_query_surface_ready_nonclaiming"
    assert result["selected_next_build_action"] == (
        "attack_r4_claim_blockers_absolute_normalization_or_likelihood"
    )
