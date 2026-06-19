"""Native tower-ownership frontier audit (v2.46).

v2.45 made generic framework claim readiness stricter than promotion readiness.
This audit applies that stricter gate to live registered frameworks and reports
the exact native-adapter artifact needed to move the frontier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.discriminator_frontier import diagnose_discriminator_frontier
from experiments.explicit_tower_basis import _json_default
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness


def _row_blockers(row: dict[str, Any]) -> list[str]:
    if not row["reference_feasible"]:
        return ["reference_excluded_before_tower"]
    if not row["engine_scope"]["in_scope"]:
        return ["engine_scope_limited"]
    blockers = []
    if not row["native_tower_spectrum_present"]:
        blockers.append("missing_native_tower_spectrum")
    if not row["native_tower_evidence_present"]:
        blockers.append("missing_native_tower_evidence")
    blockers.extend(row["tower_generic_claim_guard"]["blockers"])
    return sorted(set(blockers))


def _framework_row(
    name: str,
    frontier_row: dict[str, Any],
    readiness_row: dict[str, Any],
) -> dict[str, Any]:
    source_scope = frontier_row["tower_generic_claim_guard"].get("source_scope")
    ownership_ready = bool(
        source_scope
        and source_scope["endpoint_owned_by_framework"]
        and source_scope["displacement_owned_by_framework"]
    )
    target = bool(
        frontier_row["reference_feasible"]
        and frontier_row["engine_scope"]["in_scope"]
    )
    return {
        "framework": name,
        "target_reference_feasible_in_scope": target,
        "frontier_status": frontier_row["frontier_status"],
        "native_tower_spectrum_present": frontier_row["native_tower_spectrum_present"],
        "native_tower_evidence_present": frontier_row["native_tower_evidence_present"],
        "tower_evidence_ready": frontier_row["tower_evidence_validation"][
            "ready_for_framework_claim"
        ],
        "tower_claimable_by_math": frontier_row["tower_claimable_by_math"],
        "generic_claim_guard_ready": frontier_row["tower_generic_claim_guard"][
            "ready_for_generic_framework_claim"
        ],
        "native_ownership_ready": ownership_ready,
        "two_sigma_phi_interval": readiness_row["two_sigma_phi_interval"],
        "critical_phi_tower": readiness_row.get("critical_phi_tower"),
        "blockers": _row_blockers(frontier_row),
    }


def diagnose_native_tower_ownership_frontier() -> dict[str, Any]:
    frontier = diagnose_discriminator_frontier()
    readiness = diagnose_tower_spectrum_readiness()
    rows = {
        name: _framework_row(name, row, readiness["frameworks"][name])
        for name, row in frontier["frameworks"].items()
    }
    target_rows = {
        name: row for name, row in rows.items()
        if row["target_reference_feasible_in_scope"]
    }
    target_blockers = {
        blocker: sum(1 for row in target_rows.values() if blocker in row["blockers"])
        for blocker in sorted({
            blocker
            for row in target_rows.values()
            for blocker in row["blockers"]
        })
    }
    generic_ready = [
        name for name, row in rows.items() if row["generic_claim_guard_ready"]
    ]
    ownership_ready = [
        name for name, row in rows.items() if row["native_ownership_ready"]
    ]

    return {
        "basis": [
            "registered_frameworks",
            "native_tower_spectrum",
            "native_tower_evidence",
            "generic_framework_claim_guard",
        ],
        "registered_framework_count": frontier["registered_framework_count"],
        "critical_phi_tower": readiness["critical_phi_tower"],
        "pass_condition": {
            "target_reference_feasible_in_scope": True,
            "native_tower_evidence_present": True,
            "native_ownership_ready": True,
            "generic_claim_guard_ready": True,
            "two_sigma_lower_bound_required": (
                "phi_tower_mean - 2 * phi_tower_sigma > critical_phi_tower"
            ),
        },
        "reference_feasible_in_scope_frameworks": list(target_rows),
        "n_reference_feasible_in_scope_frameworks": len(target_rows),
        "native_tower_evidence_frameworks": [
            name for name, row in rows.items()
            if row["native_tower_evidence_present"]
        ],
        "native_ownership_ready_frameworks": ownership_ready,
        "generic_framework_claim_ready_candidates": generic_ready,
        "tower_discriminator_claim_ready": frontier["tower_discriminator_claim_ready"],
        "claimable_framework_exclusions_now": [],
        "target_blocker_counts": target_blockers,
        "frameworks": rows,
        "literature_guardrail": {
            "claim": (
                "This is a live native-adapter audit, not a solution claim. A "
                "framework can move to claim readiness only with native, sourced, "
                "owned tower evidence whose two-sigma lower phi bound exceeds the "
                "tower threshold."
            ),
            "primary_sources": [
                {
                    "title": (
                        "Dvali and Redi, Black Hole Bound on the Number of "
                        "Species and Quantum Gravity at LHC"
                    ),
                    "url": "https://arxiv.org/abs/0710.4344",
                },
                {
                    "title": (
                        "van de Heisteeg, Vafa, and Wiesner, Bounds on Species "
                        "Scale and the Distance Conjecture"
                    ),
                    "url": "https://arxiv.org/abs/2303.13580",
                },
            ],
        },
        "interpretation": (
            "The live registered framework frontier is still blocked before "
            "source-scope ownership can be evaluated: all reference-feasible, "
            "in-scope targets lack native TowerSpectrum and TowerEvidence "
            "adapters. The next frontier-moving change must implement one native "
            "adapter row, not add another external candidate row."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.46/native_tower_ownership_frontier.json",
    )
    args = parser.parse_args()

    result = diagnose_native_tower_ownership_frontier()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
