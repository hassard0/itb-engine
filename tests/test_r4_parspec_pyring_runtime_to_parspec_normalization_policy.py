"""Tests for the v2.204 pyRing runtime-to-ParSpec normalization policy."""

from __future__ import annotations

import json
import math

from experiments.r4_parspec_pyring_runtime_to_parspec_normalization_policy import (
    ALLOWED_POLICY_USES,
    DEFAULT_OUT,
    DISALLOWED_POLICY_USES,
    diagnose_r4_parspec_pyring_runtime_to_parspec_normalization_policy,
    evaluate_pyring_runtime_to_parspec_normalization_policy,
    malformed_mixed_normalization_policy,
    pyring_runtime_to_parspec_normalization_policy,
)


def test_policy_selects_pyring_runtime_normalizer_only() -> None:
    policy = pyring_runtime_to_parspec_normalization_policy()

    assert policy["status"] == (
        "runtime_normalizer_selected_comparison_isolated_nonclaiming"
    )
    selected = policy["selected_runtime_normalizer"]
    assert selected["frequency"] == "pyRing_QNM_EFT_runtime_Berti_frequency"
    assert selected["tau"] == "pyRing_QNM_EFT_runtime_Berti_tau"
    assert selected["source_backed_for_internal_pyring_rerun"] is True
    assert policy["parspec_high_spin_role"]["role"] == "comparison_only"
    assert (
        policy["parspec_high_spin_role"][
            "source_backed_as_drop_in_pyring_runtime_normalizer"
        ]
        is False
    )
    assert policy["framework_claim_allowed"] is False
    assert policy["measurement_claim_allowed"] is False


def test_policy_preserves_measured_normalization_gap_from_v2203() -> None:
    policy = pyring_runtime_to_parspec_normalization_policy()
    gap = policy["normalization_gap"]

    assert math.isclose(
        gap["max_abs_frequency_fractional_delta"],
        0.010254493215,
        abs_tol=1e-12,
    )
    assert math.isclose(
        gap["max_abs_tau_fractional_delta"],
        0.035798536953,
        abs_tol=1e-12,
    )
    assert gap["gap_is_zero"] is False
    assert gap["gap_is_claim_blocking_if_mixed"] is True


def test_runtime_contract_contains_no_parspec_high_spin_rows() -> None:
    policy = pyring_runtime_to_parspec_normalization_policy()
    contract = policy["runtime_jacobian_contract"]

    assert contract["packet_id"] == "pyring_runtime_normalized_event_spin_rows_v1"
    assert contract["columns_are_independent_operator_axes"] is False
    for event_row in contract["event_rows"]:
        assert len(event_row["matrix"]) == 4
        assert event_row["rank"] == 4
        for row in event_row["row_metadata"]:
            assert "runtime_Berti" in row["normalization"]
            assert "parspec_high_spin" not in row["row"]


def test_evaluation_resolves_normalization_policy_only() -> None:
    evaluation = evaluate_pyring_runtime_to_parspec_normalization_policy()

    assert evaluation["ready_for_internal_pyring_runtime_rerun"] is True
    assert evaluation["pyring_runtime_to_parspec_high_spin_policy_ready"] is True
    assert (
        evaluation["parspec_high_spin_may_replace_pyring_runtime_normalizer"]
        is False
    )
    assert evaluation["ready_for_bresciani_operator_axis_claim"] is False
    assert evaluation["ready_for_public_likelihood_claim"] is False
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["blockers"] == []
    assert "pyring_runtime_to_parspec_high_spin_normalization_policy_missing" not in (
        evaluation["remaining_claim_blockers"]
    )
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in (
        evaluation["remaining_claim_blockers"]
    )
    assert "pyring_plus_minus_branches_not_independent_operator_axes" in (
        evaluation["remaining_claim_blockers"]
    )


def test_allowed_and_disallowed_uses_are_complete() -> None:
    policy = pyring_runtime_to_parspec_normalization_policy()

    assert set(ALLOWED_POLICY_USES).issubset(policy["allowed_uses"])
    assert set(DISALLOWED_POLICY_USES).issubset(policy["disallowed_uses"])
    assert "internal_pyring_runtime_rerun" in policy["allowed_uses"]
    assert "nonclaiming_parspec_high_spin_comparison" in policy["allowed_uses"]
    assert "mixed_runtime_parspec_claim_axis" in policy["disallowed_uses"]
    assert "framework_exclusion_claim" in policy["disallowed_uses"]


def test_malformed_mixed_normalizer_policy_fails_claim_gates() -> None:
    evaluation = evaluate_pyring_runtime_to_parspec_normalization_policy(
        malformed_mixed_normalization_policy()
    )

    assert evaluation["ready_for_internal_pyring_runtime_rerun"] is False
    assert "parspec_high_spin_role_not_comparison_only" in evaluation["blockers"]
    assert "parspec_high_spin_marked_as_runtime_drop_in" in evaluation["blockers"]
    assert "framework_claim_not_disabled" in evaluation["blockers"]
    assert any(
        blocker.endswith("_nonruntime_row_in_contract")
        for blocker in evaluation["blockers"]
    )
    assert "pyring_runtime_normalization_policy_not_ready" in (
        evaluation["remaining_claim_blockers"]
    )


def test_diagnosis_records_nonclaiming_route_status() -> None:
    result = diagnose_r4_parspec_pyring_runtime_to_parspec_normalization_policy()

    assert result["version"] == "v2.204"
    assert result["ready_for_internal_pyring_runtime_rerun"] is True
    assert result["pyring_runtime_to_parspec_high_spin_policy_ready"] is True
    assert result["qnm_to_bresciani_sensitivity_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False
    assert result["route_status"] == (
        "pyring_runtime_normalization_policy_ready_claim_gate_still_blocked"
    )


def test_committed_artifact_matches_policy_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.204"
    assert artifact["route_status"] == (
        "pyring_runtime_normalization_policy_ready_claim_gate_still_blocked"
    )
    assert artifact["ready_for_internal_pyring_runtime_rerun"] is True
    assert artifact["ready_for_framework_claim"] is False
    assert artifact["policy"]["parspec_high_spin_role"]["role"] == "comparison_only"
