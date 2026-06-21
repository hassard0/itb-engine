"""Continuity ledger for the v2.190-v2.197 R4 ParSpec research loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_ringdown_source_bridge import load_json


VERSION = "v2.198"
DEFAULT_OUT = Path(
    "experiments/results/v2.198/r4_parspec_continuity_ledger.json"
)
EXPECTED_VERSIONS = tuple(f"v2.{minor}" for minor in range(190, 198))

PARSPEC_RUNS: tuple[dict[str, Any], ...] = (
    {
        "version": "v2.190",
        "short_title": "R4 ParSpec engine-axis map contract",
        "note_path": (
            "docs/results/2026-06-20-v2.190-"
            "r4-parspec-engine-axis-map-contract.md"
        ),
        "artifact_path": (
            "experiments/results/v2.190/"
            "r4_parspec_engine_axis_map_contract.json"
        ),
        "retained_details": [
            "source axis ell_qEFT_km is separated from engine R4 axes",
            "target engine axes are g_R4_c1, g_R4_c2, and g_R4_c3",
            "required packet fields include source-axis power, basis map, "
            "engine-axis orientation, normalization, public likelihood, "
            "event policy, systematics, and claim controls",
            "current v2.188 bridge fails the map and likelihood attachment",
            "claim controls remain disabled",
        ],
        "frontier_change": (
            "Converted the missing ell_qEFT-to-engine-axis map into an "
            "executable contract."
        ),
        "remaining_blocker": "source_backed_qeft_to_engine_r4_axis_map_missing",
    },
    {
        "version": "v2.191",
        "short_title": "R4 ParSpec qEFT source-asset audit",
        "note_path": (
            "docs/results/2026-06-20-v2.191-"
            "r4-parspec-qeft-source-asset-audit.md"
        ),
        "artifact_path": (
            "experiments/results/v2.191/"
            "r4_parspec_qeft_source_asset_audit.json"
        ),
        "retained_details": [
            "arXiv source package hash is preserved",
            "paper_alt_theory_bounds.tex hash is preserved",
            "qEFT source-axis power is p_qEFT = 6",
            "qNM deformation coefficients are preserved for nmax 0 and 1",
            "GW150914, GW200129, and combined qEFT bounds are preserved",
            "no machine-readable qEFT likelihood asset is present",
        ],
        "frontier_change": (
            "Resolved the source-axis power subpiece while leaving the "
            "operator-basis and public-likelihood blockers active."
        ),
        "remaining_blocker": "operator_basis_map_and_public_likelihood_missing",
    },
    {
        "version": "v2.192",
        "short_title": "R4 ParSpec source-event alignment manifest",
        "note_path": (
            "docs/results/2026-06-20-v2.192-"
            "r4-parspec-source-event-alignment-manifest.md"
        ),
        "artifact_path": (
            "experiments/results/v2.192/"
            "r4_parspec_source_event_alignment_manifest.json"
        ),
        "retained_details": [
            "GW150914 maps to GW150914-v3 in GWTC-1-confident",
            "GW200129 maps to GW200129_065458-v1 in GWTC-3-confident",
            "public HDF5 strain URLs are recorded for 32 s and 4096 s data",
            "GW150914 uses H1/L1 topology",
            "GW200129 requires H1/L1/V1 topology",
            "event discovery is resolved but the likelihood rerun is not yet",
        ],
        "frontier_change": (
            "Resolved public GWOSC event-version and strain-handle discovery "
            "for the ParSpec source events."
        ),
        "remaining_blocker": "same_event_likelihood_and_v1_policy_missing",
    },
    {
        "version": "v2.193",
        "short_title": "R4 ParSpec same-event H1/L1 likelihood",
        "note_path": (
            "docs/results/2026-06-20-v2.193-"
            "r4-parspec-same-event-h1l1-likelihood.md"
        ),
        "artifact_path": (
            "experiments/results/v2.193/"
            "r4_parspec_same_event_h1l1_likelihood.json"
        ),
        "retained_details": [
            "GW150914 and GW200129 are rerun on public source-event strain",
            "the rerun uses H1/L1 only for both events",
            "the coefficient grid has 125 points",
            "event slicing is event-GPS-aware",
            "posterior means are preserved per source event",
            "GW200129 V1 remains outside this artifact",
        ],
        "frontier_change": "Closed the H1/L1 same-event rerun subpiece.",
        "remaining_blocker": "gw200129_v1_detector_response_missing",
    },
    {
        "version": "v2.194",
        "short_title": "R4 ParSpec event-topology likelihood",
        "note_path": (
            "docs/results/2026-06-20-v2.194-"
            "r4-parspec-event-topology-likelihood.md"
        ),
        "artifact_path": (
            "experiments/results/v2.194/"
            "r4_parspec_event_topology_likelihood.json"
        ),
        "retained_details": [
            "GW150914 uses H1/L1",
            "GW200129 uses H1/L1/V1",
            "event-time LALSuite antenna response moments are exported",
            "V1 detector response is included for GW200129",
            "source-event network likelihoods are preserved",
            "source-event covariance is still not exported here",
        ],
        "frontier_change": "Closed the public detector-topology subpiece.",
        "remaining_blocker": "source_event_specific_nuisance_covariance_missing",
    },
    {
        "version": "v2.195",
        "short_title": "R4 ParSpec source-event covariance export",
        "note_path": (
            "docs/results/2026-06-20-v2.195-"
            "r4-parspec-source-event-covariance-export.md"
        ),
        "artifact_path": (
            "experiments/results/v2.195/"
            "r4_parspec_source_event_covariance_export.json"
        ),
        "retained_details": [
            "event-specific covariance is exported for GW150914",
            "event-specific covariance is exported for GW200129",
            "combined GW150914/GW200129 covariance is exported",
            "nuisance parameters remain total mass, eta, tc shift, and phase",
            "the grid is coarse and not a posterior sampler",
            "public ParSpec likelihood and engine-axis map remain missing",
        ],
        "frontier_change": "Closed the source-event covariance export subpiece.",
        "remaining_blocker": "parspec_public_likelihood_or_axis_map_missing",
    },
    {
        "version": "v2.196",
        "short_title": "R4 ParSpec published-bound surrogate",
        "note_path": (
            "docs/results/2026-06-20-v2.196-"
            "r4-parspec-published-bound-surrogate.md"
        ),
        "artifact_path": (
            "experiments/results/v2.196/"
            "r4_parspec_published_bound_surrogate.json"
        ),
        "retained_details": [
            "GW150914 qEFT bound is 51.7 km at 90 percent",
            "GW200129 qEFT bound is 54.8 km at 90 percent",
            "combined qEFT bound is 51.3 km at 90 percent",
            "half-normal surrogate parameters are exported",
            "event-set mismatch and source-axis mismatch are removed",
            "the surrogate is not a public posterior or likelihood object",
        ],
        "frontier_change": (
            "Attached published qEFT bounds as a nonclaiming event-aligned "
            "source-axis surrogate."
        ),
        "remaining_blocker": "public_likelihood_and_engine_axis_map_missing",
    },
    {
        "version": "v2.197",
        "short_title": "R4 ParSpec qNM deformation Jacobian",
        "note_path": (
            "docs/results/2026-06-20-v2.197-"
            "r4-parspec-qnm-deformation-jacobian.md"
        ),
        "artifact_path": (
            "experiments/results/v2.197/"
            "r4_parspec_qnm_deformation_jacobian.json"
        ),
        "retained_details": [
            "ell_qEFT is pushed into source-space qNM deformation coordinates",
            "normalized gamma uses the sixth power of ell_qEFT over bound",
            "qEFT qNM coefficients from v2.191 are preserved",
            "Jacobian rows are exported for GW150914, GW200129, and combined",
            "absolute gamma normalization still needs remnant mass and redshift",
            "qNM-to-Bresciani R4 operator map remains the decisive blocker",
        ],
        "frontier_change": "Closed the source-space qNM deformation subpiece.",
        "remaining_blocker": "qnm_to_bresciani_engine_r4_operator_map_missing",
    },
)


def _path_status(run: dict[str, Any]) -> dict[str, bool]:
    artifact_path = run.get("artifact_path")
    return {
        "note_exists": Path(run["note_path"]).exists(),
        "artifact_expected": artifact_path is not None,
        "artifact_exists": (
            Path(artifact_path).exists() if artifact_path is not None else True
        ),
    }


def _base_digest(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": artifact.get("version"),
        "route_status": artifact.get("route_status"),
        "ready_for_framework_claim": artifact.get("ready_for_framework_claim"),
        "claimable_framework_exclusions_now": artifact.get(
            "claimable_framework_exclusions_now"
        ),
        "selected_next_build_action": artifact.get("selected_next_build_action"),
    }


def _event_network_digest(event: dict[str, Any]) -> dict[str, Any]:
    network = event["network_likelihood"]
    posterior = network["posterior"]
    return {
        "paper_event": event["paper_event"],
        "event_version": event["event_version"],
        "detectors": event["detectors"],
        "grid_points": network["grid_points"],
        "nuisance_points_per_detector": network["nuisance_points_per_detector"],
        "posterior_mean": posterior["posterior_mean"],
        "posterior_covariance_eigenvalues": posterior.get(
            "posterior_covariance_eigenvalues"
        ),
        "maximum_posterior_grid_point": posterior[
            "maximum_posterior_grid_point"
        ],
    }


def _response_digest(event: dict[str, Any]) -> dict[str, Any]:
    responses = event.get("detector_channel_responses", {})
    return {
        detector: {
            "K_plus": response["K_plus"],
            "Re_K_minus": response["Re_K_minus"],
            "Im_K_minus": response["Im_K_minus"],
            "event_gmst": response["event_gmst"],
            "sample_count": response["grid"]["sample_count"],
        }
        for detector, response in responses.items()
    }


def _covariance_digest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "paper_event": row["paper_event"],
        "event_version": row["event_version"],
        "detectors": row["detectors"],
        "grid_points": row["grid_points"],
        "nuisance_points_per_detector": row["nuisance_points_per_detector"],
        "posterior_mean": row["posterior_mean"],
        "posterior_covariance_eigenvalues": row[
            "posterior_covariance_eigenvalues"
        ],
        "best_marginal_grid_point": row["best_marginal_grid_point"],
    }


def _artifact_digest(run: dict[str, Any]) -> dict[str, Any]:
    artifact_path = run.get("artifact_path")
    if artifact_path is None or not Path(artifact_path).exists():
        return {}

    artifact = load_json(artifact_path)
    digest = _base_digest(artifact)
    version = run["version"]

    if version == "v2.190":
        contract = artifact["contract"]
        current = artifact["current_v2188_evaluation"]
        digest.update({
            "contract_id": contract["contract_id"],
            "source_axis": contract["source_axis"],
            "target_engine_axes": contract["target_engine_axes"],
            "required_packet_fields": contract["required_packet_fields"],
            "current_missing_required_fields": current["missing_required_fields"],
            "current_map_blockers": current["map_blockers"],
            "current_attachment_blockers": current["attachment_blockers"],
            "split_v2_188_axis_map_blocker": current[
                "split_v2_188_axis_map_blocker"
            ],
        })
    elif version == "v2.191":
        assets = artifact["source_package_assets"]
        facts = artifact["source_equation_facts"]
        digest.update({
            "source_package_sha256": assets["source_package_tarball"][
                "sha256"
            ],
            "audited_assets": assets["audited_assets"],
            "machine_readable_likelihood_ready": assets[
                "machine_readable_likelihood_ready"
            ],
            "qeft_power": facts["parspec_gamma_relation"]["qeft_power"],
            "qnm_deformation_coefficients": facts[
                "qnm_deformation_coefficients"
            ],
            "event_bounds_90_credible_km": facts[
                "event_bounds_90_credible_km"
            ],
            "source_asset_readiness": artifact["source_asset_readiness"],
            "remaining_contract_blockers": artifact[
                "remaining_contract_blockers_after_asset_audit"
            ],
        })
    elif version == "v2.192":
        summary = artifact["source_event_manifest_summary"]
        digest.update({
            "events": [
                {
                    "paper_event": row["paper_event"],
                    "event_version": row["event_version"],
                    "catalog": row["catalog"],
                    "run": row["run"],
                    "gps": row["gps"],
                    "doi": row["doi"],
                    "detectors": row["detectors"],
                    "event_version_url": row["event_version_url"],
                }
                for row in summary["events"]
            ],
            "strain_record_count": len(summary["strain_records"]),
            "detector_topology_by_event": summary["detector_topology_by_event"],
            "gw200129_requires_v1_policy": summary[
                "gw200129_requires_v1_policy"
            ],
            "source_event_public_strain_urls_ready": summary[
                "source_event_public_strain_urls_ready"
            ],
            "alignment_blockers": artifact["evaluation"]["alignment_blockers"],
        })
    elif version in {"v2.193", "v2.194"}:
        digest.update({
            "central_values": artifact["central_values"],
            "coefficient_grid": artifact["coefficient_grid"],
            "event_networks": [
                _event_network_digest(event)
                for event in artifact["event_likelihoods"]
            ],
            "claim_blockers": artifact["evaluation"]["claim_blockers"],
        })
        if version == "v2.194":
            digest["detector_channel_responses"] = {
                event["paper_event"]: _response_digest(event)
                for event in artifact["event_likelihoods"]
            }
            digest["split_v2193_v1_blocker"] = artifact["evaluation"][
                "split_v2193_v1_blocker"
            ]
    elif version == "v2.195":
        export = artifact["source_event_covariance_export"]
        combined = export["combined_event_set_covariance"]
        digest.update({
            "event_covariances": [
                _covariance_digest(row) for row in export["event_covariances"]
            ],
            "combined_event_set_covariance": {
                "source_events": combined["source_events"],
                "detectors_by_event": combined["detectors_by_event"],
                "grid_points": combined["grid_points"],
                "posterior_mean": combined["posterior_mean"],
                "posterior_covariance_eigenvalues": combined[
                    "posterior_covariance_eigenvalues"
                ],
                "best_marginal_grid_point": combined[
                    "best_marginal_grid_point"
                ],
            },
            "remaining_claim_blockers": artifact["evaluation"][
                "remaining_claim_blockers"
            ],
        })
    elif version == "v2.196":
        surrogate = artifact["published_bound_surrogate"]
        digest.update({
            "surrogates": [
                {
                    "label": row["label"],
                    "upper_bound_km_90": row["upper_bound_km_90"],
                    "half_normal_sigma_km": row["half_normal_sigma_km"],
                    "variance_km2": row["variance_km2"],
                    "claim_use_allowed": row["claim_use_allowed"],
                }
                for row in surrogate["surrogates"]
            ],
            "machine_readable_public_likelihood_ready": artifact[
                "evaluation"
            ]["machine_readable_public_likelihood_ready"],
            "resolved_v2191_attachment_blockers": artifact["evaluation"][
                "resolved_v2191_attachment_blockers"
            ],
            "remaining_packet_blockers": artifact["evaluation"][
                "remaining_packet_blockers"
            ],
        })
    elif version == "v2.197":
        bridge = artifact["qnm_deformation_jacobian"]
        digest.update({
            "qeft_power": bridge["qeft_power"],
            "qnm_axes": bridge["qnm_axes"],
            "engine_axes": bridge["engine_axes"],
            "qnm_coefficient_vector": bridge["qnm_coefficient_vector"],
            "event_deformation_rows": [
                {
                    "label": row["label"],
                    "upper_bound_km_90": row["upper_bound_km_90"],
                    "normalization": row["normalization"],
                    "dqnm_deformation_d_ell_at_published_bound": row[
                        "dqnm_deformation_d_ell_at_published_bound"
                    ],
                    "engine_axis_map_ready": row["engine_axis_map_ready"],
                }
                for row in bridge["event_deformation_rows"]
            ],
            "source_space_jacobian_ready": bridge[
                "source_space_jacobian_ready"
            ],
            "engine_axis_map_ready": bridge["engine_axis_map_ready"],
            "remaining_claim_blockers": artifact["evaluation"][
                "remaining_claim_blockers"
            ],
        })

    return canonicalize_json_floats(digest)


def r4_parspec_continuity_ledger() -> dict[str, Any]:
    run_rows = []
    for run in PARSPEC_RUNS:
        row = dict(run)
        row["path_status"] = _path_status(run)
        row["artifact_digest"] = _artifact_digest(run)
        run_rows.append(row)

    missing_note_versions = [
        row["version"] for row in run_rows if not row["path_status"]["note_exists"]
    ]
    missing_artifact_versions = [
        row["version"]
        for row in run_rows
        if not row["path_status"]["artifact_exists"]
    ]
    missing_detail_versions = [
        row["version"] for row in run_rows if not row["retained_details"]
    ]
    claim_gate_violations = [
        row["version"]
        for row in run_rows
        if row["artifact_digest"].get("ready_for_framework_claim") is not False
        or row["artifact_digest"].get("claimable_framework_exclusions_now") != []
    ]
    versions = tuple(row["version"] for row in run_rows)
    latest_digest = run_rows[-1]["artifact_digest"]
    ledger_ready = not (
        missing_note_versions
        or missing_artifact_versions
        or missing_detail_versions
        or claim_gate_violations
        or versions != EXPECTED_VERSIONS
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "purpose": (
            "Preserve the details from the v2.190-v2.197 R4/ParSpec source "
            "event, published-bound, and qNM-deformation loop so top-level "
            "writeups, findings, and reports do not flatten the run history."
        ),
        "covered_versions": list(versions),
        "expected_versions": list(EXPECTED_VERSIONS),
        "run_count": len(run_rows),
        "runs": run_rows,
        "evaluation": {
            "continuity_ledger_ready": ledger_ready,
            "version_sequence_complete": versions == EXPECTED_VERSIONS,
            "missing_note_versions": missing_note_versions,
            "missing_artifact_versions": missing_artifact_versions,
            "missing_detail_versions": missing_detail_versions,
            "claim_gate_violations": claim_gate_violations,
            "retained_detail_count": sum(
                len(row["retained_details"]) for row in run_rows
            ),
            "claim_boundary_preserved": not claim_gate_violations,
        },
        "latest_preserved_route_status": latest_digest["route_status"],
        "latest_remaining_claim_blockers": latest_digest[
            "remaining_claim_blockers"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": (
            "r4_parspec_continuity_ledger_ready_nonclaiming"
            if ledger_ready
            else "r4_parspec_continuity_ledger_blocked"
        ),
        "selected_next_build_action": (
            "continue_with_qnm_to_bresciani_operator_map_or_public_likelihood"
        ),
        "best_next_artifact": (
            "A source-backed qNM-deformation to Bresciani R4 operator-basis "
            "map, a machine-readable public ParSpec/qEFT likelihood packet, "
            "or absolute gamma normalization metadata."
        ),
        "interpretation": (
            "This is a documentation and reproducibility artifact. It adds no "
            "new physics claim; it protects the precise ParSpec route state "
            "for future writeups and keeps the claim boundary closed."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = r4_parspec_continuity_ledger()
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
