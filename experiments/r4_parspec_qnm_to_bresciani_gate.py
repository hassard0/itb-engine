"""Acceptance gate for a ParSpec qNM-to-Bresciani R4 operator map."""

from __future__ import annotations

import argparse
import json
import math
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
from experiments.r4_parspec_absolute_gamma_metadata import (
    DEFAULT_OUT as DEFAULT_V2199_PATH,
)
from experiments.r4_parspec_engine_axis_map_contract import (
    VALID_LIKELIHOOD_STATUSES,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    PARSPEC_DOI,
    PARSPEC_EPRINT_URL,
    PARSPEC_SOURCE_URL,
)
from experiments.r4_parspec_qnm_deformation_jacobian import (
    ENGINE_AXES,
    QNM_AXES,
    qeft_qnm_coefficient_vector,
)
from experiments.r4_parspec_ringdown_source_bridge import SOURCE_EVENTS, load_json


VERSION = "v2.200"
DEFAULT_OUT = Path(
    "experiments/results/v2.200/r4_parspec_qnm_to_bresciani_gate.json"
)
SENSITIVITY_MATRIX_ID = "parspec_qnm_to_bresciani_sensitivity_matrix_v1"
VALID_SOURCE_TYPES = {
    "unit_test_control",
    "source_backed_qnm_to_bresciani_r4_sensitivity",
    "source_backed_parspec_qeft_qnm_ray",
}
REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "source_urls",
    "source_type",
    "qnm_axes",
    "target_engine_axes",
    "sensitivity_matrix",
    "bresciani_coordinate_orientation",
    "axis_normalization",
    "likelihood_reference",
    "event_set_policy",
    "systematics",
    "claim_controls",
)


def matrix_rank(matrix: list[list[float]], *, tolerance: float = 1e-12) -> int:
    """Return numeric rank using small Gaussian elimination."""

    if not matrix:
        return 0
    work = [[float(value) for value in row] for row in matrix]
    rows = len(work)
    cols = max((len(row) for row in work), default=0)
    rank = 0
    pivot_col = 0
    while rank < rows and pivot_col < cols:
        pivot = None
        for row_index in range(rank, rows):
            if pivot_col < len(work[row_index]) and (
                abs(work[row_index][pivot_col]) > tolerance
            ):
                pivot = row_index
                break
        if pivot is None:
            pivot_col += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][pivot_col]
        for col_index in range(pivot_col, len(work[rank])):
            work[rank][col_index] /= pivot_value
        for row_index in range(rows):
            if row_index == rank or pivot_col >= len(work[row_index]):
                continue
            factor = work[row_index][pivot_col]
            if abs(factor) <= tolerance:
                continue
            for col_index in range(pivot_col, len(work[row_index])):
                work[row_index][col_index] -= factor * work[rank][col_index]
        rank += 1
        pivot_col += 1
    return rank


def _missing(value: Any) -> bool:
    return value in (None, "", [], {}, ())


def _numeric_matrix(value: Any) -> list[list[float]] | None:
    if not isinstance(value, list) or not value:
        return None
    matrix: list[list[float]] = []
    width = None
    for row in value:
        if not isinstance(row, list) or not row:
            return None
        if width is None:
            width = len(row)
        elif len(row) != width:
            return None
        numeric_row: list[float] = []
        for item in row:
            if isinstance(item, bool) or not isinstance(item, int | float):
                return None
            if not math.isfinite(float(item)):
                return None
            numeric_row.append(float(item))
        matrix.append(numeric_row)
    return matrix


def _valid_square_covariance(value: Any, size: int) -> bool:
    matrix = _numeric_matrix(value)
    if matrix is None or len(matrix) != size:
        return False
    if any(len(row) != size for row in matrix):
        return False
    return all(matrix[index][index] > 0.0 for index in range(size))


