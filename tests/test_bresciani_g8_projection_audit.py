"""Tests for the v2.130 Bresciani-to-G8 projection audit."""

import pytest

from experiments.bresciani_g8_projection_audit import (
    bresciani_v2_gravity_basis,
    diagnose_bresciani_g8_projection_audit,
    engine_g8_contract,
    projection_attempts,
)


def test_engine_contract_keeps_g8_in_matter_forward_sector():
    contract = engine_g8_contract()

    assert contract["axis"] == "g_8"
    assert contract["sector"] == "matter_forward_limit"
    assert contract["amplitude_power"] == "s^4"
    assert "g_6^2 <= g_4 * g_8" in contract["formal_definition"]


def test_bresciani_basis_is_spin2_four_graviton_r4_not_engine_g8():
    basis = bresciani_v2_gravity_basis()

    assert basis["spin_S"] == 2
    assert basis["sector"] == "four_graviton_eight_derivative_gravity"
    assert basis["source_unitarity_bound"]["spin2_ratio"] == pytest.approx(1.4)
    assert "c_1^(S) * (Q^(S))^2" in basis["operator_basis"]
    assert basis["gravity_identification"]["coefficient_dimension"] == (
        "-8 for S=2"
    )


def test_projection_audit_rejects_engine_g8_jacobian():
    result = diagnose_bresciani_g8_projection_audit()

    assert result["version"] == "v2.130"
    assert result["can_define_engine_g8_jacobian"] is False
    assert result["jacobian_to_engine_g8"] is None
    assert "sector_mismatch_four_graviton_vs_matter_forward" in (
        result["blockers"]
    )
    assert "source_backed_operator_identity_missing" in result["blockers"]
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == (
        "bresciani_v2_projection_audit_no_engine_g8_jacobian"
    )


def test_same_s4_power_attempt_is_not_enough_for_projection():
    attempts = {row["label"]: row for row in projection_attempts()}
    naive = attempts["naive_same_s4_derivative_order_map"]

    assert naive["passes_derivative_order_check"] is True
    assert naive["can_define_engine_g8_jacobian"] is False
    assert "sector_mismatch_four_graviton_vs_matter_forward" in naive["blockers"]
    assert "dimensionful_gravity_coefficients_not_engine_normalized" in (
        naive["blockers"]
    )


def test_next_action_preserves_source_as_gravity_axis_candidate():
    result = diagnose_bresciani_g8_projection_audit()

    assert result["selected_next_build_action"] == (
        "register_bresciani_v2_as_gravity_r4_axis_extension_candidate"
    )
    assert any(
        row["label"] == "use_bresciani_as_gravity_r4_axis_extension"
        for row in result["projection_attempts"]
    )
