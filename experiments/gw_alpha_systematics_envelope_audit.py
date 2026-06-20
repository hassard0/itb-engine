"""Quantitative proxy envelopes for remaining alpha-packet systematics."""

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
from experiments.gw_alpha_systematics_budget_gate import (
    evaluate_alpha_systematics_budget,
    load_json,
)
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
)


VERSION = "v2.119"
DEFAULT_GR_REFERENCE_PATH = Path(
    "experiments/results/v2.112/gw_gr_inspiral_reference_projection.json"
)
DEFAULT_IMR_REFERENCE_PATH = Path(
    "experiments/results/v2.113/gw_lalsuite_imr_projection.json"
)
DEFAULT_MARGINAL_RESULT_PATH = Path(
    "experiments/results/v2.115/gw_lalsuite_marginal_alpha_likelihood.json"
)
DEFAULT_PARTIAL_SYSTEMATICS_PATH = Path(
    "experiments/results/v2.118/gw_alpha_systematics_budget_gate.json"
)


def _projection_delta(
    left: dict[str, Any],
    right: dict[str, Any],
    parameter: str,
    field: str,
) -> float:
    key = f"{parameter}_{field}"
    return float(right["network_projection"][key] - left["network_projection"][key])


def waveform_systematics_proxy(
    gr_reference: dict[str, Any],
    imr_reference: dict[str, Any],
) -> dict[str, Any]:
    rows = {}
    max_abs_delta = 0.0
    for parameter in ("alpha_bar_1", "alpha_bar_2"):
        abs_delta = _projection_delta(gr_reference, imr_reference, parameter, "abs_mean")
        real_delta = _projection_delta(
            gr_reference,
            imr_reference,
            parameter,
            "real_mean",
        )
        imag_delta = _projection_delta(
            gr_reference,
            imr_reference,
            parameter,
            "imag_mean",
        )
        max_abs_delta = max(max_abs_delta, abs(abs_delta), abs(real_delta), abs(imag_delta))
        rows[parameter] = {
            "leading_order_gr_abs_mean": gr_reference["network_projection"][
                f"{parameter}_abs_mean"
            ],
            "imrphenomd_abs_mean": imr_reference["network_projection"][
                f"{parameter}_abs_mean"
            ],
            "abs_mean_delta": abs_delta,
            "real_mean_delta": real_delta,
            "imag_mean_delta": imag_delta,
        }
    return {
        "status": "open",
        "proxy_kind": "leading_order_gr_vs_lalsuite_imrphenomd_projection_delta",
        "parameters": rows,
        "max_network_projection_component_delta": max_abs_delta,
        "closure_target": (
            "Replace this proxy with source-backed cubic-EFT IMR waveform "
            "uncertainty, not just GR-baseline comparison."
        ),
    }


def detector_calibration_proxy(imr_reference: dict[str, Any]) -> dict[str, Any]:
    network = imr_reference["network_projection"]
    spreads = {
        "alpha_bar_1_abs_detector_spread": network[
            "alpha_bar_1_abs_detector_spread"
        ],
        "alpha_bar_2_abs_detector_spread": network[
            "alpha_bar_2_abs_detector_spread"
        ],
    }
    return {
        "status": "open",
        "proxy_kind": "h1_l1_projection_spread_not_calibration_model",
        "detector_spreads": spreads,
        "max_abs_detector_spread": max(abs(value) for value in spreads.values()),
        "closure_target": (
            "Propagate H1/L1 calibration amplitude-phase uncertainty envelopes "
            "through the alpha likelihood."
        ),
    }


def prior_sensitivity_proxy(marginal_result: dict[str, Any]) -> dict[str, Any]:
    network = marginal_result["network_likelihood"]
    marginal = network["best_marginal_grid_point"]
    profile = network["best_profile_grid_point"]
    shift = math.sqrt(
        (float(profile["alpha_bar_1"]) - float(marginal["alpha_bar_1"])) ** 2
        + (float(profile["alpha_bar_2"]) - float(marginal["alpha_bar_2"])) ** 2
    )
    log_gap = float(profile["profile_log_likelihood"]) - float(
        marginal["log_marginal_likelihood"]
    )
    return {
        "status": "open",
        "proxy_kind": "marginal_vs_profile_best_point_shift",
        "best_marginal_grid_point": marginal,
        "best_profile_grid_point": profile,
        "alpha_best_point_euclidean_shift": shift,
        "profile_minus_marginal_log_likelihood_gap": log_gap,
        "closure_target": (
            "Run a posterior sampler or prior-weight sweep that demonstrates "
            "stable alpha constraints under justified nuisance priors."
        ),
    }


def eft_truncation_proxy(imr_reference: dict[str, Any]) -> dict[str, Any]:
    window = imr_reference["detector_projections"][0]["lalsuite_imr_projection"][
        "frequency_window"
    ]
    v_f_max = float(window["v_f_max"])
    next_order_suppression = v_f_max * v_f_max
    return {
        "status": "open",
        "proxy_kind": "dimensionless_next_pn_power_v_f_squared",
        "v_f_max": v_f_max,
        "next_order_power_suppression_proxy": next_order_suppression,
        "closure_target": (
            "Attach source-backed higher-order cubic-EFT coefficient or "
            "remainder bound over the alpha confidence domain."
        ),
    }


