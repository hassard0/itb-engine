"""Source-backed R4 PN/IMR response derivation for the GWOSC route."""

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
from experiments.bresciani_r4_axis_dictionary import (
    BRESCIANI_SOURCE_URL,
    PROJECTION_AXES,
    bresciani_r4_axis_mapping_sidecar,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_lalsuite_waveform_response_contract import default_r4_vf_grid


VERSION = "v2.180"
BERNARD_SOURCE_URL = "https://arxiv.org/abs/2507.17143"
LIU_YUNES_SOURCE_URL = "https://arxiv.org/abs/2407.08929"
SOURCE_CHANNELS = ("K_plus", "Re_K_minus", "Im_K_minus")
PHASE_TERMS = ("tidal_5pn", "direct_bulk_7pn")
AMPLITUDE_TERMS = ("tidal_5pn", "direct_bulk_7pn")
ENGINE_AXIS_CHANNEL_WEIGHTS = {
    "g_R4_c1": {"K_plus": 0.5, "Re_K_minus": 0.5, "Im_K_minus": 0.0},
    "g_R4_c2": {"K_plus": 0.5, "Re_K_minus": -0.5, "Im_K_minus": 0.0},
    "g_R4_c3": {"K_plus": 0.0, "Re_K_minus": 0.0, "Im_K_minus": 1.0},
}
REMAINING_REAL_REANALYSIS_BLOCKERS = (
    "full_imr_r4_merger_ringdown_completion_missing",
    "lalsuite_r4_runtime_projection_not_run",
    "nuisance_marginalized_covariance_not_exported",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


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


def _validate_grid(v_f: np.ndarray) -> np.ndarray:
    grid = np.asarray(v_f, dtype=float)
    if grid.ndim != 1 or grid.size < 3:
        raise ValueError("v_f must be a one-dimensional grid with at least 3 points")
    if not np.all(np.isfinite(grid)) or not np.all(np.diff(grid) > 0.0):
        raise ValueError("v_f grid must be finite and strictly increasing")
    if float(grid[0]) <= 0.0:
        raise ValueError("v_f grid must be positive")
    return grid


def quartic_curvature_pn_dictionary() -> dict[str, Any]:
    return {
        "source_reference": BERNARD_SOURCE_URL,
        "dictionary_scope": (
            "generic local EFT curvature corrections in compact-binary "
            "inspiral, no extra scalar/tensor degree of freedom"
        ),
        "quartic_no_scalar_no_derivatives": {
            "curvature_order_p": 4,
            "extra_degrees_of_freedom": False,
            "derivatives_of_riemann": False,
            "direct_bulk_pn_order": 7.0,
            "tidal_pn_order": 5.0,
            "dominant_nonspinning_bh_note": (
                "The source dictionary gives a direct quartic-curvature bulk "
                "effect at 7PN, while quartic tidal effects can enter at 5PN "
                "and scale with the lighter compact object."
            ),
            "source_equation_refs": [
                "section_II_executive_summary_no_scalar_curvature_order",
                "section_VII_1_general_curvature_rule",
                "section_VIII_1_quartic_gravity",
                "table_1_quartic_gravity_pn_order",
            ],
        },
    }


def r4_pn_power_law_terms(v_f: np.ndarray | None = None) -> dict[str, Any]:
    grid = default_r4_vf_grid() if v_f is None else _validate_grid(v_f)
    phase_terms = {
        "tidal_5pn": grid**5,
        "direct_bulk_7pn": grid**9,
    }
    amplitude_terms = {
        "tidal_5pn": grid**10,
        "direct_bulk_7pn": grid**14,
    }
    return canonicalize_json_floats({
        "v_f_grid": _as_floats(grid),
        "source_reference": BERNARD_SOURCE_URL,
        "phase_delta_psi_power_rule": "nPN -> v_f^(2*n - 5)",
        "relative_amplitude_power_rule": "nPN -> v_f^(2*n)",
        "phase_delta_psi": {
            label: _as_floats(values) for label, values in phase_terms.items()
        },
        "relative_amplitude_delta_a_over_a_newt": {
            label: _as_floats(values) for label, values in amplitude_terms.items()
        },
        "term_summary": {
            "phase_delta_psi": {
                label: _kernel_summary(values)
                for label, values in phase_terms.items()
            },
            "relative_amplitude_delta_a_over_a_newt": {
                label: _kernel_summary(values)
                for label, values in amplitude_terms.items()
            },
        },
    })


def _axis_flattened_vector(
    terms: dict[str, Any],
    axis: str,
) -> np.ndarray:
    grid = np.asarray(terms["v_f_grid"], dtype=float)
    parts: list[np.ndarray] = []
    weights = ENGINE_AXIS_CHANNEL_WEIGHTS[axis]
    term_families = (
        ("phase_delta_psi", PHASE_TERMS),
        ("relative_amplitude_delta_a_over_a_newt", AMPLITUDE_TERMS),
    )
    for family, labels in term_families:
        for label in labels:
            values = np.asarray(terms[family][label], dtype=float)
            if values.shape != grid.shape:
                raise ValueError(f"{family}.{label} does not match v_f_grid")
            for channel in SOURCE_CHANNELS:
                parts.append(float(weights[channel]) * values)
    return np.concatenate(parts)


def _channel_rank_and_gram(terms: dict[str, Any]) -> dict[str, Any]:
    vectors = {
        axis: _axis_flattened_vector(terms, axis) for axis in PROJECTION_AXES
    }
    matrix = np.vstack([vectors[axis] for axis in PROJECTION_AXES])
    gram = matrix @ matrix.T
    return canonicalize_json_floats({
        "axis_order": list(PROJECTION_AXES),
        "source_channels": list(SOURCE_CHANNELS),
        "flattened_vector_length": int(matrix.shape[1]),
        "channel_kernel_rank": int(np.linalg.matrix_rank(matrix, tol=1.0e-18)),
        "axis_vector_norms": {
            axis: float(np.linalg.norm(vector))
            for axis, vector in vectors.items()
        },
        "gram_matrix": [
            [float(value) for value in row]
            for row in np.asarray(gram, dtype=float)
        ],
    })


def source_backed_r4_pn_imr_response_derivation(
    v_f: np.ndarray | None = None,
) -> dict[str, Any]:
    terms = r4_pn_power_law_terms(v_f)
    rank_probe = _channel_rank_and_gram(terms)
    sidecar = bresciani_r4_axis_mapping_sidecar()
    return canonicalize_json_floats({
        "version": VERSION,
        "derivation_id": "r4_source_backed_pn_imr_response_derivation_v1",
        "source_backed_waveform_derivation": True,
        "kernel_kind": "source_backed_quartic_curvature_pn_channel_response",
        "derivation_scope": (
            "Source-backed inspiral PN scaling and Bresciani helicity-channel "
            "axis map for R4 shape kernels; not an event-level R4 likelihood "
            "or a complete merger-ringdown waveform."
        ),
        "source_evidence": {
            "bernard_giri_lehner_sturani_2025": {
                "url": BERNARD_SOURCE_URL,
                "role": "quartic_curvature_inspiral_pn_scaling_dictionary",
                "source_equation_refs": [
                    "section_II",
                    "section_VII_1",
                    "section_VIII_1",
                    "table_1",
                ],
            },
            "bresciani_levati_paradisi_2025": {
                "url": BRESCIANI_SOURCE_URL,
                "role": "spin_2_R4_helicity_axis_contract",
                "source_equation_refs": [
                    "eq:Lag-quartic",
                    "eq:amplitude",
                    "c_plus_c_minus_definitions",
                ],
            },
            "liu_yunes_2024": {
                "url": LIU_YUNES_SOURCE_URL,
                "role": (
                    "IMRPhenomD-style higher-curvature waveform construction "
                    "pattern; not an R4 coefficient source"
                ),
                "source_equation_refs": [
                    "inspiral_phase_amplitude_pn_response",
                    "imrphenomd_modified_waveform_workflow",
                ],
            },
        },
        "pn_dictionary": quartic_curvature_pn_dictionary(),
        "axis_mapping": sidecar,
        "source_channels": list(SOURCE_CHANNELS),
        "engine_axis_channel_weights": ENGINE_AXIS_CHANNEL_WEIGHTS,
        "channel_kernel_terms": terms,
        "channel_rank_probe": rank_probe,
        "lalsuite_handoff_contract": {
            "base_waveform": "IMRPhenomD_or_successor",
            "hook_point": "frequency_domain_h_plus_linearized_multiplier",
            "inspiral_source_backed": True,
            "full_imr_response_complete": False,
            "runtime_required_for_real_reanalysis": True,
            "merger_ringdown_completion_required": True,
            "parameter_axes": list(PROJECTION_AXES),
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "source_backed_kernel_derivation_only_not_claim_evidence": True,
        },
    })


def evaluate_r4_source_backed_pn_imr_derivation(
    derivation: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = set()
    if derivation.get("source_backed_waveform_derivation") is not True:
        blockers.add("response_not_marked_source_backed")
    if derivation.get("kernel_kind") != (
        "source_backed_quartic_curvature_pn_channel_response"
    ):
        blockers.add("kernel_kind_unexpected")

    evidence = derivation.get("source_evidence", {})
    evidence_urls = {
        row.get("url") for row in evidence.values() if isinstance(row, dict)
    }
    for url in (BERNARD_SOURCE_URL, BRESCIANI_SOURCE_URL, LIU_YUNES_SOURCE_URL):
        if url not in evidence_urls:
            blockers.add(f"source_url_missing:{url}")

    axis_mapping = derivation.get("axis_mapping")
    if not isinstance(axis_mapping, dict):
        blockers.add("axis_mapping_missing")
    elif axis_mapping.get("status") != "maps_to_bresciani_r4_axes":
        blockers.add("axis_mapping_not_bresciani")
    elif list(axis_mapping.get("projection_axes", [])) != list(PROJECTION_AXES):
        blockers.add("axis_mapping_projection_axes_mismatch")

    pn = (
        derivation.get("pn_dictionary", {})
        .get("quartic_no_scalar_no_derivatives", {})
    )
    if pn.get("curvature_order_p") != 4:
        blockers.add("quartic_curvature_order_missing")
    if pn.get("extra_degrees_of_freedom") is not False:
        blockers.add("extra_degree_policy_not_pure_metric")
    if pn.get("derivatives_of_riemann") is not False:
        blockers.add("riemann_derivative_policy_not_plain_r4")
    if float(pn.get("direct_bulk_pn_order", math.nan)) != 7.0:
        blockers.add("direct_bulk_pn_order_not_7pn")
    if float(pn.get("tidal_pn_order", math.nan)) != 5.0:
        blockers.add("tidal_pn_order_not_5pn")

    terms = derivation.get("channel_kernel_terms", {})
    try:
        grid = _validate_grid(np.asarray(terms.get("v_f_grid", []), dtype=float))
        expected_terms = {
            "phase_delta_psi": {
                "tidal_5pn": grid**5,
                "direct_bulk_7pn": grid**9,
            },
            "relative_amplitude_delta_a_over_a_newt": {
                "tidal_5pn": grid**10,
                "direct_bulk_7pn": grid**14,
            },
        }
        for family, rows in expected_terms.items():
            family_terms = terms.get(family, {})
            if not isinstance(family_terms, dict):
                blockers.add(f"{family}_terms_missing")
                continue
            for label, expected in rows.items():
                values = np.asarray(family_terms.get(label, []), dtype=float)
                expected_values = np.asarray(
                    canonicalize_json_floats(_as_floats(expected)),
                    dtype=float,
                )
                if values.shape != grid.shape or not np.all(np.isfinite(values)):
                    blockers.add(f"{family}_{label}_kernel_invalid")
                elif not np.allclose(
                    values,
                    expected_values,
                    rtol=0.0,
                    atol=1.0e-15,
                ):
                    blockers.add(f"{family}_{label}_power_law_mismatch")
    except (TypeError, ValueError):
        blockers.add("v_f_grid_invalid")
        terms = {}

    weights = derivation.get("engine_axis_channel_weights")
    if weights != ENGINE_AXIS_CHANNEL_WEIGHTS:
        blockers.add("engine_axis_channel_weights_changed")

    rank = 0
    try:
        rank = _channel_rank_and_gram(terms)["channel_kernel_rank"]
        if rank < len(PROJECTION_AXES):
            blockers.add("channel_response_rank_not_three")
    except (KeyError, TypeError, ValueError):
        blockers.add("channel_response_rank_unavailable")

    handoff = derivation.get("lalsuite_handoff_contract")
    if not isinstance(handoff, dict):
        blockers.add("lalsuite_handoff_contract_missing")
    else:
        if handoff.get("inspiral_source_backed") is not True:
            blockers.add("inspiral_handoff_not_source_backed")
        if handoff.get("parameter_axes") != list(PROJECTION_AXES):
            blockers.add("handoff_parameter_axes_mismatch")

    controls = derivation.get("claim_controls")
    if not isinstance(controls, dict):
        blockers.add("claim_controls_missing")
    else:
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_not_disabled")

    ready = not blockers
    remaining = set(REMAINING_REAL_REANALYSIS_BLOCKERS)
    if not ready:
        remaining.add("source_backed_r4_pn_or_imr_waveform_derivation")
    return canonicalize_json_floats({
        "derivation_id": derivation.get("derivation_id"),
        "response_derivation_ready": ready,
        "ready_to_replace_v2_177_ansatz_kernel_basis": ready,
        "ready_to_wire_into_v2_179_hdf5_projection": ready,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "derivation_blockers": sorted(blockers),
        "remaining_real_reanalysis_blockers": sorted(remaining),
        "claim_blockers": sorted(
            remaining | {"framework_claim_controls_disabled"}
        ),
        "removed_v2_179_blocker": (
            "r4_response_kernels_are_ansatz_not_source_backed"
            if ready else None
        ),
        "channel_kernel_rank": rank,
        "route_status": (
            "r4_source_backed_pn_imr_derivation_ready_nonclaiming"
            if ready
            else "r4_source_backed_pn_imr_derivation_blocked"
        ),
    })


def malformed_r4_source_backed_pn_imr_derivation() -> dict[str, Any]:
    derivation = deepcopy(source_backed_r4_pn_imr_response_derivation())
    derivation["source_backed_waveform_derivation"] = False
    derivation["source_evidence"]["bernard_giri_lehner_sturani_2025"][
        "url"
    ] = "https://example.invalid/source"
    pn = derivation["pn_dictionary"]["quartic_no_scalar_no_derivatives"]
    pn["direct_bulk_pn_order"] = 6.0
    terms = derivation["channel_kernel_terms"]
    terms["phase_delta_psi"]["direct_bulk_7pn"] = list(
        terms["phase_delta_psi"]["tidal_5pn"]
    )
    derivation["engine_axis_channel_weights"]["g_R4_c3"] = {
        "K_plus": 0.0,
        "Re_K_minus": 0.0,
        "Im_K_minus": 0.0,
    }
    derivation["claim_controls"]["claim_use_allowed"] = True
    return derivation


def diagnose_r4_source_backed_pn_imr_derivation() -> dict[str, Any]:
    derivation = source_backed_r4_pn_imr_response_derivation()
    evaluation = evaluate_r4_source_backed_pn_imr_derivation(derivation)
    malformed = evaluate_r4_source_backed_pn_imr_derivation(
        malformed_r4_source_backed_pn_imr_derivation()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.179_r4_response_gwosc_hdf5_projection",
            "v2.177_r4_lalsuite_waveform_response_contract",
            "v2.175_bresciani_r4_axis_dictionary",
            "Bernard_Giri_Lehner_Sturani_arXiv_2507_17143_quartic_PN_rules",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855_R4_axes",
        ],
        "derivation": derivation,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "response_derivation_ready": evaluation["response_derivation_ready"],
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "wire_source_backed_r4_pn_kernels_into_gwosc_hdf5_projection"
        ),
        "best_next_artifact": (
            "Replace the v2.179 projection template basis with the v2.180 "
            "source-backed R4 PN channel kernels, then regenerate the GWOSC "
            "H1/L1 projection seed while keeping covariance/systematics gates."
        ),
        "interpretation": (
            "The arbitrary v2.177 R4 response-shape ansatz now has a "
            "source-backed replacement for inspiral PN scaling and Bresciani "
            "helicity-channel axis structure. This removes the ansatz-kernel "
            "blocker for the software route, but remains nonclaiming until the "
            "source-backed kernels are wired through LALSuite/GWOSC runtime "
            "sampling with nuisance covariance, systematics, and review."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.180/"
            "r4_source_backed_pn_imr_derivation.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_source_backed_pn_imr_derivation()
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
