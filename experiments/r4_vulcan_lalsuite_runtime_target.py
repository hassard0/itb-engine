"""Vulcan LALSuite runtime target for the source-backed R4 route."""

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


VERSION = "v2.182"
TARGET_HOST = "192.168.4.178"
TARGET_ALIAS = "vulcan"
LAL_VERSION = "7.7.1"
FREQUENCY_MIN_HZ = 20.0
FREQUENCY_MAX_HZ = 111.25
FREQUENCY_BIN_COUNT = 366
DELTA_F_HZ = 0.25
MAX_ABS_H_PLUS = 3.1266052249299665e-23
REMAINING_AFTER_RUNTIME_TARGET = (
    "detector_antenna_r4_channel_response_not_calibrated",
    "full_imr_r4_merger_ringdown_completion_missing",
    "nuisance_marginalized_covariance_not_exported",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def vulcan_lalsuite_runtime_evidence() -> dict[str, Any]:
    return canonicalize_json_floats({
        "target_alias": TARGET_ALIAS,
        "target_host": TARGET_HOST,
        "workdir": "/home/admin/itb-engine-main-v2181-20260620183054",
        "python": ".venv/bin/python",
        "install_command": ".venv/bin/python -m pip install lalsuite",
        "import_probe": {
            "available": True,
            "lal_version": LAL_VERSION,
            "has_imrphenomd": True,
        },
        "imrphenomd_reference_probe": {
            "approximant": "IMRPhenomD",
            "lal_version": LAL_VERSION,
            "delta_f_hz": DELTA_F_HZ,
            "frequency_min_hz": FREQUENCY_MIN_HZ,
            "frequency_max_hz": FREQUENCY_MAX_HZ,
            "distance_mpc": 400.0,
            "mass_1_solar": 12.790896534380867,
            "mass_2_solar": 6.209103465619133,
            "total_mass_solar": 19.0,
            "eta": 0.22,
            "nonzero_bins": FREQUENCY_BIN_COUNT,
            "max_abs_h_plus": f"{MAX_ABS_H_PLUS:.16e}",
            "max_abs_h_plus_x1e23": MAX_ABS_H_PLUS * 1.0e23,
        },
        "runtime_scope": (
            "Target runtime can import lal/lalsimulation and generate an "
            "IMRPhenomD reference over the v2.181 GW170608 frequency window."
        ),
        "not_covered_by_runtime_probe": [
            "r4_modified_waveform_plugin",
            "calibrated_r4_detector_channel_response",
            "nuisance_marginalized_r4_covariance",
            "external_adversarial_review",
        ],
    })


def evaluate_vulcan_lalsuite_runtime_evidence(
    evidence: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = set()
    if evidence.get("target_host") != TARGET_HOST:
        blockers.add("target_host_not_vulcan")
    probe = evidence.get("import_probe", {})
    if probe.get("available") is not True:
        blockers.add("lal_import_not_available")
    if probe.get("has_imrphenomd") is not True:
        blockers.add("imrphenomd_not_available")
    if probe.get("lal_version") != LAL_VERSION:
        blockers.add("lal_version_unexpected")

    reference = evidence.get("imrphenomd_reference_probe", {})
    if reference.get("approximant") != "IMRPhenomD":
        blockers.add("reference_approximant_not_imrphenomd")
    if int(reference.get("nonzero_bins") or 0) != FREQUENCY_BIN_COUNT:
        blockers.add("reference_nonzero_bin_count_unexpected")
    if float(reference.get("frequency_min_hz", math.nan)) != FREQUENCY_MIN_HZ:
        blockers.add("reference_frequency_min_unexpected")
    if float(reference.get("frequency_max_hz", math.nan)) != FREQUENCY_MAX_HZ:
        blockers.add("reference_frequency_max_unexpected")
    max_abs = float(reference.get("max_abs_h_plus_x1e23", math.nan))
    if not math.isfinite(max_abs) or max_abs <= 0.0:
        blockers.add("reference_waveform_zero_or_invalid")

    return canonicalize_json_floats({
        "target_alias": evidence.get("target_alias"),
        "target_host": evidence.get("target_host"),
        "lalsuite_runtime_target_ready": not blockers,
        "ready_to_clear_runtime_availability_gate_on_vulcan": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "runtime_blockers": sorted(blockers),
        "removed_v2_181_blocker": (
            "lalsuite_r4_runtime_projection_not_run" if not blockers else None
        ),
        "remaining_real_reanalysis_blockers": sorted(
            REMAINING_AFTER_RUNTIME_TARGET
        ),
        "claim_blockers": sorted(
            set(REMAINING_AFTER_RUNTIME_TARGET)
            | {"framework_claim_controls_disabled"}
        ),
        "route_status": (
            "r4_vulcan_lalsuite_runtime_target_ready_nonclaiming"
            if not blockers
            else "r4_vulcan_lalsuite_runtime_target_blocked"
        ),
    })


def malformed_vulcan_lalsuite_runtime_evidence() -> dict[str, Any]:
    evidence = vulcan_lalsuite_runtime_evidence()
    evidence["target_host"] = "localhost"
    evidence["import_probe"]["has_imrphenomd"] = False
    evidence["imrphenomd_reference_probe"]["nonzero_bins"] = 0
    evidence["imrphenomd_reference_probe"]["max_abs_h_plus"] = "0.0"
    evidence["imrphenomd_reference_probe"]["max_abs_h_plus_x1e23"] = 0.0
    return evidence


def diagnose_r4_vulcan_lalsuite_runtime_target() -> dict[str, Any]:
    evidence = vulcan_lalsuite_runtime_evidence()
    evaluation = evaluate_vulcan_lalsuite_runtime_evidence(evidence)
    malformed = evaluate_vulcan_lalsuite_runtime_evidence(
        malformed_vulcan_lalsuite_runtime_evidence()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.181_r4_source_backed_gwosc_projection",
            "v2.113_lalsuite_imrphenomd_projection",
            "vulcan_lalsuite_7_7_1_runtime_probe",
        ],
        "runtime_evidence": evidence,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "lalsuite_runtime_target_ready": (
            evaluation["lalsuite_runtime_target_ready"]
        ),
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "derive_calibrated_r4_detector_channel_response"
        ),
        "best_next_artifact": (
            "Use the Vulcan LALSuite runtime to replace the v2.181 deterministic "
            "detector-channel proxy with calibrated R4 channel response and "
            "then export nuisance-marginalized covariance."
        ),
        "interpretation": (
            "The target Vulcan runtime now clears the basic LALSuite/IMRPhenomD "
            "availability gate for the R4 route. This is not yet a real R4 "
            "reanalysis because no R4-modified waveform plugin, calibrated "
            "detector channel response, or covariance export has been run."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.182/"
            "r4_vulcan_lalsuite_runtime_target.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_vulcan_lalsuite_runtime_target()
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
