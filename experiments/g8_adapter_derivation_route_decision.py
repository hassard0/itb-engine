"""g_8 adapter derivation route decision after source audit (v2.87)."""

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
    shared_identity_blockers = [
        "source_backed_operator_identity_to_engine_g8_missing",
        "public_g8_jacobian_or_projection_missing",
        "public_covariance_or_likelihood_missing",
        "registered_framework_exclusion_math_missing",
    ]
    return [
        _decision_row(
            route="current_detector_formalism_direct_g8_adapter",
            status="retired_for_current_sources",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.86 found gravity detector and energy-correlator formalism, "
                "but no source maps those observables to the engine g_8 basis."
            ),
            next_action=(
                "Do not promote detector formalism papers into g_8 adapters "
                "without a cited operator identity and covariance."
            ),
            blockers=[
                *shared_identity_blockers,
                "bounded_low_energy_qg_eft_domain_missing",
                "component_level_systematics_budget_missing",
            ],
        ),
        _decision_row(
            route="current_wilson_formalism_direct_detector_adapter",
            status="retired_for_current_sources",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.86 found useful gravitational EFT Wilson-coefficient "
                "formalism, but no source connects it to a public detector "
                "measurement or covariance."
            ),
            next_action=(
                "Do not treat Wilson-coefficient formalism as a measured adapter "
                "without a detector observable and likelihood."
            ),
            blockers=[
                *shared_identity_blockers,
                "detector_or_energy_correlator_observable_missing",
                "component_level_systematics_budget_missing",
            ],
        ),
        _decision_row(
            route="public_energy_correlator_data_without_operator_identity",
            status="retired_for_current_sources",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.80 and v2.86 together show public energy-correlator data "
                "exist, but lack the operator identity and g_8 covariance needed "
                "for an engine adapter."
            ),
            next_action=(
                "Do not re-open public data promotion unless the missing identity "
                "and covariance are supplied by a source."
            ),
            blockers=[
                *shared_identity_blockers,
                "observable_basis_not_qg_g8",
                "low_energy_qg_eft_domain_missing",
            ],
        ),
        _decision_row(
            route="new_source_backed_g8_operator_identity_search",
            status="retained_as_future_source_search",
            retained=True,
            claim_ready=False,
            reason=(
                "The derivation route could reopen if a future source explicitly "
                "joins detector observables to engine g_8 with a public Jacobian."
            ),
            next_action=(
                "Monitor or search for papers that provide the missing operator "
                "identity, covariance, and QG EFT domain."
            ),
            blockers=[
                "future_source_operator_identity_missing",
                "future_source_public_covariance_missing",
                "future_source_framework_exclusion_missing",
            ],
        ),
        _decision_row(
            route="new_spin4_or_detector_g8_measurement",
            status="retained_as_cleanest_measurement_route",
            retained=True,
            claim_ready=False,
            reason=(
                "A direct measurement in the spin-4/detector low-energy QG EFT "
                "basis would bypass the failed current-source derivation route."
            ),
            next_action=(
                "Specify or find a measurement packet already published in the "
                "engine g_8 basis."
            ),
            blockers=[
                "external_numeric_g8_measurement_missing",
                "public_g8_likelihood_or_covariance_missing",
                "registered_framework_exclusion_math_missing",
            ],
        ),
        _decision_row(
            route="g8_formalism_source_archive",
            status="retained_as_nonpromoting_design_material",
            retained=True,
            claim_ready=False,
            reason=(
                "The audited formalism sources are useful for adapter design even "
                "though they are not adapters."
            ),
            next_action=(
                "Keep detector and Wilson-formalism sources archived with their "
                "missing-identity blockers."
            ),
            blockers=[
                "formalism_source_not_measurement_adapter",
                "source_archive_not_framework_claim",
            ],
        ),
    ]


def diagnose_g8_adapter_derivation_route_decision() -> dict[str, Any]:
    rows = route_decision_rows()
    retired = [row["route"] for row in rows if row["status"].startswith("retired")]
    retained = [row["route"] for row in rows if row["retained"]]
    claim_ready = [row["route"] for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.87",
        "basis": [
            "v2.86_g8_adapter_derivation_source_audit",
            "v2.85_post_native_tower_route_decision_frontier",
            "v2.80_g8_public_data_product_acquisition_audit",
        ],
        "decision_scope": "current_g8_adapter_derivation_sources",
        "route_count": len(rows),
        "retired_routes": retired,
        "retained_nonpromoting_routes": retained,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "current_g8_adapter_derivation_retired_no_claim_ready_route",
        "best_next_artifact": (
            "Pivot out of current-source g_8 adapter derivation. The next live "
            "route is a direct spin-4/detector measurement packet, unless a new "
            "source supplies the missing operator identity."
        ),
        "interpretation": (
            "The current derivation sources are useful but non-promoting. They "
            "lack the source-backed operator identity, public g_8 projection, "
            "covariance, systematics, and framework-exclusion math required by "
            "the adapter gate."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.87/"
            "g8_adapter_derivation_route_decision.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_adapter_derivation_route_decision()
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
