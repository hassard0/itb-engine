"""Tower promotion guard audit (v2.41).

v2.40 recommended a conservative promotion guard. This audit verifies the guard
against the known positive controls and a non-positive-control excluding fixture.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.analytic_kk_tower_benchmark import (
    SOURCE as ANALYTIC_KK_SOURCE,
    diagnose_analytic_kk_tower_benchmark,
)
from experiments.explicit_tower_basis import _json_default
from experiments.large_volume_sdc_benchmark import diagnose_large_volume_sdc_benchmark
from itb.predict import FRAMEWORKS
from itb.tower import (
    TowerEvidence,
    TowerSpectrum,
    evaluate_tower_promotion_guard,
)


def _row(
    *,
    label: str,
    evidence: TowerEvidence | dict[str, Any],
    tower_claimable_by_math: bool,
    fixture: bool = False,
) -> dict[str, Any]:
    guard = evaluate_tower_promotion_guard(
        evidence,
        tower_claimable_by_math=tower_claimable_by_math,
    )
    if "known_qg_positive_control_family" in guard["blockers"]:
        status = "promotion_blocked_known_positive_control"
    elif guard["ready_for_promotion"] and fixture:
        status = "promotion_guard_ready_fixture"
    elif guard["ready_for_promotion"]:
        status = "promotion_guard_ready_candidate"
    else:
        status = "promotion_guard_blocked_other"
    row = evidence.to_dict() if hasattr(evidence, "to_dict") else dict(evidence)
    return {
        "label": label,
        "evidence": row,
        "tower_claimable_by_math": tower_claimable_by_math,
        "promotion_guard": guard,
        "status": status,
        "claimable_now": False,
    }


def _analytic_kk_evidence(candidate: dict[str, Any]) -> TowerEvidence:
    spectrum = TowerSpectrum(
        tower_family=candidate["label"],
        phi_tower_mean=candidate["phi_tower_mean"],
        phi_tower_sigma=candidate["phi_tower_sigma"],
        tower_mass_gap=candidate["tower_mass_gap"],
        normalization=(
            "phi_tower = |zeta_KK,p| * Delta_moduli with Delta_moduli=1 "
            "benchmark"
        ),
        source=f"{ANALYTIC_KK_SOURCE['title']}, {ANALYTIC_KK_SOURCE['formula']}",
        metadata={
            "source_family": "analytic_kk_decompactification_vector",
            "known_qg_positive_control": True,
            "dimension": candidate["dimension"],
            "internal_dimension": candidate["internal_dimension"],
        },
    )
    return TowerEvidence(
        framework="string_tree_eft",
        spectrum=spectrum,
        adapter_kind="analytic_kk_vector_benchmark",
        source_url=ANALYTIC_KK_SOURCE["url"],
        source_type="primary_literature",
        derivation_kind="analytic_kk_vector_formula",
        uncertainty_kind="exact_formula_sigma_zero",
        normalization_reference=(
            "|zeta_KK,p| = sqrt((d + p - 2) / (p * (d - 2))); "
            "benchmark sets Delta_moduli=1"
        ),
        metadata={
            "source_family": "analytic_kk_decompactification_vector",
            "known_qg_positive_control": True,
        },
    )


def _non_positive_control_fixture() -> TowerEvidence:
    spectrum = TowerSpectrum(
        tower_family="non_positive_control_excluding_fixture",
        phi_tower_mean=1.0,
        phi_tower_sigma=0.0,
        tower_mass_gap=math.exp(-1.0),
        normalization="diagnostic fixture with no positive-control family marker",
        source="synthetic v2.41 promotion-guard fixture",
        metadata={"source_family": "hypothetical_non_positive_control"},
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
        metadata={"fixture": True},
    )


def diagnose_tower_promotion_guard_audit() -> dict[str, Any]:
    large_volume = diagnose_large_volume_sdc_benchmark()["candidate"]
    analytic = diagnose_analytic_kk_tower_benchmark()
    candidates = [
        _row(
            label=large_volume["label"],
            evidence=large_volume["evidence"],
            tower_claimable_by_math=large_volume["tower_claimable_by_math"],
        )
    ]
    candidates.extend(
        _row(
            label=candidate["label"],
            evidence=_analytic_kk_evidence(candidate),
            tower_claimable_by_math=candidate["benchmark_tower_verdict"]
            == "benchmark_excluding",
        )
        for candidate in analytic["candidates"]
    )
    candidates.append(
        _row(
            label="non_positive_control_excluding_fixture",
            evidence=_non_positive_control_fixture(),
            tower_claimable_by_math=True,
            fixture=True,
        )
    )

    status_counts = {
        status: sum(1 for row in candidates if row["status"] == status)
        for status in sorted({row["status"] for row in candidates})
    }
    return {
        "basis": ["TowerEvidence", "promotion_guard", "positive_control_block"],
        "registered_framework_count": len(FRAMEWORKS),
        "candidate_count": len(candidates),
        "positive_control_promotion_blocked": [
            row["label"] for row in candidates
            if row["status"] == "promotion_blocked_known_positive_control"
        ],
        "promotion_guard_ready_non_positive_control_fixtures": [
            row["label"] for row in candidates
            if row["status"] == "promotion_guard_ready_fixture"
        ],
        "status_counts": status_counts,
        "tower_discriminator_candidates_now": [],
        "claimable_framework_exclusions_now": [],
        "candidates": candidates,
        "literature_guardrail": {
            "claim": (
                "The promotion guard blocks known string-compatible positive "
                "controls from becoming framework claims. A synthetic non-positive "
                "fixture can still pass the guard, proving the guard is scoped."
            ),
            "primary_sources": [
                {
                    "title": (
                        "Blumenhagen, Klaewer, Schlechter, and Wolf, The Refined "
                        "Swampland Distance Conjecture in Calabi-Yau Moduli Spaces"
                    ),
                    "url": "https://arxiv.org/abs/1803.04989",
                },
                {
                    "title": ANALYTIC_KK_SOURCE["title"],
                    "url": ANALYTIC_KK_SOURCE["url"],
                },
            ],
        },
        "interpretation": (
            "The guard implements the v2.40 recommendation: keep tower math as a "
            "diagnostic, but block promotion for known string-compatible "
            "decompactification positive controls."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.41/tower_promotion_guard_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_tower_promotion_guard_audit()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
