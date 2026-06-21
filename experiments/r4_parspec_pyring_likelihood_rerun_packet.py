"""Reproducible pyRing EFT likelihood-rerun packet in runtime coordinates."""

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
    EVENT_SPIN_ROWS,
    MODE_LABELS,
)
from experiments.r4_parspec_pyring_runtime_to_parspec_normalization_policy import (
    POLICY_ID,
)
from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH,
    PYRING_BRANCH_HEAD_SHA,
    PYRING_INITIALISE_SOURCE_URL,
    PYRING_REPO_URL,
    PYRING_SOURCE_DIRECTIONS,
    PYRING_TREE_URL,
    PYRING_WAVEFORM_SOURCE_URL,
)
from experiments.r4_parspec_qnm_bresciani_source_route_graph import (
    DEFAULT_OUT as DEFAULT_V2207_PATH,
    PYRING_EFT_RINGDOWN_ANALYSIS_URL,
)
from experiments.r4_parspec_ringdown_source_bridge import load_json
from experiments.r4_parspec_source_event_alignment_manifest import (
    SAMPLE_RATE_HZ,
    parspec_source_event_records,
    parspec_source_event_strain_records,
)


VERSION = "v2.208"
DEFAULT_OUT = Path(
    "experiments/results/v2.208/r4_parspec_pyring_likelihood_rerun_packet.json"
)

PACKET_ID = "r4_parspec_pyring_likelihood_rerun_packet_v1"
COORDINATE_SCOPE = "pyring_runtime_branch_coordinates"
PYRING_PAPER_COMMIT_SHA = "6553253b4521d4bd2e82f5b86769373850b8b10c"
PYRING_PAPER_COMMIT_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/commit/"
    f"{PYRING_PAPER_COMMIT_SHA}"
)
PYRING_PAPER_INSTALL_DOC_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/blob/"
    f"{PYRING_PAPER_COMMIT_SHA}/docs/install_and_run.rst"
)
PYRING_PAPER_IO_DOC_URL = (
    "https://git.ligo.org/lscsoft/pyring/-/blob/"
    f"{PYRING_PAPER_COMMIT_SHA}/docs/basic_usage.rst"
)
REQUIRED_OUTPUT_ARTIFACTS = (
    "pyring_run_config",
    "posterior_samples_or_log_likelihood_grid",
    "prior_specification",
    "sampler_diagnostics",
    "environment_lock",
    "config_hash",
    "output_hash_manifest",
    "nonclaiming_coordinate_label",
    "event_detector_strain_manifest",
    "waveform_systematics_statement",
)
RERUN_BLOCKERS = (
    "pyring_sampler_execution_not_run",
    "runtime_likelihood_export_missing",
    "posterior_samples_or_loglikelihood_grid_missing",
    "calibration_and_waveform_systematics_missing",
    "qnm_deformation_to_bresciani_engine_r4_map_missing",
    "paper_production_ini_files_missing",
    "exact_event_runtime_settings_missing",
    "dependency_lock_missing",
    "external_adversarial_review_missing",
)


def _source_manifest() -> dict[str, Any]:
    return {
        "pyring_repo_url": PYRING_REPO_URL,
        "pyring_branch": PYRING_BRANCH,
        "pyring_branch_probe_head_sha": PYRING_BRANCH_HEAD_SHA,
        "pyring_execution_commit_sha": PYRING_PAPER_COMMIT_SHA,
        "pyring_execution_commit_url": PYRING_PAPER_COMMIT_URL,
        "pyring_install_doc_url": PYRING_PAPER_INSTALL_DOC_URL,
        "pyring_io_doc_url": PYRING_PAPER_IO_DOC_URL,
        "pyring_tree_url": PYRING_TREE_URL,
        "pyring_waveform_source_url": PYRING_WAVEFORM_SOURCE_URL,
        "pyring_initialise_source_url": PYRING_INITIALISE_SOURCE_URL,
        "pyring_eft_ringdown_analysis_url": PYRING_EFT_RINGDOWN_ANALYSIS_URL,
        "normalization_policy_id": POLICY_ID,
        "previous_route_graph_artifact": str(DEFAULT_V2207_PATH),
        "source_scope": (
            "public pyRing EFT_QNMs branch plus public GWOSC strain/event "
            "metadata; no private likelihood or unpublished posterior is used"
        ),
        "execution_pin_policy": (
            "Use the pyRing commit named by the public EFT ringdown analysis "
            "for executable reruns; retain the moving EFT_QNMs branch probe "
            "head only as coefficient-table provenance from v2.201."
        ),
    }


