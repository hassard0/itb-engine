"""Claim-safe R4 shape likelihood ingestion adapter (v2.162)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_r4_shape_unitarity_diagnostic import (
    diagnose_bresciani_r4_shape_unitarity_diagnostic,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_shape_likelihood_packet_manifest import (
    empty_r4_shape_likelihood_packet,
    evaluate_r4_shape_likelihood_packet,
    synthetic_complete_r4_shape_likelihood_packet,
)


VERSION = "v2.162"
SHAPE_SCORE_AXES = ("g_R4_c1", "g_R4_c2", "g_R4_c3")
SUPPORTED_INGESTION_LIKELIHOOD_STATUSES = {"public_covariance_matrix"}
PIVOT_TOLERANCE = 1.0e-14


def _finite_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        numeric = float(value)
        return numeric if math.isfinite(numeric) else None
    return None


def _shape_reference_coefficients() -> dict[str, float]:
    diagnostic = diagnose_bresciani_r4_shape_unitarity_diagnostic()
    coefficients = diagnostic["evaluation"]["diagnostics"]["coefficients"]
    return {
        axis: float(coefficients[axis])
        for axis in SHAPE_SCORE_AXES
    }


def _solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    augmented = [
        [float(matrix[row][col]) for col in range(n)] + [float(vector[row])]
        for row in range(n)
    ]

    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) <= PIVOT_TOLERANCE:
            raise ValueError("covariance matrix is singular")
        if pivot != col:
            augmented[col], augmented[pivot] = augmented[pivot], augmented[col]

        pivot_value = augmented[col][col]
        for idx in range(col, n + 1):
            augmented[col][idx] /= pivot_value
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            for idx in range(col, n + 1):
                augmented[row][idx] -= factor * augmented[col][idx]

    return [augmented[row][n] for row in range(n)]


def _covariance_for_axes(
    likelihood: dict[str, Any],
    axes: tuple[str, ...],
) -> tuple[list[list[float]] | None, list[str]]:
    blockers: list[str] = []
    declared_axes = list(likelihood.get("axes") or [])
    covariance = likelihood.get("covariance")
    if not declared_axes:
        return None, ["likelihood_axes_missing_for_covariance"]
    if not isinstance(covariance, list):
        return None, ["covariance_matrix_missing_for_shape_score"]
    if any(axis not in declared_axes for axis in axes):
        return None, ["covariance_axes_missing_required_shape_axes"]
    if len(covariance) != len(declared_axes):
        return None, ["covariance_dimension_mismatch"]

    index = [declared_axes.index(axis) for axis in axes]
    selected: list[list[float]] = []
    for row_idx in index:
        row = covariance[row_idx]
        if not isinstance(row, list) or len(row) != len(declared_axes):
            return None, ["covariance_dimension_mismatch"]
        selected_row: list[float] = []
        for col_idx in index:
            numeric = _finite_float(row[col_idx])
            if numeric is None:
                return None, ["covariance_nonfinite_value"]
            selected_row.append(numeric)
        selected.append(selected_row)

    for idx, axis in enumerate(axes):
        if selected[idx][idx] <= 0.0:
            blockers.append(f"covariance_nonpositive_variance_{axis}")
    return selected, blockers


def r4_shape_likelihood_score(packet: dict[str, Any]) -> dict[str, Any]:
    likelihood = packet.get("likelihood")
    blockers: set[str] = set()
    if not isinstance(likelihood, dict):
        return {
            "score_available": False,
            "axes": list(SHAPE_SCORE_AXES),
            "blockers": ["likelihood_missing"],
        }
    if likelihood.get("status") not in SUPPORTED_INGESTION_LIKELIHOOD_STATUSES:
        blockers.add("likelihood_status_not_supported_by_shape_score")

    central_values = likelihood.get("central_values")
    if not isinstance(central_values, dict):
        central_values = {}
    missing_central = [
        axis for axis in SHAPE_SCORE_AXES
        if _finite_float(central_values.get(axis)) is None
    ]
    if missing_central:
        blockers.add("central_shape_values_missing")

    covariance, covariance_blockers = _covariance_for_axes(likelihood, SHAPE_SCORE_AXES)
    blockers.update(covariance_blockers)
    if blockers:
        return canonicalize_json_floats({
            "score_available": False,
            "axes": list(SHAPE_SCORE_AXES),
            "blockers": sorted(blockers),
            "missing_central_axes": missing_central,
        })

    assert covariance is not None
    reference = _shape_reference_coefficients()
    packet_vector = [
        float(central_values[axis])
        for axis in SHAPE_SCORE_AXES
    ]
    reference_vector = [reference[axis] for axis in SHAPE_SCORE_AXES]
    residual = [
        packet_value - reference_value
        for packet_value, reference_value in zip(packet_vector, reference_vector)
    ]
    try:
        weighted = _solve_linear_system(covariance, residual)
    except ValueError:
        return canonicalize_json_floats({
            "score_available": False,
            "axes": list(SHAPE_SCORE_AXES),
            "blockers": ["covariance_matrix_singular"],
            "missing_central_axes": [],
        })

    chi_square = sum(
        residual_value * weighted_value
        for residual_value, weighted_value in zip(residual, weighted)
    )
    if not math.isfinite(chi_square) or chi_square < -PIVOT_TOLERANCE:
        return canonicalize_json_floats({
            "score_available": False,
            "axes": list(SHAPE_SCORE_AXES),
            "blockers": ["shape_score_not_finite_or_negative"],
            "missing_central_axes": [],
        })

    chi_square = max(0.0, float(chi_square))
    sigma_distance = math.sqrt(chi_square)
    return canonicalize_json_floats({
        "score_available": True,
        "axes": list(SHAPE_SCORE_AXES),
        "reference_shape": reference,
        "packet_central_values": dict(zip(SHAPE_SCORE_AXES, packet_vector)),
        "residual": dict(zip(SHAPE_SCORE_AXES, residual)),
        "chi_square_to_string_tree_r4_shape": chi_square,
        "sigma_distance_to_string_tree_r4_shape": sigma_distance,
        "degrees_of_freedom": len(SHAPE_SCORE_AXES),
        "inside_one_sigma_shape_tube": sigma_distance <= 1.0,
        "blockers": [],
        "missing_central_axes": [],
    })


def evaluate_r4_shape_likelihood_ingestion_packet(
    packet: dict[str, Any],
) -> dict[str, Any]:
    manifest = evaluate_r4_shape_likelihood_packet(packet)
    shape_score = r4_shape_likelihood_score(packet)
    synthetic_control = bool(
        packet.get("provenance", {}).get("synthetic_control")
        or packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence")
    )

    blockers: set[str] = set()
    if manifest["ready_for_engine_likelihood_packet"] is not True:
        blockers.add("manifest_packet_gate_failed")
    if shape_score["score_available"] is not True:
        blockers.add("shape_likelihood_score_unavailable")
    adapter_ready = not blockers

    claim_blockers = {
        "framework_claim_controls_disabled",
        "external_adversarial_review_missing",
    }
    if synthetic_control:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if not adapter_ready:
        claim_blockers.add("adapter_ingestion_not_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "manifest_evaluation": manifest,
        "shape_score": shape_score,
        "synthetic_control": synthetic_control,
        "adapter_ingestion_ready": adapter_ready,
        "ready_for_shape_likelihood_diagnostic": adapter_ready,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions": [],
        "ingestion_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "r4_shape_likelihood_packet_ingestion_ready_nonclaiming"
            if adapter_ready
            else "r4_shape_likelihood_packet_ingestion_blocked"
        ),
    })


def current_missing_public_r4_likelihood_slot() -> dict[str, Any]:
    packet = empty_r4_shape_likelihood_packet()
    packet["packet_id"] = "current_missing_public_r4_likelihood_slot"
    return packet


def synthetic_offset_r4_likelihood_packet() -> dict[str, Any]:
    packet = deepcopy(synthetic_complete_r4_shape_likelihood_packet())
    packet["packet_id"] = "synthetic_offset_r4_shape_likelihood_packet"
    packet["likelihood"]["central_values"]["g_R4_c3"] = 0.1
    return packet


def diagnose_r4_shape_likelihood_ingestion_adapter() -> dict[str, Any]:
    synthetic_exact = evaluate_r4_shape_likelihood_ingestion_packet(
        synthetic_complete_r4_shape_likelihood_packet()
    )
    synthetic_offset = evaluate_r4_shape_likelihood_ingestion_packet(
        synthetic_offset_r4_likelihood_packet()
    )
    current_missing = evaluate_r4_shape_likelihood_ingestion_packet(
        current_missing_public_r4_likelihood_slot()
    )

    current_public_packets = [current_missing]
    ready_public_packets = [
        row["packet_id"] for row in current_public_packets
        if row["adapter_ingestion_ready"]
    ]

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.158_bresciani_r4_shape_unitarity_diagnostic",
            "v2.160_r4_shape_likelihood_packet_manifest",
            "v2.161_post_r4_likelihood_manifest_frontier",
        ],
        "route": "future_public_r4_shape_likelihood_ingestion",
        "supported_shape_score_axes": list(SHAPE_SCORE_AXES),
        "supported_ingestion_likelihood_statuses": sorted(
            SUPPORTED_INGESTION_LIKELIHOOD_STATUSES
        ),
        "synthetic_exact_control": synthetic_exact,
        "synthetic_offset_control": synthetic_offset,
        "current_public_packet_assessments": current_public_packets,
        "ready_public_r4_likelihood_packets_now": ready_public_packets,
        "claimable_framework_exclusions_now": [],
        "claimable_discriminator_now": False,
        "route_status": "r4_shape_likelihood_ingestion_adapter_ready_no_public_packet",
        "selected_next_build_action": (
            "wire_real_public_r4_shape_likelihood_packet_when_source_exists"
        ),
        "best_next_artifact": (
            "A real public packet satisfying the v2.160 manifest with a "
            "covariance over g_R4_c1, g_R4_c2, and g_R4_c3. The adapter will "
            "score it against the registered string-tree R4 shape but will "
            "still require adversarial review before any framework claim."
        ),
        "interpretation": (
            "The R4 likelihood route is now implementation-ready: a future "
            "packet can be loaded, manifest-gated, and scored against the "
            "Bresciani shape diagnostic. The current public slot remains empty, "
            "so no claimable discriminator exists."
        ),
    })


def load_packet(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", default=None)
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.162/"
            "r4_shape_likelihood_ingestion_adapter.json"
        ),
    )
    args = parser.parse_args()

    if args.packet:
        result = {
            "version": VERSION,
            "packet_path": args.packet,
            "evaluation": evaluate_r4_shape_likelihood_ingestion_packet(
                load_packet(args.packet)
            ),
        }
    else:
        result = diagnose_r4_shape_likelihood_ingestion_adapter()

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
