"""qEFT source-axis pushforward into ParSpec QNM deformation coordinates."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_published_bound_surrogate import (
    DEFAULT_OUT as DEFAULT_V2196_PATH,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    QEFT_POWER,
    QEFT_QNM_DEFORMATION_COEFFICIENTS,
)
from experiments.r4_parspec_ringdown_source_bridge import SOURCE_EVENTS, load_json


VERSION = "v2.197"
DEFAULT_OUT = Path(
    "experiments/results/v2.197/r4_parspec_qnm_deformation_jacobian.json"
)
QNM_AXES = (
    "delta_omega_qeft_0",
    "delta_tau_qeft_0",
    "delta_omega_qeft_1",
    "delta_tau_qeft_1",
)
ENGINE_AXES = ("g_R4_c1", "g_R4_c2", "g_R4_c3")


def qeft_qnm_coefficient_vector() -> dict[str, float]:
    return canonicalize_json_floats({
        "delta_omega_qeft_0": QEFT_QNM_DEFORMATION_COEFFICIENTS["nmax_0"][
            "delta_omega_qeft_0"
        ],
        "delta_tau_qeft_0": QEFT_QNM_DEFORMATION_COEFFICIENTS["nmax_0"][
            "delta_tau_qeft_0"
        ],
        "delta_omega_qeft_1": QEFT_QNM_DEFORMATION_COEFFICIENTS["nmax_1"][
            "delta_omega_qeft_1"
        ],
        "delta_tau_qeft_1": QEFT_QNM_DEFORMATION_COEFFICIENTS["nmax_1"][
            "delta_tau_qeft_1"
        ],
    })


def normalized_gamma_from_ell(
    ell_qeft_km: float,
    upper_bound_km_90: float,
) -> float:
    if upper_bound_km_90 <= 0:
        raise ValueError("upper_bound_km_90 must be positive")
    ratio = ell_qeft_km / upper_bound_km_90
    return ratio**QEFT_POWER


def normalized_gamma_derivative(
    ell_qeft_km: float,
    upper_bound_km_90: float,
) -> float:
    if upper_bound_km_90 <= 0:
        raise ValueError("upper_bound_km_90 must be positive")
    if ell_qeft_km == 0:
        return 0.0
    return (
        QEFT_POWER
        * (ell_qeft_km ** (QEFT_POWER - 1))
        / (upper_bound_km_90**QEFT_POWER)
    )


def qnm_deformation_rows_for_surrogate(
    surrogate_row: dict[str, Any],
) -> dict[str, Any]:
    coefficients = qeft_qnm_coefficient_vector()
    upper_bound = float(surrogate_row["upper_bound_km_90"])
    rows = []
    for point in surrogate_row["grid"]:
        ell = float(point["ell_qEFT_km"])
        gamma_norm = normalized_gamma_from_ell(ell, upper_bound)
        gamma_prime = normalized_gamma_derivative(ell, upper_bound)
        qnm = {
            axis: coefficient * gamma_norm
            for axis, coefficient in coefficients.items()
        }
        jacobian = {
            axis: coefficient * gamma_prime
            for axis, coefficient in coefficients.items()
        }
        rows.append({
            "ell_qEFT_km": ell,
            "fraction_of_published_bound": point["fraction_of_published_bound"],
            "normalized_gamma": gamma_norm,
            "d_normalized_gamma_d_ell_km": gamma_prime,
            "qnm_deformation": qnm,
            "dqnm_deformation_d_ell_km": jacobian,
            "log_relative_surrogate_likelihood": point[
                "log_relative_surrogate_likelihood"
            ],
        })
    bound_gamma_prime = normalized_gamma_derivative(upper_bound, upper_bound)
    return canonicalize_json_floats({
        "label": surrogate_row["label"],
        "source_axis": surrogate_row["source_axis"],
        "upper_bound_km_90": upper_bound,
        "qeft_power": QEFT_POWER,
        "normalization": (
            "normalized_gamma=(ell_qEFT_km/upper_bound_km_90)^6; source "
            "absolute gamma still requires remnant mass and redshift."
        ),
        "qnm_axes": list(QNM_AXES),
        "coefficient_vector": coefficients,
        "grid": rows,
        "qnm_deformation_at_published_bound": coefficients,
        "dqnm_deformation_d_ell_at_published_bound": {
            axis: coefficient * bound_gamma_prime
            for axis, coefficient in coefficients.items()
        },
        "engine_axis_map_ready": False,
    })


def qeft_qnm_source_axis_deformation_jacobian(
    v2196_path: Path = DEFAULT_V2196_PATH,
) -> dict[str, Any]:
    v2196 = load_json(v2196_path)
    source_surrogates = v2196["published_bound_surrogate"]["surrogates"]
    rows = [qnm_deformation_rows_for_surrogate(row) for row in source_surrogates]
    return canonicalize_json_floats({
        "bridge_id": "parspec_qeft_qnm_source_axis_deformation_jacobian_v1",
        "basis_surrogate_version": v2196["version"],
        "source_events": list(SOURCE_EVENTS),
        "source_axis": "ell_qEFT_km",
        "qeft_power": QEFT_POWER,
        "qnm_axes": list(QNM_AXES),
        "engine_axes": list(ENGINE_AXES),
        "qnm_coefficient_vector": qeft_qnm_coefficient_vector(),
        "event_deformation_rows": rows,
        "source_space_jacobian_ready": True,
        "engine_axis_map_ready": False,
        "engine_axis_map_blocker": (
            "qnm_deformation_to_bresciani_engine_r4_operator_basis_map_missing"
        ),
        "claim_use_allowed": False,
    })


def evaluate_qnm_deformation_jacobian(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = result or diagnose_r4_parspec_qnm_deformation_jacobian()
    bridge = result["qnm_deformation_jacobian"]
    blockers: set[str] = set()

    if bridge.get("source_space_jacobian_ready") is not True:
        blockers.add("source_space_jacobian_not_ready")
    if bridge.get("engine_axis_map_ready") is not False:
        blockers.add("engine_axis_map_unexpectedly_ready")
    if bridge.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")
    if tuple(bridge.get("qnm_axes", [])) != QNM_AXES:
        blockers.add("qnm_axes_mismatch")
    if tuple(bridge.get("engine_axes", [])) != ENGINE_AXES:
        blockers.add("engine_axes_mismatch")
    coefficients = bridge.get("qnm_coefficient_vector", {})
    if set(coefficients) != set(QNM_AXES):
        blockers.add("qnm_coefficient_vector_incomplete")

    for row in bridge.get("event_deformation_rows", []):
        label = row.get("label", "unknown")
        if row.get("engine_axis_map_ready") is not False:
            blockers.add(f"{label}_engine_axis_map_unexpectedly_ready")
        upper_bound = float(row.get("upper_bound_km_90", 0.0))
        if upper_bound <= 0:
            blockers.add(f"{label}_upper_bound_invalid")
            continue
        bound_row = next(
            (
                point for point in row.get("grid", [])
                if math.isclose(
                    float(point.get("fraction_of_published_bound", -1.0)),
                    1.0,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
            ),
            None,
        )
        if not bound_row:
            blockers.add(f"{label}_published_bound_grid_point_missing")
            continue
        if not math.isclose(
            float(bound_row.get("normalized_gamma", -1.0)),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            blockers.add(f"{label}_published_bound_gamma_not_one")
        for axis, coefficient in coefficients.items():
            value = bound_row["qnm_deformation"].get(axis)
            if not math.isclose(
                float(value),
                float(coefficient),
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                blockers.add(f"{label}_{axis}_bound_deformation_mismatch")

    claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_operator_basis_map_missing",
        "engine_axis_orientation_missing",
        "axis_normalization_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if blockers:
        claim_blockers.add("qnm_source_axis_jacobian_not_ready")

    return canonicalize_json_floats({
        "qnm_source_axis_jacobian_ready": not blockers,
        "engine_axis_map_ready": False,
        "ready_for_framework_claim": False,
        "jacobian_blockers": sorted(blockers),
        "resolved_v2196_subpiece": (
            "qeft_source_axis_to_qnm_deformation_jacobian"
            if not blockers else None
        ),
        "remaining_claim_blockers": sorted(claim_blockers),
        "claim_blockers": sorted(claim_blockers),
        "claimable_framework_exclusions_now": [],
        "route_status": (
            "parspec_qnm_deformation_jacobian_ready_engine_axis_map_missing"
            if not blockers
            else "parspec_qnm_deformation_jacobian_not_ready"
        ),
    })


def malformed_qnm_deformation_jacobian(
    v2196_path: Path = DEFAULT_V2196_PATH,
) -> dict[str, Any]:
    result = base_qnm_deformation_jacobian_result(v2196_path)
    bridge = result["qnm_deformation_jacobian"]
    bridge["engine_axis_map_ready"] = True
    bridge["claim_use_allowed"] = True
    first = bridge["event_deformation_rows"][0]
    first["grid"][4]["normalized_gamma"] = 0.5
    return result


def base_qnm_deformation_jacobian_result(
    v2196_path: Path = DEFAULT_V2196_PATH,
) -> dict[str, Any]:
    v2196 = load_json(v2196_path)
    bridge = qeft_qnm_source_axis_deformation_jacobian(v2196_path)
    return {
        "version": VERSION,
        "basis": [
            "v2.191_qeft_qnm_deformation_coefficients",
            "v2.196_published_bound_surrogate",
            "normalized_ell_qeft_power_six_source_axis",
        ],
        "v2196_route_status": v2196["route_status"],
        "published_bound_surrogate_ready": v2196[
            "published_bound_surrogate_ready"
        ],
        "qnm_deformation_jacobian": bridge,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_qnm_deformation_to_bresciani_engine_r4_operator_basis_map"
        ),
        "interpretation": (
            "The qEFT source-axis route now has a checked pushforward from "
            "ell_qEFT into ParSpec qNM deformation coordinates. This is still "
            "not an engine-axis map: the missing operator-basis map from qNM "
            "deformations to Bresciani R4 axes remains the decisive blocker."
        ),
    }


def diagnose_r4_parspec_qnm_deformation_jacobian(
    *,
    v2196_path: Path = DEFAULT_V2196_PATH,
) -> dict[str, Any]:
    result = base_qnm_deformation_jacobian_result(v2196_path)
    evaluation = evaluate_qnm_deformation_jacobian(result)
    malformed = evaluate_qnm_deformation_jacobian(
        malformed_qnm_deformation_jacobian(v2196_path)
    )
    result["evaluation"] = evaluation
    result["malformed_control_evaluation"] = malformed
    result["qnm_source_axis_jacobian_ready"] = evaluation[
        "qnm_source_axis_jacobian_ready"
    ]
    result["route_status"] = evaluation["route_status"]
    return canonicalize_json_floats(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2196", default=str(DEFAULT_V2196_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_qnm_deformation_jacobian(
        v2196_path=Path(args.v2196)
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
