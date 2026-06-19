"""Non-tower promotion guard audit (v2.52).

v2.51 found source-backed theory for g_C/g_8 but no external numerical
measurement route. This audit makes that blocker enforceable and checks the
guard against current routes plus a synthetic fully sourced fixture.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.weyl_g8_observable_sourceability import (
    diagnose_weyl_g8_observable_sourceability,
)
from itb.nontower import ExternalMeasurementEvidence, evaluate_nontower_promotion_guard


def _sourceability_evidence(row: dict[str, Any]) -> ExternalMeasurementEvidence:
    source_url = (
        row["primary_sources"][0]["url"]
        if row.get("primary_sources")
        else "internal"
    )
    return ExternalMeasurementEvidence(
        axis=row["axis"],
        route=row["route"],
        source_url=source_url,
        source_type="primary_literature" if row["source_backed_theory"] else "internal",
        measurement_kind=(
            "external_numeric_measurement"
            if row["external_numeric_measurement"]
            else row["measurement_program_status"]
        ),
        numerical_value=None,
        uncertainty=None,
        axis_mapping_kind=(
            "source_backed_direct"
            if row["source_backed_axis_mapping"]
            else "toy_or_structural_proxy"
        ),
        systematics_status="unresolved",
        metadata={
            "status": row["status"],
            "implementation": row["implementation"],
            "internal_cut_only": row["measurement_program_status"]
            != "external_numeric_measurement",
        },
    )


def _birefringence_hint_evidence() -> ExternalMeasurementEvidence:
    return ExternalMeasurementEvidence(
        axis="g_R2_parity",
        route="cosmic_birefringence_hint",
        source_url="https://arxiv.org/abs/2509.13654",
        source_type="primary_literature",
        measurement_kind="external_detection",
        numerical_value=0.215,
        uncertainty=0.074,
        axis_mapping_kind="toy_or_structural_proxy",
        systematics_status="unresolved",
        metadata={
            "internal_cut_only": False,
            "blocker_context": [
                "sub_5sigma_detection",
                "instrument_angle_miscalibration_degeneracy",
                "one_observable_dominated_engine_route",
            ],
        },
    )


def _synthetic_ready_evidence() -> ExternalMeasurementEvidence:
    return ExternalMeasurementEvidence(
        axis="g_8",
        route="synthetic_external_spin4_measurement",
        source_url="https://doi.org/10.0000/synthetic.v2.52",
        source_type="validated_measurement",
        measurement_kind="external_numeric_measurement",
        numerical_value=0.41,
        uncertainty=0.02,
        axis_mapping_kind="source_backed_direct",
        systematics_status="closed",
        metadata={"synthetic_fixture": True, "internal_cut_only": False},
    )


def _guard_row(
    *,
    label: str,
    evidence: ExternalMeasurementEvidence,
    discriminator_claimable_by_math: bool,
) -> dict[str, Any]:
    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=discriminator_claimable_by_math,
    )
    return {
        "label": label,
        "evidence": evidence.to_dict(),
        "guard": guard,
        "frontier_status": (
            "non_tower_discriminator_claim_ready"
            if guard["ready_for_promotion"]
            else "non_tower_promotion_guard_blocked"
        ),
    }


def diagnose_nontower_promotion_guard_audit() -> dict[str, Any]:
    sourceability = diagnose_weyl_g8_observable_sourceability()
    current_rows = [
        _guard_row(
            label=f"sourceability:{row['route']}",
            evidence=_sourceability_evidence(row),
            discriminator_claimable_by_math=False,
        )
        for row in sourceability["rows"]
    ]
    birefringence_row = _guard_row(
        label="birefringence:act_dr6_hint",
        evidence=_birefringence_hint_evidence(),
        discriminator_claimable_by_math=False,
    )
    synthetic_row = _guard_row(
        label="synthetic:ready_external_measurement",
        evidence=_synthetic_ready_evidence(),
        discriminator_claimable_by_math=True,
    )
    rows = [*current_rows, birefringence_row, synthetic_row]
    status_counts = {
        status: sum(1 for row in rows if row["frontier_status"] == status)
        for status in sorted({row["frontier_status"] for row in rows})
    }
    current_claim_ready = [
        row["label"] for row in rows
        if row["frontier_status"] == "non_tower_discriminator_claim_ready"
        and not row["label"].startswith("synthetic:")
    ]
    blocker_counts = {
        blocker: sum(1 for row in rows if blocker in row["guard"]["blockers"])
        for blocker in sorted({
            blocker for row in rows for blocker in row["guard"]["blockers"]
        })
    }
    return {
        "basis": [
            "ExternalMeasurementEvidence",
            "non_tower_promotion_guard",
            "v2.51_sourceability_rows",
            "birefringence_hint_guard",
        ],
        "scenario_count": len(rows),
        "status_counts": status_counts,
        "current_claim_ready_routes": current_claim_ready,
        "synthetic_claim_ready_routes": [
            row["label"] for row in rows
            if row["frontier_status"] == "non_tower_discriminator_claim_ready"
        ],
        "claimable_discriminator_now": bool(current_claim_ready),
        "blocker_counts": blocker_counts,
        "scenarios": rows,
        "route_status": "promotion_guard_enforced",
        "interpretation": (
            "The non-tower promotion guard blocks every current g_C/g_8 and "
            "birefringence route. A synthetic fixture proves the positive path: "
            "external numeric evidence, source-backed axis mapping, closed "
            "systematics, and excluding math are all required."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.52/nontower_promotion_guard_audit.json",
    )
    args = parser.parse_args()

    result = diagnose_nontower_promotion_guard_audit()
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
