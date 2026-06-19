"""Sourceability audit for the Weyl/g8 frontier (v2.51).

v2.50 confirmed that g_C and g_8 are the next non-tower frontier directions.
This audit asks whether the existing candidate observables are sourced and
measurement-ready enough to promote those internal directions into a real
framework discriminator.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from explicit_tower_basis import _json_default
from min_experiment_set import HighScatteringMoment
from itb.frameworks.data_driven import DiscoveredDataDriven
from itb.gravitational_observables import BlackHoleEntropyShift, HolographicComplexityRate
from itb.observables import Observable, ScalarForwardAmplitude


PARAMS = [
    "g_4",
    "g_6",
    "g_8",
    "g_R2",
    "g_R3",
    "g_C",
    "g_R2_parity",
    "g_R3_parity",
]

PRIMARY_SOURCES = {
    "hofman_maldacena": {
        "title": "Hofman and Maldacena, Conformal collider physics",
        "url": "https://arxiv.org/abs/0803.1467",
    },
    "conformal_collider_proof": {
        "title": "Hofman et al., A Proof of the Conformal Collider Bounds",
        "url": "https://arxiv.org/abs/1603.03771",
    },
    "brigante_causality": {
        "title": "Brigante et al., Viscosity Bound and Causality Violation",
        "url": "https://arxiv.org/abs/0802.3318",
    },
    "complexity_action": {
        "title": "Brown et al., Complexity Equals Action",
        "url": "https://arxiv.org/abs/1509.07876",
    },
    "action_growth": {
        "title": "Cai et al., Action Growth for AdS Black Holes",
        "url": "https://arxiv.org/abs/1606.08307",
    },
    "black_hole_entropy": {
        "title": "Cheung, Liu, and Remmen, Proof of the WGC from Black Hole Entropy",
        "url": "https://arxiv.org/abs/1801.08546",
    },
    "sharp_swampland": {
        "title": "Caron-Huot et al., Sharp Boundaries for the Swampland",
        "url": "https://arxiv.org/abs/2102.08951",
    },
    "detectors": {
        "title": "Caron-Huot et al., Detectors in weakly-coupled field theories",
        "url": "https://arxiv.org/abs/2209.00008",
    },
    "partial_wave_unitarity": {
        "title": "Bresciani, Levati, and Paradisi, Amplitudes and partial wave unitarity bounds",
        "url": "https://arxiv.org/abs/2504.12855",
    },
}


def _nonzero_jacobian_coefficients(observable: Observable) -> list[str]:
    theory = DiscoveredDataDriven().encode()
    for key in PARAMS:
        theory.coefficients.setdefault(key, 0.0)
    jacobian = observable.jacobian(theory, PARAMS)
    touched = []
    for index, key in enumerate(PARAMS):
        if bool(np.any(np.abs(jacobian[:, index]) > 1e-12)):
            touched.append(key)
    return touched


def _sourceability_row(
    *,
    axis: str,
    route: str,
    implementation: str,
    observable: Observable | None = None,
    static_touched: list[str] | None = None,
    primary_source_keys: list[str],
    source_backed_theory: bool,
    source_backed_axis_mapping: bool,
    external_numeric_measurement: bool,
    measurement_program_status: str,
    status: str,
    blockers: list[str],
) -> dict[str, Any]:
    touched = (
        _nonzero_jacobian_coefficients(observable)
        if observable is not None
        else static_touched or []
    )
    claim_ready = bool(
        source_backed_theory
        and source_backed_axis_mapping
        and external_numeric_measurement
        and axis in touched
    )
    return {
        "axis": axis,
        "route": route,
        "implementation": implementation,
        "implemented_target_coefficients": touched,
        "primary_sources": [PRIMARY_SOURCES[key] for key in primary_source_keys],
        "source_backed_theory": source_backed_theory,
        "source_backed_axis_mapping": source_backed_axis_mapping,
        "external_numeric_measurement": external_numeric_measurement,
        "measurement_program_status": measurement_program_status,
        "status": status,
        "claim_ready": claim_ready,
        "blockers": blockers,
    }


def sourceability_rows() -> list[dict[str, Any]]:
    return [
        _sourceability_row(
            axis="g_C",
            route="conformal_collider_a_over_c_wedge",
            implementation="src/itb/constraints/hofman_maldacena.py",
            static_touched=["g_R2", "g_C"],
            primary_source_keys=["hofman_maldacena", "conformal_collider_proof"],
            source_backed_theory=True,
            source_backed_axis_mapping=True,
            external_numeric_measurement=False,
            measurement_program_status="structural_cft_consistency_bound",
            status="source_backed_structural_bound",
            blockers=[
                "already_in_stack_as_consistency_bound",
                "not_an_external_framework_measurement",
                "many_framework_g_C_values_are_portrait_derived",
            ],
        ),
        _sourceability_row(
            axis="g_C",
            route="holographic_complexity_rate",
            implementation="src/itb/gravitational_observables.py:HolographicComplexityRate",
            observable=HolographicComplexityRate(),
            primary_source_keys=["complexity_action", "action_growth"],
            source_backed_theory=True,
            source_backed_axis_mapping=False,
            external_numeric_measurement=False,
            measurement_program_status="holographic_proxy_toy_normalization",
            status="source_backed_proxy_not_measurement_ready",
            blockers=[
                "toy_kappa_normalization",
                "requires_holographic_dual_identification",
                "no_external_measurement_of_framework_g_C",
            ],
        ),
        _sourceability_row(
            axis="g_C",
            route="black_hole_entropy_shift",
            implementation="src/itb/gravitational_observables.py:BlackHoleEntropyShift",
            observable=BlackHoleEntropyShift(),
            primary_source_keys=["black_hole_entropy"],
            source_backed_theory=True,
            source_backed_axis_mapping=False,
            external_numeric_measurement=False,
            measurement_program_status="thermodynamic_sign_proxy",
            status="source_backed_proxy_not_measurement_ready",
            blockers=[
                "sign_structure_sourced_but_coefficients_are_model_dependent",
                "mixes_g_C_with_g_4_in_engine_observable",
                "no_observed_extremal_black_hole_entropy_shift",
            ],
        ),
        _sourceability_row(
            axis="g_8",
            route="core_scalar_forward_amplitude",
            implementation="src/itb/observables.py:ScalarForwardAmplitude",
            observable=ScalarForwardAmplitude(np.array([0.5, 1.0])),
            primary_source_keys=["sharp_swampland"],
            source_backed_theory=True,
            source_backed_axis_mapping=False,
            external_numeric_measurement=False,
            measurement_program_status="implemented_but_blind_to_g_8",
            status="implemented_core_observable_does_not_touch_axis",
            blockers=[
                "current_core_forward_amplitude_touches_only_g_4_and_g_6",
                "cannot_promote_g_8_cut_from_this_observable",
            ],
        ),
        _sourceability_row(
            axis="g_8",
            route="high_scattering_moment_design_probe",
            implementation="experiments/min_experiment_set.py:HighScatteringMoment",
            observable=HighScatteringMoment(np.array([1.0, 1.5])),
            primary_source_keys=["detectors", "partial_wave_unitarity"],
            source_backed_theory=True,
            source_backed_axis_mapping=False,
            external_numeric_measurement=False,
            measurement_program_status="internal_design_probe_no_program",
            status="source_motivated_design_probe_not_measurement_ready",
            blockers=[
                "engine_mapping_to_exact_g_8_is_toy",
                "no_funded_or_sourced_measurement_program",
                "requires_partial_wave_or_detector_observable_specification",
            ],
        ),
        _sourceability_row(
            axis="g_8",
            route="spin_four_positivity_constraint",
            implementation="src/itb/constraints/spin_four_positivity.py",
            static_touched=["g_4", "g_8", "g_R2", "g_R3"],
            primary_source_keys=["sharp_swampland", "partial_wave_unitarity"],
            source_backed_theory=True,
            source_backed_axis_mapping=True,
            external_numeric_measurement=False,
            measurement_program_status="source_backed_consistency_bound",
            status="source_backed_structural_bound",
            blockers=[
                "constraint_not_external_measurement",
                "axis_mixed_with_g_4_g_R2_g_R3",
                "already_part_of_consistency_reasoning_not_new_data",
            ],
        ),
    ]


def diagnose_weyl_g8_observable_sourceability() -> dict[str, Any]:
    rows = sourceability_rows()
    axis_summary = {}
    for axis in ("g_C", "g_8"):
        axis_rows = [row for row in rows if row["axis"] == axis]
        axis_summary[axis] = {
            "candidate_routes": len(axis_rows),
            "source_backed_theory_routes": sum(
                1 for row in axis_rows if row["source_backed_theory"]
            ),
            "external_numeric_measurement_routes": sum(
                1 for row in axis_rows if row["external_numeric_measurement"]
            ),
            "claim_ready_routes": sum(1 for row in axis_rows if row["claim_ready"]),
            "implemented_routes_touching_axis": [
                row["route"] for row in axis_rows
                if axis in row["implemented_target_coefficients"]
            ],
        }

    claim_ready = [row for row in rows if row["claim_ready"]]
    return {
        "basis": [
            "v2.50_weyl_g8_frontier",
            "implemented_observable_jacobians",
            "primary_sourceability_classification",
        ],
        "candidate_count": len(rows),
        "axis_summary": axis_summary,
        "rows": rows,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "claim_blockers": [
            "no_external_numeric_measurement_for_g_C_or_g_8",
            "g_C_routes_are_structural_or_holographic_proxies",
            "g_8_high_moment_route_is_still_an_internal_design_probe",
            "no_framework_level_source_backed_cut_to_apply_to_v2_50_frontier",
        ],
        "route_status": "sourceability_blocked",
        "best_next_steps": [
            "turn_high_scattering_moment_into_a_sourced_partial_wave_or_detector_observable",
            "separate_native_g_C_framework_values_from_portrait_derived_values",
            "define_promotion_gate_requiring_external_measurement_before_framework_exclusion",
        ],
        "interpretation": (
            "The g_C/g_8 frontier has source-backed theory structure, but no route "
            "currently supplies an external numerical measurement that can be "
            "applied as a framework-level discriminator. g_C is source-rich but "
            "mostly structural or holographic-proxy based; g_8 has the clearest "
            "measurement concept but remains an internal design probe."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.51/weyl_g8_observable_sourceability.json",
    )
    args = parser.parse_args()

    result = diagnose_weyl_g8_observable_sourceability()
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
