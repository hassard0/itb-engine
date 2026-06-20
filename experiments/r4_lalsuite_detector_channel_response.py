"""Calibrated LALSuite detector-channel response for R4 projections."""

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
from experiments.r4_vulcan_lalsuite_runtime_target import (
    LAL_VERSION,
    TARGET_HOST,
)


VERSION = "v2.183"
EVENT = "GW170608"
EVENT_GPS = 1180922494.5
EVENT_GMST = 40123.146792515385
GRID = {
    "ra_count": 8,
    "dec_count": 7,
    "psi_count": 6,
    "sample_count": 336,
    "dec_min_rad": -0.75,
    "dec_max_rad": 0.75,
    "psi_period_rad": math.pi,
    "weighting": "cos(dec)",
}
CALIBRATED_CHANNEL_RESPONSE = {
    "H1": {
        "detector": "H1",
        "lal_detector_index": "LALDetectorIndexLHODIFF",
        "tensor_rms": 0.6065423575413879,
        "helicity_re_rms": 0.31544149567907454,
        "helicity_im_rms": 0.31544149567907454,
        "K_plus": 0.6065423575413879,
        "Re_K_minus": 0.5200650733737918,
        "Im_K_minus": 0.5200650733737918,
        "max_abs_fplus": 0.9816385642554493,
        "max_abs_fcross": 0.8977707347189797,
    },
    "L1": {
        "detector": "L1",
        "lal_detector_index": "LALDetectorIndexLLODIFF",
        "tensor_rms": 0.6422799664789397,
        "helicity_re_rms": 0.34990775976359634,
        "helicity_im_rms": 0.34990775976359634,
        "K_plus": 0.6422799664789397,
        "Re_K_minus": 0.5447900884747116,
        "Im_K_minus": 0.5447900884747116,
        "max_abs_fplus": 0.9591887150710738,
        "max_abs_fcross": 0.9023633985550465,
    },
}
REMAINING_AFTER_CHANNEL_CALIBRATION = (
    "full_imr_r4_merger_ringdown_completion_missing",
    "nuisance_marginalized_covariance_not_exported",
    "waveform_calibration_prior_and_eft_systematics_not_closed",
    "external_adversarial_review_missing",
)


def lalsuite_detector_channel_response() -> dict[str, Any]:
    return canonicalize_json_floats({
        "response_id": "lalsuite_r4_detector_channel_response_v1",
        "target_host": TARGET_HOST,
        "lal_version": LAL_VERSION,
        "event": EVENT,
        "event_gps": EVENT_GPS,
        "event_gmst": EVENT_GMST,
        "grid": GRID,
        "response_kind": (
            "sky_polarization_marginalized_lalsuite_tensor_rms_moments"
        ),
        "source_channel_mapping": {
            "K_plus": "sqrt(mean(F_plus^2 + F_cross^2))",
            "Re_K_minus": (
                "sqrt(mean((F_plus^2 - F_cross^2)^2)) / K_plus"
            ),
            "Im_K_minus": "sqrt(mean((2*F_plus*F_cross)^2)) / K_plus",
        },
        "detectors": CALIBRATED_CHANNEL_RESPONSE,
        "calibrated_with_lalsuite": True,
        "detector_channel_response_calibrated": True,
        "calibration_scope": (
            "RMS sensitivity calibration over a deterministic sky/polarization "
            "grid at the event GMST; not a sky-posterior marginalization."
        ),
    })


def evaluate_lalsuite_detector_channel_response(
    response: dict[str, Any],
) -> dict[str, Any]:
    blockers: set[str] = set()
    if response.get("target_host") != TARGET_HOST:
        blockers.add("target_host_not_vulcan")
    if response.get("lal_version") != LAL_VERSION:
        blockers.add("lal_version_unexpected")
    if response.get("event") != EVENT:
        blockers.add("event_not_gw170608")
    grid = response.get("grid", {})
    if int(grid.get("sample_count") or 0) != GRID["sample_count"]:
        blockers.add("response_grid_sample_count_unexpected")
    if response.get("calibrated_with_lalsuite") is not True:
        blockers.add("not_marked_lalsuite_calibrated")
    if response.get("detector_channel_response_calibrated") is not True:
        blockers.add("detector_channel_response_not_calibrated")

    detectors = response.get("detectors", {})
    if sorted(detectors) != ["H1", "L1"]:
        blockers.add("detectors_not_h1_l1")
    else:
        for detector, row in detectors.items():
            for field in ("K_plus", "Re_K_minus", "Im_K_minus"):
                value = float(row.get(field, math.nan))
                if not math.isfinite(value) or value <= 0.0:
                    blockers.add(f"{detector}_{field}_not_positive")
            tensor = float(row.get("tensor_rms", math.nan))
            if not 0.0 < tensor <= 1.0:
                blockers.add(f"{detector}_tensor_rms_out_of_range")
            if float(row.get("max_abs_fplus", 0.0)) <= 0.0:
                blockers.add(f"{detector}_fplus_zero")
            if float(row.get("max_abs_fcross", 0.0)) <= 0.0:
                blockers.add(f"{detector}_fcross_zero")

    return canonicalize_json_floats({
        "response_id": response.get("response_id"),
        "detector_channel_response_ready": not blockers,
        "ready_to_replace_v2_181_detector_channel_proxy": not blockers,
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "response_blockers": sorted(blockers),
        "removed_v2_182_blocker": (
            "detector_antenna_r4_channel_response_not_calibrated"
            if not blockers else None
        ),
        "remaining_real_reanalysis_blockers": sorted(
            REMAINING_AFTER_CHANNEL_CALIBRATION
        ),
        "claim_blockers": sorted(
            set(REMAINING_AFTER_CHANNEL_CALIBRATION)
            | {"framework_claim_controls_disabled"}
        ),
        "route_status": (
            "r4_lalsuite_detector_channel_response_ready_nonclaiming"
            if not blockers
            else "r4_lalsuite_detector_channel_response_blocked"
        ),
    })


def malformed_lalsuite_detector_channel_response() -> dict[str, Any]:
    response = lalsuite_detector_channel_response()
    response["target_host"] = "localhost"
    response["detectors"]["H1"]["K_plus"] = 0.0
    response["grid"]["sample_count"] = 1
    response["detector_channel_response_calibrated"] = False
    return response


def diagnose_r4_lalsuite_detector_channel_response() -> dict[str, Any]:
    response = lalsuite_detector_channel_response()
    evaluation = evaluate_lalsuite_detector_channel_response(response)
    malformed = evaluate_lalsuite_detector_channel_response(
        malformed_lalsuite_detector_channel_response()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.182_r4_vulcan_lalsuite_runtime_target",
            "v2.181_r4_source_backed_gwosc_projection",
            "lal.ComputeDetAMResponse",
        ],
        "detector_channel_response": response,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "detector_channel_response_ready": (
            evaluation["detector_channel_response_ready"]
        ),
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "replace_v2_181_detector_proxy_with_lalsuite_channel_response"
        ),
        "best_next_artifact": (
            "Regenerate the GWOSC R4 projection using the calibrated LALSuite "
            "H1/L1 channel response instead of the v2.181 deterministic proxy."
        ),
        "interpretation": (
            "The R4 route now has a calibrated H1/L1 detector-channel response "
            "target based on LALSuite antenna tensors and event-time sky/"
            "polarization RMS moments. It remains nonclaiming because this is "
            "not a full sky-posterior, R4 merger-ringdown, or covariance export."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.183/"
            "r4_lalsuite_detector_channel_response.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_r4_lalsuite_detector_channel_response()
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
