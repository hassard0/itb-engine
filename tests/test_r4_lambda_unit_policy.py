"""Tests for the v2.154 symbolic Lambda_R4 unit policy."""

from copy import deepcopy

import pytest

from experiments.r4_lambda_unit_policy import (
    DISALLOWED_POLICY_USES,
    NUMERIC_CLAIM_BLOCKERS,
    diagnose_r4_lambda_unit_policy,
    engine_r4_lambda_alpha_prime_policy,
    evaluate_r4_lambda_alpha_prime_policy,
    evaluate_symbolic_lambda_r4_sidecar,
    symbolic_lambda_r4_sidecar_for_packet,
)


def test_lambda_policy_preserves_symbolic_alpha_prime_and_kappa_factor():
    policy = engine_r4_lambda_alpha_prime_policy()
    source_bridge = policy["source_bridge"]
    projection = policy["symbolic_projection"]

    assert policy["status"] == "engine_convention_symbolic_nonclaiming"
    assert policy["depends_on_shape_policy"]["policy_id"] == (
        "engine_r4_shape_unit_v1"
    )
    assert source_bridge["source_backed_open_rederivation"] is True
    assert source_bridge["symbolic_factor_without_shape"] == (
        "2*zeta(3)*alpha_prime^3/(64*kappa^2)"
    )
    assert source_bridge["k_russo_over_shape"] == (
        "alpha_prime^3/(64*kappa^4)"
    )
    assert policy["engine_axis_contract"]["source_formula"] == (
        "g_R4_ci = Lambda_R4^8 * c_i^(2)"
    )
    assert policy["engine_axis_contract"]["lambda_power"] == 8
    assert policy["symbolic_scale"]["expression"] == (
        "Lambda_R4^8*alpha_prime^3/kappa^2"
    )
    assert projection["overall_R4_factor_symbolic"] == (
        "2*zeta(3)*Lambda_R4^8*alpha_prime^3/(64*kappa^2)"
    )
    assert projection["coefficients_symbolic"]["g_R4_c1"] == (
        "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
    )
    assert projection["derived_symbolic"]["g_R4_plus"] == (
        "zeta(3)*Lambda_R4^8*alpha_prime^3/(256*kappa^2)"
    )
    assert policy["engine_axis_policy"]["unit_status"] == "symbolic_only"
    assert policy["engine_axis_policy"]["numeric_coefficient_export_allowed"] is False
    assert policy["framework_claim_allowed"] is False


