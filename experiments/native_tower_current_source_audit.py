"""Native tower current-source audit (v2.83).

v2.82 selected native tower evidence as the next no-new-experiment frontier.
This audit checks current source classes against the v2.46 native pass
condition: a registered framework must expose owned TowerSpectrum and
TowerEvidence adapters with asymptotic endpoint and displacement ownership.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.native_tower_ownership_frontier import (
    diagnose_native_tower_ownership_frontier,
)
from itb.predict import FRAMEWORKS


REGISTERED_FRAMEWORKS = set(FRAMEWORKS)


def _candidate(
    *,
    label: str,
    title: str,
    source_url: str,
    target_framework: str,
    source_role: str,
    native_tower_spectrum_present: bool,
    native_tower_evidence_present: bool,
    endpoint_owned_by_registered_framework: bool,
    displacement_owned_by_registered_framework: bool,
    range_scope: str,
    compactification_scope: str,
    tower_scope: str,
    two_sigma_lower_bound_above_threshold: bool | None,
    source_specific_blockers: list[str],
) -> dict[str, Any]:
    blockers = set(source_specific_blockers)
    if target_framework not in REGISTERED_FRAMEWORKS:
        blockers.add("target_framework_not_registered")
    if not native_tower_spectrum_present:
        blockers.add("missing_native_tower_spectrum")
    if not native_tower_evidence_present:
        blockers.add("missing_native_tower_evidence")
    if not endpoint_owned_by_registered_framework:
        blockers.add("missing_framework_owned_endpoint")
    if not displacement_owned_by_registered_framework:
        blockers.add("missing_framework_owned_displacement")
    if range_scope == "finite_range":
        blockers.add("finite_range_not_asymptotic")
    elif range_scope != "asymptotic":
        blockers.add("missing_asymptotic_range_scope")
    if compactification_scope == "single_compactification":
        blockers.add("single_compactification_not_generic_framework")
    if tower_scope == "positive_control_decompactification":
        blockers.add("known_qg_positive_control_family")
    if two_sigma_lower_bound_above_threshold is not True:
        blockers.add("tower_math_not_excluding_or_not_computable")

    native_adapter_ready = not blockers
    return {
        "label": label,
        "title": title,
        "source_url": source_url,
        "target_framework": target_framework,
        "target_framework_registered": target_framework in REGISTERED_FRAMEWORKS,
        "source_role": source_role,
        "native_tower_spectrum_present": native_tower_spectrum_present,
        "native_tower_evidence_present": native_tower_evidence_present,
        "endpoint_owned_by_registered_framework": (
            endpoint_owned_by_registered_framework
        ),
        "displacement_owned_by_registered_framework": (
            displacement_owned_by_registered_framework
        ),
        "range_scope": range_scope,
        "compactification_scope": compactification_scope,
        "tower_scope": tower_scope,
        "two_sigma_lower_bound_above_threshold": (
            two_sigma_lower_bound_above_threshold
        ),
        "native_adapter_ready": native_adapter_ready,
        "claim_ready": False,
        "blockers": sorted(blockers),
    }


def current_source_candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            label="ashmore_ruehle_quintic_laplacian_kk",
            title=(
                "Moduli-dependent KK towers and the swampland distance "
                "conjecture on the quintic Calabi-Yau manifold"
            ),
            source_url="https://arxiv.org/abs/2103.07472",
            target_framework="string_tree_eft",
            source_role="numeric_single_compactification_kk_subtower",
            native_tower_spectrum_present=True,
            native_tower_evidence_present=True,
            endpoint_owned_by_registered_framework=False,
            displacement_owned_by_registered_framework=False,
            range_scope="finite_range",
            compactification_scope="single_compactification",
            tower_scope="scalar_laplacian_subtower",
            two_sigma_lower_bound_above_threshold=False,
            source_specific_blockers=[
                "single_scalar_laplacian_subtower_not_complete_tower_spectrum",
                "not_exposed_by_registered_framework_adapter",
            ],
        ),
        _candidate(
            label="blumenhagen_refined_sdc_large_volume",
            title=(
                "The Refined Swampland Distance Conjecture in Calabi-Yau "
                "Moduli Spaces"
            ),
            source_url="https://arxiv.org/abs/1803.04989",
            target_framework="string_tree_eft",
            source_role="known_string_positive_control",
            native_tower_spectrum_present=True,
            native_tower_evidence_present=True,
            endpoint_owned_by_registered_framework=False,
            displacement_owned_by_registered_framework=False,
            range_scope="asymptotic",
            compactification_scope="decompactification_or_large_volume_benchmark",
            tower_scope="positive_control_decompactification",
            two_sigma_lower_bound_above_threshold=True,
            source_specific_blockers=[
                "not_exposed_by_registered_framework_adapter",
            ],
        ),
        _candidate(
            label="aoufia_laplacian_various_dimensions",
            title="Laplacians in Various Dimensions and the Swampland",
            source_url="https://arxiv.org/abs/2506.03253",
            target_framework="string_tree_eft",
            source_role="analytic_kk_positive_control_family",
            native_tower_spectrum_present=True,
            native_tower_evidence_present=True,
            endpoint_owned_by_registered_framework=False,
            displacement_owned_by_registered_framework=False,
            range_scope="asymptotic",
            compactification_scope="decompactification_or_large_volume_benchmark",
            tower_scope="positive_control_decompactification",
            two_sigma_lower_bound_above_threshold=True,
            source_specific_blockers=[
                "not_exposed_by_registered_framework_adapter",
            ],
        ),
        _candidate(
            label="species_scale_distance_bounds",
            title="Bounds on Species Scale and the Distance Conjecture",
            source_url="https://arxiv.org/abs/2303.13580",
            target_framework="string_tree_eft",
            source_role="species_scale_bound_not_framework_adapter",
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            endpoint_owned_by_registered_framework=False,
            displacement_owned_by_registered_framework=False,
            range_scope="asymptotic",
            compactification_scope="generic_sdc_bound",
            tower_scope="bound_not_spectrum",
            two_sigma_lower_bound_above_threshold=None,
            source_specific_blockers=[
                "species_bound_not_native_tower_spectrum",
            ],
        ),
        _candidate(
            label="asymptotic_safety_swampland_assessment",
            title="Asymptotic safety, quantum gravity, and the swampland",
            source_url="https://arxiv.org/abs/2502.12290",
            target_framework="asymptotic_safety",
            source_role="conceptual_swampland_comparison",
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            endpoint_owned_by_registered_framework=False,
            displacement_owned_by_registered_framework=False,
            range_scope="unspecified",
            compactification_scope="not_a_tower_compactification",
            tower_scope="conceptual_not_spectrum",
            two_sigma_lower_bound_above_threshold=None,
            source_specific_blockers=[
                "framework_relative_swampland_assessment_not_tower_spectrum",
            ],
        ),
        _candidate(
            label="horava_witten_dark_dimension_candidate",
            title="Towards the Realization of the Dark Dimension Scenario in Horava-Witten Theory",
            source_url="https://arxiv.org/abs/2605.11068",
            target_framework="horava_lifshitz",
            source_role="string_horava_witten_not_registered_horava_lifshitz",
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            endpoint_owned_by_registered_framework=False,
            displacement_owned_by_registered_framework=False,
            range_scope="asymptotic",
            compactification_scope="horava_witten_extra_dimension",
            tower_scope="kk_dark_dimension_candidate",
            two_sigma_lower_bound_above_threshold=None,
            source_specific_blockers=[
                "horava_witten_string_setup_not_horava_lifshitz_framework",
                "dark_dimension_candidate_not_registered_framework_adapter",
            ],
        ),
    ]


def diagnose_native_tower_current_source_audit() -> dict[str, Any]:
    ownership = diagnose_native_tower_ownership_frontier()
    rows = current_source_candidates()
    ready = [row["label"] for row in rows if row["native_adapter_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.83",
        "basis": [
            "v2.82_post_g8_route_decision_frontier",
            "v2.46_native_tower_ownership_frontier",
            "v2.47_native_adapter_acceptance_harness",
            "v2.48_candidate_native_adapter_promotion_audit",
            "current_primary_source_search_2026_06_19",
        ],
        "route": "native_tower_evidence",
        "pass_condition": ownership["pass_condition"],
        "critical_phi_tower": ownership["critical_phi_tower"],
        "candidate_count": len(rows),
        "native_adapter_ready_candidates": ready,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "current_sources_no_registered_native_tower_adapter",
        "best_next_artifact": (
            "Implement a registered-framework native adapter only when a source "
            "owns the framework endpoint and displacement and provides an "
            "asymptotic TowerSpectrum/TowerEvidence pair."
        ),
        "interpretation": (
            "Current string/swampland sources provide useful tower candidates, "
            "positive controls, and framework-adjacent theory context. None is a "
            "registered-framework native adapter: ownership metadata is missing, "
            "single-compactification or positive-control scope blocks promotion, "
            "and non-string frameworks lack native spectra altogether."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.83/"
            "native_tower_current_source_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_native_tower_current_source_audit()
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
