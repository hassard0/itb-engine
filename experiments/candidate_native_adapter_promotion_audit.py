"""Candidate-to-native adapter promotion audit (v2.48).

v2.47 proved that the live frontier will accept a properly owned native tower
adapter. This audit asks whether any current non-synthetic tower evidence row is
honestly ready to become that adapter today.
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
from itb.predict import FRAMEWORKS
from itb.tower import (
    classify_tower_source_scope,
    evaluate_generic_framework_claim_guard,
    validate_tower_evidence,
)


def _metadata_has_fixture_marker(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            key == "fixture" and item is True
            or _metadata_has_fixture_marker(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set)):
        return any(_metadata_has_fixture_marker(item) for item in value)
    return False


def _candidate_rows() -> list[dict[str, Any]]:
    guard_rows = [
        row for row in diagnose_tower_promotion_guard_audit()["candidates"]
        if not _metadata_has_fixture_marker(row["evidence"])
    ]
    quintic = diagnose_quintic_tower_evidence_candidate()["candidates"][0]
    return [
        {
            "label": row["label"],
            "evidence": row["evidence"],
            "tower_claimable_by_math": row["tower_claimable_by_math"],
        }
        for row in guard_rows
    ] + [
        {
            "label": quintic["label"],
            "evidence": quintic["evidence"],
            "tower_claimable_by_math": quintic["tower_claimable_by_math"],
        }
    ]


def _framework_native_evidence_present(framework_name: str) -> bool:
    framework = FRAMEWORKS.get(framework_name)
    if framework is None:
        return False
    method = getattr(framework, "tower_evidence", None)
    return bool(callable(method) and method() is not None)


def _row(candidate: dict[str, Any]) -> dict[str, Any]:
    evidence = candidate["evidence"]
    framework = evidence["framework"]
    validation = validate_tower_evidence(evidence)
    source_scope = classify_tower_source_scope(evidence)
    generic_guard = evaluate_generic_framework_claim_guard(
        evidence,
        tower_claimable_by_math=candidate["tower_claimable_by_math"],
    )
    blockers = set(generic_guard["blockers"])
    if not _framework_native_evidence_present(framework):
        blockers.add("not_exposed_by_registered_framework_adapter")
    if not validation["ready_for_framework_claim"]:
        blockers.add("tower_evidence_not_ready")

    promotable = (
        validation["ready_for_framework_claim"]
        and candidate["tower_claimable_by_math"]
        and generic_guard["ready_for_generic_framework_claim"]
        and _framework_native_evidence_present(framework)
    )

    return {
        "label": candidate["label"],
        "framework": framework,
        "source_type": evidence["source_type"],
        "source_url": evidence["source_url"],
        "tower_claimable_by_math": candidate["tower_claimable_by_math"],
        "evidence_ready": validation["ready_for_framework_claim"],
        "native_adapter_present": _framework_native_evidence_present(framework),
        "source_scope": source_scope,
        "generic_claim_guard_ready": generic_guard[
            "ready_for_generic_framework_claim"
        ],
        "promotable_to_native_adapter_now": promotable,
        "promotion_blockers": sorted(blockers),
        "claimable_now": False,
    }


def diagnose_candidate_native_adapter_promotion_audit() -> dict[str, Any]:
    rows = [_row(candidate) for candidate in _candidate_rows()]
    blocker_counts = {
        blocker: sum(1 for row in rows if blocker in row["promotion_blockers"])
        for blocker in sorted({
            blocker
            for row in rows
            for blocker in row["promotion_blockers"]
        })
    }
    return {
        "basis": [
            "non_synthetic_tower_candidates",
            "native_adapter_contract",
            "generic_framework_claim_guard",
        ],
        "candidate_count": len(rows),
        "tower_math_excluding_candidates": [
            row["label"] for row in rows if row["tower_claimable_by_math"]
        ],
        "generic_claim_guard_ready_candidates": [
            row["label"] for row in rows if row["generic_claim_guard_ready"]
        ],
        "promotable_native_adapter_candidates": [
            row["label"] for row in rows
            if row["promotable_to_native_adapter_now"]
        ],
        "positive_control_candidates": [
            row["label"] for row in rows
            if row["source_scope"]["positive_control_matches"]
        ],
        "finite_range_candidates": [
            row["label"] for row in rows
            if row["source_scope"]["range_scope"] == "finite_range"
        ],
        "promotion_blocker_counts": blocker_counts,
        "claimable_framework_exclusions_now": [],
        "candidates": rows,
        "literature_guardrail": {
            "claim": (
                "This is a promotion-readiness audit over existing non-synthetic "
                "candidate rows. It does not convert external compactification "
                "or decompactification evidence into native framework evidence."
            ),
            "primary_sources": [
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
            "Current non-synthetic tower candidates include math-excluding rows, "
            "but none can be promoted into a live native adapter today. The common "
            "blocker is missing registered-framework adapter ownership, with "
            "positive-control and finite-range blockers separating the source "
            "families."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.48/"
            "candidate_native_adapter_promotion_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_candidate_native_adapter_promotion_audit()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