def qnm_to_bresciani_gate_contract() -> dict[str, Any]:
    return {
        "contract_id": "parspec_qnm_to_bresciani_gate_contract_v1",
        "version": VERSION,
        "matrix_id": SENSITIVITY_MATRIX_ID,
        "qnm_axes": list(QNM_AXES),
        "target_engine_axes": list(ENGINE_AXES),
        "required_packet_fields": list(REQUIRED_PACKET_FIELDS),
        "valid_source_types": sorted(VALID_SOURCE_TYPES),
        "minimum_sensitivity_matrix": {
            "rows": list(ENGINE_AXES),
            "columns": list(QNM_AXES),
            "matrix_kind": "d_engine_axis_d_qnm_deformation_axis",
            "required_rank": len(ENGINE_AXES),
            "reason": (
                "A one-dimensional qEFT gamma ray is not enough to infer the "
                "three Bresciani R4 engine axes. A source-backed 3x4 "
                "sensitivity matrix or equivalent full-rank operator map is "
                "required."
            ),
        },
        "claim_rule": (
            "Even a source-backed qNM-to-Bresciani map only enables a "
            "nonclaiming likelihood attachment. Framework claims still require "
            "public likelihood/posterior data, waveform systematics, and "
            "external adversarial review."
        ),
    }


