"""Tests for the v2.134 string R4 basis-translation source audit."""

from experiments.string_r4_basis_translation_source_audit import (
    diagnose_string_r4_basis_translation_source_audit,
    string_r4_source_candidates,
)


def test_source_audit_finds_string_r4_sources_but_no_guard_ready_adapter():
    result = diagnose_string_r4_basis_translation_source_audit()

    assert result["version"] == "v2.134"
    assert result["source_count"] >= 5
    assert "gross_witten_1986" in result["useful_string_r4_sources"]
    assert "gross_sloan_1987" in result["useful_string_r4_sources"]
    assert result["direct_guard_ready_projection_sources"] == []
    assert result["can_build_guard_passing_string_r4_adapter_now"] is False
    assert result["claimable_framework_exclusions_now"] == []


def test_gross_sources_establish_r4_family_without_bresciani_projection():
    rows = {row["source_id"]: row for row in string_r4_source_candidates()}

    for source_id in ("gross_witten_1986", "gross_sloan_1987"):
        row = rows[source_id]
        assert row["establishes_string_r4_family"] is True
        assert row["gives_four_graviton_r4_action_or_amplitude"] is True
        assert row["gives_bresciani_c_i_spin2_values"] is False
        assert row["gives_string_to_bresciani_projection_matrix"] is False


def test_bresciani_source_is_target_basis_not_string_translation():
    row = {
        source["source_id"]: source
        for source in string_r4_source_candidates()
    }["bresciani_levati_paradisi_2026"]

    assert row["establishes_bresciani_target_basis"] is True
    assert row["gives_bresciani_c_i_spin2_values"] is True
    assert row["establishes_string_r4_family"] is False
    assert row["gives_string_to_bresciani_projection_matrix"] is False


def test_guard_probe_rejects_partial_string_tree_packet():
    probe = diagnose_string_r4_basis_translation_source_audit()[
        "string_tree_guard_probe"
    ]

    assert probe["ready_for_framework_projection"] is False
    assert "r4_coefficients_missing_or_nonnumeric" in (
        probe["projection_blockers"]
    )
    assert "r4_operator_projection_matrix_not_source_backed" in (
        probe["projection_blockers"]
    )
    assert probe["ownership_summary"]["framework_source_owned"] is True


def test_translation_steps_identify_projection_normalization_and_uncertainty_blockers():
    result = diagnose_string_r4_basis_translation_source_audit()

    assert "string_to_bresciani_operator_projection_matrix_missing" in (
        result["translation_blockers"]
    )
    assert "engine_lambda_r4_normalization_missing" in (
        result["translation_blockers"]
    )
    assert "r4_uncertainty_or_covariance_missing" in (
        result["translation_blockers"]
    )


def test_next_action_builds_symbolic_projection_plan():
    result = diagnose_string_r4_basis_translation_source_audit()

    assert result["route_status"] == (
        "string_r4_sources_found_no_bresciani_projection_adapter"
    )
    assert result["selected_next_build_action"] == (
        "build_symbolic_string_r4_to_bresciani_projection_plan"
    )
