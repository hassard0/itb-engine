"""Source-event covariance export from the ParSpec event-topology likelihood."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_lalsuite_waveform_likelihood_posterior import (
    AXES,
    GRID_OFFSETS,
    posterior_summary_from_grid,
)
from experiments.r4_nuisance_covariance_export import REFERENCE_NUISANCE, load_json
from experiments.r4_parspec_event_topology_likelihood import (
    DEFAULT_OUT as DEFAULT_V2194_PATH,
)
from experiments.r4_parspec_qeft_source_asset_audit import DEFAULT_OUT as DEFAULT_V2191_PATH
from experiments.r4_parspec_ringdown_source_bridge import SOURCE_EVENTS


VERSION = "v2.195"
DEFAULT_OUT = Path(
    "experiments/results/v2.195/r4_parspec_source_event_covariance_export.json"
)
CLAIM_GRADE_REMAINING_BLOCKERS = (
    "public_parspec_qeft_likelihood_or_posterior_samples_missing",
    "operator_basis_map_missing",
    "engine_axis_orientation_missing",
    "axis_normalization_missing",
    "nuisance_grid_is_coarse_not_posterior_sampler",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def source_event_covariance_rows(
    event_topology_likelihood: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = []
    for event in event_topology_likelihood["event_likelihoods"]:
        network = event["network_likelihood"]
        posterior = network["posterior"]
        covariance = np.asarray(posterior["posterior_covariance"], dtype=float)
        eigenvalues = np.linalg.eigvalsh(covariance)
        rows.append({
            "paper_event": event["paper_event"],
            "gwosc_event_name": event["gwosc_event_name"],
            "event_version": event["event_version"],
            "detectors": event["detectors"],
            "axes": list(AXES),
            "grid_points": int(network["grid_points"]),
            "nuisance_points_per_detector": network[
                "nuisance_points_per_detector"
            ],
            "nuisance_grid": {
                "parameters": list(REFERENCE_NUISANCE),
                "grid_is_posterior_sampler": False,
            },
            "best_marginal_grid_point": network["best_marginal_grid_point"],
            "posterior_mean": posterior["posterior_mean"],
            "posterior_covariance": posterior["posterior_covariance"],
            "posterior_covariance_eigenvalues": eigenvalues.tolist(),
            "posterior_positive_semidefinite": bool(
                np.all(eigenvalues >= -1.0e-14)
            ),
            "top_posterior_points": posterior["top_posterior_points"],
        })
    return canonicalize_json_floats(rows)


def combined_event_set_grid(
    event_topology_likelihood: dict[str, Any],
) -> list[dict[str, float]]:
    event_grids = [
        event["network_likelihood"]["posterior"]["grid"]
        for event in event_topology_likelihood["event_likelihoods"]
    ]
    if not event_grids:
        return []
    lookups = [
        {
            tuple(row[axis] for axis in AXES): row
            for row in grid
        }
        for grid in event_grids
    ]
    first_keys = list(lookups[0])
    rows = []
    for key in first_keys:
        combined = {axis: float(value) for axis, value in zip(AXES, key, strict=True)}
        for axis in AXES:
            combined[f"delta_{axis}"] = float(lookups[0][key][f"delta_{axis}"])
        combined["log_marginal_likelihood"] = float(
            sum(lookup[key]["log_marginal_likelihood"] for lookup in lookups)
        )
        combined["profile_log_likelihood"] = float(
            sum(lookup[key]["profile_log_likelihood"] for lookup in lookups)
        )
        rows.append(combined)
    return canonicalize_json_floats(rows)


def combined_event_set_covariance(
    event_topology_likelihood: dict[str, Any],
) -> dict[str, Any]:
    grid = combined_event_set_grid(event_topology_likelihood)
    posterior = posterior_summary_from_grid(grid)
    covariance = np.asarray(posterior["posterior_covariance"], dtype=float)
    eigenvalues = np.linalg.eigvalsh(covariance)
    detectors_by_event = {
        event["paper_event"]: event["detectors"]
        for event in event_topology_likelihood["event_likelihoods"]
    }
    return canonicalize_json_floats({
        "covariance_kind": (
            "combined_source_event_nuisance_marginalized_r4_likelihood_covariance"
        ),
        "source_events": list(SOURCE_EVENTS),
        "detectors_by_event": detectors_by_event,
        "axes": list(AXES),
        "grid_points": len(grid),
        "nuisance_grid": {
            "parameters": list(REFERENCE_NUISANCE),
            "grid_is_posterior_sampler": False,
        },
        "best_marginal_grid_point": max(
            grid,
            key=lambda row: row["log_marginal_likelihood"],
        ),
        "posterior_mean": posterior["posterior_mean"],
        "posterior_covariance": posterior["posterior_covariance"],
        "posterior_covariance_eigenvalues": eigenvalues.tolist(),
        "posterior_positive_semidefinite": bool(np.all(eigenvalues >= -1.0e-14)),
        "top_posterior_points": posterior["top_posterior_points"],
    })


def source_event_covariance_export(
    event_topology_likelihood: dict[str, Any],
) -> dict[str, Any]:
    event_rows = source_event_covariance_rows(event_topology_likelihood)
    combined = combined_event_set_covariance(event_topology_likelihood)
    return canonicalize_json_floats({
        "export_id": "r4_parspec_source_event_covariance_export_v1",
        "covariance_kind": (
            "source_event_nuisance_marginalized_r4_likelihood_covariance"
        ),
        "basis_likelihood_version": event_topology_likelihood["version"],
        "source_events": list(SOURCE_EVENTS),
        "axes": list(AXES),
        "coefficient_grid": {
            "offsets": list(GRID_OFFSETS),
            "grid_points": len(GRID_OFFSETS) ** len(AXES),
        },
        "event_covariances": event_rows,
        "combined_event_set_covariance": combined,
    })


def evaluate_source_event_covariance_export(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = result or diagnose_r4_parspec_source_event_covariance_export()
    likelihood = result["source_event_topology_likelihood"]
    export = result["source_event_covariance_export"]
    blockers: set[str] = set()
    if likelihood.get("source_event_detector_topology_likelihood_ready") is not True:
        blockers.add("v2_194_event_topology_likelihood_not_ready")
    if tuple(export.get("source_events", [])) != SOURCE_EVENTS:
        blockers.add("source_event_covariance_events_not_parspec_source_events")
    event_rows = export.get("event_covariances", [])
    if tuple(row.get("paper_event") for row in event_rows) != SOURCE_EVENTS:
        blockers.add("event_covariance_rows_not_exact_parspec_events")
    for row in event_rows:
        event = row.get("paper_event", "unknown_event")
        if int(row.get("grid_points", 0)) != len(GRID_OFFSETS) ** len(AXES):
            blockers.add(f"{event}_covariance_grid_missing")
        if row.get("posterior_positive_semidefinite") is not True:
            blockers.add(f"{event}_covariance_not_psd")
        if row.get("nuisance_grid", {}).get("grid_is_posterior_sampler") is not False:
            blockers.add(f"{event}_nuisance_grid_sampler_flag_unexpected")
        covariance = np.asarray(row.get("posterior_covariance", []), dtype=float)
        if covariance.shape != (len(AXES), len(AXES)):
            blockers.add(f"{event}_covariance_shape_unexpected")
    combined = export.get("combined_event_set_covariance", {})
    if int(combined.get("grid_points", 0)) != len(GRID_OFFSETS) ** len(AXES):
        blockers.add("combined_event_set_covariance_grid_missing")
    if combined.get("posterior_positive_semidefinite") is not True:
        blockers.add("combined_event_set_covariance_not_psd")

    claim_blockers = set(CLAIM_GRADE_REMAINING_BLOCKERS)
    if blockers:
        claim_blockers.add("source_event_specific_nuisance_covariance_export_not_ready")
    return canonicalize_json_floats({
        "source_event_specific_nuisance_covariance_export_ready": not blockers,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "export_blockers": sorted(blockers),
        "removed_v2_194_blocker": (
            "source_event_specific_nuisance_covariance_export_missing"
            if not blockers else None
        ),
        "remaining_claim_blockers": sorted(claim_blockers),
        "claim_blockers": sorted(claim_blockers),
        "route_status": (
            "parspec_source_event_covariance_export_ready_axis_map_missing"
            if not blockers
            else "parspec_source_event_covariance_export_not_ready"
        ),
    })


def malformed_source_event_covariance_export(
    v2194_path: Path = DEFAULT_V2194_PATH,
) -> dict[str, Any]:
    likelihood = load_json(v2194_path)
    result = {
        "source_event_topology_likelihood": {
            "version": likelihood["version"],
            "route_status": likelihood["route_status"],
            "source_event_detector_topology_likelihood_ready": likelihood[
                "source_event_detector_topology_likelihood_ready"
            ],
            "event_set_alignment_ready": likelihood["event_set_alignment_ready"],
            "claim_blockers": likelihood["evaluation"]["claim_blockers"],
        },
        "source_event_covariance_export": source_event_covariance_export(
            likelihood
        ),
    }
    export = result["source_event_covariance_export"]
    export["event_covariances"][0]["posterior_positive_semidefinite"] = False
    export["event_covariances"][0]["posterior_covariance"] = [[1.0]]
    export["combined_event_set_covariance"]["grid_points"] = 1
    return result


def diagnose_r4_parspec_source_event_covariance_export(
    *,
    v2194_path: Path = DEFAULT_V2194_PATH,
    v2191_path: Path = DEFAULT_V2191_PATH,
) -> dict[str, Any]:
    likelihood = load_json(v2194_path)
    v2191 = load_json(v2191_path)
    export = source_event_covariance_export(likelihood)
    result = {
        "version": VERSION,
        "basis": [
            "v2.194_r4_parspec_event_topology_likelihood",
            "v2.191_r4_parspec_qeft_source_asset_audit",
            "coarse_nuisance_marginalized_r4_likelihood_grid",
        ],
        "v2194_event_topology_likelihood_path": Path(v2194_path).as_posix(),
        "source_event_topology_likelihood": {
            "version": likelihood["version"],
            "route_status": likelihood["route_status"],
            "source_event_detector_topology_likelihood_ready": likelihood[
                "source_event_detector_topology_likelihood_ready"
            ],
            "event_set_alignment_ready": likelihood["event_set_alignment_ready"],
            "claim_blockers": likelihood["evaluation"]["claim_blockers"],
        },
        "source_event_covariance_export": export,
        "v2191_remaining_state": {
            "route_status": v2191["route_status"],
            "remaining_contract_blockers_after_asset_audit": v2191[
                "remaining_contract_blockers_after_asset_audit"
            ],
        },
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "attach_public_parspec_qeft_likelihood_or_axis_map"
        ),
        "interpretation": (
            "The ParSpec source-event route now exports event-specific and "
            "combined R4 covariance from the actual v2.194 nuisance-marginalized "
            "likelihood grids. This removes the source-event covariance export "
            "subpiece, but it remains nonclaiming because the nuisance grid is "
            "coarse, no public ParSpec/qEFT likelihood samples are attached, "
            "and the source-backed qEFT-to-engine axis map is still missing."
        ),
    }
    evaluation = evaluate_source_event_covariance_export(result)
    malformed = evaluate_source_event_covariance_export(
        malformed_source_event_covariance_export(v2194_path)
    )
    result["evaluation"] = evaluation
    result["malformed_control_evaluation"] = malformed
    result["source_event_specific_nuisance_covariance_export_ready"] = evaluation[
        "source_event_specific_nuisance_covariance_export_ready"
    ]
    result["route_status"] = evaluation["route_status"]
    return canonicalize_json_floats(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2194", default=str(DEFAULT_V2194_PATH))
    parser.add_argument("--v2191", default=str(DEFAULT_V2191_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_source_event_covariance_export(
        v2194_path=Path(args.v2194),
        v2191_path=Path(args.v2191),
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
