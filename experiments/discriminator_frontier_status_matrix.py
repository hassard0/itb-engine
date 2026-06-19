"""Discriminator frontier status matrix.

This audit locks the pure frontier status classifier so the guard-blocked paths
are explicit and separate from claim-ready synthetic fixtures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.discriminator_frontier import classify_discriminator_frontier_status
from experiments.explicit_tower_basis import _json_default


SCENARIOS = (
    {
        "label": "reference_excluded_fixture",
        "reference_feasible": False,
        "engine_in_scope": True,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": True,
        "tower_claimable_by_math": True,
        "promotion_ready": True,
        "generic_claim_ready": True,
    },
    {
        "label": "scope_limited_fixture",
        "reference_feasible": True,
        "engine_in_scope": False,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": True,
        "tower_claimable_by_math": True,
        "promotion_ready": True,
        "generic_claim_ready": True,
    },
    {
        "label": "missing_spectrum_fixture",
        "reference_feasible": True,
        "engine_in_scope": True,
        "native_tower_spectrum_present": False,
        "evidence_ready_for_framework_claim": False,
        "tower_claimable_by_math": False,
        "promotion_ready": False,
        "generic_claim_ready": False,
    },
    {
        "label": "missing_evidence_fixture",
        "reference_feasible": True,
        "engine_in_scope": True,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": False,
        "tower_claimable_by_math": True,
        "promotion_ready": False,
        "generic_claim_ready": False,
    },
    {
        "label": "non_excluding_evidence_fixture",
        "reference_feasible": True,
        "engine_in_scope": True,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": True,
        "tower_claimable_by_math": False,
        "promotion_ready": False,
        "generic_claim_ready": False,
    },
    {
        "label": "promotion_guard_blocked_fixture",
        "reference_feasible": True,
        "engine_in_scope": True,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": True,
        "tower_claimable_by_math": True,
        "promotion_ready": False,
        "generic_claim_ready": False,
    },
    {
        "label": "generic_claim_guard_blocked_fixture",
        "reference_feasible": True,
        "engine_in_scope": True,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": True,
        "tower_claimable_by_math": True,
        "promotion_ready": True,
        "generic_claim_ready": False,
    },
    {
        "label": "claim_ready_fixture",
        "reference_feasible": True,
        "engine_in_scope": True,
        "native_tower_spectrum_present": True,
        "evidence_ready_for_framework_claim": True,
        "tower_claimable_by_math": True,
        "promotion_ready": True,
        "generic_claim_ready": True,
    },
)


def diagnose_discriminator_frontier_status_matrix() -> dict:
    rows = []
    for scenario in SCENARIOS:
        status = classify_discriminator_frontier_status(
            reference_feasible=scenario["reference_feasible"],
            engine_in_scope=scenario["engine_in_scope"],
            native_tower_spectrum_present=scenario["native_tower_spectrum_present"],
            evidence_ready_for_framework_claim=(
                scenario["evidence_ready_for_framework_claim"]
            ),
            tower_claimable_by_math=scenario["tower_claimable_by_math"],
            promotion_ready=scenario["promotion_ready"],
            generic_claim_ready=scenario["generic_claim_ready"],
        )
        rows.append({**scenario, **status, "claimable_now": False})

    status_counts = {
        status: sum(1 for row in rows if row["frontier_status"] == status)
        for status in sorted({row["frontier_status"] for row in rows})
    }
    return {
        "basis": [
            "frontier_status_classifier",
            "promotion_guard",
            "generic_framework_claim_guard",
            "branch_matrix",
        ],
        "scenario_count": len(rows),
        "status_counts": status_counts,
        "tower_discriminator_claim_ready_fixtures": [
            row["label"] for row in rows
            if row["frontier_status"] == "tower_discriminator_claim_ready"
        ],
        "promotion_guard_blocked_fixtures": [
            row["label"] for row in rows
            if row["frontier_status"] == "tower_promotion_guard_blocked"
        ],
        "generic_claim_guard_blocked_fixtures": [
            row["label"] for row in rows
            if row["frontier_status"] == "tower_generic_claim_guard_blocked"
        ],
        "claimable_framework_exclusions_now": [],
        "scenarios": rows,
        "literature_guardrail": {
            "claim": (
                "This is a synthetic branch matrix. It proves classifier behavior, "
                "not a framework-level quantum-gravity claim."
            ),
            "primary_sources": [],
        },
        "interpretation": (
            "The frontier has distinct promotion-guard and generic-claim-guard "
            "blocked states between math exclusion and claim readiness. A row "
            "must clear both before adversarial-review eligibility."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.45/discriminator_frontier_status_matrix.json",
    )
    args = parser.parse_args()

    result = diagnose_discriminator_frontier_status_matrix()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
