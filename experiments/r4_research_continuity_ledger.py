"""Continuity ledger for the v2.170-v2.188 R4 research loop."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.189"
DEFAULT_OUT = Path(
    "experiments/results/v2.189/r4_research_continuity_ledger.json"
)
EXPECTED_VERSIONS = tuple(f"v2.{minor}" for minor in range(170, 189))

RECENT_RUNS: tuple[dict[str, Any], ...] = (
    {
        "version": "v2.170",
        "short_title": "R4 symbolic-scale resolution contract",
        "note_path": (
            "docs/results/2026-06-20-v2.170-"
            "r4-symbolic-scale-resolution-contract.md"
        ),
        "artifact_path": (
            "experiments/results/v2.170/"
            "r4_symbolic_scale_resolution_contract.json"
        ),
        "retained_details": [
            "strict source-backed numeric Lambda_R4 packet contract",
            "symbolic-only current policy remains nonclaiming",
            "claim controls must stay disabled until a real numeric scale exists",
        ],
        "frontier_change": (
            "Converted the unresolved R4 scale into an executable packet gate."
        ),
        "remaining_blocker": "source_backed_numeric_lambda_r4_policy_missing",
    },
    {
        "version": "v2.171",
        "short_title": "post R4-scale-contract frontier",
        "note_path": (
            "docs/results/2026-06-20-v2.171-"
            "post-r4-scale-contract-frontier.md"
        ),
        "artifact_path": (
            "experiments/results/v2.171/post_r4_scale_contract_frontier.json"
        ),
        "retained_details": [
            "R4 remains the top diagnostic route",
            "numeric Lambda_R4 is still source-blocked",
            "next useful work should attack an external likelihood packet",
        ],
        "frontier_change": "Ranked the post-contract R4 path against alternatives.",
        "remaining_blocker": "external_source_packet_required",
    },
    {
        "version": "v2.172",
        "short_title": "Weyl/G8 dual-likelihood contract",
        "note_path": (
            "docs/results/2026-06-20-v2.172-"
            "weyl-g8-dual-likelihood-contract.md"
        ),
        "artifact_path": (
            "experiments/results/v2.172/weyl_g8_dual_likelihood_contract.json"
        ),
        "retained_details": [
            "joint g_C plus g_8 likelihood contract",
            "cross-axis covariance is required",
            "synthetic controls prove the gate but do not count as evidence",
        ],
        "frontier_change": (
            "Made the parallel Weyl/G8 route a machine-checkable packet gate."
        ),
        "remaining_blocker": "real_joint_engine_gC_g8_likelihood_missing",
    },
    {
        "version": "v2.173",
        "short_title": "post Weyl/G8-contract frontier",
        "note_path": (
            "docs/results/2026-06-20-v2.173-"
            "post-weyl-g8-contract-frontier.md"
        ),
        "artifact_path": (
            "experiments/results/v2.173/post_weyl_g8_contract_frontier.json"
        ),
        "retained_details": [
            "Weyl/G8 is diagnostic-ready but evidence-blocked",
            "R4 remains the more actionable live-source route",
            "claimable framework exclusions remain empty",
        ],
        "frontier_change": "Kept both active frontiers scoped without promotion.",
        "remaining_blocker": "real_dual_likelihood_packet_missing",
    },
    {
        "version": "v2.174",
        "short_title": "R4 live-source acquisition queue",
        "note_path": (
            "docs/results/2026-06-20-v2.174-"
            "r4-live-source-acquisition-queue.md"
        ),
        "artifact_path": (
            "experiments/results/v2.174/r4_live_source_acquisition_queue.json"
        ),
        "retained_details": [
            "Bresciani-axis plus public-GWOSC reanalysis selected",
            "source candidates checked before implementation",
            "next action is a machine-readable Bresciani axis dictionary",
        ],
        "frontier_change": "Moved from abstract packet waiting to source acquisition.",
        "remaining_blocker": "bresciani_axis_dictionary_missing",
    },
    {
        "version": "v2.175",
        "short_title": "Bresciani R4 axis dictionary",
        "note_path": (
            "docs/results/2026-06-20-v2.175-"
            "bresciani-r4-axis-dictionary.md"
        ),
        "artifact_path": (
            "experiments/results/v2.175/bresciani_r4_axis_dictionary.json"
        ),
        "retained_details": [
            "K_plus maps into g_R4_c1",
            "Re(K_minus) maps into g_R4_c2",
            "Im(K_minus) maps into g_R4_c3",
            "derived axes g_R4_plus and g_R4_minus_abs are recorded",
        ],
        "frontier_change": "Made the R4 shape-axis map machine-readable.",
        "remaining_blocker": "public_likelihood_or_covariance_missing",
    },
    {
        "version": "v2.176",
        "short_title": "public-GW R4 reanalysis fixture",
        "note_path": (
            "docs/results/2026-06-20-v2.176-"
            "public-gw-r4-reanalysis-fixture.md"
        ),
        "artifact_path": (
            "experiments/results/v2.176/public_gw_r4_reanalysis_fixture.json"
        ),
        "retained_details": [
            "GW170608-v3 selected",
            "H1 and L1 public strain declarations recorded",
            "committed artifacts keep metadata while cache bytes stay ignored",
        ],
        "frontier_change": "Bound the R4 route to a public GWOSC event fixture.",
        "remaining_blocker": "real_hdf5_strain_loading_missing",
    },
    {
        "version": "v2.177",
        "short_title": "R4 LALSuite waveform response contract",
        "note_path": (
            "docs/results/2026-06-20-v2.177-"
            "r4-lalsuite-waveform-response-contract.md"
        ),
        "artifact_path": (
            "experiments/results/v2.177/"
            "r4_lalsuite_waveform_response_contract.json"
        ),
        "retained_details": [
            "waveform response fields required for LALSuite replacement",
            "synthetic response is explicitly nonclaiming",
            "merger-ringdown completion remains open",
        ],
        "frontier_change": "Specified the waveform-response gate before ingestion.",
        "remaining_blocker": "source_owned_r4_waveform_response_missing",
    },
    {
        "version": "v2.178",
        "short_title": "R4 response public-strain projection",
        "note_path": (
            "docs/results/2026-06-20-v2.178-"
            "r4-response-public-strain-projection.md"
        ),
        "artifact_path": (
            "experiments/results/v2.178/"
            "r4_response_public_strain_projection.json"
        ),
        "retained_details": [
            "public-strain projection path exercised",
            "synthetic rows remain separate from claim evidence",
            "HDF5 byte ingestion is the next required replacement",
        ],
        "frontier_change": "Connected the response contract to public strain rows.",
        "remaining_blocker": "real_hdf5_bytes_not_loaded",
    },
    {
        "version": "v2.179",
        "short_title": "R4 response GWOSC HDF5 projection",
        "note_path": (
            "docs/results/2026-06-20-v2.179-"
            "r4-response-gwosc-hdf5-projection.md"
        ),
        "artifact_path": (
            "experiments/results/v2.179/r4_response_gwosc_hdf5_projection.json"
        ),
        "retained_details": [
            "real GWOSC H1 and L1 32-second HDF5 files loaded",
            "GW170608 cache bytes are not committed",
            "metadata, hashes, and projections are committed",
        ],
        "frontier_change": "Replaced declared strain rows with real HDF5 ingestion.",
        "remaining_blocker": "source_backed_r4_response_shape_missing",
    },
    {
        "version": "v2.180",
        "short_title": "R4 source-backed PN/IMR derivation",
        "note_path": (
            "docs/results/2026-06-20-v2.180-"
            "r4-source-backed-pn-imr-derivation.md"
        ),
        "artifact_path": (
            "experiments/results/v2.180/r4_source_backed_pn_imr_derivation.json"
        ),
        "retained_details": [
            "5PN tidal phase scales as v_f^5",
            "7PN direct-bulk phase scales as v_f^9",
            "5PN tidal amplitude scales as v_f^10",
            "7PN direct-bulk amplitude scales as v_f^14",
            "flattened Bresciani channel basis has rank three",
        ],
        "frontier_change": "Replaced the response-shape ansatz with source-backed kernels.",
        "remaining_blocker": "detector_channel_response_not_calibrated",
    },
    {
        "version": "v2.181",
        "short_title": "R4 source-backed GWOSC projection",
        "note_path": (
            "docs/results/2026-06-20-v2.181-"
            "r4-source-backed-gwosc-projection.md"
        ),
        "artifact_path": (
            "experiments/results/v2.181/r4_source_backed_gwosc_projection.json"
        ),
        "retained_details": [
            "v2.180 source-backed kernels pushed through real GWOSC HDF5 data",
            "projection axes are g_R4_c1, g_R4_c2, and g_R4_c3",
            "detector channel is still a deterministic proxy",
        ],
        "frontier_change": "Produced the first source-backed GWOSC projection seed.",
        "remaining_blocker": "deterministic_detector_channel_proxy_used",
    },
    {
        "version": "v2.182",
        "short_title": "R4 Vulcan LALSuite runtime target",
        "note_path": (
            "docs/results/2026-06-20-v2.182-"
            "r4-vulcan-lalsuite-runtime-target.md"
        ),
        "artifact_path": (
            "experiments/results/v2.182/r4_vulcan_lalsuite_runtime_target.json"
        ),
        "retained_details": [
            "Vulcan imports LALSuite 7.7.1",
            "IMRPhenomD availability is true",
            "reference waveform covers 20.0 Hz to 111.25 Hz",
            "366 nonzero bins are generated",
        ],
        "frontier_change": "Cleared the remote runtime availability gate on Vulcan.",
        "remaining_blocker": "r4_modified_waveform_likelihood_missing",
    },
    {
        "version": "v2.183",
        "short_title": "R4 LALSuite detector-channel response",
        "note_path": (
            "docs/results/2026-06-20-v2.183-"
            "r4-lalsuite-detector-channel-response.md"
        ),
        "artifact_path": (
            "experiments/results/v2.183/"
            "r4_lalsuite_detector_channel_response.json"
        ),
        "retained_details": [
            "H1 K_plus=0.606542357541",
            "L1 K_plus=0.642279966479",
            "H1 and L1 Re/Im K_minus RMS targets are recorded",
            "sky-posterior marginalization is not yet performed",
        ],
        "frontier_change": "Replaced the immediate detector proxy target.",
        "remaining_blocker": "sky_posterior_marginalization_missing",
    },
    {
        "version": "v2.184",
        "short_title": "R4/GWOSC/LALSuite research report refresh",
        "note_path": (
            "docs/results/2026-06-20-v2.184-"
            "r4-gwosc-lalsuite-research-report.md"
        ),
        "artifact_path": None,
        "retained_details": [
            "v2.170-v2.183 narrative consolidated",
            "local validation reached 1377 passed and 7 skipped",
            "Vulcan validation reached 1384 passed with LALSuite installed",
            "claim boundary explicitly rejects framework exclusions",
        ],
        "frontier_change": "Created the first live-data frontier synthesis report.",
        "remaining_blocker": "calibrated_projection_and_covariance_followups_open",
    },
    {
        "version": "v2.185",
        "short_title": "R4 LALSuite-calibrated GWOSC projection",
        "note_path": (
            "docs/results/2026-06-20-v2.185-"
            "r4-lalsuite-calibrated-gwosc-projection.md"
        ),
        "artifact_path": (
            "experiments/results/v2.185/"
            "r4_lalsuite_calibrated_gwosc_projection.json"
        ),
        "retained_details": [
            "calibrated central g_R4_c1=0.495629103212",
            "calibrated central g_R4_c2=0.495614794648",
            "calibrated central g_R4_c3=-0.003513023764",
            "JSON hash matched across Windows and Vulcan",
        ],
        "frontier_change": "Replaced the v2.181 detector proxy in the real projection.",
        "remaining_blocker": "nuisance_marginalized_covariance_not_exported",
    },
    {
        "version": "v2.186",
        "short_title": "R4 nuisance covariance export",
        "note_path": (
            "docs/results/2026-06-20-v2.186-"
            "r4-nuisance-covariance-export.md"
        ),
        "artifact_path": (
            "experiments/results/v2.186/r4_nuisance_covariance_export.json"
        ),
        "retained_details": [
            "81 uniformly weighted nuisance points",
            "nuisance axes: total_mass_solar, eta, tc_shift_seconds, phic_rad",
            "exported covariance is positive definite",
            "JSON hash matched across Windows and Vulcan",
        ],
        "frontier_change": "Removed the covariance-export blocker.",
        "remaining_blocker": "nuisance_grid_is_coarse_not_posterior_sampler",
    },
    {
        "version": "v2.187",
        "short_title": "R4 LALSuite waveform-likelihood posterior",
        "note_path": (
            "docs/results/2026-06-20-v2.187-"
            "r4-lalsuite-waveform-likelihood-posterior.md"
        ),
        "artifact_path": (
            "experiments/results/v2.187/"
            "r4_lalsuite_waveform_likelihood_posterior.json"
        ),
        "retained_details": [
            "125 coefficient grid points",
            "81 nuisance points per detector",
            "posterior mean g_R4_c1=0.495635486753",
            "posterior mean g_R4_c2=0.495621203259",
            "posterior mean g_R4_c3=-0.003508798916",
            "JSON hash matched across Windows and Vulcan",
        ],
        "frontier_change": "Replaced the covariance scaffold with a coarse posterior.",
        "remaining_blocker": "source_owned_full_r4_imr_sampler_missing",
    },
    {
        "version": "v2.188",
        "short_title": "R4 ParSpec ringdown source bridge",
        "note_path": (
            "docs/results/2026-06-20-v2.188-"
            "r4-parspec-ringdown-source-bridge.md"
        ),
        "artifact_path": (
            "experiments/results/v2.188/"
            "r4_parspec_ringdown_source_bridge.json"
        ),
        "retained_details": [
            "primary source arXiv:2205.05132",
            "PhysRevD 107, 044030 source DOI recorded",
            "quartic EFT ell_qEFT <= 51.3 km at 90% credible level",
            "source events are GW150914 and GW200129",
            "current engine event remains GW170608",
            "JSON hash matched across Windows and Vulcan",
        ],
        "frontier_change": "Split the source-owned IMR blocker via ParSpec.",
        "remaining_blocker": "ell_qEFT_to_engine_r4_axis_map_missing",
    },
)


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _path_status(run: dict[str, Any]) -> dict[str, bool]:
    artifact_path = run.get("artifact_path")
    return {
        "note_exists": Path(run["note_path"]).exists(),
        "artifact_expected": artifact_path is not None,
        "artifact_exists": (
            Path(artifact_path).exists() if artifact_path is not None else True
        ),
    }


def _artifact_digest(run: dict[str, Any]) -> dict[str, Any]:
    artifact_path = run.get("artifact_path")
    if artifact_path is None or not Path(artifact_path).exists():
        return {}

    artifact = load_json(artifact_path)
    digest: dict[str, Any] = {
        "version": artifact.get("version"),
        "route_status": artifact.get("route_status"),
        "ready_for_framework_claim": artifact.get("ready_for_framework_claim"),
        "claimable_framework_exclusions_now": artifact.get(
            "claimable_framework_exclusions_now"
        ),
        "selected_next_build_action": artifact.get("selected_next_build_action"),
    }

    version = run["version"]
    if version == "v2.185":
        likelihood = artifact["projected_packet"]["likelihood"]
        digest["central_values"] = likelihood["central_values"]
        digest["covariance_diagonal"] = [
            likelihood["covariance"][idx][idx] for idx in range(3)
        ]
    elif version == "v2.186":
        export = artifact["nuisance_covariance_export"]
        digest["nuisance_points"] = export["nuisance_grid"]["points"]
        digest["nuisance_parameters"] = export["nuisance_grid"]["parameters"]
        digest["exported_covariance"] = export["exported_covariance"]
        digest["exported_covariance_eigenvalues"] = export[
            "exported_covariance_eigenvalues"
        ]
    elif version == "v2.187":
        posterior = artifact["network_likelihood"]["posterior"]
        digest["coefficient_grid"] = artifact["coefficient_grid"]
        digest["nuisance_points_per_detector"] = artifact[
            "network_likelihood"
        ]["nuisance_points_per_detector"]
        digest["posterior_mean"] = posterior["posterior_mean"]
        digest["posterior_covariance"] = posterior["posterior_covariance"]
        digest["maximum_posterior_grid_point"] = posterior[
            "maximum_posterior_grid_point"
        ]
    elif version == "v2.188":
        bridge = artifact["bridge_packet"]
        evaluation = artifact["evaluation"]
        digest["parspec_bound_imported"] = evaluation["parspec_bound_imported"]
        digest["source_events"] = bridge["source_evidence"]["events"]
        digest["current_engine_event"] = bridge["event_bridge"][
            "current_engine_event"
        ]
        digest["bridge_blockers"] = evaluation["bridge_blockers"]
        digest["split_v2_187_blocker"] = evaluation["split_v2_187_blocker"]

    return canonicalize_json_floats(digest)


def research_continuity_ledger() -> dict[str, Any]:
    run_rows = []
    for run in RECENT_RUNS:
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
    versions = tuple(row["version"] for row in run_rows)
    ledger_ready = not (
        missing_note_versions
        or missing_artifact_versions
        or missing_detail_versions
        or versions != EXPECTED_VERSIONS
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "purpose": (
            "Preserve the details from the v2.170-v2.188 R4/GWOSC/LALSuite "
            "research loop so top-level docs do not flatten intermediate runs."
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
            "retained_detail_count": sum(
                len(row["retained_details"]) for row in run_rows
            ),
            "claim_boundary_preserved": True,
        },
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": (
            "r4_research_continuity_ledger_ready_nonclaiming"
            if ledger_ready
            else "r4_research_continuity_ledger_blocked"
        ),
        "selected_next_build_action": (
            "continue_with_parspec_qeft_axis_map_or_public_likelihood_packet"
        ),
        "best_next_artifact": (
            "A source-backed ParSpec ell_qEFT to engine R4-axis map, or a "
            "public ParSpec/qEFT posterior sample or likelihood grid."
        ),
        "interpretation": (
            "This is a documentation and reproducibility artifact. It protects "
            "the current research state from summary loss, but it adds no new "
            "physics claim and leaves the v2.188 blockers in force."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = research_continuity_ledger()
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
