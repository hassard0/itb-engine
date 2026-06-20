"""Per-framework native tower adapter requirement sheet (v2.164)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.native_tower_live_source_triage import (
    diagnose_native_tower_live_source_triage,
    live_native_tower_source_candidates,
)
from experiments.native_tower_ownership_frontier import (
    diagnose_native_tower_ownership_frontier,
)
from itb.predict import FRAMEWORKS
from itb.tower import REQUIRED_TOWER_EVIDENCE_FIELDS


VERSION = "v2.164"

REQUIRED_SPECTRUM_FIELDS = (
    "tower_family",
    "phi_tower_mean",
    "phi_tower_sigma",
    "normalization",
    "source",
)

REQUIRED_NATIVE_OWNERSHIP_FIELDS = (
    "native_framework_endpoint",
    "native_framework_displacement",
    "range_scope_asymptotic",
    "positive_control_screen",
)

REQUIRED_CLAIM_FIELDS = (
    "two_sigma_lower_phi_tower_above_critical_threshold",
    "registered_framework_exclusion_math",
    "external_adversarial_review_status",
)


def native_adapter_authoring_contract() -> dict[str, Any]:
    return {
        "tower_spectrum_required_fields": list(REQUIRED_SPECTRUM_FIELDS),
        "tower_evidence_required_fields": list(REQUIRED_TOWER_EVIDENCE_FIELDS),
        "native_ownership_required_fields": list(REQUIRED_NATIVE_OWNERSHIP_FIELDS),
        "claim_required_fields": list(REQUIRED_CLAIM_FIELDS),
        "source_url_policy": "https://arxiv.org/ or https://doi.org/",
        "allowed_source_types": [
            "primary_literature",
            "computed_compactification",
            "validated_measurement",
        ],
        "threshold_rule": (
            "phi_tower_mean - 2 * phi_tower_sigma > critical_phi_tower"
        ),
        "claim_rule": (
            "A native adapter can become claim-ready only when all contract "
            "fields are source-backed, the generic tower claim guard passes, "
            "and adversarial review is complete."
        ),
    }


def _live_candidates_by_framework() -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {
        name: [] for name in sorted(FRAMEWORKS)
    }
    for row in live_native_tower_source_candidates():
        grouped.setdefault(row["target_framework"], []).append(row)
    return grouped


def _missing_requirements(
    ownership_row: dict[str, Any],
    live_rows: list[dict[str, Any]],
) -> list[str]:
    missing: set[str] = set()
    if not ownership_row["native_tower_spectrum_present"]:
        missing.update(f"spectrum.{field}" for field in REQUIRED_SPECTRUM_FIELDS)
    if not ownership_row["native_tower_evidence_present"]:
        missing.update(REQUIRED_TOWER_EVIDENCE_FIELDS)
    if not ownership_row["native_ownership_ready"]:
        missing.update(REQUIRED_NATIVE_OWNERSHIP_FIELDS)
    if not ownership_row["tower_claimable_by_math"]:
        missing.add("two_sigma_lower_phi_tower_above_critical_threshold")
        missing.add("registered_framework_exclusion_math")
    if not ownership_row["generic_claim_guard_ready"]:
        missing.add("generic_framework_claim_guard_ready")
    if not live_rows:
        missing.add("live_source_candidate")
    for live_row in live_rows:
        if not live_row["adapter_normalization_present"]:
            missing.add("adapter_normalization")
        if not live_row["native_tower_evidence_present"]:
            missing.add("source_owned_tower_evidence")
        if not live_row["registered_target_match"]:
            missing.add("registered_target_match")
    missing.add("external_adversarial_review_status")
    return sorted(missing)


def per_framework_native_adapter_requirements() -> list[dict[str, Any]]:
    ownership = diagnose_native_tower_ownership_frontier()
    live_by_framework = _live_candidates_by_framework()
    rows: list[dict[str, Any]] = []
    for framework in sorted(FRAMEWORKS):
        ownership_row = ownership["frameworks"][framework]
        live_rows = live_by_framework.get(framework, [])
        missing = _missing_requirements(ownership_row, live_rows)
        source_context = [
            {
                "label": row["label"],
                "source_url": row["source_url"],
                "source_class": row["source_class"],
                "native_adapter_triage_ready": row["native_adapter_triage_ready"],
                "blockers": row["blockers"],
            }
            for row in live_rows
        ]
        source_context_ready = any(
            row["native_adapter_triage_ready"] for row in live_rows
        )
        adapter_authoring_ready = (
            ownership_row["target_reference_feasible_in_scope"]
            and source_context_ready
            and not missing
        )
        rows.append({
            "framework": framework,
            "target_reference_feasible_in_scope": (
                ownership_row["target_reference_feasible_in_scope"]
            ),
            "live_source_candidate_count": len(live_rows),
            "live_source_labels": [row["label"] for row in live_rows],
            "source_context": source_context,
            "native_tower_spectrum_present": (
                ownership_row["native_tower_spectrum_present"]
            ),
            "native_tower_evidence_present": (
                ownership_row["native_tower_evidence_present"]
            ),
            "native_ownership_ready": ownership_row["native_ownership_ready"],
            "tower_claimable_by_math": ownership_row["tower_claimable_by_math"],
            "generic_claim_guard_ready": ownership_row["generic_claim_guard_ready"],
            "two_sigma_phi_interval": ownership_row["two_sigma_phi_interval"],
            "missing_requirements": missing,
            "adapter_authoring_ready": adapter_authoring_ready,
            "claim_ready": False,
            "status": (
                "source_context_present_requirements_missing"
                if live_rows
                else "no_live_source_context_requirements_defined"
            ),
        })
    return rows


def diagnose_native_tower_adapter_requirement_sheet() -> dict[str, Any]:
    ownership = diagnose_native_tower_ownership_frontier()
    live_triage = diagnose_native_tower_live_source_triage()
    rows = per_framework_native_adapter_requirements()
    authoring_ready = [
        row["framework"] for row in rows if row["adapter_authoring_ready"]
    ]
    live_context = [
        row["framework"] for row in rows if row["live_source_candidate_count"] > 0
    ]
    no_live_context = [
        row["framework"] for row in rows if row["live_source_candidate_count"] == 0
    ]
    requirement_counts: dict[str, int] = {}
    for row in rows:
        for requirement in row["missing_requirements"]:
            requirement_counts[requirement] = (
                requirement_counts.get(requirement, 0) + 1
            )

    return {
        "version": VERSION,
        "basis": [
            "v2.46_native_tower_ownership_frontier",
            "v2.163_native_tower_live_source_triage",
            "itb.tower.TowerSpectrum",
            "itb.tower.TowerEvidence",
        ],
        "route": "registered_native_tower_adapter_authoring",
        "authoring_contract": native_adapter_authoring_contract(),
        "critical_phi_tower": ownership["critical_phi_tower"],
        "pass_condition": ownership["pass_condition"],
        "live_triage_route_status": live_triage["route_status"],
        "registered_framework_count": len(rows),
        "frameworks_with_live_source_context": live_context,
        "frameworks_without_live_source_context": no_live_context,
        "adapter_authoring_ready_frameworks": authoring_ready,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "missing_requirement_counts": dict(sorted(requirement_counts.items())),
        "rows": rows,
        "route_status": "native_adapter_requirements_defined_no_source_ready",
        "selected_next_build_action": (
            "monitor_or_author_native_adapter_only_when_one_framework_row_fills_contract"
        ),
        "best_next_artifact": (
            "A source-backed adapter packet for one registered framework that "
            "fills the TowerSpectrum, TowerEvidence, ownership, normalization, "
            "threshold, and review fields in this sheet."
        ),
        "interpretation": (
            "The native tower route now has per-framework acceptance criteria. "
            "Live sources cover four registered-framework buckets, but none "
            "fills the contract. Frameworks without live source context should "
            "not be hand-authored from analogies or positive controls."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.164/"
            "native_tower_adapter_requirement_sheet.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_native_tower_adapter_requirement_sheet()
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