def synthetic_ready_qnm_to_bresciani_packet() -> dict[str, Any]:
    """Complete positive control; not evidence for the real qEFT map."""

    return {
        "packet_id": "synthetic_qnm_to_bresciani_operator_map_v1",
        "source_urls": [PARSPEC_SOURCE_URL, BRESCIANI_SOURCE_URL],
        "source_type": "unit_test_control",
        "qnm_axes": list(QNM_AXES),
        "target_engine_axes": list(ENGINE_AXES),
        "sensitivity_matrix": {
            "status": "source_backed",
            "matrix_id": SENSITIVITY_MATRIX_ID,
            "matrix_kind": "d_engine_axis_d_qnm_deformation_axis",
            "rows": list(ENGINE_AXES),
            "columns": list(QNM_AXES),
            "matrix": [
                [1.0, 0.0, 0.0, 0.25],
                [0.0, 1.0, 0.0, -0.5],
                [0.0, 0.0, 1.0, 0.75],
            ],
            "rank": 3,
            "covariance_pushforward_available": True,
        },
        "bresciani_coordinate_orientation": {
            "status": "source_backed",
            "source_coordinates": ["K_plus", "Re(K_minus)", "Im(K_minus)"],
            "target_basis": DICTIONARY_ID,
            "field_redefinition_policy": "closed_for_packet",
        },
        "axis_normalization": {
            "status": "source_backed_absolute_or_equivalent",
            "uses_absolute_gamma_metadata": True,
            "uses_numeric_lambda_r4_scale_or_equivalent": True,
            "normalization_uncertainty_exported": True,
        },
        "likelihood_reference": {
            "status": "public_covariance_matrix",
            "source_axis": "qnm_deformation_axes",
            "events": list(SOURCE_EVENTS),
            "covariance": [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            "posterior_or_likelihood_exported": True,
        },
        "event_set_policy": {
            "status": "aligned",
            "source_events": list(SOURCE_EVENTS),
            "engine_events": list(SOURCE_EVENTS),
            "same_event_set": True,
        },
        "systematics": {
            "status": "engine_export_ready",
            "items": [
                "waveform_systematics_budget",
                "calibration_prior",
                "eft_validity_domain",
            ],
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
            "synthetic_control_not_claim_evidence": True,
        },
    }


def current_qeft_qnm_ray_packet(
    v2199_path: str | Path = DEFAULT_V2199_PATH,
) -> dict[str, Any]:
    v2199 = load_json(v2199_path)
    coefficients = qeft_qnm_coefficient_vector()
    absolute_packet = v2199["absolute_gamma_metadata_packet"]
    return canonicalize_json_floats({
        "packet_id": "current_qeft_qnm_ray_not_bresciani_operator_map",
        "source_urls": [
            PARSPEC_SOURCE_URL,
            PARSPEC_EPRINT_URL,
            PARSPEC_DOI,
            BRESCIANI_SOURCE_URL,
        ],
        "source_type": "source_backed_parspec_qeft_qnm_ray",
        "qnm_axes": list(QNM_AXES),
        "target_engine_axes": list(ENGINE_AXES),
        "sensitivity_matrix": {
            "status": "source_backed",
            "matrix_id": "parspec_qeft_gamma_to_qnm_ray_v1",
            "matrix_kind": "d_qnm_deformation_axis_d_absolute_gamma_qeft",
            "rows": list(QNM_AXES),
            "columns": ["absolute_gamma_qeft"],
            "matrix": [[coefficients[axis]] for axis in QNM_AXES],
            "rank": 1,
            "covariance_pushforward_available": False,
            "source_scope": (
                "ParSpec qEFT supplies one deformation ray in qNM space, not a "
                "three-axis Bresciani R4 operator basis."
            ),
        },
        "source_event_absolute_gamma_rows": (
            absolute_packet["event_bound_absolute_gamma_rows"]
        ),
        "bresciani_coordinate_orientation": {
            "status": "missing",
            "target_basis": DICTIONARY_ID,
            "available_dictionary_ready": True,
            "missing_link": (
                "No source-backed relation from qNM deformation axes to "
                "K_plus/Re(K_minus)/Im(K_minus) or g_R4_c1/c2/c3."
            ),
        },
        "axis_normalization": {
            "status": "parspec_absolute_gamma_ready_only",
            "uses_absolute_gamma_metadata": True,
            "uses_numeric_lambda_r4_scale_or_equivalent": False,
            "normalization_uncertainty_exported": True,
        },
        "likelihood_reference": {
            "status": "published_bound_and_metadata_only",
            "source_axis": "ell_qEFT_km",
            "events": list(SOURCE_EVENTS),
            "posterior_or_likelihood_exported": False,
        },
        "event_set_policy": {
            "status": "aligned",
            "source_events": list(SOURCE_EVENTS),
            "engine_events": list(SOURCE_EVENTS),
            "same_event_set": True,
        },
        "systematics": {
            "status": "not_claim_grade",
            "items": [],
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
        },
    })


def malformed_qnm_to_bresciani_packet() -> dict[str, Any]:
    packet = synthetic_ready_qnm_to_bresciani_packet()
    packet["source_urls"] = ["https://example.invalid/not-primary"]
    packet["sensitivity_matrix"]["rows"] = ["g_R4_c1"]
    packet["sensitivity_matrix"]["matrix"] = [[1.0, 1.0]]
    packet["sensitivity_matrix"]["rank"] = 1
    packet["claim_controls"]["claim_use_allowed"] = True
    return packet


def evaluate_qnm_to_bresciani_packet(
    packet: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = {
        field for field in REQUIRED_PACKET_FIELDS if _missing(packet.get(field))
    }

    source_urls = packet.get("source_urls")
    if not isinstance(source_urls, list) or PARSPEC_SOURCE_URL not in source_urls:
        blockers.add("parspec_source_url_missing")
    if not isinstance(source_urls, list) or BRESCIANI_SOURCE_URL not in source_urls:
        blockers.add("bresciani_source_url_missing")
    if packet.get("source_type") not in VALID_SOURCE_TYPES:
        blockers.add("source_type_not_allowed")
    if tuple(packet.get("qnm_axes", [])) != QNM_AXES:
        blockers.add("qnm_axes_mismatch")
    if tuple(packet.get("target_engine_axes", [])) != ENGINE_AXES:
        blockers.add("target_engine_axes_mismatch")

    matrix_info = packet.get("sensitivity_matrix")
    matrix_rank_value = 0
    if not isinstance(matrix_info, dict) or _missing(matrix_info):
        blockers.add("sensitivity_matrix_missing")
    else:
        if matrix_info.get("status") != "source_backed":
            blockers.add("sensitivity_matrix_not_source_backed")
        if tuple(matrix_info.get("rows", [])) != ENGINE_AXES:
            blockers.add("sensitivity_matrix_not_three_engine_rows")
        columns = tuple(matrix_info.get("columns", []))
        if columns != QNM_AXES:
            blockers.add("sensitivity_matrix_not_four_qnm_columns")
            if (
                tuple(matrix_info.get("rows", [])) == QNM_AXES
                and columns == ("absolute_gamma_qeft",)
            ):
                blockers.add("source_maps_only_one_qeft_ray")
        matrix = _numeric_matrix(matrix_info.get("matrix"))
        if matrix is None:
            blockers.add("sensitivity_matrix_non_numeric_or_ragged")
        else:
            expected_shape = (
                len(matrix_info.get("rows", [])),
                len(matrix_info.get("columns", [])),
            )
            actual_shape = (len(matrix), len(matrix[0]) if matrix else 0)
            if actual_shape != expected_shape:
                blockers.add("sensitivity_matrix_shape_mismatch")
            matrix_rank_value = matrix_rank(matrix)
            if matrix_rank_value < len(ENGINE_AXES):
                blockers.add("sensitivity_matrix_rank_deficient")
        if matrix_info.get("covariance_pushforward_available") is not True:
            blockers.add("covariance_pushforward_missing")

    orientation = packet.get("bresciani_coordinate_orientation")
    if not isinstance(orientation, dict) or _missing(orientation):
        blockers.add("bresciani_coordinate_orientation_missing")
    else:
        if orientation.get("status") != "source_backed":
            blockers.add("bresciani_coordinate_orientation_missing")
        if orientation.get("target_basis") != DICTIONARY_ID:
            blockers.add("bresciani_target_basis_mismatch")
        if orientation.get("field_redefinition_policy") != "closed_for_packet":
            blockers.add("field_redefinition_policy_missing")

    normalization = packet.get("axis_normalization")
    if not isinstance(normalization, dict) or _missing(normalization):
        blockers.add("engine_axis_normalization_missing")
    else:
        if normalization.get("status") != "source_backed_absolute_or_equivalent":
            blockers.add("engine_axis_normalization_missing")
        if normalization.get("uses_numeric_lambda_r4_scale_or_equivalent") is not True:
            blockers.add("numeric_lambda_r4_or_equivalent_normalization_missing")
        if normalization.get("normalization_uncertainty_exported") is not True:
            blockers.add("normalization_uncertainty_missing")

    likelihood = packet.get("likelihood_reference")
    if not isinstance(likelihood, dict) or _missing(likelihood):
        blockers.add("public_parspec_qeft_likelihood_or_posterior_samples_missing")
    else:
        if likelihood.get("status") not in VALID_LIKELIHOOD_STATUSES:
            blockers.add("public_parspec_qeft_likelihood_or_posterior_samples_missing")
        if likelihood.get("posterior_or_likelihood_exported") is not True:
            blockers.add("parspec_likelihood_export_not_confirmed")
        if likelihood.get("status") == "public_covariance_matrix" and not (
            _valid_square_covariance(likelihood.get("covariance"), len(ENGINE_AXES))
        ):
            blockers.add("parspec_likelihood_covariance_invalid")

    events = packet.get("event_set_policy")
    if not isinstance(events, dict) or _missing(events):
        blockers.add("event_set_policy_missing")
    else:
        if events.get("same_event_set") is not True:
            blockers.add("event_set_mismatch")
        if not set(SOURCE_EVENTS).issubset(set(events.get("source_events") or [])):
            blockers.add("source_events_missing_from_event_policy")

    systematics = packet.get("systematics")
    if not isinstance(systematics, dict) or _missing(systematics):
        blockers.add("claim_grade_systematics_export_missing")
    elif systematics.get("status") != "engine_export_ready":
        blockers.add("claim_grade_systematics_export_missing")

    controls = packet.get("claim_controls")
    if not isinstance(controls, dict) or _missing(controls):
        blockers.add("claim_controls_missing")
    else:
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_not_disabled")
        if controls.get("external_adversarial_review_complete") is True:
            blockers.add("external_review_unexpectedly_complete")

    map_blockers = sorted({
        blocker for blocker in blockers
        if blocker.startswith("sensitivity_matrix")
        or blocker.startswith("source_maps")
        or blocker.startswith("covariance_pushforward")
        or blocker.startswith("bresciani")
        or blocker.startswith("field_redefinition")
        or blocker.startswith("engine_axis_normalization")
        or blocker.startswith("numeric_lambda")
        or blocker.startswith("normalization")
    })
    operator_map_ready = not map_blockers
    likelihood_attachment_ready = operator_map_ready and not {
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "parspec_likelihood_export_not_confirmed",
        "parspec_likelihood_covariance_invalid",
        "claim_grade_systematics_export_missing",
    } & blockers

    claim_blockers = {
        "external_adversarial_review_missing",
        "framework_claim_controls_disabled",
    }
    if not operator_map_ready:
        claim_blockers.add("qnm_deformation_to_bresciani_engine_r4_map_missing")
    if not likelihood_attachment_ready:
        claim_blockers.add("parspec_engine_axis_likelihood_attachment_not_ready")
    if packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence"):
        claim_blockers.add("synthetic_control_not_claim_evidence")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "sensitivity_matrix_rank": matrix_rank_value,
        "required_rank": len(ENGINE_AXES),
        "operator_map_ready": operator_map_ready,
        "likelihood_attachment_ready": likelihood_attachment_ready,
        "ready_for_framework_claim": False,
        "map_blockers": map_blockers,
        "all_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "qnm_to_bresciani_operator_map_ready_nonclaiming"
            if likelihood_attachment_ready
            else "qnm_to_bresciani_operator_map_blocked"
        ),
    })


