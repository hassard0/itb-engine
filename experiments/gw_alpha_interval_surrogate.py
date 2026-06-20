"""Interval-derived alpha-bar covariance surrogate for v2.103."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_cubic_source_native_adapter import (
    evaluate_gw_cubic_source_native_packet,
    liu_yunes_paper_summary_source_native_candidate,
)


VERSION = "v2.103"
Z_SCORE_90_CENTRAL = 1.6448536269514722
ASYMMETRY_WARNING_RATIO = 1.25


def _float(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"expected numeric interval value, got {value!r}")
    return float(value)


def interval_to_gaussian_surrogate(row: dict[str, Any]) -> dict[str, float]:
    central = _float(row["central"])
    lower = _float(row["lower_90"])
    upper = _float(row["upper_90"])
    sigma_minus = (central - lower) / Z_SCORE_90_CENTRAL
    sigma_plus = (upper - central) / Z_SCORE_90_CENTRAL
    sigma_average = 0.5 * (sigma_minus + sigma_plus)
    asymmetry_ratio = (
        max(sigma_minus, sigma_plus) / min(sigma_minus, sigma_plus)
        if min(sigma_minus, sigma_plus) > 0.0
        else float("inf")
    )
    return {
        "central": central,
        "lower_90": lower,
        "upper_90": upper,
        "sigma_minus_from_90": sigma_minus,
        "sigma_plus_from_90": sigma_plus,
        "sigma_average": sigma_average,
        "variance_average": sigma_average * sigma_average,
        "asymmetry_ratio": asymmetry_ratio,
        "asymmetric_interval": asymmetry_ratio > ASYMMETRY_WARNING_RATIO,
    }


def build_alpha_interval_surrogate_packet() -> dict[str, Any]:
    packet = liu_yunes_paper_summary_source_native_candidate()
    constraints = packet["parameter_constraints"]
    rows = {
        parameter: interval_to_gaussian_surrogate(constraints[parameter])
        for parameter in ("alpha_bar_1", "alpha_bar_2")
    }
    covariance_matrix = [
        [rows["alpha_bar_1"]["variance_average"], 0.0],
        [0.0, rows["alpha_bar_2"]["variance_average"]],
    ]
    packet.update(
        {
            "label": "liu_yunes_interval_gaussian_surrogate_nonclaiming",
            "posterior_or_likelihood_export": {
                "status": "paper_interval_gaussian_surrogate_not_likelihood",
                "kind": "diagonal_gaussian_from_marginal_90_intervals",
                "parameters": ["alpha_bar_1", "alpha_bar_2"],
                "source_limit": (
                    "uses marginal intervals only; no posterior samples, no "
                    "correlation, no source-native likelihood surface"
                ),
            },
            "source_parameter_covariance": {
                "parameters": ["alpha_bar_1", "alpha_bar_2"],
                "matrix": covariance_matrix,
                "correlation_status": "unknown_forced_zero_nonclaiming",
            },
            "systematics_budget": "summary_interval_surrogate_not_adapter_budget",
            "shared_eft_domain": "summary_interval_surrogate_not_bounded_domain",
            "validation_reference": "v2.103_interval_surrogate",
        }
    )
    return packet


def diagnose_gw_alpha_interval_surrogate() -> dict[str, Any]:
    surrogate_packet = build_alpha_interval_surrogate_packet()
    adapter_evaluation = evaluate_gw_cubic_source_native_packet(surrogate_packet)
    constraints = surrogate_packet["parameter_constraints"]
    parameter_rows = {
        parameter: interval_to_gaussian_surrogate(constraints[parameter])
        for parameter in ("alpha_bar_1", "alpha_bar_2")
    }
    covariance = surrogate_packet["source_parameter_covariance"]
    asymmetric_parameters = [
        parameter
        for parameter, row in parameter_rows.items()
        if row["asymmetric_interval"]
    ]

    return {
        "version": VERSION,
        "basis": [
            "v2.102_gw_cubic_source_native_adapter",
            "arXiv_2407.08929_alpha_bar_marginal_intervals",
        ],
        "surrogate_scope": (
            "development_covariance_fixture_from_paper_intervals_only"
        ),
        "z_score_90_central": Z_SCORE_90_CENTRAL,
        "asymmetry_warning_ratio": ASYMMETRY_WARNING_RATIO,
        "parameter_surrogates": parameter_rows,
        "surrogate_packet_label": surrogate_packet["label"],
        "surrogate_covariance": covariance,
        "adapter_evaluation": adapter_evaluation,
        "asymmetric_parameters": asymmetric_parameters,
        "interval_asymmetry_exceeds_gaussian_limit": bool(asymmetric_parameters),
        "claimable_discriminator_now": False,
        "route_status": (
            "alpha_interval_surrogate_built_nonclaiming_reanalysis_required"
        ),
        "selected_next_build_action": (
            "build_public_gw170608_reanalysis_run_manifest"
        ),
        "best_next_artifact": (
            "A run manifest that lists public strain inputs, O2 posterior "
            "validation inputs, waveform implementation requirements, sampler "
            "settings, and output files needed to reproduce the alpha_bar "
            "likelihood instead of using this interval-only surrogate."
        ),
        "interpretation": (
            "The paper intervals can seed a diagonal Gaussian development "
            "fixture, but the intervals are asymmetric and provide no "
            "correlation. The v2.102 gate correctly rejects the surrogate as a "
            "claim source, so the next concrete step is a reproducible public "
            "GW170608 reanalysis manifest."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.103/gw_alpha_interval_surrogate.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_interval_surrogate()
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
