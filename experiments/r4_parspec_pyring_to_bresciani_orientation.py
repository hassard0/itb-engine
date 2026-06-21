"""Audit pyRing quartic directions against Bresciani R4 operator axes."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_r4_axis_dictionary import (
    BRESCIANI_SOURCE_URL,
    DICTIONARY_ID,
    PROJECTION_AXES,
    bresciani_r4_axis_dictionary,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_pyring_runtime_to_parspec_normalization_policy import (
    POLICY_ID as NORMALIZATION_POLICY_ID,
    evaluate_pyring_runtime_to_parspec_normalization_policy,
    pyring_runtime_to_parspec_normalization_policy,
)
from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH,
    PYRING_BRANCH_HEAD_SHA,
    PYRING_INITIALISE_SOURCE_URL,
    PYRING_QUARTIC_THEORIES,
    PYRING_SOURCE_DIRECTIONS,
    PYRING_TREE_URL,
    PYRING_WAVEFORM_SOURCE_URL,
    ROTATING_QNM_SOURCE_URL,
    pyring_quartic_table_manifest,
)
from experiments.r4_parspec_qnm_to_bresciani_gate import matrix_rank


VERSION = "v2.205"
DEFAULT_OUT = Path(
    "experiments/results/v2.205/r4_parspec_pyring_to_bresciani_orientation.json"
)

REQUIRED_BRESCIANI_COORDINATES = (
    "K_plus",
    "Re(K_minus)",
    "Im(K_minus)",
)
REQUIRED_ORIENTATION_EVIDENCE = (
    "quartic_label_to_bresciani_coordinate_identity",
    "plus_minus_branch_to_operator_axis_semantics",
    "field_redefinition_policy",
    "normalization_policy",
    "finite_orientation_matrix",
    "source_line_refs",
)
DISALLOWED_ORIENTATION_USES = (
    "synthetic_branch_to_operator_map",
    "rank_only_orientation_claim",
    "pyring_plus_minus_as_independent_wilson_axes",
    "framework_exclusion_claim",
    "measurement_likelihood_claim",
)
PUBLIC_PRIMARY_SOURCE_FINDINGS = (
    {
        "source": "pyRing initialise.py",
        "url": PYRING_INITIALISE_SOURCE_URL,
        "location": "initialise.py:1003-1005",
        "finding": (
            "pyRing exposes EFT options cubic_even, cubic_odd, quartic_1, "
            "quartic_2, and quartic_3; it does not identify these labels with "
            "Bresciani K coordinates."
        ),
    },
    {
        "source": "pyRing waveform.pyx",
        "url": PYRING_WAVEFORM_SOURCE_URL,
        "location": "waveform.pyx:71-82",
        "finding": (
            "pyRing loads plus/minus QNM coefficient files for quartic_1/2/3 "
            "and cites the rotating higher-derivative QNM source; this is "
            "table provenance, not a Bresciani operator-axis map."
        ),
    },
    {
        "source": "pyRing waveform.pyx",
        "url": PYRING_WAVEFORM_SOURCE_URL,
        "location": "waveform.pyx:1166-1168,1274-1286",
        "finding": (
            "pyRing treats plus/minus as EFT QNM branches or eigenmodes, not "
            "as independent Wilson or Bresciani coupling directions."
        ),
    },
    {
        "source": "Cano-Fransen-Hertog-Maenaut rotating higher-derivative QNMs",
        "url": ROTATING_QNM_SOURCE_URL,
        "location": "Effective field theory of gravity, eqs. (1)-(2)",
        "finding": (
            "The QNM source defines quartic EFT couplings in its own epsilon_i "
            "or alpha_i basis; no Bresciani K_plus/Re(K_minus)/Im(K_minus) "
            "orientation is stated."
        ),
    },
    {
        "source": "Cano-Fransen-Hertog-Maenaut rotating higher-derivative QNMs",
        "url": ROTATING_QNM_SOURCE_URL,
        "location": "Quasinormal modes, around eqs. (8)-(10)",
        "finding": (
            "For parity-preserving terms plus/minus distinguish polar and "
            "axial branches; for parity-breaking terms they are mixed "
            "polarization branches with opposite shifts. They are not declared "
            "as Bresciani K coordinates."
        ),
    },
    {
        "source": "Bresciani-Levati-Paradisi amplitudes and unitarity bounds",
        "url": BRESCIANI_SOURCE_URL,
        "location": "EFT of gravity and light-by-light scattering, eqs. (13)-(16)",
        "finding": (
            "The Bresciani source defines its own c_plus/c_minus or K basis "
            "for spin-2 R4 amplitudes. It does not tie those coordinates to "
            "pyRing quartic filenames or QNM plus/minus branches."
        ),
    },
)


def _shared_label_tokens(left: tuple[str, ...], right: tuple[str, ...]) -> list[str]:
    left_tokens = {
        token
        for item in left
        for token in item.replace("(", "_").replace(")", "_").split("_")
        if token
    }
    right_tokens = {
        token
        for item in right
        for token in item.replace("(", "_").replace(")", "_").split("_")
        if token
    }
    return sorted(left_tokens & right_tokens)


def _candidate_matrix_rank(candidate: dict[str, Any] | None) -> int:
    if not isinstance(candidate, dict):
        return 0
    matrix = candidate.get("orientation_matrix")
    if not isinstance(matrix, list):
        return 0
    try:
        return matrix_rank(matrix)
    except (TypeError, ValueError):
        return 0


def pyring_to_bresciani_orientation_audit_packet(
    candidate_orientation_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    axis_dictionary = bresciani_r4_axis_dictionary()
    normalization_policy = pyring_runtime_to_parspec_normalization_policy()
    normalization_evaluation = (
        evaluate_pyring_runtime_to_parspec_normalization_policy(
            normalization_policy
        )
    )
    table_manifest = pyring_quartic_table_manifest()

    bresciani_coordinates = tuple(
        axis_dictionary["source_to_engine_relations"]["source_coordinates"][1:]
    )
    candidate = candidate_orientation_map or {
        "status": "absent",
        "reason": (
            "No source-backed map from pyRing quartic_1/2/3 plus/minus "
            "branch-splitting directions to Bresciani K coordinates is "
            "present in the current source set."
        ),
    }

    return canonicalize_json_floats({
        "packet_id": "pyring_to_bresciani_orientation_audit_v1",
        "version": VERSION,
        "source_manifest": {
            "pyring": {
                "branch": PYRING_BRANCH,
                "branch_head_sha": PYRING_BRANCH_HEAD_SHA,
                "tree_url": PYRING_TREE_URL,
                "waveform_source_url": PYRING_WAVEFORM_SOURCE_URL,
                "initialise_source_url": PYRING_INITIALISE_SOURCE_URL,
                "rotating_qnm_source_url": ROTATING_QNM_SOURCE_URL,
                "quartic_tables": table_manifest["tables"],
                "quartic_theories": list(PYRING_QUARTIC_THEORIES),
                "source_directions": list(PYRING_SOURCE_DIRECTIONS),
                "source_line_refs": {
                    "table_ingest": "waveform.pyx:72-80",
                    "runtime_quartic_options": "initialise.py:1000-1007",
                    "runtime_frequency_formula": "waveform.pyx:526-532",
                    "runtime_tau_formula": "waveform.pyx:534-540",
                },
            },
            "bresciani": {
                "source_url": BRESCIANI_SOURCE_URL,
                "dictionary_id": DICTIONARY_ID,
                "source_coordinates": list(REQUIRED_BRESCIANI_COORDINATES),
                "engine_projection_axes": list(PROJECTION_AXES),
                "engine_axis_equations": axis_dictionary[
                    "source_to_engine_relations"
                ]["engine_axis_equations"],
                "projection_matrix": axis_dictionary[
                    "operator_projection_matrix"
                ]["matrix_for_overall_R4_factor_8"],
            },
            "normalization_policy": {
                "policy_id": NORMALIZATION_POLICY_ID,
                "ready_for_internal_pyring_runtime_rerun": (
                    normalization_evaluation[
                        "ready_for_internal_pyring_runtime_rerun"
                    ]
                ),
                "parspec_high_spin_may_replace_pyring_runtime_normalizer": (
                    normalization_evaluation[
                        "parspec_high_spin_may_replace_pyring_runtime_normalizer"
                    ]
                ),
            },
        },
        "public_primary_source_findings": list(PUBLIC_PRIMARY_SOURCE_FINDINGS),
        "required_orientation_evidence": list(REQUIRED_ORIENTATION_EVIDENCE),
        "current_evidence": {
            "pyring_has_hash_pinned_qnm_branch_tables": True,
            "pyring_has_bresciani_K_coordinate_labels": False,
            "pyring_has_field_redefinition_policy_to_bresciani_basis": False,
            "pyring_plus_minus_are_independent_operator_axes": False,
            "bresciani_dictionary_maps_K_to_engine_axes": True,
            "normalization_policy_isolated": normalization_evaluation[
                "pyring_runtime_to_parspec_high_spin_policy_ready"
            ],
            "public_likelihood_attached": False,
        },
        "label_intersection": {
            "pyring_direction_labels": list(PYRING_SOURCE_DIRECTIONS),
            "bresciani_coordinate_labels": list(bresciani_coordinates),
            "shared_tokens": _shared_label_tokens(
                PYRING_SOURCE_DIRECTIONS,
                bresciani_coordinates,
            ),
            "shared_tokens_are_orientation_evidence": False,
        },
        "candidate_orientation_map": candidate,
        "candidate_orientation_rank": _candidate_matrix_rank(candidate),
        "no_map_ledger": {
            "status": "source_audit_complete_map_absent",
            "synthetic_orientation_allowed": False,
            "rank_only_orientation_allowed": False,
            "reason": (
                "The pyRing tables give local QNM branch-splitting directions. "
                "The Bresciani dictionary requires coordinates in "
                "K_plus/Re(K_minus)/Im(K_minus). No source currently supplies "
                "the operator identity, field-redefinition policy, or finite "
                "orientation matrix connecting these coordinate systems."
            ),
        },
        "disallowed_uses": list(DISALLOWED_ORIENTATION_USES),
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "orientation_map_source_backed": False,
            "qnm_to_bresciani_sensitivity_ready": False,
            "public_likelihood_ready": False,
        },
    })


def evaluate_pyring_to_bresciani_orientation_audit(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or pyring_to_bresciani_orientation_audit_packet()
    blockers: set[str] = set()
    warnings: set[str] = set()

    if packet.get("packet_id") != "pyring_to_bresciani_orientation_audit_v1":
        blockers.add("orientation_packet_id_mismatch")
    if tuple(packet.get("required_orientation_evidence", ())) != (
        REQUIRED_ORIENTATION_EVIDENCE
    ):
        blockers.add("required_orientation_evidence_changed")

    evidence = packet.get("current_evidence", {})
    if evidence.get("pyring_has_hash_pinned_qnm_branch_tables") is not True:
        blockers.add("pyring_qnm_branch_tables_not_hash_pinned")
    if evidence.get("bresciani_dictionary_maps_K_to_engine_axes") is not True:
        blockers.add("bresciani_axis_dictionary_missing")
    if evidence.get("normalization_policy_isolated") is not True:
        blockers.add("normalization_policy_not_ready")

    no_map = packet.get("no_map_ledger", {})
    if no_map.get("status") != "source_audit_complete_map_absent":
        blockers.add("no_map_ledger_status_mismatch")
    if no_map.get("synthetic_orientation_allowed") is not False:
        blockers.add("synthetic_orientation_not_forbidden")
    if no_map.get("rank_only_orientation_allowed") is not False:
        blockers.add("rank_only_orientation_not_forbidden")

    candidate = packet.get("candidate_orientation_map", {})
    candidate_status = candidate.get("status") if isinstance(candidate, dict) else None
    if candidate_status == "source_backed":
        blockers.add("unexpected_source_backed_orientation_claim")
        if candidate.get("field_redefinition_policy") != "closed_for_packet":
            blockers.add("source_backed_orientation_field_policy_missing")
        if candidate.get("source_line_refs") in (None, {}, []):
            blockers.add("source_backed_orientation_line_refs_missing")
        if tuple(candidate.get("columns", ())) != PYRING_SOURCE_DIRECTIONS:
            blockers.add("source_backed_orientation_column_set_mismatch")
        if tuple(candidate.get("rows", ())) != REQUIRED_BRESCIANI_COORDINATES:
            blockers.add("source_backed_orientation_row_set_mismatch")
        if packet.get("candidate_orientation_rank", 0) < len(
            REQUIRED_BRESCIANI_COORDINATES
        ):
            blockers.add("source_backed_orientation_rank_deficient")
    elif candidate_status not in {"absent", "unit_test_control", None}:
        warnings.add("unknown_candidate_orientation_status")

    label_intersection = packet.get("label_intersection", {})
    if label_intersection.get("shared_tokens_are_orientation_evidence") is not False:
        blockers.add("label_tokens_promoted_to_orientation_evidence")

    disallowed = set(packet.get("disallowed_uses", []))
    if not set(DISALLOWED_ORIENTATION_USES).issubset(disallowed):
        blockers.add("disallowed_orientation_uses_incomplete")

    controls = packet.get("claim_controls", {})
    if controls.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")
    if controls.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")
    if controls.get("orientation_map_source_backed") is not False:
        blockers.add("orientation_claim_not_disabled")
    if controls.get("qnm_to_bresciani_sensitivity_ready") is not False:
        blockers.add("qnm_to_bresciani_sensitivity_claim_not_disabled")

    no_map_ready = not blockers
    remaining_claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "pyring_plus_minus_branches_not_independent_operator_axes",
        "pyring_quartic_direction_to_bresciani_axis_orientation_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if not no_map_ready:
        remaining_claim_blockers.add("pyring_to_bresciani_no_map_ledger_not_ready")

    return canonicalize_json_floats({
        "pyring_to_bresciani_orientation_audit_ready": no_map_ready,
        "pyring_to_bresciani_orientation_source_backed": False,
        "no_map_ledger_ready": no_map_ready,
        "synthetic_orientation_allowed": False,
        "rank_only_orientation_allowed": False,
        "qnm_to_bresciani_sensitivity_ready": False,
        "public_likelihood_ready": False,
        "ready_for_framework_claim": False,
        "resolved_v2204_subpieces": (
            [
                "pyring_to_bresciani_orientation_audit_complete",
                "synthetic_orientation_map_forbidden",
            ]
            if no_map_ready
            else []
        ),
        "blockers": sorted(blockers),
        "warnings": sorted(warnings),
        "remaining_claim_blockers": sorted(remaining_claim_blockers),
        "route_status": (
            "pyring_to_bresciani_no_map_ledger_ready_claim_gate_blocked"
            if no_map_ready
            else "pyring_to_bresciani_orientation_audit_not_ready"
        ),
    })


def malformed_synthetic_orientation_claim() -> dict[str, Any]:
    packet = copy.deepcopy(pyring_to_bresciani_orientation_audit_packet())
    packet["candidate_orientation_map"] = {
        "status": "source_backed",
        "rows": list(REQUIRED_BRESCIANI_COORDINATES),
        "columns": list(PYRING_SOURCE_DIRECTIONS),
        "orientation_matrix": [
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
        ],
        "field_redefinition_policy": "not_supplied",
        "source_line_refs": {},
    }
    packet["candidate_orientation_rank"] = 3
    packet["no_map_ledger"]["synthetic_orientation_allowed"] = True
    packet["claim_controls"]["claim_use_allowed"] = True
    packet["claim_controls"]["orientation_map_source_backed"] = True
    return packet


def diagnose_r4_parspec_pyring_to_bresciani_orientation() -> dict[str, Any]:
    packet = pyring_to_bresciani_orientation_audit_packet()
    evaluation = evaluate_pyring_to_bresciani_orientation_audit(packet)
    malformed_evaluation = evaluate_pyring_to_bresciani_orientation_audit(
        malformed_synthetic_orientation_claim()
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.200_qnm_to_bresciani_gate",
            "v2.201_pyring_source_probe",
            "v2.204_pyring_runtime_to_parspec_normalization_policy",
            "public_pyring_EFT_QNMs_branch",
        ],
        "orientation_audit": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed_evaluation,
        "pyring_to_bresciani_orientation_audit_ready": evaluation[
            "pyring_to_bresciani_orientation_audit_ready"
        ],
        "pyring_to_bresciani_orientation_source_backed": False,
        "qnm_to_bresciani_sensitivity_ready": False,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_qnm_to_bresciani_sensitivity_source_or_public_parspec_qeft_likelihood"
        ),
        "route_status": evaluation["route_status"],
        "interpretation": (
            "v2.205 completes the source audit for pyRing-to-Bresciani "
            "orientation and records a no-map ledger. pyRing quartic tables "
            "are source-backed QNM branch-splitting directions, while the "
            "Bresciani dictionary requires K_plus/Re(K_minus)/Im(K_minus) "
            "operator coordinates. No current source supplies the orientation "
            "identity or field-redefinition policy connecting them, so a "
            "synthetic branch-to-operator map is explicitly forbidden."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_pyring_to_bresciani_orientation()
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