def diagnose_r4_parspec_qnm_to_bresciani_gate(
    *,
    v2199_path: str | Path = DEFAULT_V2199_PATH,
) -> dict[str, Any]:
    dictionary = bresciani_r4_axis_dictionary()
    current_packet = current_qeft_qnm_ray_packet(v2199_path)
    synthetic_packet = synthetic_ready_qnm_to_bresciani_packet()
    malformed_packet = malformed_qnm_to_bresciani_packet()
    current_eval = evaluate_qnm_to_bresciani_packet(current_packet)
    synthetic_eval = evaluate_qnm_to_bresciani_packet(synthetic_packet)
    malformed_eval = evaluate_qnm_to_bresciani_packet(malformed_packet)

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.190_parspec_engine_axis_map_contract",
            "v2.197_parspec_qnm_deformation_jacobian",
            "v2.199_parspec_absolute_gamma_metadata",
        ],
        "contract": qnm_to_bresciani_gate_contract(),
        "sourceability_findings": {
            "bresciani_dictionary_ready": (
                dictionary["operator_projection_matrix"]["status"]
                == "maps_to_bresciani_r4_axes"
            ),
            "bresciani_projection_axes": list(PROJECTION_AXES),
            "parspec_qeft_qnm_ray_ready": True,
            "full_rank_qnm_to_engine_sensitivity_ready": False,
            "public_qeft_likelihood_ready": False,
            "finding": (
                "Current sources supply Bresciani K-to-engine axes and a "
                "ParSpec qEFT gamma-to-qNM ray. They do not supply the "
                "full-rank qNM-to-Bresciani sensitivity matrix needed to "
                "invert qNM deformation coordinates into g_R4_c1/c2/c3."
            ),
        },
        "qeft_qnm_ray_coefficients": qeft_qnm_coefficient_vector(),
        "current_qeft_qnm_ray_packet": current_packet,
        "current_qeft_qnm_ray_evaluation": current_eval,
        "synthetic_ready_packet": synthetic_packet,
        "synthetic_ready_evaluation": synthetic_eval,
        "malformed_control_evaluation": malformed_eval,
        "operator_map_gate_ready": True,
        "current_operator_map_ready": current_eval["operator_map_ready"],
        "current_likelihood_attachment_ready": current_eval[
            "likelihood_attachment_ready"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "resolved_v2199_subpiece": "qnm_to_bresciani_sensitivity_gate_defined",
        "remaining_claim_blockers": sorted({
            "qnm_deformation_to_bresciani_engine_r4_map_missing",
            "public_parspec_qeft_likelihood_or_posterior_samples_missing",
            "claim_grade_systematics_export_missing",
            "external_adversarial_review_missing",
        }),
        "route_status": "parspec_qnm_to_bresciani_gate_ready_map_missing",
        "selected_next_build_action": (
            "acquire_source_backed_qnm_to_bresciani_sensitivity_matrix_or_"
            "public_qeft_likelihood"
        ),
        "interpretation": (
            "v2.200 closes the ambiguity in the next blocker. The qEFT source "
            "ray is one-dimensional in qNM deformation space; the Bresciani "
            "engine basis is three-dimensional. A claim-grade bridge needs a "
            "source-backed 3x4 sensitivity matrix, or an equivalent full-rank "
            "operator map with normalization and public likelihood data."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2199", default=str(DEFAULT_V2199_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_qnm_to_bresciani_gate(
        v2199_path=Path(args.v2199)
    )
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