def _event_manifest() -> dict[str, Any]:
    events = parspec_source_event_records()
    strain_records = parspec_source_event_strain_records()
    event_by_label = {event["paper_event"]: event for event in events}
    public_strain_by_event: dict[str, dict[str, Any]] = {}
    for event in events:
        event_label = event["paper_event"]
        public_strain_by_event[event_label] = {
            "event_version": event["event_version"],
            "event_version_url": event["event_version_url"],
            "doi": event["doi"],
            "gps": event["gps"],
            "detectors": event["detectors"],
            "strain_records_32s_4khz_hdf5": [],
            "strain_records_4096s_4khz_hdf5": [],
        }
    for record in strain_records:
        duration = int(record["duration"])
        key = (
            "strain_records_32s_4khz_hdf5"
            if duration == 32
            else "strain_records_4096s_4khz_hdf5"
        )
        public_strain_by_event[record["paper_event"]][key].append({
            "detector": record["detector"],
            "duration": duration,
            "sample_rate_hz": int(record["sample_rate_hz"]),
            "gps_start": int(record["gps_start"]),
            "download_url": record["download_url"],
        })

    return canonicalize_json_floats({
        "source_events": list(public_strain_by_event),
        "detector_topology_by_event": {
            event["paper_event"]: list(event["detectors"]) for event in events
        },
        "public_strain_by_event": public_strain_by_event,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "remnant_spin_policy": {
            label: EVENT_SPIN_ROWS[label]
            for label in public_strain_by_event
            if label in EVENT_SPIN_ROWS
        },
        "event_records": [
            {
                "paper_event": label,
                "gwosc_event_name": event_by_label[label]["gwosc_event_name"],
                "event_version": event_by_label[label]["event_version"],
                "gps": event_by_label[label]["gps"],
                "detectors": event_by_label[label]["detectors"],
            }
            for label in public_strain_by_event
        ],
    })


def _runtime_coordinate_policy() -> dict[str, Any]:
    return {
        "coordinate_scope": COORDINATE_SCOPE,
        "source_directions": list(PYRING_SOURCE_DIRECTIONS),
        "modes": list(MODE_LABELS),
        "paper_reported_theories": ["quartic_1", "quartic_2"],
        "branch_extension_control_theories": ["quartic_3"],
        "sampled_unit": (
            "signed ell_km prior transformed by pyRing to gamma_EFT_runtime "
            "for one fixed EFT theory and branch direction per rerun row"
        ),
        "paper_prior_policy": {
            "Mf_Msun": [10.0, 500.0],
            "af": [0.0, 0.93],
            "amplitude": [0.0, 50.0],
            "phase": [0.0, "2*pi"],
            "ell_km": [-740.0, 740.0],
            "luminosity_distance": "uniform_within_event_95_percent_bounds",
            "dist_flat_prior": True,
        },
        "paper_runtime_settings": {
            "template": "Kerr",
            "kerr_modes": ["(2,2,2,0)", "(2,2,2,1)"],
            "domega_tgr_modes": ["(2,2,0)", "(2,2,1)"],
            "dtau_tgr_modes": ["(2,2,0)", "(2,2,1)"],
            "analysis_segment_seconds": 0.2,
            "event_peak_time_policy": "fixed_to_reconstructed_peak",
            "sky_position_policy": "fixed_from_full_signal_maximum_likelihood",
        },
        "normalization_policy_id": POLICY_ID,
        "columns_are_branch_splitting_directions": True,
        "columns_are_independent_operator_axes": False,
        "columns_are_bresciani_axes": False,
        "allowed_interpretation": (
            "Use these coordinates for a reproducible pyRing runtime likelihood "
            "export only. They are not Bresciani K coordinates and are not "
            "claim-grade framework-exclusion axes."
        ),
    }