def test_lambda_policy_evaluation_is_symbolic_only():
    policy = engine_r4_lambda_alpha_prime_policy()
    result = evaluate_r4_lambda_alpha_prime_policy(policy)

    assert result["ready_for_symbolic_engine_lambda_policy"] is True
    assert result["ready_for_numeric_engine_lambda_r4"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["symbolic_policy_blockers"] == []
    assert result["numeric_claim_blockers"] == sorted(NUMERIC_CLAIM_BLOCKERS)
    assert set(DISALLOWED_POLICY_USES).issubset(result["disallowed_uses"])


def test_lambda_policy_rejects_numeric_or_claim_toggles():
    policy = deepcopy(engine_r4_lambda_alpha_prime_policy())
    policy["engine_axis_policy"]["numeric_kappa_value"] = 1.0
    policy["engine_axis_policy"]["numeric_coefficient_export_allowed"] = True
    policy["framework_claim_allowed"] = True

    result = evaluate_r4_lambda_alpha_prime_policy(policy)

    assert result["ready_for_symbolic_engine_lambda_policy"] is False
    assert "numeric_kappa_value_must_remain_unset" in (
        result["symbolic_policy_blockers"]
    )
    assert "numeric_coefficient_export_not_disabled" in (
        result["symbolic_policy_blockers"]
    )
    assert "framework_claim_not_disabled" in result["symbolic_policy_blockers"]


@pytest.mark.parametrize(
    ("section", "field", "value", "expected_blocker"),
    [
        (
            "engine_axis_policy",
            "numeric_lambda_r4_value",
            1.0,
            "numeric_lambda_r4_value_must_remain_unset",
        ),
        (
            "engine_axis_policy",
            "numeric_alpha_prime_value",
            1.0,
            "numeric_alpha_prime_value_must_remain_unset",
        ),
        (
            "engine_axis_policy",
            "numeric_kappa_value",
            1.0,
            "numeric_kappa_value_must_remain_unset",
        ),
        (
            "engine_axis_policy",
            "frame_choice",
            "einstein_frame",
            "frame_choice_must_remain_unset",
        ),
        (
            "engine_axis_contract",
            "numeric_lambda_r4_value",
            1.0,
            "numeric_lambda_r4_value_must_remain_unset",
        ),
        (
            "symbolic_scale",
            "numeric_value",
            1.0,
            "symbolic_scale_numeric_value_must_remain_unset",
        ),
    ],
)
def test_lambda_policy_rejects_any_numeric_symbol_collapse(
    section,
    field,
    value,
    expected_blocker,
):
    policy = deepcopy(engine_r4_lambda_alpha_prime_policy())
    policy[section][field] = value

    result = evaluate_r4_lambda_alpha_prime_policy(policy)

    assert result["ready_for_symbolic_engine_lambda_policy"] is False
    assert expected_blocker in result["symbolic_policy_blockers"]


def test_symbolic_sidecar_keeps_shape_numeric_but_absolute_factor_symbolic():
    sidecar = symbolic_lambda_r4_sidecar_for_packet()

    assert sidecar["framework"] == "string_tree_eft"
    assert sidecar["axis_family"] == "gravity_R4_Riemann4"
    assert sidecar["numeric_shape_coefficients"] == {
        "g_R4_c1": 0.5,
        "g_R4_c2": 0.5,
        "g_R4_c3": 0.0,
    }
    assert sidecar["symbolic_raw_contact_factor"] == (
        "2*zeta(3)*alpha_prime^3/(64*kappa^2)"
    )
    assert sidecar["symbolic_absolute_factor"] == (
        "2*zeta(3)*Lambda_R4^8*alpha_prime^3/(64*kappa^2)"
    )
    assert sidecar["symbolic_coefficients"]["g_R4_c1"] == (
        "zeta(3)*Lambda_R4^8*alpha_prime^3/(512*kappa^2)"
    )
    assert sidecar["numeric_values_exported"] is False
    assert sidecar["claim_use_allowed"] is False
    assert all(
        "alpha_prime" in value and "kappa" in value and "Lambda_R4^8" in value
        for value in sidecar["symbolic_coefficients"].values()
        if value != "0"
    )


def test_sidecar_evaluation_blocks_numeric_export_or_lost_symbolic_factor():
    sidecar = deepcopy(symbolic_lambda_r4_sidecar_for_packet())
    sidecar["numeric_values_exported"] = True
    sidecar["symbolic_coefficients"]["g_R4_c1"] = "0.5"

    result = evaluate_symbolic_lambda_r4_sidecar(sidecar)

    assert result["ready_for_internal_symbolic_query"] is False
    assert result["ready_for_numeric_wilson_export"] is False
    assert result["ready_for_framework_claim"] is False
    assert "numeric_values_exported" in result["blockers"]
    assert "symbolic_coefficients_lost_alpha_prime_or_kappa" in result["blockers"]


def test_diagnosis_records_next_query_surface_attachment():
    result = diagnose_r4_lambda_unit_policy()

    assert result["version"] == "v2.154"
    assert result["ready_for_symbolic_engine_lambda_policy"] is True
    assert result["ready_for_internal_symbolic_query"] is True
    assert result["ready_for_numeric_engine_lambda_r4"] is False
    assert result["ready_for_framework_claim"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["route_status"] == (
        "symbolic_lambda_r4_alpha_prime_policy_ready_nonclaiming"
    )
    assert result["selected_next_build_action"] == (
        "attach_symbolic_lambda_policy_to_r4_query_surface"
    )
