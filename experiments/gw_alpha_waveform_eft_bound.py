"""Waveform and EFT truncation component bounds for the GW alpha packet."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    REQUIRED_SYSTEMATICS_COMPONENTS,
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.124"
DEFAULT_PRIOR_REWEIGHT_PATH = Path(
    "experiments/results/v2.123/gw_alpha_prior_reweight_sweep.json"
)
DEFAULT_GR_REFERENCE_PATH = Path(
    "experiments/results/v2.112/gw_gr_inspiral_reference_projection.json"
)
DEFAULT_IMR_REFERENCE_PATH = Path(
    "experiments/results/v2.113/gw_lalsuite_imr_projection.json"
)
DEFAULT_SOURCE_RESPONSE_PATH = Path(
    "experiments/results/v2.109/gw_source_backed_cubic_waveform_response.json"
)
WAVEFORM_ENVELOPE_SAFETY_FACTOR = 1.25
NATURALNESS_COEFFICIENT_RATIO_CAP = 10.0
FLOAT_TOLERANCE = 1.0e-12


def _projection_delta(
    left: dict[str, Any],
    right: dict[str, Any],
    parameter: str,
    field: str,
) -> float:
    key = f"{parameter}_{field}"
    return float(right["network_projection"][key] - left["network_projection"][key])


def prior_alpha_domain(prior_reweight: dict[str, Any]) -> dict[str, float]:
    sweep = prior_reweight["prior_reweight_sweep"]
    axis_step = float(sweep["alpha_axis_step"])
    max_abs_best_alpha = 0.0
    for row in sweep["prior_summary_rows"]:
        best = row["best_grid_point"]
        max_abs_best_alpha = max(
            max_abs_best_alpha,
            abs(float(best["alpha_bar_1"])),
            abs(float(best["alpha_bar_2"])),
        )
    domain_half_width = max_abs_best_alpha + axis_step
    return {
        "axis_step": axis_step,
        "max_abs_best_alpha": max_abs_best_alpha,
        "domain_half_width": domain_half_width,
        "max_delta_log_likelihood_best_vs_gr": float(
            sweep["max_delta_log_likelihood_best_vs_gr"]
        ),
    }


def waveform_component_bound(
    gr_reference: dict[str, Any],
    imr_reference: dict[str, Any],
    domain: dict[str, float],
    *,
    safety_factor: float = WAVEFORM_ENVELOPE_SAFETY_FACTOR,
) -> dict[str, Any]:
    if not math.isfinite(safety_factor) or safety_factor < 1.0:
        raise ValueError("safety_factor must be finite and at least 1")
    rows = {}
    max_abs_delta = 0.0
    for parameter in ("alpha_bar_1", "alpha_bar_2"):
        row = {}
        for field in ("abs_mean", "real_mean", "imag_mean"):
            delta = _projection_delta(gr_reference, imr_reference, parameter, field)
            row[f"{field}_delta"] = delta
            max_abs_delta = max(max_abs_delta, abs(delta))
        rows[parameter] = row
    envelope = safety_factor * max_abs_delta
    bounded_ready = (
        gr_reference["source_reference"] == imr_reference["source_reference"]
        and imr_reference["evaluation"]["lalsuite_imr_projection_ready"] is True
        and max_abs_delta > 0.0
        and math.isfinite(envelope)
        and envelope >= max_abs_delta
    )
    return {
        "status": "bounded" if bounded_ready else "open",
        "basis": "source_backed_imr_minus_inspiral_projection_envelope",
        "source_reference": imr_reference["source_reference"],
        "reference_models": {
            "left": "leading_order_gr_stationary_phase_inspiral",
            "right": "LALSuite_IMRPhenomD",
        },
        "parameters": rows,
        "max_network_projection_component_delta": max_abs_delta,
        "safety_factor": safety_factor,
        "waveform_projection_envelope": envelope,
        "alpha_domain": domain,
        "bounded_ready": bounded_ready,
        "scope": (
            "Finite conservative component bound for the current source-backed "
            "alpha projection. It is not a replacement for a published full-IMR "
            "cubic-EFT waveform family and is therefore paired with a top-level "
            "budget hold."
        ),
    }


def _max_abs_kernel_value(response: dict[str, Any]) -> float:
    kernels = response["response"]["kernels"]
    maximum = 0.0
    for family in (
        "phase_delta_psi",
        "relative_amplitude_delta_a_over_a_newt",
    ):
        for parameter in ("alpha_bar_1", "alpha_bar_2"):
            maximum = max(
                maximum,
                max(abs(float(value)) for value in kernels[family][parameter]),
            )
    return maximum


def eft_truncation_component_bound(
    source_response: dict[str, Any],
    imr_reference: dict[str, Any],
    domain: dict[str, float],
    *,
    coefficient_ratio_cap: float = NATURALNESS_COEFFICIENT_RATIO_CAP,
) -> dict[str, Any]:
    if not math.isfinite(coefficient_ratio_cap) or coefficient_ratio_cap <= 0.0:
        raise ValueError("coefficient_ratio_cap must be positive and finite")
    window = imr_reference["detector_projections"][0]["lalsuite_imr_projection"][
        "frequency_window"
    ]
    v_f_max = float(window["v_f_max"])
    next_pn_power = v_f_max * v_f_max
    relative_remainder_bound = coefficient_ratio_cap * next_pn_power
    max_kernel = _max_abs_kernel_value(source_response)
    alpha_equivalent_remainder_bound = (
        domain["domain_half_width"] * relative_remainder_bound
    )
    kernel_remainder_bound = max_kernel * relative_remainder_bound
    bounded_ready = (
        source_response["response"]["source_backed"] is True
        and source_response["source_reference"] == imr_reference["source_reference"]
        and v_f_max > 0.0
        and math.isfinite(relative_remainder_bound)
        and math.isfinite(kernel_remainder_bound)
    )
    return {
        "status": "bounded" if bounded_ready else "open",
        "basis": "source_backed_next_pn_power_counting_remainder_bound",
        "source_reference": source_response["source_reference"],
        "source_equation_refs": source_response["response"]["source_equation_refs"],
        "v_f_max": v_f_max,
        "next_order_power_suppression": next_pn_power,
        "coefficient_ratio_cap": coefficient_ratio_cap,
        "relative_remainder_bound": relative_remainder_bound,
        "max_source_kernel_abs_value": max_kernel,
        "kernel_remainder_bound": kernel_remainder_bound,
        "alpha_domain": domain,
        "alpha_equivalent_remainder_bound": alpha_equivalent_remainder_bound,
        "bounded_ready": bounded_ready,
        "scope": (
            "Finite EFT truncation component bound under the declared Wilson "
            "coefficient-ratio cap. The cap is deliberately conservative and "
            "keeps the route nonclaiming until likelihood-scale and joint "
            "posterior checks are built."
        ),
    }


def packet_with_waveform_eft_bounds(
    prior_packet: dict[str, Any],
    waveform_bound: dict[str, Any],
    eft_bound: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(prior_packet)
    evidence = packet["systematics_budget"]["evidence"]
    evidence["waveform_systematics"] = waveform_bound
    evidence["eft_truncation"] = eft_bound
    components = {
        component: evidence[component]["status"]
        for component in REQUIRED_SYSTEMATICS_COMPONENTS
    }
    component_budget_bounded = all(
        status == "bounded" for status in components.values()
    )
    packet["label"] = "v2_124_waveform_eft_component_bounded_alpha_packet"
    packet["systematics_budget"]["evidence"] = evidence
    packet["systematics_budget"]["components"] = components
    packet["systematics_budget"]["component_status"] = (
        "bounded" if component_budget_bounded else "open"
    )
    packet["systematics_budget"]["status"] = "open"
    packet["systematics_budget"]["budget_hold"] = {
        "status": "open",
        "reason": (
            "All required component rows are bounded, but the top-level adapter "
            "budget remains open until the detector-separable likelihood cube is "
            "replaced or justified as a joint-event posterior, likelihood scale "
            "is calibrated to noise evidence, and the G8 joint component is "
            "supplied."
        ),
        "held_blockers": [
            "detector_separable_cube_not_joint_event_posterior",
            "likelihood_scale_not_calibrated_to_noise_evidence",
            "g8_joint_component_missing",
        ],
    }
    packet["validation_reference"] = "v2.124_alpha_waveform_eft_bound"
    return packet


def evaluate_alpha_waveform_eft_bound(packet: dict[str, Any]) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget_eval = evaluate_alpha_systematics_budget(packet)
    components = packet["systematics_budget"]["components"]
    component_systematics_bounded = all(
        components.get(component) == "bounded"
        for component in REQUIRED_SYSTEMATICS_COMPONENTS
    )
    return {
        "waveform_systematics_bounded": (
            components.get("waveform_systematics") == "bounded"
        ),
        "eft_truncation_bounded": components.get("eft_truncation") == "bounded",
        "component_systematics_bounded": component_systematics_bounded,
        "top_level_budget_status": packet["systematics_budget"]["status"],
        "bounded_components": budget_eval["bounded_components"],
        "open_components": budget_eval["open_components"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "remaining_nonclaiming_reasons": sorted(
            {
                "component_systematics_bounded_but_budget_meta_hold_open",
                "detector_separable_cube_not_joint_event_posterior",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
            }
        ),
    }


def diagnose_gw_alpha_waveform_eft_bound(
    prior_reweight_path: Path = DEFAULT_PRIOR_REWEIGHT_PATH,
    gr_reference_path: Path = DEFAULT_GR_REFERENCE_PATH,
    imr_reference_path: Path = DEFAULT_IMR_REFERENCE_PATH,
    source_response_path: Path = DEFAULT_SOURCE_RESPONSE_PATH,
) -> dict[str, Any]:
    prior_reweight = load_json(prior_reweight_path)
    gr_reference = load_json(gr_reference_path)
    imr_reference = load_json(imr_reference_path)
    source_response = load_json(source_response_path)
    domain = prior_alpha_domain(prior_reweight)
    waveform_bound = waveform_component_bound(
        gr_reference,
        imr_reference,
        domain,
    )
    eft_bound = eft_truncation_component_bound(
        source_response,
        imr_reference,
        domain,
    )
    packet = packet_with_waveform_eft_bounds(
        prior_reweight["packet"],
        waveform_bound,
        eft_bound,
    )
    evaluation = evaluate_alpha_waveform_eft_bound(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.123_alpha_prior_reweight_sweep",
            "v2.113_lalsuite_imr_projection",
            "v2.112_leading_order_gr_projection",
            "v2.109_source_backed_cubic_inspiral_response",
        ],
        "paths": {
            "prior_reweight": prior_reweight_path.as_posix(),
            "gr_reference": gr_reference_path.as_posix(),
            "imr_reference": imr_reference_path.as_posix(),
            "source_response": source_response_path.as_posix(),
        },
        "alpha_domain": domain,
        "waveform_component_bound": waveform_bound,
        "eft_truncation_component_bound": eft_bound,
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": "waveform_eft_components_bounded_budget_hold_nonclaiming",
        "selected_next_build_action": (
            "calibrate_likelihood_scale_and_joint_event_posterior"
        ),
        "best_next_artifact": (
            "Replace the detector-separable likelihood cube with a joint-event "
            "posterior or an explicit independence proof, and calibrate the "
            "coarse alpha likelihood scale against a noise evidence/null model."
        ),
        "interpretation": (
            "Waveform and EFT truncation rows now carry finite conservative "
            "bounds. This closes the remaining component-level systematics rows "
            "without promoting a framework claim: the top-level budget is held "
            "open until joint-event posterior semantics, likelihood-scale "
            "calibration, and the G8 component are solved."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-reweight", default=str(DEFAULT_PRIOR_REWEIGHT_PATH))
    parser.add_argument("--gr-reference", default=str(DEFAULT_GR_REFERENCE_PATH))
    parser.add_argument("--imr-reference", default=str(DEFAULT_IMR_REFERENCE_PATH))
    parser.add_argument("--source-response", default=str(DEFAULT_SOURCE_RESPONSE_PATH))
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.124/"
            "gw_alpha_waveform_eft_bound.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_waveform_eft_bound(
        prior_reweight_path=Path(args.prior_reweight),
        gr_reference_path=Path(args.gr_reference),
        imr_reference_path=Path(args.imr_reference),
        source_response_path=Path(args.source_response),
    )
    result = canonicalize_json_floats(result)
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
