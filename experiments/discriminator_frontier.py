"""Current discriminator frontier audit (v2.32).

v2.31 added a provenance gate for tower claims. This audit summarizes the
current state across all registered frameworks: reference-stack status, engine
scope, native tower spectra, native tower evidence, and the exact blocker that
prevents a framework-level tower discriminator today.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_framework_scenarios import _framework_reference_verdicts
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness
from itb.predict import FRAMEWORKS
from itb.scope import engine_validity
from itb.tower import validate_tower_evidence


def _to_dict(value: Any) -> dict | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return dict(to_dict())
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {"adapter_error": f"unsupported object type: {type(value).__name__}"}


def _native_spectrum(framework: Any) -> dict | None:
    method = getattr(framework, "tower_spectrum", None)
    return _to_dict(method()) if callable(method) else None


def _native_evidence(framework: Any) -> dict | None:
    method = getattr(framework, "tower_evidence", None)
    return _to_dict(method()) if callable(method) else None


def _framework_row(
    name: str,
    reference: dict[str, dict],
    readiness: dict,
) -> dict:
    framework = FRAMEWORKS[name]
    scope = engine_validity(framework)
    spectrum = _native_spectrum(framework)
    evidence = _native_evidence(framework)
    evidence_validation = (
        validate_tower_evidence(evidence)
        if evidence is not None
        else {
            "ready_for_framework_claim": False,
            "missing_fields": ["TowerEvidence"],
            "source_url_valid": False,
            "source_type_valid": False,
            "blockers": ["missing_native_tower_evidence"],
        }
    )
    tower_row = readiness["frameworks"][name]
    ref_ok = bool(reference[name]["reference_feasible"])
    if not ref_ok:
        frontier_status = "reference_excluded_before_tower"
        next_required_artifact = "Adversarial review of the reference-stack exclusion."
    elif not scope.in_scope:
        frontier_status = "scope_limited_reference_survivor"
        next_required_artifact = "Resolve engine scope assumptions before treating verdict as physical."
    elif spectrum is None:
        frontier_status = "missing_native_tower_spectrum"
        next_required_artifact = "Implement a sourced TowerSpectrum or TowerEvidence adapter."
    elif not evidence_validation["ready_for_framework_claim"]:
        frontier_status = "missing_or_rejected_tower_evidence"
        next_required_artifact = "Supply TowerEvidence with source, derivation, normalization, and uncertainty."
    elif not tower_row["claimable_exclusion"]:
        frontier_status = "tower_evidence_present_but_not_excluding"
        next_required_artifact = "Improve tower precision or accept non-excluding tower evidence."
    else:
        frontier_status = "tower_discriminator_claim_ready"
        next_required_artifact = "Run adversarial review before solution claim."

    return {
        "framework": name,
        "reference_feasible": ref_ok,
        "reference_binding": reference[name]["binding"],
        "engine_scope": {
            "in_scope": scope.in_scope,
            "violations": scope.violations,
            "note": scope.note,
        },
        "native_tower_spectrum_present": spectrum is not None,
        "native_tower_evidence_present": evidence is not None,
        "tower_evidence_validation": evidence_validation,
        "tower_readiness_verdict": tower_row["framework_tower_verdict"],
        "tower_claimable_by_math": tower_row["claimable_exclusion"],
        "frontier_status": frontier_status,
        "next_required_artifact": next_required_artifact,
    }


def diagnose_discriminator_frontier() -> dict:
    reference = _framework_reference_verdicts()
    readiness = diagnose_tower_spectrum_readiness()
    rows = {
        name: _framework_row(name, reference, readiness)
        for name in FRAMEWORKS
    }
    statuses = sorted({row["frontier_status"] for row in rows.values()})
    status_counts = {
        status: sum(1 for row in rows.values() if row["frontier_status"] == status)
        for status in statuses
    }
    claim_ready = [
        name for name, row in rows.items()
        if row["frontier_status"] == "tower_discriminator_claim_ready"
    ]
    reference_feasible = [
        name for name, row in rows.items() if row["reference_feasible"]
    ]
    return {
        "basis": ["framework", "reference_stack", "TowerSpectrum", "TowerEvidence"],
        "registered_framework_count": len(rows),
        "reference_feasible_frameworks": reference_feasible,
        "reference_excluded_frameworks": [
            name for name, row in rows.items() if not row["reference_feasible"]
        ],
        "frontier_status_counts": status_counts,
        "tower_discriminator_claim_ready": claim_ready,
        "claimable_framework_exclusions_now": [],
        "frameworks": rows,
        "literature_guardrail": {
            "claim": (
                "This is a frontier audit, not a solution claim. A framework "
                "requires reference feasibility, in-scope assumptions, native "
                "tower evidence, and an excluding two-sigma tower interval before "
                "the engine can promote it to an adversarial-review candidate."
            ),
            "primary_sources": [
                {
                    "title": "Dvali and Redi, Black Hole Bound on the Number of Species and Quantum Gravity at LHC",
                    "url": "https://arxiv.org/abs/0710.4344",
                },
                {
                    "title": "Corvilain, Grimm, and Valenzuela, The Swampland Distance Conjecture for Kahler moduli",
                    "url": "https://arxiv.org/abs/1812.07548",
                },
            ],
        },
        "interpretation": (
            "The current frontier has reference-stack exclusions and reference-feasible "
            "survivors, but no registered framework has native non-synthetic tower "
            "evidence. The next required artifact is a sourced TowerEvidence row for "
            "one reference-feasible, in-scope framework."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.32/discriminator_frontier.json")
    args = parser.parse_args()

    result = diagnose_discriminator_frontier()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
