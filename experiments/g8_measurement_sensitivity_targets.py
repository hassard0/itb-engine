"""g8 measurement sensitivity targets for registered frameworks (v2.96)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_framework_scenarios import _framework_reference_verdicts
from itb.predict import FRAMEWORKS
from itb.scope import engine_validity


VERSION = "v2.96"
EPSILON = 1e-12
Z_SCORE = 2.0


def _framework_rows() -> list[dict[str, Any]]:
    reference = _framework_reference_verdicts()
    rows = []
    for name, framework in FRAMEWORKS.items():
        coefficients = framework.encode().coefficients
        scope = engine_validity(framework)
        ref_row = reference[name]
        eligible = bool(scope.in_scope and ref_row["reference_feasible"])
        ineligible_reasons = []
        if not scope.in_scope:
            ineligible_reasons.append("engine_scope_excluded")
        if not ref_row["reference_feasible"]:
            ineligible_reasons.append("reference_stack_infeasible")

        rows.append(
            {
                "framework": name,
                "g8": float(coefficients.get("g_8", 0.0)),
                "engine_in_scope": bool(scope.in_scope),
                "scope_violations": list(scope.violations),
                "reference_feasible": bool(ref_row["reference_feasible"]),
                "reference_binding": ref_row["binding"],
                "eligible_for_current_g8_target": eligible,
                "ineligible_reasons": ineligible_reasons,
            }
        )
    return sorted(rows, key=lambda row: (row["g8"], row["framework"]))


def _clusters(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_g8: dict[float, list[dict[str, Any]]] = {}
    for row in rows:
        by_g8.setdefault(round(row["g8"], 12), []).append(row)

    clusters = []
    for g8, members in sorted(by_g8.items()):
        frameworks = sorted(row["framework"] for row in members)
        clusters.append(
            {
                "g8": g8,
                "frameworks": frameworks,
                "cluster_size": len(frameworks),
                "exact_degeneracy": len(frameworks) > 1,
            }
        )
    return clusters


def _pairwise_separations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = sorted(rows, key=lambda row: (row["g8"], row["framework"]))
    pairs = []
    for index, left in enumerate(selected):
        for right in selected[index + 1 :]:
            separation = abs(right["g8"] - left["g8"])
            pairs.append(
                {
                    "framework_a": left["framework"],
                    "framework_b": right["framework"],
                    "g8_a": left["g8"],
                    "g8_b": right["g8"],
                    "separation": separation,
                    "exact_degenerate": separation <= EPSILON,
                    "required_total_sigma_for_2sigma_distinguishability": (
                        None if separation <= EPSILON else separation / Z_SCORE
                    ),
                }
            )
    return sorted(
        pairs,
        key=lambda row: (
            row["separation"],
            row["framework_a"],
            row["framework_b"],
        ),
    )


def _cluster_targets(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets = []
    for cluster in clusters:
        other_clusters = [
            other
            for other in clusters
            if abs(other["g8"] - cluster["g8"]) > EPSILON
        ]
        nearest = (
            min(
                other_clusters,
                key=lambda other: (
                    abs(other["g8"] - cluster["g8"]),
                    other["frameworks"],
                ),
            )
            if other_clusters
            else None
        )
        gap = None if nearest is None else abs(nearest["g8"] - cluster["g8"])
        target_status = (
            "single_axis_g8_degenerate_requires_additional_axis"
            if cluster["exact_degeneracy"]
            else "single_axis_g8_target_viable_if_external_packet_precision_met"
        )
        targets.append(
            {
                "g8": cluster["g8"],
                "frameworks": cluster["frameworks"],
                "target_status": target_status,
                "unresolvable_same_g8_frameworks": (
                    cluster["frameworks"] if cluster["exact_degeneracy"] else []
                ),
                "nearest_distinct_cluster": nearest,
                "nearest_distinct_gap": gap,
                "required_total_sigma_to_exclude_nearest_distinct_at_2sigma": (
                    None if gap is None else gap / Z_SCORE
                ),
            }
        )
    return sorted(
        targets,
        key=lambda row: (
            row["required_total_sigma_to_exclude_nearest_distinct_at_2sigma"]
            if row["required_total_sigma_to_exclude_nearest_distinct_at_2sigma"]
            is not None
            else -1.0,
            row["g8"],
        ),
    )


def diagnose_g8_measurement_sensitivity_targets() -> dict[str, Any]:
    rows = _framework_rows()
    eligible_rows = [
        row for row in rows if row["eligible_for_current_g8_target"]
    ]
    ineligible_rows = [
        row for row in rows if not row["eligible_for_current_g8_target"]
    ]

    all_clusters = _clusters(rows)
    eligible_clusters = _clusters(eligible_rows)
    all_targets = _cluster_targets(all_clusters)
    eligible_targets = _cluster_targets(eligible_clusters)
    eligible_pairs = _pairwise_separations(eligible_rows)
    all_pairs = _pairwise_separations(rows)

    tightest_pair = eligible_pairs[0]
    widest_target = max(
        eligible_targets,
        key=lambda row: (
            row["required_total_sigma_to_exclude_nearest_distinct_at_2sigma"]
            or -1.0
        ),
    )
    tightest_sigma = tightest_pair[
        "required_total_sigma_for_2sigma_distinguishability"
    ]

    return {
        "version": VERSION,
        "basis": [
            "itb.predict.FRAMEWORKS",
            "itb.scope.engine_validity",
            "experiments.tower_framework_scenarios._framework_reference_verdicts",
            "v2.93_external_evidence_intake_gate",
            "v2.95_external_dependency_blocker_synthesis",
        ],
        "route": "future_public_g8_measurement_ingestion",
        "route_status": "g8_sensitivity_targets_defined_no_external_packet",
        "claimable_discriminator_now": False,
        "external_packet_present": False,
        "uncertainty_model": (
            "One-dimensional Gaussian proxy on engine-normalized g_8. A real "
            "packet must still pass the v2.93 intake gate with public "
            "likelihood, covariance, closed systematics, and EFT-domain bounds."
        ),
        "z_score": Z_SCORE,
        "registered_framework_count": len(rows),
        "eligible_framework_count": len(eligible_rows),
        "ineligible_frameworks": ineligible_rows,
        "framework_g8_rows": rows,
        "all_registered_clusters": all_clusters,
        "eligible_clusters": eligible_clusters,
        "all_registered_exact_degenerate_clusters": [
            row for row in all_clusters if row["exact_degeneracy"]
        ],
        "eligible_exact_degenerate_clusters": [
            row for row in eligible_clusters if row["exact_degeneracy"]
        ],
        "all_registered_pairwise_separations": all_pairs,
        "eligible_pairwise_separations": eligible_pairs,
        "all_registered_cluster_targets": all_targets,
        "eligible_cluster_targets": eligible_targets,
        "tightest_eligible_pair": tightest_pair,
        "widest_eligible_single_axis_target": widest_target,
        "minimum_total_sigma_to_resolve_all_eligible_g8_targets_at_2sigma": (
            tightest_sigma
        ),
        "claim_blockers": [
            "real_engine_normalized_g8_packet_missing",
            "public_likelihood_and_covariance_missing",
            "closed_systematics_budget_missing",
            "eft_domain_bounds_missing",
        ],
        "best_next_artifact": (
            "A real engine-normalized g_8 measurement packet with total sigma "
            f"below {tightest_sigma:.6g} to resolve the tightest eligible pair "
            "or, for a narrower target, below the target-specific threshold in "
            "eligible_cluster_targets."
        ),
        "interpretation": (
            "This converts the v2.95 external-packet blocker into numeric "
            "precision targets. It is not a discriminator claim: without a real "
            "packet, the thresholds only define what future evidence must beat."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.96/"
            "g8_measurement_sensitivity_targets.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_measurement_sensitivity_targets()
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
