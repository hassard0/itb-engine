"""Tests for the v2.156 R4 frame and Lambda scale policy audit."""

from experiments.r4_frame_scale_policy_audit import (
    FRAME_SCALE_REQUIREMENTS,
    candidate_frame_scale_policies,
    diagnose_r4_frame_scale_policy_audit,
    evaluate_frame_scale_candidate,
    frame_scale_policy_requirements,
    frame_scale_source_inputs,
)


def test_frame_scale_sources_are_machine_usable_but_incomplete_for_scale():
    rows = frame_scale_source_inputs()
    source_ids = {row["source_id"] for row in rows}

    assert "bresciani_levati_paradisi_2025_spin2_target" in source_ids
    assert "kallosh_lee_rube_2008_r4_helicity_shape" in source_ids
    assert "russo_1997_type_iib_virasoro_shapiro" in source_ids
    assert "peeters_vanhove_westerberg_2000_higher_derivative_actions" in source_ids
    assert all(row["machine_usable"] is True for row in rows)
    assert any(
        "engine Lambda_R4 numeric convention" in row["does_not_provide"]
        for row in rows
    )
    assert any(
        "field-redefinition policy into Bresciani c_i coordinates"
        in row["does_not_provide"]
        for row in rows
    )


def test_frame_scale_requirements_are_all_missing_for_claims():
    rows = frame_scale_policy_requirements()

    assert {row["requirement"] for row in rows} == set(FRAME_SCALE_REQUIREMENTS)
    assert all(row["status"] == "missing" for row in rows)
    assert all(row["claim_blocker"] in FRAME_SCALE_REQUIREMENTS for row in rows)


def test_candidate_policies_keep_symbolic_route_separate_from_numeric_scale():
    candidates = candidate_frame_scale_policies()
    by_name = {row["candidate"]: row for row in candidates}

    assert "symbolic_lambda_r4_sidecar_v1" in by_name
    assert by_name["symbolic_lambda_r4_sidecar_v1"][
        "ready_for_internal_symbolic_query"
    ] is True
    assert by_name["symbolic_lambda_r4_sidecar_v1"][
        "ready_for_numeric_engine_lambda_r4"
    ] is False
    assert "direct_type_II_alpha_prime_to_engine_lambda_r4" in by_name
    assert "bresciani_target_axis_as_scale_policy" in by_name


def test_evaluation_rejects_numeric_scale_for_each_candidate():
    for candidate in candidate_frame_scale_policies():
        result = evaluate_frame_scale_candidate(candidate)

        assert result["ready_for_internal_symbolic_query"] is True
        assert result["ready_for_numeric_engine_lambda_r4"] is False
        assert result["ready_for_framework_claim"] is False
        assert result["missing_requirements"]
        assert "measurement_likelihood_missing_or_incomplete" in (
            result["missing_requirements"]
        )


def test_diagnosis_records_symbolic_only_policy_and_next_observable_route():
    result = diagnose_r4_frame_scale_policy_audit()

    assert result["version"] == "v2.156"
    assert result["symbolic_policy_ready_candidates"] == [
        "symbolic_lambda_r4_sidecar_v1",
        "direct_type_II_alpha_prime_to_engine_lambda_r4",
        "bresciani_target_axis_as_scale_policy",
        "kallosh_shape_unit_as_scale_policy",
    ]
    assert result["numeric_lambda_r4_ready_candidates"] == []
    assert result["ready_four_dimensional_frame_policy"] is False
    assert result["ready_numeric_lambda_r4_scale_policy"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == "r4_frame_scale_policy_audit_symbolic_only"
    assert result["selected_next_build_action"] == (
        "design_compactification_agnostic_r4_observable_or_measurement_route"
    )
