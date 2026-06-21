"""Policy boundary for pyRing runtime and ParSpec high-spin normalizers."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_pyring_event_spin_jacobian import (
    EVENT_LABELS,
    MODE_LABELS,
    diagnose_r4_parspec_pyring_event_spin_jacobian,
    event_spin_jacobian_packet,
)
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES
from experiments.r4_parspec_qnm_to_bresciani_gate import matrix_rank


VERSION = "v2.204"
DEFAULT_OUT = Path(
    "experiments/results/v2.204/"
    "r4_parspec_pyring_runtime_to_parspec_normalization_policy.json"
)

POLICY_ID = "pyring_runtime_to_parspec_high_spin_normalization_policy_v1"
ALLOWED_POLICY_USES = (
    "internal_pyring_runtime_rerun",
    "source_event_spin_jacobian_normalization",
    "normalization_delta_audit",
    "nonclaiming_parspec_high_spin_comparison",
)
DISALLOWED_POLICY_USES = (
    "mixed_runtime_parspec_claim_axis",
    "bresciani_operator_axis_claim",
    "framework_exclusion_claim",
    "measurement_likelihood_claim",
    "wilson_coefficient_magnitude_claim",
)


def _runtime_rows_from_event_spin_packet(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or event_spin_jacobian_packet()
    event_rows = []
    for event_row in packet["event_rows"]:
        runtime_rows = [
            row
            for row in event_row["row_metadata"]
            if row["normalization"].startswith("pyRing_QNM_EFT_runtime_Berti")
        ]
        matrix = [row["values"] for row in runtime_rows]
        event_rows.append({
            "event": event_row["event"],
            "rows": [row["row"] for row in runtime_rows],
            "columns": event_row["columns"],
            "matrix": matrix,
            "row_metadata": runtime_rows,
            "rank": matrix_rank(matrix),
        })
    return canonicalize_json_floats({
        "packet_id": "pyring_runtime_normalized_event_spin_rows_v1",
        "source_packet": packet["packet_id"],
        "events": list(EVENT_LABELS),
        "modes": list(MODE_LABELS),
        "columns": packet["columns"],
        "columns_are_branch_splitting_directions": True,
        "columns_are_independent_operator_axes": False,
        "normalization": {
            "frequency": "pyRing_QNM_EFT_runtime_Berti_frequency",
            "tau": "pyRing_QNM_EFT_runtime_Berti_tau",
        },
        "event_rows": event_rows,
    })


def pyring_runtime_to_parspec_normalization_policy(
    event_spin_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event_spin_result = (
        event_spin_result or diagnose_r4_parspec_pyring_event_spin_jacobian()
    )
    packet = event_spin_result["event_spin_jacobian"]
    runtime_rows = _runtime_rows_from_event_spin_packet(packet)

    return canonicalize_json_floats({
        "policy_id": POLICY_ID,
        "version": VERSION,
        "status": "runtime_normalizer_selected_comparison_isolated_nonclaiming",
        "basis": [
            "v2.201_pyring_source_probe",
            "v2.202_pyring_tau_axis_jacobian",
            "v2.203_pyring_event_spin_jacobian",
            "public_pyring_EFT_QNMs_branch",
        ],
        "source_manifest": {
            "branch": event_spin_result["source_manifest"]["branch"],
            "branch_head_sha": event_spin_result["source_manifest"][
                "branch_head_sha"
            ],
            "tree_url": event_spin_result["source_manifest"]["tree_url"],
            "waveform_source_url": event_spin_result["source_manifest"][
                "waveform_source_url"
            ],
            "source_line_refs": event_spin_result["source_manifest"][
                "source_line_refs"
            ],
        },
        "selected_runtime_normalizer": {
            "frequency": "pyRing_QNM_EFT_runtime_Berti_frequency",
            "tau": "pyRing_QNM_EFT_runtime_Berti_tau",
            "frequency_formula": packet["source_formulae"][
                "runtime_fractional_frequency"
            ],
            "tau_formula": packet["source_formulae"]["runtime_fractional_tau"],
            "source_backed_for_internal_pyring_rerun": True,
            "reason": (
                "The public pyRing QNM_EFT runtime path applies quartic EFT "
                "df/domi shifts to the Berti GR QNM fit used by pyRing. "
                "Internal pyRing reruns therefore keep that runtime "
                "normalizer."
            ),
        },
        "parspec_high_spin_role": {
            "role": "comparison_only",
            "source_backed_as_drop_in_pyring_runtime_normalizer": False,
            "source_backed_as_bresciani_operator_axis_normalizer": False,
            "allowed_rows": [
                "delta_omega_*_parspec_high_spin_frac",
                "delta_tau_*_parspec_high_spin_frac",
            ],
            "allowed_use": (
                "Expose the size and spin dependence of the normalization "
                "gap; do not feed these rows into claim-grade ParSpec or "
                "Bresciani-axis inference."
            ),
        },
        "normalization_gap": {
            "max_abs_frequency_fractional_delta": packet[
                "max_abs_frequency_normalization_delta"
            ],
            "max_abs_tau_fractional_delta": packet[
                "max_abs_tau_normalization_delta"
            ],
            "comparison_rows": packet["normalization_comparison"],
            "gap_is_zero": False,
            "gap_is_claim_blocking_if_mixed": True,
        },
        "runtime_jacobian_contract": runtime_rows,
        "allowed_uses": list(ALLOWED_POLICY_USES),
        "disallowed_uses": list(DISALLOWED_POLICY_USES),
        "qnm_to_bresciani_orientation_source_backed": False,
        "public_likelihood_source_backed": False,
        "framework_claim_allowed": False,
        "measurement_claim_allowed": False,
    })


def evaluate_pyring_runtime_to_parspec_normalization_policy(
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    policy = policy or pyring_runtime_to_parspec_normalization_policy()
    blockers: set[str] = set()
    warnings: set[str] = set()

    if policy.get("policy_id") != POLICY_ID:
        blockers.add("normalization_policy_id_mismatch")
    if policy.get("status") != (
        "runtime_normalizer_selected_comparison_isolated_nonclaiming"
    ):
        blockers.add("normalization_policy_status_mismatch")

    selected = policy.get("selected_runtime_normalizer", {})
    if selected.get("source_backed_for_internal_pyring_rerun") is not True:
        blockers.add("runtime_normalizer_not_source_backed")
    if selected.get("frequency") != "pyRing_QNM_EFT_runtime_Berti_frequency":
        blockers.add("frequency_runtime_normalizer_changed")
    if selected.get("tau") != "pyRing_QNM_EFT_runtime_Berti_tau":
        blockers.add("tau_runtime_normalizer_changed")

    parspec_role = policy.get("parspec_high_spin_role", {})
    if parspec_role.get("role") != "comparison_only":
        blockers.add("parspec_high_spin_role_not_comparison_only")
    if parspec_role.get("source_backed_as_drop_in_pyring_runtime_normalizer"):
        blockers.add("parspec_high_spin_marked_as_runtime_drop_in")
    if parspec_role.get("source_backed_as_bresciani_operator_axis_normalizer"):
        blockers.add("parspec_high_spin_marked_as_bresciani_axis")

    gap = policy.get("normalization_gap", {})
    if float(gap.get("max_abs_frequency_fractional_delta", 0.0)) <= 0.0:
        blockers.add("frequency_normalization_gap_not_measured")
    if float(gap.get("max_abs_tau_fractional_delta", 0.0)) <= 0.0:
        blockers.add("tau_normalization_gap_not_measured")
    if gap.get("gap_is_claim_blocking_if_mixed") is not True:
        blockers.add("mixed_normalizer_gap_not_claim_blocking")

    runtime_contract = policy.get("runtime_jacobian_contract", {})
    if runtime_contract.get("columns_are_independent_operator_axes") is not False:
        blockers.add("runtime_contract_promotes_operator_axes")
    for event_row in runtime_contract.get("event_rows", []):
        if event_row.get("rank", 0) < 4:
            blockers.add(f"{event_row.get('event', 'unknown')}_runtime_rank_deficient")
        for row in event_row.get("row_metadata", []):
            normalization = row.get("normalization", "")
            if "runtime_Berti" not in normalization:
                blockers.add(f"{row.get('row', 'unknown')}_nonruntime_row_in_contract")

    allowed = set(policy.get("allowed_uses", []))
    disallowed = set(policy.get("disallowed_uses", []))
    if not set(ALLOWED_POLICY_USES).issubset(allowed):
        blockers.add("allowed_uses_incomplete")
    if not set(DISALLOWED_POLICY_USES).issubset(disallowed):
        blockers.add("disallowed_uses_incomplete")

    if policy.get("qnm_to_bresciani_orientation_source_backed") is True:
        warnings.add("policy_would_enable_orientation_claim")
    if policy.get("public_likelihood_source_backed") is True:
        warnings.add("policy_would_enable_likelihood_claim")
    if policy.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")
    if policy.get("measurement_claim_allowed") is not False:
        blockers.add("measurement_claim_not_disabled")

    ready = not blockers
    remaining_claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "pyring_plus_minus_branches_not_independent_operator_axes",
        "pyring_quartic_direction_to_bresciani_axis_orientation_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if not ready:
        remaining_claim_blockers.add("pyring_runtime_normalization_policy_not_ready")

    return canonicalize_json_floats({
        "policy_id": policy.get("policy_id"),
        "ready_for_internal_pyring_runtime_rerun": ready,
        "pyring_runtime_to_parspec_high_spin_policy_ready": ready,
        "parspec_high_spin_may_replace_pyring_runtime_normalizer": False,
        "ready_for_bresciani_operator_axis_claim": False,
        "ready_for_public_likelihood_claim": False,
        "ready_for_framework_claim": False,
        "resolved_v2203_subpieces": (
            [
                "pyring_runtime_to_parspec_high_spin_normalization_policy_formally_isolated"
            ]
            if ready
            else []
        ),
        "blockers": sorted(blockers),
        "warnings": sorted(warnings),
        "allowed_uses": sorted(allowed),
        "disallowed_uses": sorted(disallowed),
        "remaining_claim_blockers": sorted(remaining_claim_blockers),
        "route_status": (
            "pyring_runtime_normalization_policy_ready_claim_gate_still_blocked"
            if ready
            else "pyring_runtime_normalization_policy_not_ready"
        ),
    })


def malformed_mixed_normalization_policy() -> dict[str, Any]:
    policy = copy.deepcopy(pyring_runtime_to_parspec_normalization_policy())
    policy["parspec_high_spin_role"]["role"] = "drop_in_runtime_normalizer"
    policy["parspec_high_spin_role"][
        "source_backed_as_drop_in_pyring_runtime_normalizer"
    ] = True
    policy["framework_claim_allowed"] = True
    for event_row in policy["runtime_jacobian_contract"]["event_rows"]:
        event_row["row_metadata"].append({
            "row": f"{event_row['event']}_delta_omega_220_parspec_high_spin_frac",
            "mode": "220",
            "normalization": "ParSpec_high_spin_frequency_polynomial",
            "values": [0.0 for _ in event_row["columns"]],
        })
    return policy


def diagnose_r4_parspec_pyring_runtime_to_parspec_normalization_policy() -> dict[str, Any]:
    policy = pyring_runtime_to_parspec_normalization_policy()
    evaluation = evaluate_pyring_runtime_to_parspec_normalization_policy(policy)
    malformed_evaluation = evaluate_pyring_runtime_to_parspec_normalization_policy(
        malformed_mixed_normalization_policy()
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": policy["basis"],
        "engine_target_axes": list(ENGINE_AXES),
        "policy": policy,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed_evaluation,
        "ready_for_internal_pyring_runtime_rerun": evaluation[
            "ready_for_internal_pyring_runtime_rerun"
        ],
        "pyring_runtime_to_parspec_high_spin_policy_ready": evaluation[
            "pyring_runtime_to_parspec_high_spin_policy_ready"
        ],
        "qnm_to_bresciani_sensitivity_ready": False,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_pyring_quartic_direction_to_bresciani_axis_orientation_or_"
            "public_parspec_qeft_likelihood_packet"
        ),
        "route_status": evaluation["route_status"],
        "interpretation": (
            "v2.204 formally isolates the v2.203 normalization gap. pyRing "
            "runtime Berti-GR normalization is now the allowed normalizer for "
            "internal pyRing reruns, while ParSpec high-spin polynomial rows "
            "remain comparison-only. This removes the normalization-policy "
            "blocker without promoting pyRing branch columns to Bresciani "
            "operator axes or creating a public likelihood."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_pyring_runtime_to_parspec_normalization_policy()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
