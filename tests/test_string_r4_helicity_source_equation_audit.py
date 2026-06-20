"""Tests for the v2.138 string R4 source-equation audit."""

from experiments.string_r4_helicity_source_equation_audit import (
    diagnose_string_r4_helicity_source_equation_audit,
    partial_string_r4_packet_probe,
    required_source_backed_helicity_steps,
    source_equation_rows,
)


def test_source_rows_separate_target_contract_from_string_sources():
    rows = source_equation_rows()
    by_id = {row["source_id"]: row for row in rows}

    assert by_id["bresciani_levati_paradisi_2026"][
        "provides_c_plus_c_minus_contract"
    ] is True
    assert by_id["russo_1997_type_iib_four_graviton"][
        "provides_string_helicity_amplitude_expansion"
    ] is True
    assert by_id["peeters_vanhove_westerberg_2001"][
        "provides_string_r4_family"
    ] is True
    assert not any(
        row["provides_four_dimensional_string_to_bresciani_projection"]
        for row in rows
    )


def test_required_steps_record_missing_projection_not_missing_sources():
    steps = required_source_backed_helicity_steps()
    statuses = {step["step"]: step["status"] for step in steps}
    blockers = {step["blocker"] for step in steps if step["blocker"]}

    assert statuses["target_coordinate_contract"] == "sourced"
    assert statuses["string_r4_family_and_amplitude"] == "sourced"
    assert "string_tensor_to_bresciani_projection_missing" in blockers
    assert "source_backed_c_plus_c_minus_values_missing" in blockers


def test_partial_packet_probe_is_honest_about_source_family_only():
    packet = partial_string_r4_packet_probe()

    assert packet["source_provenance"]["source_backed_derivation"] is False
    assert packet["source_provenance"]["derivation_kind"] == "source_family_only"
    assert packet["coefficients"] == {}
    assert packet["derived"] == {}


def test_diagnosis_does_not_replace_fixture_without_projection_source():
    result = diagnose_string_r4_helicity_source_equation_audit()

    assert result["version"] == "v2.138"
    assert result["can_replace_fixture_with_source_backed_evaluation_now"] is False
    assert result["direct_string_to_bresciani_projection_sources"] == []
    assert result["source_backed_c_plus_c_minus_sources"] == []
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "string_r4_helicity_sources_audited_projection_missing"
    )
    assert result["selected_next_build_action"] == (
        "build_four_dimensional_r4_projection_derivation_workbench"
    )


def test_strict_guard_probe_remains_blocked_by_missing_coefficients():
    result = diagnose_string_r4_helicity_source_equation_audit()
    probe = result["strict_guard_probe"]

    assert probe["ready_for_source_backed_framework_projection"] is False
    assert "r4_coefficients_missing_or_nonnumeric" in (
        probe["strict_projection_blockers"]
    )
    assert "source_provenance_missing_or_incomplete" in (
        probe["strict_projection_blockers"]
    )