def quantitative_open_systematics_evidence(
    gr_reference: dict[str, Any],
    imr_reference: dict[str, Any],
    marginal_result: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "waveform_systematics": waveform_systematics_proxy(
            gr_reference,
            imr_reference,
        ),
        "detector_calibration": detector_calibration_proxy(imr_reference),
        "prior_sensitivity": prior_sensitivity_proxy(marginal_result),
        "eft_truncation": eft_truncation_proxy(imr_reference),
    }


def packet_with_quantitative_systematics_envelopes(
    partial_packet: dict[str, Any],
    gr_reference: dict[str, Any],
    imr_reference: dict[str, Any],
    marginal_result: dict[str, Any],
) -> dict[str, Any]:
    packet = deepcopy(partial_packet)
    evidence = packet["systematics_budget"]["evidence"]
    evidence.update(
        quantitative_open_systematics_evidence(
            gr_reference,
            imr_reference,
            marginal_result,
        )
    )
    packet["label"] = "v2_119_quantified_systematics_alpha_packet"
    packet["systematics_budget"]["evidence"] = evidence
    packet["systematics_budget"]["components"] = {
        component: row["status"] for component, row in evidence.items()
    }
    packet["systematics_budget"]["status"] = "open"
    packet["validation_reference"] = "v2.119_alpha_systematics_envelope_audit"
    return packet


def evaluate_alpha_systematics_envelopes(
    packet: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    budget_eval = evaluate_alpha_systematics_budget(packet)
    evidence = packet["systematics_budget"]["evidence"]
    quantified_open = [
        component
        for component in (
            "waveform_systematics",
            "detector_calibration",
            "prior_sensitivity",
            "eft_truncation",
        )
        if "proxy_kind" in evidence[component]
    ]
    return {
        "quantitative_envelopes_ready": len(quantified_open) == 4,
        "quantified_open_components": quantified_open,
        "bounded_components": budget_eval["bounded_components"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "removed_v2_118_subblockers": [
            "unquantified_waveform_systematics_proxy",
            "unquantified_detector_spread_proxy",
            "unquantified_prior_sensitivity_proxy",
            "unquantified_eft_truncation_proxy",
        ],
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_not_closed",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "proxy_envelopes_not_calibrated_systematics_bounds",
            }
        ),
    }


def diagnose_gw_alpha_systematics_envelope_audit(
    gr_reference_path: Path = DEFAULT_GR_REFERENCE_PATH,
    imr_reference_path: Path = DEFAULT_IMR_REFERENCE_PATH,
    marginal_result_path: Path = DEFAULT_MARGINAL_RESULT_PATH,
    partial_systematics_path: Path = DEFAULT_PARTIAL_SYSTEMATICS_PATH,
) -> dict[str, Any]:
    gr_reference = load_json(gr_reference_path)
    imr_reference = load_json(imr_reference_path)
    marginal_result = load_json(marginal_result_path)
    partial = load_json(partial_systematics_path)
    packet = packet_with_quantitative_systematics_envelopes(
        partial["packet"],
        gr_reference,
        imr_reference,
        marginal_result,
    )
    evaluation = evaluate_alpha_systematics_envelopes(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.118_alpha_systematics_budget_gate",
            "v2.113_lalsuite_imr_projection",
            "v2.112_leading_order_gr_projection",
            "v2.115_marginal_alpha_likelihood",
        ],
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": "alpha_systematics_proxies_quantified_nonclaiming",
        "selected_next_build_action": (
            "replace_proxy_envelopes_with_calibrated_systematics_bounds"
        ),
        "best_next_artifact": (
            "Replace each proxy envelope with a calibrated source-backed "
            "systematics bound that can change component status from open to "
            "bounded under the v2.102 adapter."
        ),
        "interpretation": (
            "The four remaining open systematics are now quantified by explicit "
            "proxy envelopes. This improves the audit surface but does not close "
            "the systematics budget because proxy envelopes are not calibrated "
            "waveform, calibration, prior, or EFT-truncation bounds."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gr-reference", default=str(DEFAULT_GR_REFERENCE_PATH))
    parser.add_argument("--imr-reference", default=str(DEFAULT_IMR_REFERENCE_PATH))
    parser.add_argument("--marginal-result", default=str(DEFAULT_MARGINAL_RESULT_PATH))
    parser.add_argument(
        "--partial-systematics",
        default=str(DEFAULT_PARTIAL_SYSTEMATICS_PATH),
    )
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.119/"
            "gw_alpha_systematics_envelope_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_systematics_envelope_audit(
        gr_reference_path=Path(args.gr_reference),
        imr_reference_path=Path(args.imr_reference),
        marginal_result_path=Path(args.marginal_result),
        partial_systematics_path=Path(args.partial_systematics),
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
