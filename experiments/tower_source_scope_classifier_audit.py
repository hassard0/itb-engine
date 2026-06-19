"""Tower source-scope classifier audit (v2.44).

v2.41-v2.43 installed a positive-control promotion guard. This audit adds a
source-scope layer that distinguishes guard behavior from the stronger question
of generic framework claim readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.quintic_tower_evidence_candidate import (
    diagnose_quintic_tower_evidence_candidate,
)
from experiments.tower_promotion_guard_audit import (
    diagnose_tower_promotion_guard_audit,
)
from itb.tower import classify_tower_source_scope, evaluate_tower_promotion_guard


def _row(label: str, evidence: dict[str, Any], tower_claimable_by_math: bool) -> dict:
    source_scope = classify_tower_source_scope(evidence)
    promotion_guard = evaluate_tower_promotion_guard(
        evidence,
        tower_claimable_by_math=tower_claimable_by_math,
    )
    return {
        "label": label,
        "source_scope": source_scope,
        "promotion_guard_ready": promotion_guard["ready_for_promotion"],
        "generic_framework_claim_ready": source_scope["generic_framework_claim_ready"],
        "positive_control": bool(source_scope["positive_control_matches"]),
        "finite_range": source_scope["range_scope"] == "finite_range",
        "claimable_now": False,
    }


def diagnose_tower_source_scope_classifier_audit() -> dict[str, Any]:
    guard_audit = diagnose_tower_promotion_guard_audit()
    rows = [
        _row(
            label=candidate["label"],
            evidence=candidate["evidence"],
            tower_claimable_by_math=candidate["tower_claimable_by_math"],
        )
        for candidate in guard_audit["candidates"]
    ]
    quintic = diagnose_quintic_tower_evidence_candidate()["candidates"][0]
    rows.append(
        _row(
            label=quintic["label"],
            evidence=quintic["evidence"],
            tower_claimable_by_math=quintic["tower_claimable_by_math"],
        )
    )

    return {
        "basis": ["TowerEvidence", "source_scope_classifier", "promotion_guard"],
        "candidate_count": len(rows),
        "positive_control_candidates": [
            row["label"] for row in rows if row["positive_control"]
        ],
        "finite_range_candidates": [
            row["label"] for row in rows if row["finite_range"]
        ],
        "promotion_guard_ready_candidates": [
            row["label"] for row in rows if row["promotion_guard_ready"]
        ],
        "generic_framework_claim_ready_candidates": [
            row["label"] for row in rows if row["generic_framework_claim_ready"]
        ],
        "claimable_framework_exclusions_now": [],
        "candidates": rows,
        "literature_guardrail": {
            "claim": (
                "Source-scope readiness is stricter than the positive-control "
                "promotion guard. This audit classifies evidence rows but does "
                "not promote any framework claim."
            ),
            "primary_sources": [
                {
                    "title": (
                        "Ashmore and Ruehle, Moduli-dependent KK towers and the "
                        "swampland distance conjecture on the quintic Calabi-Yau manifold"
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
            "Known positive controls and finite-range single-compactification rows "
            "are now classified separately. No current evidence row has framework-"
            "owned endpoint and displacement metadata, so none is generically "
            "framework-claim ready."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.44/tower_source_scope_classifier_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_tower_source_scope_classifier_audit()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
