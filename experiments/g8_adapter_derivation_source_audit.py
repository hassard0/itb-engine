"""Source-backed g_8 adapter derivation audit (v2.86)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


DERIVATION_REQUIREMENTS = (
    "detector_or_energy_correlator_observable",
    "source_backed_operator_identity_to_engine_g8",
    "public_g8_jacobian_or_projection",
    "public_covariance_or_likelihood",
    "bounded_low_energy_qg_eft_domain",
    "component_level_systematics_budget",
    "registered_framework_exclusion_math",
)


def _candidate(
    *,
    label: str,
    title: str,
    source_url: str,
    source_role: str,
    detector_or_energy_observable: bool,
    wilson_coefficient_formalism: bool,
    source_backed_operator_identity_to_engine_g8: bool,
    public_g8_jacobian_or_projection: bool,
    public_covariance_or_likelihood: bool,
    bounded_low_energy_qg_eft_domain: bool,
    component_level_systematics_budget: bool,
    registered_framework_exclusion_math: bool,
    notes: list[str],
) -> dict[str, Any]:
    gates = {
        "detector_or_energy_correlator_observable": detector_or_energy_observable,
        "wilson_coefficient_formalism": wilson_coefficient_formalism,
        "source_backed_operator_identity_to_engine_g8": (
            source_backed_operator_identity_to_engine_g8
        ),
        "public_g8_jacobian_or_projection": public_g8_jacobian_or_projection,
        "public_covariance_or_likelihood": public_covariance_or_likelihood,
        "bounded_low_energy_qg_eft_domain": bounded_low_energy_qg_eft_domain,
        "component_level_systematics_budget": component_level_systematics_budget,
        "registered_framework_exclusion_math": registered_framework_exclusion_math,
    }
    blockers = []
    if not detector_or_energy_observable:
        blockers.append("detector_or_energy_correlator_observable_missing")
    if not source_backed_operator_identity_to_engine_g8:
        blockers.append("source_backed_operator_identity_to_engine_g8_missing")
    if not public_g8_jacobian_or_projection:
        blockers.append("public_g8_jacobian_or_projection_missing")
    if not public_covariance_or_likelihood:
        blockers.append("public_covariance_or_likelihood_missing")
    if not bounded_low_energy_qg_eft_domain:
        blockers.append("bounded_low_energy_qg_eft_domain_missing")
    if not component_level_systematics_budget:
        blockers.append("component_level_systematics_budget_missing")
    if not registered_framework_exclusion_math:
        blockers.append("registered_framework_exclusion_math_missing")

    return {
        "label": label,
        "title": title,
        "source_url": source_url,
        "source_role": source_role,
        "gates": gates,
        "adapter_derivation_ready": not blockers,
        "ready_for_g8_claim": False,
        "blockers": sorted(set(blockers)),
        "notes": notes,
    }


def derivation_source_candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            label="energy_correlators_four_dimensional_gravity",
            title="Energy correlators in four-dimensional gravity",
            source_url="https://arxiv.org/abs/2512.23791",
            source_role="gravity_detector_formalism",
            detector_or_energy_observable=True,
            wilson_coefficient_formalism=False,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=False,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Computes gravity energy correlators as infrared-finite observables.",
                "Does not publish an engine g_8 projection or measurement covariance.",
            ],
        ),
        _candidate(
            label="light_ray_operators_gravitational_event_shapes",
            title="Light-ray operators, detectors and gravitational event shapes",
            source_url="https://arxiv.org/abs/2012.01406",
            source_role="gravity_detector_operator_formalism",
            detector_or_energy_observable=True,
            wilson_coefficient_formalism=False,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=False,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Connects light-ray operators to gravitational detector event shapes.",
                "No low-energy Wilson-coordinate adapter or public likelihood is supplied.",
            ],
        ),
        _candidate(
            label="energy_correlator_conformal_blocks_positivity",
            title="Energy Correlator Conformal Blocks and Positivity",
            source_url="https://arxiv.org/abs/2512.09986",
            source_role="energy_correlator_positivity_formalism",
            detector_or_energy_observable=True,
            wilson_coefficient_formalism=False,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=False,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Develops source-detector OPE language and positivity context.",
                "Not a measured quantum-gravity g_8 adapter.",
            ],
        ),
        _candidate(
            label="energy_correlators_perturbative_quantum_gravity",
            title="Energy Correlators in Perturbative Quantum Gravity",
            source_url="https://arxiv.org/abs/2412.05384",
            source_role="perturbative_quantum_gravity_detector_calculation",
            detector_or_energy_observable=True,
            wilson_coefficient_formalism=False,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=False,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Computes detector-operator correlators from squared amplitudes.",
                "Provides theory context, not an engine-normalized g_8 likelihood.",
            ],
        ),
        _candidate(
            label="bootstrapping_string_theory_eft",
            title="Bootstrapping string theory EFT",
            source_url="https://arxiv.org/abs/2310.10710",
            source_role="gravitational_eft_partial_wave_wilson_formalism",
            detector_or_energy_observable=False,
            wilson_coefficient_formalism=True,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=True,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Uses gravitational EFT Wilson coefficients and partial-wave language.",
                "Does not connect a public detector measurement to engine g_8.",
            ],
        ),
        _candidate(
            label="graviton_loops_and_negativity",
            title="Graviton loops and negativity",
            source_url="https://arxiv.org/abs/2501.17949",
            source_role="gravitational_eft_sum_rule_formalism",
            detector_or_energy_observable=False,
            wilson_coefficient_formalism=True,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=True,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Analyzes gravitational EFT Wilson coefficients and sum rules.",
                "No detector-observable-to-engine-g_8 adapter is present.",
            ],
        ),
        _candidate(
            label="gravity_universal_cutoff_field_theory",
            title="Gravity and a universal cutoff for field theory",
            source_url="https://arxiv.org/abs/2408.06440",
            source_role="gravitational_sum_rule_and_species_context",
            detector_or_energy_observable=False,
            wilson_coefficient_formalism=True,
            source_backed_operator_identity_to_engine_g8=False,
            public_g8_jacobian_or_projection=False,
            public_covariance_or_likelihood=False,
            bounded_low_energy_qg_eft_domain=True,
            component_level_systematics_budget=False,
            registered_framework_exclusion_math=False,
            notes=[
                "Discusses gravitational sum rules and low-energy Wilson coefficients.",
                "Coefficient basis is not an adapter from public detector data to engine g_8.",
            ],
        ),
    ]


def diagnose_g8_adapter_derivation_source_audit() -> dict[str, Any]:
    rows = derivation_source_candidates()
    ready = [row["label"] for row in rows if row["adapter_derivation_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    detector_formalism = [
        row["label"] for row in rows
        if row["gates"]["detector_or_energy_correlator_observable"]
    ]
    wilson_formalism = [
        row["label"] for row in rows
        if row["gates"]["wilson_coefficient_formalism"]
    ]

    return {
        "version": "v2.86",
        "basis": [
            "v2.85_post_native_tower_route_decision_frontier",
            "v2.79_g8_adapter_acceptance_harness",
            "v2.80_g8_public_data_product_acquisition_audit",
            "current_primary_source_search_2026_06_19",
        ],
        "route": "source_backed_g8_adapter_derivation",
        "requirements": list(DERIVATION_REQUIREMENTS),
        "candidate_count": len(rows),
        "detector_formalism_sources": detector_formalism,
        "wilson_formalism_sources": wilson_formalism,
        "adapter_derivation_ready_candidates": ready,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "current_sources_no_source_backed_g8_adapter_identity",
        "best_next_artifact": (
            "Retire the source-backed g_8 adapter derivation route unless a "
            "new source supplies the missing operator identity and covariance."
        ),
        "interpretation": (
            "Current sources split into detector/energy-correlator formalism and "
            "Wilson-coefficient formalism, but none joins them with a cited "
            "operator identity, public g_8 projection, covariance, systematics, "
            "and registered-framework exclusion math. The retained g_8 adapter "
            "route therefore remains non-claimable."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.86/"
            "g8_adapter_derivation_source_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_adapter_derivation_source_audit()
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
