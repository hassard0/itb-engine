"""Detector-calibration systematics bound for the GW alpha packet."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.120"
DEFAULT_ENVELOPE_AUDIT_PATH = Path(
    "experiments/results/v2.119/gw_alpha_systematics_envelope_audit.json"
)
DEFAULT_IMR_REFERENCE_PATH = Path(
    "experiments/results/v2.113/gw_lalsuite_imr_projection.json"
)
GW170608_CALIBRATION_SOURCE = {
    "title": "GW170608: Observation of a 19-solar-mass Binary Black Hole Coalescence",
    "url": "https://arxiv.org/abs/1711.05578",
    "reported_max_1sigma_amplitude_fraction": 0.05,
    "reported_max_1sigma_phase_degrees": 3.0,
    "frequency_band_hz": [20.0, 111.25],
}
SIGMA_MULTIPLIER = 2.0


def calibration_corner_factors(
    *,
    amplitude_fraction: float,
    phase_degrees: float,
) -> list[complex]:
    if not math.isfinite(amplitude_fraction) or amplitude_fraction < 0.0:
        raise ValueError("amplitude_fraction must be non-negative and finite")
    if not math.isfinite(phase_degrees) or phase_degrees < 0.0:
        raise ValueError("phase_degrees must be non-negative and finite")
    phase_radians = math.radians(phase_degrees)
    return [
        (1.0 + amp_sign * amplitude_fraction)
        * complex(math.cos(phase_sign * phase_radians), math.sin(phase_sign * phase_radians))
        for amp_sign in (-1.0, 1.0)
        for phase_sign in (-1.0, 1.0)
    ]


def detector_projection_complexes(
    imr_reference: dict[str, Any],
    parameter: str,
) -> dict[str, complex]:
    rows = {}
    for detector_row in imr_reference["detector_projections"]:
        projection = detector_row["lalsuite_imr_projection"]["projections"][parameter]
        rows[detector_row["detector"]] = complex(
            float(projection["real"]),
            float(projection["imag"]),
        )
    if sorted(rows) != ["H1", "L1"]:
        raise ValueError("detector calibration bound requires H1 and L1 projections")
    return rows


def calibration_bound_for_parameter(
    detector_projections: dict[str, complex],
    *,
    amplitude_fraction: float,
    phase_degrees: float,
) -> dict[str, Any]:
    detectors = sorted(detector_projections)
    bases = [detector_projections[detector] for detector in detectors]
    base_complex_mean = sum(bases) / len(bases)
    base_abs_detector_mean = sum(abs(value) for value in bases) / len(bases)
    factors = calibration_corner_factors(
        amplitude_fraction=amplitude_fraction,
        phase_degrees=phase_degrees,
    )

    max_real_mean_shift = 0.0
    max_imag_mean_shift = 0.0
    max_abs_detector_mean_shift = 0.0
    max_complex_mean_shift = 0.0
    for corner in itertools.product(factors, repeat=len(detectors)):
        shifted = [factor * value for factor, value in zip(corner, bases)]
        shifted_complex_mean = sum(shifted) / len(shifted)
        shifted_abs_detector_mean = sum(abs(value) for value in shifted) / len(shifted)
        max_real_mean_shift = max(
            max_real_mean_shift,
            abs(shifted_complex_mean.real - base_complex_mean.real),
        )
        max_imag_mean_shift = max(
            max_imag_mean_shift,
            abs(shifted_complex_mean.imag - base_complex_mean.imag),
        )
        max_abs_detector_mean_shift = max(
            max_abs_detector_mean_shift,
            abs(shifted_abs_detector_mean - base_abs_detector_mean),
        )
        max_complex_mean_shift = max(
            max_complex_mean_shift,
            abs(shifted_complex_mean - base_complex_mean),
        )

    return {
        "base_complex_mean_real": base_complex_mean.real,
        "base_complex_mean_imag": base_complex_mean.imag,
        "base_abs_detector_mean": base_abs_detector_mean,
        "max_real_mean_shift": max_real_mean_shift,
        "max_imag_mean_shift": max_imag_mean_shift,
        "max_abs_detector_mean_shift": max_abs_detector_mean_shift,
        "max_complex_mean_shift": max_complex_mean_shift,
        "calibration_corner_count": len(factors) ** len(detectors),
    }


def detector_calibration_bound(
    imr_reference: dict[str, Any],
    *,
    sigma_multiplier: float = SIGMA_MULTIPLIER,
) -> dict[str, Any]:
    if not math.isfinite(sigma_multiplier) or sigma_multiplier <= 0.0:
        raise ValueError("sigma_multiplier must be positive and finite")
    amplitude_fraction = (
        sigma_multiplier
        * GW170608_CALIBRATION_SOURCE["reported_max_1sigma_amplitude_fraction"]
    )
    phase_degrees = (
        sigma_multiplier
        * GW170608_CALIBRATION_SOURCE["reported_max_1sigma_phase_degrees"]
    )

    rows = {}
    max_network_projection_shift = 0.0
    for parameter in ("alpha_bar_1", "alpha_bar_2"):
        bound = calibration_bound_for_parameter(
            detector_projection_complexes(imr_reference, parameter),
            amplitude_fraction=amplitude_fraction,
            phase_degrees=phase_degrees,
        )
        rows[parameter] = bound
        max_network_projection_shift = max(
            max_network_projection_shift,
            bound["max_real_mean_shift"],
            bound["max_imag_mean_shift"],
            bound["max_abs_detector_mean_shift"],
            bound["max_complex_mean_shift"],
        )

    bounded_ready = (
        sorted(imr_reference["network_projection"]["detectors"]) == ["H1", "L1"]
        and max_network_projection_shift > 0.0
        and all(row["calibration_corner_count"] == 16 for row in rows.values())
    )
    return {
        "status": "bounded" if bounded_ready else "open",
        "basis": (
            "gw170608_published_calibration_uncertainty_2sigma_corner_propagation"
        ),
        "calibration_source": GW170608_CALIBRATION_SOURCE,
        "applied_envelope": {
            "sigma_multiplier": sigma_multiplier,
            "amplitude_fraction": amplitude_fraction,
            "phase_degrees": phase_degrees,
            "detectors": imr_reference["network_projection"]["detectors"],
        },
        "parameters": rows,
        "max_network_projection_shift": max_network_projection_shift,
        "bounded_ready": bounded_ready,
        "scope": (
            "Bounds detector calibration propagation for the v2.113 H1/L1 "
            "complex alpha projections. It does not close waveform, prior, "
            "or EFT-truncation systematics."
        ),
    }


def packet_with_detector_calibration_bound(
    envelope_packet: dict[str, Any],
    imr_reference: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(envelope_packet)
    evidence = packet["systematics_budget"]["evidence"]
    evidence["detector_calibration"] = detector_calibration_bound(imr_reference)
    packet["label"] = "v2_120_detector_calibration_bounded_alpha_packet"
    packet["systematics_budget"]["evidence"] = evidence
    packet["systematics_budget"]["components"] = {
        component: row["status"] for component, row in evidence.items()
    }
    packet["systematics_budget"]["status"] = (
        "bounded"
        if all(row["status"] == "bounded" for row in evidence.values())
        else "open"
    )
    packet["validation_reference"] = "v2.120_alpha_detector_calibration_bound"
    return packet


def evaluate_alpha_detector_calibration_bound(
    packet: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget_eval = evaluate_alpha_systematics_budget(packet)
    return {
        "detector_calibration_bounded": (
            packet["systematics_budget"]["components"].get("detector_calibration")
            == "bounded"
        ),
        "bounded_components": budget_eval["bounded_components"],
        "open_components": budget_eval["open_components"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "removed_v2_119_subblockers": [
            "detector_calibration_proxy_not_calibrated_bound",
        ],
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_not_closed",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "waveform_prior_and_eft_systematics_still_open",
            }
        ),
    }


def diagnose_gw_alpha_detector_calibration_bound(
    envelope_audit_path: Path = DEFAULT_ENVELOPE_AUDIT_PATH,
    imr_reference_path: Path = DEFAULT_IMR_REFERENCE_PATH,
) -> dict[str, Any]:
    envelope_audit = load_json(envelope_audit_path)
    imr_reference = load_json(imr_reference_path)
    packet = packet_with_detector_calibration_bound(
        envelope_audit["packet"],
        imr_reference,
    )
    evaluation = evaluate_alpha_detector_calibration_bound(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.119_alpha_systematics_envelope_audit",
            "v2.113_lalsuite_imr_projection",
            "gw170608_published_calibration_uncertainty",
        ],
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": "detector_calibration_bounded_alpha_packet_nonclaiming",
        "selected_next_build_action": (
            "bound_waveform_prior_and_eft_systematics"
        ),
        "best_next_artifact": (
            "Use the saved v2.115 likelihood grid to build a nuisance-prior "
            "stress test, then separately replace the waveform and EFT proxies "
            "with source-backed calibrated bounds."
        ),
        "interpretation": (
            "The detector-calibration proxy is replaced by a source-declared "
            "2-sigma amplitude/phase envelope propagated through the complex "
            "H1/L1 alpha projections. The packet remains nonclaiming because "
            "waveform, prior, and EFT-truncation systematics are still open."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope-audit", default=str(DEFAULT_ENVELOPE_AUDIT_PATH))
    parser.add_argument("--imr-reference", default=str(DEFAULT_IMR_REFERENCE_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.120/"
            "gw_alpha_detector_calibration_bound.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_detector_calibration_bound(
        envelope_audit_path=Path(args.envelope_audit),
        imr_reference_path=Path(args.imr_reference),
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
