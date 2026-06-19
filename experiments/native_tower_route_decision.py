"""Native tower route decision after current-source audit (v2.84)."""

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
    shared_ownership_blockers = [
        "missing_framework_owned_endpoint",
        "missing_framework_owned_displacement",
        "not_exposed_by_registered_framework_adapter",
        "registered_framework_exclusion_math_missing",
    ]
    return [
        _decision_row(
            route="quintic_single_compactification_direct_string_tree_promotion",
            status="retired_for_generic_framework_claims",
            retained=False,
            claim_ready=False,
            reason=(
                "The Ashmore/Ruehle quintic row is a useful numeric KK subtower "
                "candidate, but v2.83 keeps it finite-range, single-"
                "compactification, and not owned by the registered string_tree_eft "
                "adapter."
            ),
            next_action=(
                "Do not use the quintic subtower as a generic string_tree_eft "
                "framework verdict. Keep it only as a scoped candidate row."
            ),
            blockers=[
                *shared_ownership_blockers,
                "finite_range_not_asymptotic",
                "single_compactification_not_generic_framework",
                "single_scalar_laplacian_subtower_not_complete_tower_spectrum",
            ],
        ),
        _decision_row(
            route="string_positive_control_direct_exclusion",
            status="retired_for_framework_exclusion",
            retained=False,
            claim_ready=False,
            reason=(
                "Large-volume and analytic KK decompactification sources are "
                "known string-compatible positive controls, so exclusion math "
                "cannot be promoted into a framework claim."
            ),
            next_action=(
                "Use positive controls to test guard behavior only; do not count "
                "them as quantum-gravity exclusions."
            ),
            blockers=[
                "known_qg_positive_control_family",
                *shared_ownership_blockers,
            ],
        ),
        _decision_row(
            route="asymptotic_safety_swampland_comparison_direct_tower",
            status="retired_as_native_tower_source",
            retained=False,
            claim_ready=False,
            reason=(
                "The asymptotic-safety source is a conceptual swampland "
                "assessment, not a native TowerSpectrum/TowerEvidence adapter."
            ),
            next_action=(
                "Only revisit if an asymptotic-safety source publishes explicit "
                "tower spectra with endpoint and displacement ownership."
            ),
            blockers=[
                "framework_relative_swampland_assessment_not_tower_spectrum",
                "missing_native_tower_spectrum",
                "missing_native_tower_evidence",
                *shared_ownership_blockers,
            ],
        ),
        _decision_row(
            route="horava_witten_to_horava_lifshitz_promotion",
            status="retired_wrong_registered_framework_target",
            retained=False,
            claim_ready=False,
            reason=(
                "The Horava-Witten dark-dimension source is a string setup and "
                "does not target the registered Horava-Lifshitz framework."
            ),
            next_action=(
                "Do not merge Horava-Witten string evidence into the "
                "horava_lifshitz framework adapter."
            ),
            blockers=[
                "horava_witten_string_setup_not_horava_lifshitz_framework",
                "dark_dimension_candidate_not_registered_framework_adapter",
                "missing_native_tower_spectrum",
                "missing_native_tower_evidence",
                *shared_ownership_blockers,
            ],
        ),
        _decision_row(
            route="registered_native_tower_adapter_authoring",
            status="retained_required_before_any_native_tower_claim",
            retained=True,
            claim_ready=False,
            reason=(
                "The native tower route remains possible only when a registered "
                "framework exposes source-owned TowerSpectrum and TowerEvidence "
                "methods with endpoint/displacement ownership."
            ),
            next_action=(
                "Implement a real native adapter only from a source that owns the "
                "registered framework endpoint, displacement, spectrum, and "
                "normalization."
            ),
            blockers=[
                "source_owned_tower_spectrum_missing",
                "source_owned_tower_evidence_missing",
                "framework_owned_endpoint_missing",
                "framework_owned_displacement_missing",
                "two_sigma_tower_exclusion_missing",
            ],
        ),
        _decision_row(
            route="framework_specific_asymptotic_source_search",
            status="retained_as_search_route",
            retained=True,
            claim_ready=False,
            reason=(
                "The current search did not find a registered native adapter, "
                "but a narrower framework-by-framework search could still find "
                "one."
            ),
            next_action=(
                "Search one registered framework at a time for asymptotic tower "
                "spectra and ownership metadata."
            ),
            blockers=[
                "named_framework_native_source_missing",
                "asymptotic_tower_spectrum_missing",
                "adapter_normalization_missing",
            ],
        ),
        _decision_row(
            route="native_tower_source_archive",
            status="retained_as_nonpromoting_design_material",
            retained=True,
            claim_ready=False,
            reason=(
                "The audited string/swampland sources remain useful for guard "
                "tests, positive controls, and future adapter design."
            ),
            next_action=(
                "Keep source rows archived with their blockers; never use them "
                "as framework verdicts without native ownership."
            ),
            blockers=[
                "source_archive_not_framework_claim",
                "ownership_metadata_missing",
            ],
        ),
    ]


def diagnose_native_tower_route_decision() -> dict[str, Any]:
    rows = route_decision_rows()
    retired = [row["route"] for row in rows if row["status"].startswith("retired")]
    retained = [row["route"] for row in rows if row["retained"]]
    claim_ready = [row["route"] for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.84",
        "basis": [
            "v2.83_native_tower_current_source_audit",
            "v2.82_post_g8_route_decision_frontier",
            "v2.46_native_tower_ownership_frontier",
            "v2.47_native_adapter_acceptance_harness",
        ],
        "decision_scope": "native_tower_sources_to_registered_framework_adapters",
        "route_count": len(rows),
        "retired_routes": retired,
        "retained_nonpromoting_routes": retained,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "direct_native_tower_source_promotion_retired_no_claim_ready_route",
        "best_next_artifact": (
            "Pivot out of direct native-source promotion. Either find a "
            "registered-framework-owned native tower adapter or move to the next "
            "frontier route."
        ),
        "interpretation": (
            "The current native tower sources are useful but non-promoting. Direct "
            "promotion of finite-range, positive-control, conceptual, or wrong-"
            "framework sources is retired. The only retained native route is a "
            "proper registered adapter with source-owned endpoint and displacement."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.84/native_tower_route_decision.json",
    )
    args = parser.parse_args()

    result = diagnose_native_tower_route_decision()
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
