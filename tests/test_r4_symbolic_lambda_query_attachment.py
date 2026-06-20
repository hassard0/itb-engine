"""Tests for the v2.155 symbolic Lambda_R4 query attachment."""

from experiments.r4_lambda_unit_policy import NUMERIC_CLAIM_BLOCKERS
from experiments.r4_symbolic_lambda_query_attachment import (
    SYMBOLIC_BLOCKED_CLAIM_ACTION,
    SYMBOLIC_INTERNAL_ACTION,
    attach_symbolic_lambda_policy_to_query_row,
    diagnose_r4_symbolic_lambda_query_attachment,
    query_r4_symbolic_lambda_surface,
    r4_symbolic_lambda_query_surface_rows,
)
from experiments.r4_adapter_registry_hook import r4_adapter_registry_entries
from experiments.r4_projection_query_surface import query_r4_projection_surface


def test_symbolic_lambda_attachment_enhances_registered_query_row():
    row = query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    )
    sidecar = row["symbolic_lambda_r4_sidecar"]

    assert row["query_key"] == "string_tree_eft:gravity_R4_Riemann4"
    assert row["projection_status"] == "internal_projection_ready_nonclaiming"
    assert row["symbolic_lambda_r4_policy_status"] == (
        "internal_symbolic_query_ready_nonclaiming"
    )
    assert row["ready_for_internal_symbolic_query"] is True
    assert row["ready_for_numeric_wilson_export"] is False
    assert row["ready_for_framework_claim"] is False
    assert sidecar["policy_id"] == "engine_r4_lambda_symbolic_alpha_prime_policy_v1"
    assert sidecar["symbolic_coefficients"]["g_R4_c1"] == (
        "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
    )


def test_symbolic_lambda_attachment_adds_internal_and_blocked_actions():
    row = query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    )

    assert SYMBOLIC_INTERNAL_ACTION in row["allowed_internal_actions"]
    assert SYMBOLIC_BLOCKED_CLAIM_ACTION in row["blocked_claim_actions"]
    assert "symbolic_lambda_policy_nonclaiming" in row["claim_blockers"]
    for blocker in NUMERIC_CLAIM_BLOCKERS:
        assert blocker in row["claim_blockers"]


def test_attachment_helper_does_not_mutate_claim_status_to_ready():
    entry = r4_adapter_registry_entries()[0]
    base_row = query_r4_projection_surface(entry["framework"], entry["axis_family"])
    enhanced = attach_symbolic_lambda_policy_to_query_row(base_row, entry["packet"])

    assert base_row["ready_for_framework_claim"] is False
    assert enhanced["ready_for_framework_claim"] is False
    assert enhanced["claim_status"] == "claim_blocked"
    assert enhanced["ready_for_numeric_wilson_export"] is False
    assert base_row["claim_status"] == "claim_blocked"


def test_unregistered_query_remains_explicitly_blocked():
    row = query_r4_symbolic_lambda_surface("pure_gr", "gravity_R4_Riemann4")

    assert row["projection_status"] == "adapter_not_registered"
    assert row["symbolic_lambda_r4_policy_status"] == "adapter_not_registered"
    assert row["symbolic_lambda_r4_sidecar"] is None
    assert row["ready_for_internal_symbolic_query"] is False
    assert row["ready_for_numeric_wilson_export"] is False
    assert row["ready_for_framework_claim"] is False
    assert SYMBOLIC_BLOCKED_CLAIM_ACTION in row["blocked_claim_actions"]


def test_diagnosis_records_symbolic_query_surface_and_no_claims():
    result = diagnose_r4_symbolic_lambda_query_attachment()

    assert result["version"] == "v2.155"
    assert result["query_row_count"] == 1
    assert result["ready_internal_symbolic_query_keys"] == [
        "string_tree_eft:gravity_R4_Riemann4"
    ]
    assert result["numeric_wilson_export_ready_keys"] == []
    assert result["claim_ready_query_keys"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["lookup_examples"]["unregistered_pure_gr"][
        "symbolic_lambda_r4_policy_status"
    ] == "adapter_not_registered"
    assert result["route_status"] == (
        "r4_symbolic_lambda_query_surface_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "source_four_dimensional_frame_and_lambda_r4_scale_policy"
    )


def test_query_surface_rows_match_registered_symbolic_lookup():
    rows = r4_symbolic_lambda_query_surface_rows()

    assert len(rows) == 1
    assert rows[0] == query_r4_symbolic_lambda_surface(
        "string_tree_eft",
        "gravity_R4_Riemann4",
    )