def _minimum_rerun_config_grid(
    event_manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    configs = []
    for event_label in event_manifest["source_events"]:
        event_info = event_manifest["public_strain_by_event"][event_label]
        for direction in PYRING_SOURCE_DIRECTIONS:
            theory, branch = direction.rsplit("_", 1)
            paper_reported_theory = theory in {"quartic_1", "quartic_2"}
            configs.append({
                "run_id": f"v2208_{event_label.lower()}_{direction}_runtime",
                "paper_event": event_label,
                "event_version": event_info["event_version"],
                "detectors": list(event_info["detectors"]),
                "strain_duration_seconds": 32,
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "strain_records": event_info["strain_records_32s_4khz_hdf5"],
                "pyring_repo_url": PYRING_REPO_URL,
                "pyring_branch": PYRING_BRANCH,
                "pyring_branch_probe_head_sha": PYRING_BRANCH_HEAD_SHA,
                "pyring_execution_commit_sha": PYRING_PAPER_COMMIT_SHA,
                "waveform_family": "pyRing_QNM_EFT",
                "pyring_template": "Kerr",
                "eft_theory": theory,
                "eft_branch": branch,
                "eft_direction": direction,
                "paper_reported_theory": paper_reported_theory,
                "branch_extension_control": not paper_reported_theory,
                "coordinate_scope": COORDINATE_SCOPE,
                "modes": list(MODE_LABELS),
                "kerr_modes": ["(2,2,2,0)", "(2,2,2,1)"],
                "domega_tgr_modes": ["(2,2,0)", "(2,2,1)"],
                "dtau_tgr_modes": ["(2,2,0)", "(2,2,1)"],
                "analysis_segment_seconds": 0.2,
                "normalization_policy_id": POLICY_ID,
                "prior_policy": (
                    "fixed event and direction; signed ell_km uniform prior "
                    "[-740,740] with paper mass, spin, amplitude, phase, and "
                    "distance priors exported in the executable pyRing config"
                ),
                "sampler_status": "not_executed_in_this_packet",
                "required_outputs": list(REQUIRED_OUTPUT_ARTIFACTS),
            })
    return configs


def _output_contract() -> dict[str, Any]:
    return {
        "contract_id": "pyring_runtime_likelihood_export_contract_v1",
        "required_artifacts": list(REQUIRED_OUTPUT_ARTIFACTS),
        "minimum_export_schema": {
            "samples": [
                "paper_event",
                "event_version",
                "eft_direction",
                "coordinate_scope",
                "gamma_EFT_runtime",
                "log_likelihood",
                "log_prior",
            ],
            "grid": [
                "paper_event",
                "eft_direction",
                "gamma_EFT_runtime_grid",
                "log_likelihood_grid",
            ],
            "diagnostics": [
                "sampler_name",
                "sampler_settings",
                "convergence_summary",
                "config_sha256",
                "environment_lock_sha256",
                "output_sha256",
            ],
        },
        "accepts_samples_or_grid": True,
        "requires_output_hashes": True,
        "requires_config_hash": True,
        "requires_environment_lock": True,
        "requires_nonclaiming_coordinate_label": True,
        "requires_systematics_statement": True,
        "documented_pyring_outputs": {
            "posterior_samples": "Nested_sampler/posterior.dat",
            "evidence_summary": "Nested_sampler/Evidence.txt",
            "stdout_log": "stdout_pyRing.txt",
            "stderr_log": "stderr_pyRing.txt",
            "sampler_log": "Nested_sampler/cpnest.log",
            "noise_directory": "Noise",
            "plots_directory": "Plots",
        },
        "log_likelihood_grid_status": (
            "not a documented pyRing CLI mode; requires a driver that "
            "constructs full runtime sample dictionaries and calls "
            "log_likelihood/log_prior with explicit nuisance treatment"
        ),
    }


def pyring_likelihood_rerun_packet() -> dict[str, Any]:
    event_manifest = _event_manifest()
    packet = {
        "packet_id": PACKET_ID,
        "version": VERSION,
        "source_manifest": _source_manifest(),
        "event_manifest": event_manifest,
        "runtime_coordinate_policy": _runtime_coordinate_policy(),
        "minimum_rerun_config_grid": _minimum_rerun_config_grid(event_manifest),
        "output_contract": _output_contract(),
        "execution_status": {
            "public_strain_inputs_ready": True,
            "pyring_source_pinned": True,
            "runtime_normalization_policy_ready": True,
            "rerun_config_grid_ready": True,
            "pyring_config_export_ready": False,
            "sampler_execution_ready": False,
            "posterior_samples_exported": False,
            "log_likelihood_grid_exported": False,
            "convergence_diagnostics_exported": False,
            "calibration_systematics_closed": False,
            "runtime_coordinate_likelihood_packet_ready": False,
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "bresciani_axis_claim_allowed": False,
            "runtime_coordinates_may_be_promoted_to_bresciani_axes": False,
        },
    }
    return canonicalize_json_floats(packet)


def evaluate_pyring_likelihood_rerun_packet(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or pyring_likelihood_rerun_packet()
    blockers: set[str] = set()
    warnings: set[str] = set()

    if packet.get("packet_id") != PACKET_ID:
        blockers.add("packet_id_mismatch")
    source = packet.get("source_manifest", {})
    if source.get("pyring_branch") != PYRING_BRANCH:
        blockers.add("pyring_branch_mismatch")
    if source.get("pyring_branch_probe_head_sha") != PYRING_BRANCH_HEAD_SHA:
        blockers.add("pyring_branch_probe_head_mismatch")
    if source.get("pyring_execution_commit_sha") != PYRING_PAPER_COMMIT_SHA:
        blockers.add("pyring_execution_source_not_pinned")
    if source.get("pyring_eft_ringdown_analysis_url") != (
        PYRING_EFT_RINGDOWN_ANALYSIS_URL
    ):
        blockers.add("pyring_eft_analysis_source_missing")

    runtime_policy = packet.get("runtime_coordinate_policy", {})
    if runtime_policy.get("coordinate_scope") != COORDINATE_SCOPE:
        blockers.add("runtime_coordinate_scope_mismatch")
    if tuple(runtime_policy.get("source_directions", [])) != PYRING_SOURCE_DIRECTIONS:
        blockers.add("pyring_direction_grid_mismatch")
    if runtime_policy.get("columns_are_independent_operator_axes") is not False:
        blockers.add("runtime_coordinates_promoted_to_operator_axes")
    if runtime_policy.get("columns_are_bresciani_axes") is not False:
        blockers.add("runtime_coordinates_promoted_to_bresciani_axes")
    if runtime_policy.get("normalization_policy_id") != POLICY_ID:
        blockers.add("normalization_policy_id_mismatch")

    events = packet.get("event_manifest", {})
    expected_events = ("GW150914", "GW200129")
    if tuple(events.get("source_events", [])) != expected_events:
        blockers.add("source_event_set_mismatch")
    topology = events.get("detector_topology_by_event", {})
    if topology.get("GW150914") != ["H1", "L1"]:
        blockers.add("GW150914_detector_topology_mismatch")
    if topology.get("GW200129") != ["H1", "L1", "V1"]:
        blockers.add("GW200129_detector_topology_mismatch")

    for event_label in expected_events:
        strain_rows = (
            events.get("public_strain_by_event", {})
            .get(event_label, {})
            .get("strain_records_32s_4khz_hdf5", [])
        )
        detector_set = {row.get("detector") for row in strain_rows}
        if detector_set != set(topology.get(event_label, [])):
            blockers.add(f"{event_label}_32s_strain_detector_set_mismatch")
        for row in strain_rows:
            if int(row.get("duration", 0)) != 32:
                blockers.add(f"{event_label}_non_32s_strain_row")
            if int(row.get("sample_rate_hz", 0)) != SAMPLE_RATE_HZ:
                blockers.add(f"{event_label}_strain_sample_rate_mismatch")
            if not str(row.get("download_url", "")).endswith(".hdf5"):
                blockers.add(f"{event_label}_strain_not_hdf5")

    configs = packet.get("minimum_rerun_config_grid", [])
    expected_config_count = len(expected_events) * len(PYRING_SOURCE_DIRECTIONS)
    if len(configs) != expected_config_count:
        blockers.add("rerun_config_grid_size_mismatch")
    config_keys = {
        (row.get("paper_event"), row.get("eft_direction")) for row in configs
    }
    expected_keys = {
        (event_label, direction)
        for event_label in expected_events
        for direction in PYRING_SOURCE_DIRECTIONS
    }
    if config_keys != expected_keys:
        blockers.add("rerun_config_grid_keys_mismatch")
    for row in configs:
        if row.get("coordinate_scope") != COORDINATE_SCOPE:
            blockers.add("config_runtime_scope_mismatch")
        if row.get("pyring_execution_commit_sha") != PYRING_PAPER_COMMIT_SHA:
            blockers.add("config_pyring_execution_source_not_pinned")
        if tuple(row.get("modes", [])) != MODE_LABELS:
            blockers.add("config_modes_mismatch")
        if row.get("pyring_template") != "Kerr":
            blockers.add("config_template_mismatch")
        if row.get("analysis_segment_seconds") != 0.2:
            blockers.add("config_analysis_segment_mismatch")
        if row.get("normalization_policy_id") != POLICY_ID:
            blockers.add("config_normalization_policy_mismatch")

    contract = packet.get("output_contract", {})
    required = set(contract.get("required_artifacts", []))
    missing_artifacts = set(REQUIRED_OUTPUT_ARTIFACTS) - required
    if missing_artifacts:
        blockers.add("required_output_artifacts_missing")
    if contract.get("requires_output_hashes") is not True:
        blockers.add("output_hashes_missing")
    if contract.get("requires_config_hash") is not True:
        blockers.add("config_hash_missing")
    if contract.get("requires_environment_lock") is not True:
        blockers.add("environment_lock_missing")
    if contract.get("requires_nonclaiming_coordinate_label") is not True:
        blockers.add("nonclaiming_coordinate_label_missing")
    if contract.get("requires_systematics_statement") is not True:
        blockers.add("systematics_statement_missing")

    controls = packet.get("claim_controls", {})
    if controls.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")
    if controls.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")
    if controls.get("bresciani_axis_claim_allowed") is not False:
        blockers.add("bresciani_axis_claim_not_disabled")
    if controls.get("runtime_coordinates_may_be_promoted_to_bresciani_axes"):
        blockers.add("runtime_coordinates_promoted_to_bresciani_axes")

    execution = packet.get("execution_status", {})
    if execution.get("pyring_config_export_ready") is True:
        warnings.add("pyring_config_export_unexpectedly_ready")
    runtime_export_ready = (
        execution.get("sampler_execution_ready") is True
        and (
            execution.get("posterior_samples_exported") is True
            or execution.get("log_likelihood_grid_exported") is True
        )
        and execution.get("convergence_diagnostics_exported") is True
        and execution.get("calibration_systematics_closed") is True
        and not blockers
    )

    return canonicalize_json_floats({
        "rerun_packet_spec_ready": not blockers,
        "runtime_likelihood_export_ready": runtime_export_ready,
        "ready_for_bresciani_claim": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "blockers": sorted(blockers),
        "warnings": sorted(warnings),
        "remaining_execution_blockers": list(RERUN_BLOCKERS),
        "route_status": (
            "pyring_likelihood_rerun_packet_spec_ready_execution_missing"
            if not blockers and not runtime_export_ready
            else "pyring_likelihood_rerun_packet_not_ready"
        ),
    })


def malformed_pyring_likelihood_rerun_packet() -> dict[str, Any]:
    packet = copy.deepcopy(pyring_likelihood_rerun_packet())
    packet["source_manifest"]["pyring_execution_commit_sha"] = ""
    packet["runtime_coordinate_policy"][
        "columns_are_independent_operator_axes"
    ] = True
    packet["runtime_coordinate_policy"]["columns_are_bresciani_axes"] = True
    packet["output_contract"]["required_artifacts"] = [
        artifact
        for artifact in packet["output_contract"]["required_artifacts"]
        if artifact
        not in {
            "posterior_samples_or_log_likelihood_grid",
            "output_hash_manifest",
        }
    ]
    packet["output_contract"]["requires_output_hashes"] = False
    packet["claim_controls"]["framework_claim_allowed"] = True
    packet["claim_controls"]["runtime_coordinates_may_be_promoted_to_bresciani_axes"] = (
        True
    )
    packet["execution_status"]["sampler_execution_ready"] = True
    packet["execution_status"]["posterior_samples_exported"] = True
    packet["execution_status"]["runtime_coordinate_likelihood_packet_ready"] = True
    packet["malformed_promoted_claim"] = {
        "coordinate_scope": "bresciani_operator_axes",
        "ready_for_framework_claim": True,
    }
    return packet


def diagnose_r4_parspec_pyring_likelihood_rerun_packet(
    *,
    v2207_path: str | Path = DEFAULT_V2207_PATH,
) -> dict[str, Any]:
    packet = pyring_likelihood_rerun_packet()
    evaluation = evaluate_pyring_likelihood_rerun_packet(packet)
    malformed = evaluate_pyring_likelihood_rerun_packet(
        malformed_pyring_likelihood_rerun_packet()
    )
    v2207 = load_json(v2207_path)

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.192_source_event_alignment_manifest",
            "v2.203_pyring_event_spin_jacobian",
            "v2.204_runtime_normalization_policy",
            "v2.207_qnm_bresciani_source_route_graph",
            "public_pyring_paper_commit",
            "public_pyring_EFT_QNMs_branch",
            "public_GWOSC_event_versions",
        ],
        "rerun_packet": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "v2207_route_status": v2207["route_status"],
        "rerun_packet_spec_ready": evaluation["rerun_packet_spec_ready"],
        "runtime_likelihood_export_ready": evaluation[
            "runtime_likelihood_export_ready"
        ],
        "ready_for_bresciani_claim": False,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "export_executable_pyring_runtime_configs_and_run_sampler"
        ),
        "interpretation": (
            "v2.208 turns the v2.207 next-likelihood route into a concrete "
            "rerun packet: public event strain inputs, pyRing source pins, "
            "runtime coordinate policy, minimum event-direction config grid, "
            "and the required output contract. The executable rerun target is "
            "the pyRing commit named by the public EFT ringdown analysis, not "
            "a moving branch head. It still has no executed sampler, no "
            "posterior samples or log-likelihood grid, no claim-grade "
            "systematics, and no qNM-to-Bresciani operator map."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2207", default=str(DEFAULT_V2207_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_pyring_likelihood_rerun_packet(
        v2207_path=Path(args.v2207)
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
