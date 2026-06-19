"""GW parity likelihood-to-engine adapter readiness audit (v2.61).

v2.60 found real GW parity constraints but no engine-ready measurement packet.
This audit separates public source-side reproduction material from the harder
claim that a published parameter is already normalized to the engine axes
g_R2_parity/g_R3_parity.
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


def _adapter_blockers(
    *,
    source_likelihood_material_public: bool,
    published_numeric_constraint: bool,
    maps_to_engine_axes: bool,
    source_backed_operator_map: bool,
    dimensional_conversion_ready: bool,
    frequency_normalization_ready: bool,
    framework_exclusion_math_ready: bool,
) -> list[str]:
    blockers = []
    if not source_likelihood_material_public:
        blockers.append("missing_public_source_likelihood_material")
    if not published_numeric_constraint:
        blockers.append("missing_published_numeric_constraint")
    if not maps_to_engine_axes:
        blockers.append("missing_engine_axis_map")
    if not source_backed_operator_map:
        blockers.append("missing_source_backed_operator_map")
    if not dimensional_conversion_ready:
        blockers.append("missing_dimensionful_to_engine_normalization")
    if not frequency_normalization_ready:
        blockers.append("missing_frequency_normalization")
    if not framework_exclusion_math_ready:
        blockers.append("missing_framework_exclusion_math")
    return blockers


def _row(
    *,
    label: str,
    source: dict[str, str],
    measured_parameters: list[str],
    public_code: bool,
    public_data: bool,
    public_docs: bool,
    source_likelihood_material_public: bool,
    published_numeric_constraint: bool,
    maps_to_engine_axes: bool,
    source_backed_operator_map: bool,
    dimensional_conversion_ready: bool,
    frequency_normalization_ready: bool,
    framework_exclusion_math_ready: bool,
    adapter_role: str,
    notes: list[str],
) -> dict[str, Any]:
    blockers = _adapter_blockers(
        source_likelihood_material_public=source_likelihood_material_public,
        published_numeric_constraint=published_numeric_constraint,
        maps_to_engine_axes=maps_to_engine_axes,
        source_backed_operator_map=source_backed_operator_map,
        dimensional_conversion_ready=dimensional_conversion_ready,
        frequency_normalization_ready=frequency_normalization_ready,
        framework_exclusion_math_ready=framework_exclusion_math_ready,
    )
    source_side_ready = source_likelihood_material_public and published_numeric_constraint
    engine_adapter_ready = not blockers
    return {
        "label": label,
        "source": source,
        "measured_parameters": measured_parameters,
        "public_material": {
            "code": public_code,
            "data": public_data,
            "docs": public_docs,
            "source_likelihood_material_public": source_likelihood_material_public,
        },
        "published_numeric_constraint": published_numeric_constraint,
        "source_side_likelihood_ready": source_side_ready,
        "engine_adapter_ready": engine_adapter_ready,
        "maps_to_engine_axes": maps_to_engine_axes,
        "source_backed_operator_map": source_backed_operator_map,
        "dimensional_conversion_ready": dimensional_conversion_ready,
        "frequency_normalization_ready": frequency_normalization_ready,
        "framework_exclusion_math_ready": framework_exclusion_math_ready,
        "adapter_blockers": blockers,
        "adapter_role": adapter_role,
        "notes": notes,
    }


def candidate_rows() -> list[dict[str, Any]]:
    return [
        _row(
            label="ng_gwtc3_kappa_at_100hz",
            source={
                "paper": "https://arxiv.org/abs/2305.05844",
                "code": (
                    "https://github.com/thomasckng/"
                    "Constraining-Birefringence-with-GWTC-3"
                ),
                "data": "https://zenodo.org/records/7935107",
            },
            measured_parameters=[
                "kappa_Gpc^-1_at_100_Hz",
                "M_PV_lower_bound_GeV",
            ],
            public_code=True,
            public_data=True,
            public_docs=True,
            source_likelihood_material_public=True,
            published_numeric_constraint=True,
            maps_to_engine_axes=False,
            source_backed_operator_map=False,
            dimensional_conversion_ready=False,
            frequency_normalization_ready=False,
            framework_exclusion_math_ready=False,
            adapter_role="best_source_side_reproduction_seed",
            notes=[
                "The paper reports kappa=-0.019^{+0.038}_{-0.029} Gpc^-1 at 100 Hz.",
                "The public repository and Zenodo release can seed a source-side posterior loader.",
                "The dimensionful kappa/M_PV convention is not the engine's dimensionless g_R2/g_R3 basis.",
            ],
        ),
        _row(
            label="callister_sgwb_kappaD_kappaz",
            source={
                "paper": "https://arxiv.org/abs/2312.12532",
                "code": "https://github.com/tcallister/stochastic-birefringence",
                "data": "https://zenodo.org/doi/10.5281/zenodo.10384997",
                "docs": "https://tcallister.github.io/stochastic-birefringence/",
            },
            measured_parameters=["kappa_D", "kappa_z"],
            public_code=True,
            public_data=True,
            public_docs=True,
            source_likelihood_material_public=True,
            published_numeric_constraint=True,
            maps_to_engine_axes=False,
            source_backed_operator_map=False,
            dimensional_conversion_ready=False,
            frequency_normalization_ready=False,
            framework_exclusion_math_ready=False,
            adapter_role="best_sgwb_public_release_seed",
            notes=[
                "The arXiv record advertises public code and data for regenerating results.",
                "The reported joint order-0.1 constraint is on generic SGWB birefringence parameters.",
                "The kappa_D/kappa_z parameter basis is not an engine-axis likelihood.",
            ],
        ),
        _row(
            label="jenks_parameterized_parity_formalism",
            source={"paper": "https://arxiv.org/abs/2305.10478"},
            measured_parameters=["generic_parity_parameters", "ppE_mapping"],
            public_code=False,
            public_data=False,
            public_docs=False,
            source_likelihood_material_public=False,
            published_numeric_constraint=False,
            maps_to_engine_axes=False,
            source_backed_operator_map=True,
            dimensional_conversion_ready=False,
            frequency_normalization_ready=False,
            framework_exclusion_math_ready=False,
            adapter_role="operator_language_seed_not_measurement",
            notes=[
                "The formalism is source-backed and maps generic parity parameters to ppE language.",
                "It is not an external measurement likelihood or engine normalization by itself.",
            ],
        ),
        _row(
            label="zhu_gwtc3_modified_propagation",
            source={"paper": "https://arxiv.org/abs/2304.09025"},
            measured_parameters=[
                "parity_modified_propagation_parameters",
                "lorentz_modified_propagation_parameters",
            ],
            public_code=False,
            public_data=True,
            public_docs=False,
            source_likelihood_material_public=False,
            published_numeric_constraint=True,
            maps_to_engine_axes=False,
            source_backed_operator_map=False,
            dimensional_conversion_ready=False,
            frequency_normalization_ready=False,
            framework_exclusion_math_ready=False,
            adapter_role="published_constraint_not_public_adapter_seed",
            notes=[
                "The paper analyzes open LIGO-Virgo-KAGRA events.",
                "No dedicated public likelihood/code release was identified in this audit.",
                "The modified-propagation parameterization is not projected to g_R2_parity/g_R3_parity.",
            ],
        ),
        _row(
            label="engine_gravitational_birefringence_observable",
            source={
                "implementation": (
                    "src/itb/gravitational_observables.py:"
                    "GravitationalBirefringence"
                )
            },
            measured_parameters=["g_R2_parity + omega/omega0 * g_R3_parity"],
            public_code=False,
            public_data=False,
            public_docs=False,
            source_likelihood_material_public=False,
            published_numeric_constraint=False,
            maps_to_engine_axes=True,
            source_backed_operator_map=False,
            dimensional_conversion_ready=False,
            frequency_normalization_ready=False,
            framework_exclusion_math_ready=False,
            adapter_role="engine_target_basis_toy_normalization",
            notes=[
                "The engine observable touches the right axes.",
                "Its omega0 and linear normalization are internal toy conventions until an adapter is derived.",
            ],
        ),
    ]


def diagnose_gw_parity_adapter_readiness() -> dict[str, Any]:
    rows = candidate_rows()
    source_ready = [row for row in rows if row["source_side_likelihood_ready"]]
    engine_ready = [row for row in rows if row["engine_adapter_ready"]]
    failure_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["adapter_blockers"]:
            failure_counts[blocker] = failure_counts.get(blocker, 0) + 1

    return {
        "basis": [
            "v2.59_parity_route_split",
            "v2.60_gw_parity_measurement_packet_search",
            "public_code_data_audit_2026_06_19",
        ],
        "target_axis": "g_R2_parity/g_R3_parity",
        "candidate_count": len(rows),
        "source_side_likelihood_ready_routes": [row["label"] for row in source_ready],
        "source_side_likelihood_ready_count": len(source_ready),
        "engine_adapter_ready_routes": [row["label"] for row in engine_ready],
        "engine_adapter_ready_count": len(engine_ready),
        "claimable_discriminator_now": bool(engine_ready),
        "adapter_blocker_counts": dict(sorted(failure_counts.items())),
        "legacy_stack_warning": (
            "The existing LIGOBirefringenceBound is a legacy toy constraint and "
            "must not be treated as an external claim-ready likelihood."
        ),
        "can_build_nonpromoting_source_loader_now": bool(source_ready),
        "can_promote_engine_packet_now": bool(engine_ready),
        "recommended_intermediate_basis": {
            "name": "gw_parity_native_or_ppv_basis",
            "native_axes": [
                "ng:kappa_Gpc^-1_at_100_Hz",
                "callister:kappa_D",
                "callister:kappa_z",
                "jenks:ppE_or_parameterized_parity_basis",
            ],
            "engine_projection_status": (
                "blocked_pending_source_backed_operator_normalization"
            ),
        },
        "rows": rows,
        "route_status": "public_gw_likelihood_material_exists_engine_adapter_missing",
        "best_next_artifact": (
            "A native-parameter or PPV-basis source packet for Ng and/or "
            "Callister, followed by a source-backed operator-normalization "
            "concordance before any engine g_R2_parity/g_R3_parity projection."
        ),
        "interpretation": (
            "Public reproduction material exists for source-side GW parity constraints, "
            "but no audited route supplies the operator map, dimensional conversion, "
            "frequency normalization, and framework-exclusion math required for an "
            "engine claim packet."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.61/gw_parity_adapter_readiness.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_adapter_readiness()
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
