"""g_8 route decision after public data-product acquisition audit (v2.81)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


def _decision_row(
    *,
    route: str,
    status: str,
    retained: bool,
    claim_ready: bool,
    reason: str,
    next_action: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "route": route,
        "status": status,
        "retained": retained,
        "claim_ready": claim_ready,
        "reason": reason,
        "next_action": next_action,
        "blockers": sorted(set(blockers)),
    }


def route_decision_rows() -> list[dict[str, Any]]:
    shared_public_data_blockers = [
        "observable_basis_not_qg_g8",
        "source_backed_engine_g8_normalization_missing",
        "public_g8_likelihood_or_covariance_missing",
        "qg_eft_applicability_domain_missing",
        "registered_framework_exclusion_math_missing",
    ]
    return [
        _decision_row(
            route="cms_energy_correlator_direct_g8_promotion",
            status="retired_for_current_engine",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.80 identified a real CMS HEPData energy-correlator "
                "collection, but the measured product targets QCD jet structure "
                "and alpha_s rather than the engine g_8 coefficient."
            ),
            next_action=(
                "Do not promote CMS SMP-22-015 tables directly into g_8. Use "
                "them only as data seeds for a separately sourced adapter."
            ),
            blockers=[
                *shared_public_data_blockers,
                "qcd_alpha_s_measurement_not_quantum_gravity_g8",
            ],
        ),
        _decision_row(
            route="heavy_ion_eec_direct_g8_promotion",
            status="retired_for_current_engine",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.80 found a public CMS heavy-ion EEC measurement, but its "
                "target is QCD medium response rather than a low-energy quantum "
                "gravity EFT coefficient."
            ),
            next_action=(
                "Do not use the heavy-ion EEC result as a framework discriminator "
                "unless a source-backed low-energy QG EFT map is published."
            ),
            blockers=[
                *shared_public_data_blockers,
                "heavy_ion_medium_observable_not_low_energy_qg_eft",
            ],
        ),
        _decision_row(
            route="open_data_reanalysis_without_source_adapter",
            status="retired_as_direct_promotion",
            retained=False,
            claim_ready=False,
            reason=(
                "Open data can support method development, but a private or "
                "engine-internal reanalysis would not create a source-backed "
                "operator map or public g_8 likelihood by itself."
            ),
            next_action=(
                "Only revisit CMS open data through the retained source-backed "
                "adapter-derivation route."
            ),
            blockers=[
                "internal_reanalysis_not_source_backed",
                "public_g8_likelihood_or_covariance_missing",
                "source_backed_engine_g8_normalization_missing",
                "registered_framework_exclusion_math_missing",
            ],
        ),
        _decision_row(
            route="source_backed_energy_correlator_to_g8_adapter_derivation",
            status="retained_required_before_any_data_based_g8_claim",
            retained=True,
            claim_ready=False,
            reason=(
                "A data-based g_8 claim remains possible only if a published "
                "derivation maps an energy-correlator or detector observable into "
                "the engine Wilson basis with covariance."
            ),
            next_action=(
                "Search for or derive a citable adapter with a Jacobian to g_8, "
                "component-level systematics, public covariance, and QG EFT domain."
            ),
            blockers=[
                "source_backed_jacobian_to_engine_g8_missing",
                "component_level_systematics_budget_missing",
                "public_g8_covariance_missing",
                "low_energy_qg_eft_domain_missing",
                "noncircular_framework_exclusion_missing",
            ],
        ),
        _decision_row(
            route="new_spin4_or_detector_g8_measurement",
            status="retained_as_cleanest_measurement_route",
            retained=True,
            claim_ready=False,
            reason=(
                "v2.79 proves a correctly shaped spin-4 or detector-moment "
                "packet can pass the gate; v2.80 shows no current packet exists."
            ),
            next_action=(
                "Specify or find a measurement published directly in the "
                "spin-4/detector low-energy QG EFT basis."
            ),
            blockers=[
                "external_numeric_g8_measurement_missing",
                "public_g8_likelihood_or_covariance_missing",
                "component_level_systematics_budget_missing",
                "registered_framework_exclusion_math_missing",
            ],
        ),
        _decision_row(
            route="g8_theory_bridge_archive",
            status="retained_as_nonpromoting_design_material",
            retained=True,
            claim_ready=False,
            reason=(
                "Gravity energy-correlator, spinning-correlator, and long-range "
                "partial-wave papers improve adapter language but do not provide "
                "external numerical evidence."
            ),
            next_action=(
                "Keep these sources as design constraints for adapters; do not "
                "treat them as measurements."
            ),
            blockers=[
                "theory_formalism_not_external_measurement",
                "public_g8_likelihood_or_covariance_missing",
                "registered_framework_exclusion_math_missing",
            ],
        ),
    ]


def diagnose_g8_route_decision() -> dict[str, Any]:
    rows = route_decision_rows()
    retired = [row["route"] for row in rows if row["status"].startswith("retired")]
    retained = [row["route"] for row in rows if row["retained"]]
    claim_ready = [row["route"] for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.81",
        "basis": [
            "v2.79_g8_adapter_acceptance_harness",
            "v2.80_g8_public_data_product_acquisition_audit",
            "v2.54_g8_high_moment_measurement_specification",
        ],
        "decision_scope": "g8_public_data_products_to_engine_routes",
        "route_count": len(rows),
        "retired_routes": retired,
        "retained_nonpromoting_routes": retained,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "direct_public_data_g8_promotion_retired_no_claim_ready_route",
        "best_next_artifact": (
            "Pivot out of direct public-data promotion. Either produce a "
            "source-backed energy-correlator-to-g_8 adapter with covariance, "
            "or move to a different frontier while the clean spin-4/detector "
            "measurement route remains open."
        ),
        "interpretation": (
            "The current g_8 work produced an executable adapter gate and a "
            "public-data acquisition map. It did not produce an engine-normalized "
            "quantum-gravity discriminator. Direct promotion of current QCD "
            "energy-correlator products is therefore retired for the current "
            "engine rather than left as an ambiguous maybe."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.81/g8_route_decision.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_route_decision()
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
