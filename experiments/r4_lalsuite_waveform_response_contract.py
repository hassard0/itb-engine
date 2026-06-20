"""LALSuite-compatible R4 waveform response contract for GW reanalysis."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.bresciani_r4_axis_dictionary import bresciani_r4_axis_mapping_sidecar
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_lalsuite_imr_projection import lalsuite_status


VERSION = "v2.177"
RESPONSE_AXES = ("g_R4_c1", "g_R4_c2", "g_R4_c3")
VF_GRID_MIN = 0.08
VF_GRID_MAX = 0.32
VF_GRID_COUNT = 129
REQUIRED_REAL_REANALYSIS_CLOSURES = (
    "source_backed_r4_pn_or_imr_waveform_derivation",
    "lalsuite_runtime_with_imrphenomd_or_successor",
    "public_strain_projection_over_g_R4_c1_c2_c3",
    "nuisance_marginalized_public_covariance_export",
    "waveform_calibration_prior_and_eft_systematics_closed",
    "external_adversarial_review_complete",
)


def default_r4_vf_grid(
    *,
    count: int = VF_GRID_COUNT,
    minimum: float = VF_GRID_MIN,
    maximum: float = VF_GRID_MAX,
) -> np.ndarray:
    if count < 3:
        raise ValueError("count must be at least 3")
    if not math.isfinite(minimum) or not math.isfinite(maximum):
        raise ValueError("grid bounds must be finite")
    if minimum <= 0.0 or minimum >= maximum:
        raise ValueError("grid must satisfy 0 < minimum < maximum")
    return np.linspace(float(minimum), float(maximum), int(count))


def _as_floats(values: np.ndarray) -> list[float]:
    return [float(value) for value in np.asarray(values, dtype=float)]


def _kernel_summary(values: np.ndarray) -> dict[str, float]:
    kernel = np.asarray(values, dtype=float)
    return {
        "min": float(np.min(kernel)),
        "max": float(np.max(kernel)),
        "l2_norm": float(np.linalg.norm(kernel)),
        "mean": float(np.mean(kernel)),
        "first": float(kernel[0]),
        "last": float(kernel[-1]),
    }


def _gram_matrix(kernels: dict[str, np.ndarray]) -> list[list[float]]:
    rows = [np.asarray(kernels[axis], dtype=float) for axis in RESPONSE_AXES]
    return [
        [float(np.dot(left, right)) for right in rows]
        for left in rows
    ]


def r4_shape_response_kernels(v_f: np.ndarray | None = None) -> dict[str, Any]:
    grid = default_r4_vf_grid() if v_f is None else np.asarray(v_f, dtype=float)
    if grid.ndim != 1 or grid.size < 3:
        raise ValueError("v_f must be a one-dimensional grid with at least 3 points")
    if not np.all(np.isfinite(grid)) or not np.all(np.diff(grid) > 0.0):
        raise ValueError("v_f grid must be finite and strictly increasing")
    if float(grid[0]) <= 0.0:
        raise ValueError("v_f grid must be positive")

    kernels = {
        "g_R4_c1": grid**8 * (1.0 + 0.25 * grid**2),
        "g_R4_c2": grid**8 * (1.0 - 0.20 * grid**2 + 0.05 * grid**4),
        "g_R4_c3": grid**9 * (1.0 + 0.15 * grid),
    }
    matrix = np.column_stack([kernels[axis] for axis in RESPONSE_AXES])
    rank = int(np.linalg.matrix_rank(matrix, tol=1.0e-18))
    return canonicalize_json_floats({
        "source_backed_waveform_derivation": False,
        "kernel_kind": "dimensionless_linearized_r4_shape_response_ansatz",
        "v_f_grid": _as_floats(grid),
        "axes": list(RESPONSE_AXES),
        "kernels": {
            axis: _as_floats(values) for axis, values in kernels.items()
        },
        "kernel_summary": {
            axis: _kernel_summary(values) for axis, values in kernels.items()
        },
        "gram_matrix": _gram_matrix(kernels),
        "kernel_rank": rank,
        "rank_ready": rank == len(RESPONSE_AXES),
        "claim_boundary": (
            "These kernels are an executable response-shape contract, not a "
            "source-backed R4 waveform derivation."
        ),
    })


def lalsuite_r4_waveform_response_contract() -> dict[str, Any]:
    sidecar = bresciani_r4_axis_mapping_sidecar()
    status = lalsuite_status()
    return canonicalize_json_floats({
        "version": VERSION,
        "contract_id": "lalsuite_r4_shape_response_contract_v1",
        "base_waveform": {
            "approximant": "IMRPhenomD",
            "runtime_status": status,
            "required_lalsuite_module": "lalsimulation",
        },
        "axis_mapping": sidecar,
        "response_axes": list(RESPONSE_AXES),
        "kernel_basis": r4_shape_response_kernels(),
        "lalsuite_hook": {
            "status": "compatible_contract_defined",
            "hook_point": "frequency_domain_h_plus_linearized_multiplier",
            "required_inputs": [
                "frequencies_hz",
                "v_f",
                "psd",
                "gr_h_plus",
                "g_R4_c1",
                "g_R4_c2",
                "g_R4_c3",
            ],
            "runtime_required_for_real_reanalysis": True,
        },
        "packet_export_target": {
            "source_artifact": "v2.176_public_gw_r4_reanalysis_fixture",
            "target_packet": "v2.160_r4_shape_likelihood_packet_manifest",
            "target_adapter": "v2.162_r4_shape_likelihood_ingestion_adapter",
        },
        "required_real_reanalysis_closures": list(
            REQUIRED_REAL_REANALYSIS_CLOSURES
        ),
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "response_contract_only_not_claim_evidence": True,
        },
    })


def synthetic_lalsuite_r4_response_candidate() -> dict[str, Any]:
    contract = lalsuite_r4_waveform_response_contract()
    return canonicalize_json_floats({
        "label": "synthetic_lalsuite_r4_response_contract_candidate",
        "contract_id": contract["contract_id"],
        "response_axes": contract["response_axes"],
        "axis_mapping": contract["axis_mapping"],
        "kernel_basis": contract["kernel_basis"],
        "lalsuite_hook": contract["lalsuite_hook"],
        "packet_export_target": contract["packet_export_target"],
        "source_backed_waveform_derivation": False,
        "software_contract_candidate": True,
        "claim_controls": contract["claim_controls"],
    })


def evaluate_lalsuite_r4_response_candidate(
    candidate: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = set()
    axes = list(candidate.get("response_axes") or [])
    if axes != list(RESPONSE_AXES):
        blockers.add("response_axes_not_bresciani_r4_shape_axes")

    mapping = candidate.get("axis_mapping")
    if not isinstance(mapping, dict) or mapping.get("status") != "maps_to_bresciani_r4_axes":
        blockers.add("axis_mapping_not_bresciani")
    elif not set(RESPONSE_AXES).issubset(set(mapping.get("projection_axes", []))):
        blockers.add("axis_mapping_projection_axes_incomplete")

    basis = candidate.get("kernel_basis")
    if not isinstance(basis, dict):
        blockers.add("kernel_basis_missing")
        rank = 0
    else:
        rank = int(basis.get("kernel_rank") or 0)
        if basis.get("rank_ready") is not True or rank < len(RESPONSE_AXES):
            blockers.add("r4_response_kernels_not_rank_three")
        grid = np.asarray(basis.get("v_f_grid", []), dtype=float)
        if grid.ndim != 1 or grid.size < 3 or not np.all(np.diff(grid) > 0.0):
            blockers.add("vf_grid_invalid")
        kernels = basis.get("kernels", {})
        if not isinstance(kernels, dict):
            blockers.add("kernels_missing")
        else:
            for axis in RESPONSE_AXES:
                values = np.asarray(kernels.get(axis, []), dtype=float)
                if values.shape != grid.shape or not np.all(np.isfinite(values)):
                    blockers.add(f"{axis}_kernel_invalid")

    hook = candidate.get("lalsuite_hook")
    if not isinstance(hook, dict) or hook.get("status") != "compatible_contract_defined":
        blockers.add("lalsuite_hook_not_defined")

    target = candidate.get("packet_export_target")
    if not isinstance(target, dict):
        blockers.add("packet_export_target_missing")
    elif target.get("target_packet") != "v2.160_r4_shape_likelihood_packet_manifest":
        blockers.add("packet_export_target_not_v2_160")

    controls = candidate.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
    else:
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_not_disabled")

    runtime = lalsuite_status()
    real_reanalysis_blockers = set(REQUIRED_REAL_REANALYSIS_CLOSURES)
    if runtime["available"] and runtime["has_imrphenomd"]:
        real_reanalysis_blockers.discard(
            "lalsuite_runtime_with_imrphenomd_or_successor"
        )
    if candidate.get("source_backed_waveform_derivation") is True:
        real_reanalysis_blockers.discard(
            "source_backed_r4_pn_or_imr_waveform_derivation"
        )

    return canonicalize_json_floats({
        "label": candidate.get("label"),
        "software_response_contract_ready": not blockers,
        "ready_to_replace_v2_176_fixture_response_contract": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "contract_blockers": sorted(blockers),
        "real_reanalysis_blockers": sorted(real_reanalysis_blockers),
        "claim_blockers": sorted(
            set(real_reanalysis_blockers)
            | {"framework_claim_controls_disabled"}
        ),
        "kernel_rank": rank,
        "lalsuite_runtime_status": runtime,
        "route_status": (
            "lalsuite_r4_response_contract_ready_nonclaiming"
            if not blockers
            else "lalsuite_r4_response_contract_blocked"
        ),
    })


def malformed_lalsuite_r4_response_candidate() -> dict[str, Any]:
    candidate = deepcopy(synthetic_lalsuite_r4_response_candidate())
    candidate["label"] = "malformed_lalsuite_r4_response_candidate"
    candidate["response_axes"].remove("g_R4_c3")
    candidate["kernel_basis"]["kernels"]["g_R4_c3"] = list(
        candidate["kernel_basis"]["kernels"]["g_R4_c2"]
    )
    candidate["kernel_basis"]["kernel_rank"] = 2
    candidate["kernel_basis"]["rank_ready"] = False
    candidate["claim_controls"]["claim_use_allowed"] = True
    return candidate


def diagnose_r4_lalsuite_waveform_response_contract() -> dict[str, Any]:
    contract = lalsuite_r4_waveform_response_contract()
    candidate = synthetic_lalsuite_r4_response_candidate()
    malformed = malformed_lalsuite_r4_response_candidate()
    candidate_eval = evaluate_lalsuite_r4_response_candidate(candidate)
    malformed_eval = evaluate_lalsuite_r4_response_candidate(malformed)

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.176_public_gw_r4_reanalysis_fixture",
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.113_lalsuite_imrphenomd_projection",
            "v2.109_source_backed_cubic_waveform_response_pattern",
        ],
        "contract": contract,
        "candidate_evaluation": candidate_eval,
        "malformed_control_evaluation": malformed_eval,
        "software_response_contract_ready": (
            candidate_eval["software_response_contract_ready"]
        ),
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "lalsuite_r4_waveform_response_contract_ready_nonclaiming",
        "selected_next_build_action": (
            "project_r4_response_contract_onto_public_strain_harness"
        ),
        "best_next_artifact": (
            "Use the v2.177 R4 response kernels as a software contract in the "
            "GW170608 public-strain conditioning harness, while separately "
            "replacing the ansatz kernels with source-backed R4 PN/IMR kernels."
        ),
        "interpretation": (
            "The synthetic v2.176 response is now replaced by an executable "
            "rank-three LALSuite-compatible response contract. This is still "
            "not a real public R4 reanalysis: the R4 PN/IMR waveform derivation, "
            "LALSuite runtime sampling, nuisance covariance export, systematics, "
            "and external review remain explicit gates."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.177/"
            "r4_lalsuite_waveform_response_contract.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_lalsuite_waveform_response_contract()
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
