"""Promotion forecast for the quintic tower candidate (v2.36).

v2.34 added a sourced compactification-specific TowerEvidence candidate and
v2.35 showed it does not adjudicate an asymptotic SDC bound. This audit asks
what would happen if we tried to promote the candidate into the framework
catalogue.
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
from itb.predict import FRAMEWORKS


def diagnose_quintic_promotion_forecast() -> dict[str, Any]:
    candidate = diagnose_quintic_tower_evidence_candidate()["candidates"][0]
    schema_ready = candidate["evidence_validation"]["ready_for_framework_claim"]
    tower_verdict = candidate["framework_tower_verdict"]
    tower_excluding = bool(candidate["tower_claimable_by_math"])
    generic_blockers = [
        "source_covers_one_parameter_quintic_not_generic_string_tree_eft",
        "source_covers_scalar_laplacian_subtower_not_full_tower_spectrum",
        "finite_range_fit_not_asymptotic_lightest_tower",
    ]
    scoped_registration_effect = {
        "new_framework_name": "string_tree_quintic_compactification",
        "would_increase_registered_framework_count_to": len(FRAMEWORKS) + 1,
        "would_have_native_tower_evidence": schema_ready,
        "expected_tower_verdict": tower_verdict,
        "would_create_framework_exclusion": tower_excluding,
        "expected_frontier_status": (
            "tower_evidence_present_but_not_excluding"
            if schema_ready and not tower_excluding
            else "not_ready"
        ),
    }
    return {
        "basis": ["TowerEvidence", "framework_scope", "promotion_forecast"],
        "current_registered_framework_count": len(FRAMEWORKS),
        "candidate": {
            "label": candidate["label"],
            "framework": candidate["framework"],
            "schema_ready": schema_ready,
            "tower_verdict": tower_verdict,
            "tower_excluding": tower_excluding,
        },
        "promotion_modes": {
            "attach_to_generic_string_tree_eft": {
                "allowed": False,
                "blockers": generic_blockers,
            },
            "register_scoped_quintic_framework": {
                "allowed": True,
                "blockers": [],
                "forecast": scoped_registration_effect,
            },
            "keep_external_candidate": {
                "allowed": True,
                "blockers": [],
                "forecast": {
                    "registered_framework_count": len(FRAMEWORKS),
                    "claimable_framework_exclusions_now": [],
                },
            },
        },
        "recommended_next_action": (
            "Do not attach the quintic row to generic string_tree_eft. Register a "
            "scoped quintic framework only if the catalogue needs compactification "
            "benchmarks; it will improve evidence coverage but will not create a "
            "tower exclusion. For a discriminator, prioritize asymptotic lightest-"
            "tower extraction or a compactification source with phi_tower above "
            "the critical threshold."
        ),
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "Promotion changes catalogue ownership, not the physics verdict. "
                "The sourced quintic row is schema-ready but tower-allowed."
            ),
            "primary_sources": [
                {
                    "title": (
                        "Ashmore and Ruehle, Moduli-dependent KK towers and the "
                        "swampland distance conjecture on the quintic Calabi-Yau manifold"
                    ),
                    "url": "https://arxiv.org/abs/2103.07472",
                },
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.36/quintic_promotion_forecast.json",
    )
    args = parser.parse_args()

    result = diagnose_quintic_promotion_forecast()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
