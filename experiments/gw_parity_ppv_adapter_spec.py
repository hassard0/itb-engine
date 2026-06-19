"""GW parity PPV/native adapter specification (v2.63).

v2.62 registered Ng and Callister as native non-promoting packets. This spec
defines the next adapter layer: a shared propagation basis for amplitude
birefringence, while keeping engine-axis projection out of scope.
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


def _spec(
    *,
    label: str,
    native_packet: str,
    source_urls: dict[str, str],
    native_axes: list[str],
    target_basis: str,
    target_axes: list[str],
    source_support: list[str],
    required_formula_components: list[str],
    blockers: list[str],
    required_validation_tests: list[str],
) -> dict[str, Any]:
    implementation_ready = not blockers
    return {
        "label": label,
        "native_packet": native_packet,
        "source_urls": source_urls,
        "native_axes": native_axes,
        "target_basis": target_basis,
        "target_axes": target_axes,
        "source_support": source_support,
        "required_formula_components": required_formula_components,
        "implementation_ready": implementation_ready,
        "engine_projection_allowed": False,
        "blockers": blockers,
        "required_validation_tests": required_validation_tests,
        "status": (
            "ppv_adapter_ready_nonpromoting"
            if implementation_ready
            else "ppv_adapter_spec_defined_formula_missing"
        ),
    }


def adapter_specs() -> list[dict[str, Any]]:
    return [
        _spec(
            label="ng_kappa_to_ppv_amplitude_branch",
            native_packet="ng_gwtc3_kappa_at_100hz",
            source_urls={
                "measurement": "https://arxiv.org/abs/2305.05844",
                "formalism": "https://arxiv.org/abs/2305.10478",
                "repository": (
                    "https://github.com/thomasckng/"
                    "Constraining-Birefringence-with-GWTC-3"
                ),
            },
            native_axes=[
                "kappa_Gpc_inv",
                "f_ref_hz=100",
                "comoving_distance_Gpc",
            ],
            target_basis="ppv_amplitude_birefringence_branch",
            target_axes=[
                "ppv_amplitude_distance_slope",
                "ppv_frequency_power_n1",
                "helicity_sign",
            ],
            source_support=[
                "Ng reports amplitude birefringence at 100 Hz in Gpc^-1.",
                "Jenks supplies parameterized amplitude/velocity parity propagation language.",
            ],
            required_formula_components=[
                "native exponent convention for h_L/h_R",
                "Jenks PPV amplitude-branch axis and sign convention",
                "distance normalization and cosmology convention",
                "frequency reference conversion at 100 Hz",
                "posterior sample parser for kappa",
            ],
            blockers=[
                "missing_explicit_native_to_ppv_formula",
                "missing_helicity_sign_convention",
                "missing_distance_normalization",
                "missing_posterior_parser",
                "engine_projection_out_of_scope",
            ],
            required_validation_tests=[
                "zero_kappa_maps_to_zero_ppv_amplitude",
                "positive_negative_kappa_preserve_helicity_sign",
                "100hz_reference_frequency_roundtrip",
                "posterior_mass_normalizes_to_one",
            ],
        ),
        _spec(
            label="callister_kappaD_kappaz_to_ppv_amplitude_branch",
            native_packet="callister_sgwb_kappaD_kappaz",
            source_urls={
                "measurement": "https://arxiv.org/abs/2312.12532",
                "formalism": "https://arxiv.org/abs/2305.10478",
                "repository": "https://github.com/tcallister/stochastic-birefringence",
            },
            native_axes=[
                "kappa_D",
                "kappa_z",
                "f_ref_hz=100",
                "comoving_distance_Gpc",
                "redshift",
            ],
            target_basis="ppv_amplitude_birefringence_branch",
            target_axes=[
                "ppv_amplitude_distance_slope",
                "ppv_amplitude_redshift_slope",
                "ppv_frequency_power_n1",
                "helicity_sign",
            ],
            source_support=[
                "Callister uses kappa_D/kappa_z for SGWB amplitude birefringence.",
                "The paper connects the stochastic-birefringence parameters to the PPV literature.",
            ],
            required_formula_components=[
                "kappa_D distance term",
                "kappa_z redshift term",
                "joint posterior-grid loader",
                "normalization between SGWB exponent and PPV amplitude branch",
                "cosmology convention used for distance/redshift conversion",
            ],
            blockers=[
                "missing_explicit_native_to_ppv_formula",
                "missing_joint_posterior_parser",
                "missing_distance_redshift_normalization",
                "engine_projection_out_of_scope",
            ],
            required_validation_tests=[
                "zero_kappaD_kappaz_maps_to_zero_ppv_amplitude",
                "posterior_grid_integrates_to_one",
                "distance_and_redshift_terms_remain_separable",
                "100hz_reference_frequency_roundtrip",
            ],
        ),
    ]


def diagnose_gw_parity_ppv_adapter_spec() -> dict[str, Any]:
    specs = adapter_specs()
    ready = [spec for spec in specs if spec["implementation_ready"]]
    blocker_counts: dict[str, int] = {}
    for spec in specs:
        for blocker in spec["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "basis": [
            "v2.62_gw_parity_native_packet_registry",
            "Jenks_parameterized_parity_formalism",
            "native_packets_nonpromoting",
        ],
        "target_intermediate_basis": "ppv_amplitude_birefringence_branch",
        "spec_count": len(specs),
        "implementation_ready_specs": [spec["label"] for spec in ready],
        "implementation_ready_count": len(ready),
        "engine_projection_allowed_now": False,
        "claimable_discriminator_now": False,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": specs,
        "route_status": "ppv_adapter_spec_defined_formula_missing",
        "best_next_artifact": (
            "A non-promoting PPV adapter implementation for one native packet, "
            "starting with explicit formula and posterior parser tests."
        ),
        "interpretation": (
            "The shared PPV amplitude branch is the right intermediate target, "
            "but neither native packet can be numerically transformed until the "
            "formula, sign, normalization, and parser obligations are implemented."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.63/gw_parity_ppv_adapter_spec.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ppv_adapter_spec()
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
