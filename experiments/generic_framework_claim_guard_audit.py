"""Generic framework claim guard audit (v2.45).

v2.44 separated source-scope classification from the narrower positive-control
promotion guard. This audit makes that separation enforceable for framework
claim readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.discriminator_frontier import classify_discriminator_frontier_status
from experiments.explicit_tower_basis import _json_default
from experiments.quintic_tower_evidence_candidate import (
    diagnose_quintic_tower_evidence_candidate,
)
from experiments.tower_promotion_guard_audit import (
    diagnose_tower_promotion_guard_audit,
)
from itb.tower import (
    TowerEvidence,
    evaluate_generic_framework_claim_guard,
    evaluate_tower_promotion_guard,
    kk_radius_tower_spectrum,
)


def _candidate_row(
    label: str,
    evidence: dict[str, Any],
    tower_claimable_by_math: bool,
) -> dict[str, Any]:
    promotion_guard = evaluate_tower_promotion_guard(
        evidence,
        tower_claimable_by_math=tower_claimable_by_math,
    )
    generic_guard = evaluate_generic_framework_claim_guard(
        evidence,
        tower_claimable_by_math=tower_claimable_by_math,
    )
    frontier = classify_discriminator_frontier_status(
        reference_feasible=True,
        engine_in_scope=True,
        native_tower_spectrum_present=True,
        evidence_ready_for_framework_claim=generic_guard["evidence_ready"],
        tower_claimable_by_math=tower_claimable_by_math,
        promotion_ready=promotion_guard["ready_for_promotion"],
        generic_claim_ready=generic_guard["ready_for_generic_framework_claim"],
    )
    return {
        "label": label,
        "promotion_guard_ready": promotion_guard["ready_for_promotion"],
        "generic_claim_guard_ready": generic_guard[
            "ready_for_generic_framework_claim"
        ],
        "generic_claim_guard_blockers": generic_guard["blockers"],
        "frontier_status": frontier["frontier_status"],
        "claimable_now": False,
    }


def _owned_asymptotic_fixture() -> TowerEvidence:
    spectrum = kk_radius_tower_spectrum(
        tower_family="synthetic_owned_asymptotic_kk_fixture",
        radius_ratio_mean=2.8,
        log_radius_sigma=0.02,
        normalization="diagnostic owned-endpoint asymptotic normalization",
        source="synthetic v2.45 generic-claim-guard fixture",
        metadata={
            "range_scope": "asymptotic",
            "native_framework_endpoint": "synthetic framework endpoint",
            "native_framework_displacement": "synthetic framework displacement",
        },
    )
    return TowerEvidence(
        framework="string_tree_eft",
        spectrum=spectrum,
        adapter_kind="diagnostic_fixture",
        source_url="https://arxiv.org/abs/1812.07548",
        source_type="primary_literature",
        derivation_kind="diagnostic_fixture",
        uncertainty_kind="exact_fixture_sigma_zero",
        normalization_reference="synthetic fixture normalization",
        metadata={
            "range_scope": "asymptotic",
            "native_framework_endpoint": "synthetic framework endpoint",
            "native_framework_displacement": "synthetic framework displacement",
            "fixture": True,
        },
    )


def diagnose_generic_framework_claim_guard_audit() -> dict[str, Any]:
    guard_audit = diagnose_tower_promotion_guard_audit()
    rows = [
        _candidate_row(
            label=candidate["label"],
            evidence=candidate["evidence"],
            tower_claimable_by_math=candidate["tower_claimable_by_math"],
        )
        for candidate in guard_audit["candidates"]
    ]
    quintic = diagnose_quintic_tower_evidence_candidate()["candidates"][0]
    rows.append(
        _candidate_row(
            label=quintic["label"],
            evidence=quintic["evidence"],
            tower_claimable_by_math=quintic["tower_claimable_by_math"],
        )
    )
    blocker_counts = {
        blocker: sum(
            1 for row in rows
            if blocker in row["generic_claim_guard_blockers"]
        )
        for blocker in sorted({
            blocker
            for row in rows
            for blocker in row["generic_claim_guard_blockers"]
        })
    }

    synthetic_evidence = _owned_asymptotic_fixture()
    synthetic_guard = evaluate_generic_framework_claim_guard(
        synthetic_evidence,
        tower_claimable_by_math=True,
    )
    synthetic_frontier = classify_discriminator_frontier_status(
        reference_feasible=True,
        engine_in_scope=True,
        native_tower_spectrum_present=True,
        evidence_ready_for_framework_claim=synthetic_guard["evidence_ready"],
        tower_claimable_by_math=True,
        promotion_ready=synthetic_guard["promotion_guard"]["ready_for_promotion"],
        generic_claim_ready=synthetic_guard["ready_for_generic_framework_claim"],
    )

    return {
        "basis": [
            "TowerEvidence",
            "promotion_guard",
            "source_scope_classifier",
            "generic_framework_claim_guard",
        ],
        "candidate_count": len(rows),
        "promotion_guard_ready_candidates": [
            row["label"] for row in rows if row["promotion_guard_ready"]
        ],
        "generic_claim_guard_ready_candidates": [
            row["label"] for row in rows if row["generic_claim_guard_ready"]
        ],
        "generic_guard_blocked_after_promotion": [
            row["label"] for row in rows
            if row["promotion_guard_ready"] and not row["generic_claim_guard_ready"]
        ],
        "frontier_status_counts": {
            status: sum(1 for row in rows if row["frontier_status"] == status)
            for status in sorted({row["frontier_status"] for row in rows})
        },
        "top_generic_claim_blockers": blocker_counts,
        "claimable_framework_exclusions_now": [],
        "candidates": rows,
        "synthetic_owned_scope_fixture": {
            "label": "synthetic_owned_asymptotic_kk_fixture",
            "generic_claim_guard_ready": synthetic_guard[
                "ready_for_generic_framework_claim"
            ],
            "generic_claim_guard_blockers": synthetic_guard["blockers"],
            "frontier_status": synthetic_frontier["frontier_status"],
            "claimable_now": False,
            "synthetic_fixture": True,
        },
        "literature_guardrail": {
            "claim": (
                "This is a guard-policy audit. The synthetic owned-scope fixture "
                "proves the pass branch but is not evidence for a framework-level "
                "quantum-gravity exclusion."
            ),
            "primary_sources": [
                {
                    "title": (
                        "Corvilain, Grimm, and Valenzuela, The Swampland "
                        "Distance Conjecture for Kahler moduli"
                    ),
                    "url": "https://arxiv.org/abs/1812.07548",
                },
                {
                    "title": (
                        "Ashmore and Ruehle, Moduli-dependent KK towers and the "
                        "swampland distance conjecture on the quintic Calabi-Yau "
                        "manifold"
                    ),
                    "url": "https://arxiv.org/abs/2103.07472",
                },
                {
                    "title": (
                        "Blumenhagen, Klaewer, Schlechter, and Wolf, The Refined "
                        "Swampland Distance Conjecture in Calabi-Yau Moduli Spaces"
                    ),
                    "url": "https://arxiv.org/abs/1803.04989",
                },
                {
                    "title": (
                        "Aoufia, Castellano, and Ibanez, Laplacians in Various "
                        "Dimensions and the Swampland"
                    ),
                    "url": "https://arxiv.org/abs/2506.03253",
                },
            ],
        },
        "interpretation": (
            "Promotion readiness is no longer sufficient for generic framework "
            "claim readiness. Current candidates still have no claimable framework "
            "exclusion; the next frontier-moving artifact must supply non-synthetic "
            "framework-owned endpoint and displacement metadata."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.45/generic_framework_claim_guard_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_generic_framework_claim_guard_audit()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
