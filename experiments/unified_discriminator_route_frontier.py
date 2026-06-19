"""Unified discriminator route frontier (v2.53).

This audit consolidates the current tower and non-tower route blockers into one
frontier table. It does not add a new discriminator; it prevents the research
loop from losing track of which artifact is required next for each route.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.birefringence_evidence_freshness import (
    diagnose_birefringence_evidence_freshness,
)
from experiments.candidate_native_adapter_promotion_audit import (
    diagnose_candidate_native_adapter_promotion_audit,
)
from experiments.explicit_tower_basis import _json_default
from experiments.nontower_promotion_guard_audit import (
    diagnose_nontower_promotion_guard_audit,
)
from experiments.weyl_g8_observable_sourceability import (
    diagnose_weyl_g8_observable_sourceability,
)


def _guard_scenarios_by_label() -> dict[str, dict[str, Any]]:
    guard = diagnose_nontower_promotion_guard_audit()
    return {row["label"]: row for row in guard["scenarios"]}


def _guard_blockers_for_axis(axis: str, scenarios: dict[str, dict[str, Any]]) -> list[str]:
    blockers = {
        blocker
        for row in scenarios.values()
        if row["evidence"]["axis"] == axis and not row["label"].startswith("synthetic:")
        for blocker in row["guard"]["blockers"]
    }
    return sorted(blockers)


def _route_row(
    *,
    route: str,
    family: str,
    current_status: str,
    latest_audit: str,
    claim_ready: bool,
    blocker_summary: list[str],
    next_required_artifact: str,
    evidence_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "route": route,
        "family": family,
        "current_status": current_status,
        "latest_audit": latest_audit,
        "claim_ready": claim_ready,
        "blocker_summary": blocker_summary,
        "next_required_artifact": next_required_artifact,
        "evidence_snapshot": evidence_snapshot,
    }


def diagnose_unified_discriminator_route_frontier() -> dict[str, Any]:
    tower = diagnose_candidate_native_adapter_promotion_audit()
    birefringence = diagnose_birefringence_evidence_freshness()
    sourceability = diagnose_weyl_g8_observable_sourceability()
    guard = diagnose_nontower_promotion_guard_audit()
    scenarios = {row["label"]: row for row in guard["scenarios"]}

    birefringence_guard = scenarios["birefringence:act_dr6_hint"]
    g_c_summary = sourceability["axis_summary"]["g_C"]
    g_8_summary = sourceability["axis_summary"]["g_8"]

    rows = [
        _route_row(
            route="native_tower_adapter",
            family="tower",
            current_status="blocked_missing_framework_owned_native_adapter",
            latest_audit="v2.48",
            claim_ready=False,
            blocker_summary=sorted(tower["promotion_blocker_counts"]),
            next_required_artifact=(
                "A registered in-scope framework-owned native TowerEvidence "
                "adapter with endpoint, displacement, source, normalization, "
                "uncertainty, and excluding tower math."
            ),
            evidence_snapshot={
                "candidate_count": tower["candidate_count"],
                "promotable_native_adapter_candidates": tower[
                    "promotable_native_adapter_candidates"
                ],
                "tower_math_excluding_candidates": tower[
                    "tower_math_excluding_candidates"
                ],
            },
        ),
        _route_row(
            route="cosmic_birefringence",
            family="non_tower_parity",
            current_status="alive_but_promotion_guard_blocked",
            latest_audit="v2.49/v2.52",
            claim_ready=False,
            blocker_summary=sorted(set(
                birefringence["claim_blockers"]
                + birefringence_guard["guard"]["blockers"]
            )),
            next_required_artifact=(
                "A systematics-closed external beta measurement with a "
                "source-backed mapping from beta to the engine parity axis."
            ),
            evidence_snapshot={
                "route_status": birefringence["route_status"],
                "positive_sign_dataset_count": birefringence[
                    "positive_sign_dataset_count"
                ],
                "dataset_count": birefringence["dataset_count"],
                "independent_pair_zero_exclusion_sigma": (
                    birefringence[
                        "independent_instrument_pair_fixed_effect"
                    ]["zero_exclusion_sigma"]
                ),
                "guard_status": birefringence_guard["frontier_status"],
            },
        ),
        _route_row(
            route="weyl_g_C",
            family="non_tower_weyl",
            current_status="sourceability_and_promotion_guard_blocked",
            latest_audit="v2.50/v2.51/v2.52",
            claim_ready=False,
            blocker_summary=_guard_blockers_for_axis("g_C", scenarios),
            next_required_artifact=(
                "A direct external numerical Weyl-sector measurement or validated "
                "framework adapter; structural a/c and holographic proxies are "
                "not enough."
            ),
            evidence_snapshot={
                "candidate_routes": g_c_summary["candidate_routes"],
                "source_backed_theory_routes": g_c_summary[
                    "source_backed_theory_routes"
                ],
                "external_numeric_measurement_routes": g_c_summary[
                    "external_numeric_measurement_routes"
                ],
                "claim_ready_routes": g_c_summary["claim_ready_routes"],
            },
        ),
        _route_row(
            route="matter_high_moment_g_8",
            family="non_tower_matter",
            current_status="design_probe_and_promotion_guard_blocked",
            latest_audit="v2.50/v2.51/v2.52",
            claim_ready=False,
            blocker_summary=_guard_blockers_for_axis("g_8", scenarios),
            next_required_artifact=(
                "A sourced spin-4, detector, or high-moment measurement program "
                "with direct mapping to g_8 and closed systematics."
            ),
            evidence_snapshot={
                "candidate_routes": g_8_summary["candidate_routes"],
                "source_backed_theory_routes": g_8_summary[
                    "source_backed_theory_routes"
                ],
                "external_numeric_measurement_routes": g_8_summary[
                    "external_numeric_measurement_routes"
                ],
                "claim_ready_routes": g_8_summary["claim_ready_routes"],
            },
        ),
    ]

    claim_ready_routes = [row["route"] for row in rows if row["claim_ready"]]
    return {
        "basis": [
            "v2.48_tower_candidate_promotion",
            "v2.49_birefringence_freshness",
            "v2.51_weyl_g8_sourceability",
            "v2.52_nontower_promotion_guard",
        ],
        "route_count": len(rows),
        "claim_ready_routes": claim_ready_routes,
        "claimable_discriminator_now": bool(claim_ready_routes),
        "routes": rows,
        "synthetic_positive_control": {
            "ready_routes": guard["synthetic_claim_ready_routes"],
            "purpose": (
                "Proves the non-tower positive path without asserting any current "
                "framework claim."
            ),
        },
        "priority_order": [
            "matter_high_moment_g_8",
            "cosmic_birefringence",
            "weyl_g_C",
            "native_tower_adapter",
        ],
        "route_status": "no_claim_ready_route",
        "interpretation": (
            "The frontier is organized but unsolved. The most actionable next "
            "artifact is an external, sourced g_8 high-moment/partial-wave "
            "measurement specification; birefringence remains empirically alive "
            "but systematics- and mapping-blocked; g_C remains structural; the "
            "tower route remains adapter-ownership blocked."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.53/unified_discriminator_route_frontier.json",
    )
    args = parser.parse_args()

    result = diagnose_unified_discriminator_route_frontier()
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
