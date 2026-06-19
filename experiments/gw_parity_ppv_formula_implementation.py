"""GW parity source-native amplitude formula implementation (v2.64).

v2.63 specified a PPV/native adapter but left the formula work open. This
iteration implements the source-native amplitude log-gain layer for Ng and
Callister while keeping helicity harmonization, posterior ingestion, and engine
projection blocked.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from itb.gw_parity import (
    callister_sgwb_amplitude_log_gain,
    callister_sgwb_energy_hyperbolic_argument,
    ng_kappa_amplitude_log_gain,
    normalize_discrete_posterior,
)


def _log_gain_row(label: str, point) -> dict[str, Any]:
    return {
        "label": label,
        "log_gain": point.to_dict(),
        "formula_ready": True,
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "blockers": [
            "helicity_convention_not_harmonized_across_sources",
            "posterior_release_parser_not_implemented",
            "ppv_beta1_normalization_not_finalized",
            "engine_projection_out_of_scope",
        ],
    }


def diagnose_gw_parity_ppv_formula_implementation() -> dict[str, Any]:
    ng_zero = ng_kappa_amplitude_log_gain(
        kappa_gpc_inv=0.0,
        distance_gpc=1.0,
        frequency_hz=100.0,
    )
    ng_example = ng_kappa_amplitude_log_gain(
        kappa_gpc_inv=-0.019,
        distance_gpc=2.0,
        frequency_hz=200.0,
    )
    callister_distance = callister_sgwb_amplitude_log_gain(
        kappa_d=0.1,
        kappa_z=0.0,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )
    callister_redshift = callister_sgwb_amplitude_log_gain(
        kappa_d=0.0,
        kappa_z=0.1,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )
    callister_energy_argument = callister_sgwb_energy_hyperbolic_argument(
        kappa_d=0.1,
        kappa_z=0.0,
        distance_gpc=2.0,
        redshift=0.3,
        frequency_hz=100.0,
    )
    posterior_check = normalize_discrete_posterior(
        coordinates=[-1.0, 0.0, 1.0],
        density=[0.0, 2.0, 0.0],
    )

    rows = [
        _log_gain_row("ng_zero_control", ng_zero),
        _log_gain_row("ng_source_native_example", ng_example),
        _log_gain_row("callister_distance_term_example", callister_distance),
        _log_gain_row("callister_redshift_term_example", callister_redshift),
        _log_gain_row(
            "callister_energy_density_argument_example",
            callister_energy_argument,
        ),
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "basis": [
            "v2.63_gw_parity_ppv_adapter_spec",
            "Ng_2305.05844_eq_waveform_modification",
            "Callister_2312.12532_eq_birefringent_v",
            "Callister_public_code_energy_density_2v_convention",
            "Jenks_2305.10478_parameterized_amplitude_branch",
        ],
        "implemented_layer": "source_native_amplitude_log_gain",
        "formula_ready_routes": [
            "ng_kappa_amplitude_log_gain",
            "callister_sgwb_amplitude_log_gain",
            "callister_sgwb_energy_hyperbolic_argument",
            "normalize_discrete_posterior",
        ],
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "posterior_normalizer_ready": posterior_check["ready"],
        "posterior_normalizer_norm": posterior_check["normalized_norm"],
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "native_amplitude_formula_ready_projection_blocked",
        "best_next_artifact": (
            "A release-specific posterior parser for the Ng or Callister public data, "
            "feeding the source-native log-gain layer without engine projection."
        ),
        "interpretation": (
            "The source-native amplitude formulas are implemented and tested. "
            "This moves the route from formula-specification to non-promoting "
            "formula code. The Callister SGWB energy-density route exposes the "
            "public-code hyperbolic argument A=2v_p separately from the waveform "
            "log-gain v_p, but this does not harmonize helicity conventions, "
            "finalize PPV beta normalization, ingest release files, or project to "
            "engine axes."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.64/gw_parity_ppv_formula_implementation.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ppv_formula_implementation()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
