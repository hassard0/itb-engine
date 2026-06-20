"""Tests for the v2.132 gravity R4 framework-projection requirements audit."""

from experiments.gravity_r4_framework_projection_requirements import (
    REQUIRED_R4_COEFFICIENTS,
    diagnose_gravity_r4_framework_projection_requirements,
    r4_framework_projection_schema,
)


def test_schema_requires_three_bresciani_r4_axes_and_metadata():
    schema = r4_framework_projection_schema()
    fields = {row["field"] for row in schema}

    for axis in REQUIRED_R4_COEFFICIENTS:
        assert f"coefficients.{axis}" in fields
    assert "derived.g_R4_plus" in fields
    assert "derived.g_R4_minus_abs" in fields
    assert "metadata.r4_operator_projection_matrix" in fields
    assert "metadata.r4_normalization_scale" in fields


def test_all_registered_frameworks_are_audited_and_none_are_ready():
    result = diagnose_gravity_r4_framework_projection_requirements()

    assert result["version"] == "v2.132"
    assert result["registered_framework_count"] == 13
    assert result["r4_projection_ready_frameworks"] == []
    assert len(result["frameworks_missing_r4_projection"]) == 13
    assert result["claimable_framework_exclusions_now"] == []


def test_string_tree_is_highest_priority_but_blocked_translation_candidate():
    row = diagnose_gravity_r4_framework_projection_requirements()["frameworks"][
        "string_tree_eft"
    ]

    assert row["projection_class"] == "highest_priority_translation_candidate"
    assert row["priority"] == 1
    assert "string_r4_basis_translation_to_bresciani_missing" in (
        row["promotion_blockers"]
    )
    assert "string_scale_to_lambda_r4_normalization_missing" in (
        row["promotion_blockers"]
    )
    assert row["r4_projection_ready"] is False


def test_out_of_scope_frameworks_get_scope_blockers():
    rows = diagnose_gravity_r4_framework_projection_requirements()["frameworks"]

    assert "framework_not_lorentz_invariant_for_current_r4_gate" in (
        rows["horava_lifshitz"]["promotion_blockers"]
    )
    assert "framework_not_fundamental_uv_gravity" in (
        rows["emergent_gravity"]["promotion_blockers"]
    )
    assert "framework_not_local_for_current_r4_gate" in (
        rows["causal_set"]["promotion_blockers"]
    )


def test_engine_generated_frameworks_do_not_define_source_owned_r4_axes():
    rows = diagnose_gravity_r4_framework_projection_requirements()["frameworks"]

    for name in [
        "discovered_novel",
        "discovered_parity_violating",
        "discovered_high_g8",
        "discovered_data_driven",
    ]:
        assert rows[name]["projection_class"] == (
            "engine_generated_not_framework_owned"
        )
        assert "engine_generated_framework_not_literature_owned" in (
            rows[name]["promotion_blockers"]
        )


def test_next_action_builds_a_projection_guard_schema():
    result = diagnose_gravity_r4_framework_projection_requirements()

    assert result["route_status"] == (
        "r4_framework_projection_requirements_defined_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "implement_r4_projection_guard_schema"
    )
