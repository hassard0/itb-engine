"""Tests for the v2.203 pyRing event-spin QNM Jacobian."""

from __future__ import annotations

import json
import math

from experiments.r4_parspec_pyring_event_spin_jacobian import (
    DEFAULT_OUT,
    EVENT_LABELS,
    EVENT_SPIN_ROWS,
    MODE_LABELS,
    diagnose_r4_parspec_pyring_event_spin_jacobian,
    evaluate_event_spin_jacobian,
    event_spin_jacobian_packet,
    exact_fractional_tau_shift,
    finite_difference_tau_derivative,
    fractional_frequency_derivative,
    fractional_tau_derivative,
    malformed_event_spin_snapshot,
)
from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH_HEAD_SHA,
    PYRING_SOURCE_DIRECTIONS,
)


def test_event_spin_sources_are_pinned() -> None:
    result = diagnose_r4_parspec_pyring_event_spin_jacobian()
    manifest = result["source_manifest"]

    assert manifest["branch_head_sha"] == PYRING_BRANCH_HEAD_SHA
    assert len(manifest["pyring_quartic_tables"]) == 6
    assert manifest["gw150914_spin_source"]["sample_count"] == 17070
    assert len(manifest["gw150914_spin_source"]["sample_sha256"]) == 64
    assert math.isclose(
        manifest["gw150914_spin_source"]["spin"],
        EVENT_SPIN_ROWS["GW150914"]["spin"],
        abs_tol=1e-12,
    )
    assert manifest["gw200129_spin_source"]["spin"] == 0.73
    assert manifest["source_line_refs"]["pyring_runtime_tau_formula"] == (
        "waveform.pyx:534-540"
    )


def test_fractional_derivative_formulae_match_known_event_spin_values() -> None:
    assert math.isclose(
        fractional_frequency_derivative(
            -0.7057280532347682,
            0.5214875364939959,
        ),
        -1.3532980250677449,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert math.isclose(
        fractional_tau_derivative(
            1.0182630943192719,
            12.102356553155843,
        ),
        -12.323383032371586,
        rel_tol=0.0,
        abs_tol=1e-12,
    )
    assert exact_fractional_tau_shift(
        gamma=1e-5,
        tau_gr_dimensionless=12.102356553155843,
        domi_fit=1.0182630943192719,
    ) < 0.0
    assert math.isclose(
        finite_difference_tau_derivative(
            tau_gr_dimensionless=12.102356553155843,
            domi_fit=1.0182630943192719,
        ),
        -12.323383032371586,
        rel_tol=0.0,
        abs_tol=1e-8,
    )


def test_event_spin_jacobian_shapes_ranks_and_known_values() -> None:
    packet = event_spin_jacobian_packet()

    assert packet["events"] == list(EVENT_LABELS)
    assert packet["modes"] == list(MODE_LABELS)
    assert packet["columns"] == list(PYRING_SOURCE_DIRECTIONS)
    assert packet["columns_are_branch_splitting_directions"] is True
    assert packet["columns_are_independent_operator_axes"] is False

    rows_by_event = {row["event"]: row for row in packet["event_rows"]}
    assert set(rows_by_event) == set(EVENT_LABELS)
    for row in rows_by_event.values():
        assert len(row["matrix"]) == 8
        assert all(len(values) == 6 for values in row["matrix"])
        assert row["rank"] == 4

    gw150914 = rows_by_event["GW150914"]["matrix"]
    assert math.isclose(gw150914[0][0], -1.353298025068, abs_tol=1e-12)
    assert math.isclose(gw150914[1][0], -12.323383032372, abs_tol=1e-12)

    gw200129 = rows_by_event["GW200129"]["matrix"]
    assert math.isclose(gw200129[4][0], -9.968567732006, abs_tol=1e-12)
    assert math.isclose(gw200129[5][0], -11.983566312312, abs_tol=1e-12)


def test_normalization_comparison_records_policy_gap() -> None:
    packet = event_spin_jacobian_packet()

    assert packet["max_abs_frequency_normalization_delta"] > 0.01
    assert packet["max_abs_tau_normalization_delta"] > 0.03
    assert any(
        row["mode"] == "221"
        and row["event"] == "GW150914"
        and row["tau_parspec_vs_pyring_runtime_fractional_delta"] > 0.03
        for row in packet["normalization_comparison"]
    )


def test_evaluation_resolves_event_spin_subpiece_but_keeps_claim_gate_closed() -> None:
    evaluation = evaluate_event_spin_jacobian()

    assert evaluation["pyring_event_spin_jacobian_ready"] is True
    assert evaluation["pyring_runtime_fractional_axes_ready"] is True
    assert evaluation["parspec_high_spin_comparison_ready"] is True
    assert evaluation["parspec_axis_normalization_policy_ready"] is False
    assert evaluation["qnm_to_bresciani_sensitivity_ready"] is False
    assert evaluation["public_likelihood_ready"] is False
    assert evaluation["ready_for_framework_claim"] is False
    assert evaluation["source_intake_blockers"] == []
    assert "pyring_event_spin_runtime_frequency_tau_jacobian_defined" in evaluation[
        "resolved_v2202_subpieces"
    ]
    assert "pyring_runtime_to_parspec_high_spin_normalization_policy_missing" in (
        evaluation["remaining_claim_blockers"]
    )
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in evaluation[
        "remaining_claim_blockers"
    ]


def test_malformed_event_spin_snapshot_fails_rank_gate() -> None:
    evaluation = evaluate_event_spin_jacobian(malformed_event_spin_snapshot())

    assert evaluation["pyring_event_spin_jacobian_ready"] is False
    assert "GW150914_event_spin_matrix_rank_deficient" in evaluation[
        "source_intake_blockers"
    ]
    assert "pyring_event_spin_jacobian_not_ready" in evaluation[
        "remaining_claim_blockers"
    ]


def test_diagnosis_preserves_axis_boundaries_and_nonclaiming_status() -> None:
    result = diagnose_r4_parspec_pyring_event_spin_jacobian()

    assert result["version"] == "v2.203"
    assert tuple(result["engine_target_axes"]) == (
        "g_R4_c1",
        "g_R4_c2",
        "g_R4_c3",
    )
    assert tuple(result["parspec_qnm_axes"]) == (
        "delta_omega_qeft_0",
        "delta_tau_qeft_0",
        "delta_omega_qeft_1",
        "delta_tau_qeft_1",
    )
    assert result["pyring_event_spin_jacobian_ready"] is True
    assert result["qnm_to_bresciani_sensitivity_ready"] is False
    assert result["claimable_framework_exclusions_now"] == []
    assert result["ready_for_framework_claim"] is False


def test_committed_artifact_matches_event_spin_contract_if_present() -> None:
    if not DEFAULT_OUT.exists():
        return

    artifact = json.loads(DEFAULT_OUT.read_text(encoding="utf-8"))
    assert artifact["version"] == "v2.203"
    assert artifact["route_status"] == (
        "pyring_event_spin_jacobian_ready_normalization_policy_missing"
    )
    assert artifact["pyring_event_spin_jacobian_ready"] is True
    assert artifact["ready_for_framework_claim"] is False
    assert artifact["event_spin_jacobian"]["event_rows"][0]["rank"] == 4
