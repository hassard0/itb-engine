"""Tower evidence gate for framework-level claims (v2.31).

v2.24-v2.30 made the tower adapter path operational. This audit adds the
provenance gate: an adapter verdict is not enough for a framework claim unless
the tower spectrum carries source, derivation, normalization, and uncertainty
evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_spectrum_readiness import diagnose_tower_spectrum_readiness
from itb.tower import TowerEvidence, kk_radius_tower_spectrum, validate_tower_evidence


def _spectrum(radius_ratio: float, log_radius_sigma: float):
    return kk_radius_tower_spectrum(
        tower_family="kk_radius_synthetic_candidate",
        radius_ratio_mean=radius_ratio,
        log_radius_sigma=log_radius_sigma,
        normalization="radius_ratio_R_over_R0_diagnostic",
        source="synthetic v2.31 evidence-gate fixture",
        metadata={"radius_ratio_source": "fixture"},
    )


def _default_candidates() -> list[dict[str, Any]]:
    excluded_spectrum = _spectrum(2.60, 0.04)
    overlap_spectrum = _spectrum(2.10, 0.05)
    return [
        {
            "label": "math_excludes_but_missing_source",
            "framework": "string_tree_eft",
            "spectrum": excluded_spectrum,
            "evidence": {
                "framework": "string_tree_eft",
                "spectrum": excluded_spectrum.to_dict(),
                "adapter_kind": "kk_radius",
                "source_url": "",
                "source_type": "",
                "derivation_kind": "diagnostic_fixture",
                "uncertainty_kind": "log_radius_one_sigma",
                "normalization_reference": "R/R0 diagnostic normalization",
            },
        },
        {
            "label": "primary_source_but_overlaps_threshold",
            "framework": "string_tree_eft",
            "spectrum": overlap_spectrum,
            "evidence": TowerEvidence(
                framework="string_tree_eft",
                spectrum=overlap_spectrum,
                adapter_kind="kk_radius",
                source_url="https://arxiv.org/abs/1812.07548",
                source_type="primary_literature",
                derivation_kind="diagnostic_fixture",
                uncertainty_kind="log_radius_one_sigma",
                normalization_reference="R/R0 diagnostic normalization",
            ),
        },
        {
            "label": "complete_schema_exclusion_fixture",
            "framework": "string_tree_eft",
            "spectrum": excluded_spectrum,
            "evidence": TowerEvidence(
                framework="string_tree_eft",
                spectrum=excluded_spectrum,
                adapter_kind="kk_radius",
                source_url="https://arxiv.org/abs/1812.07548",
                source_type="primary_literature",
                derivation_kind="diagnostic_fixture",
                uncertainty_kind="log_radius_one_sigma",
                normalization_reference="R/R0 diagnostic normalization",
            ),
        },
    ]


def _candidate_row(candidate: dict[str, Any]) -> dict:
    framework = candidate["framework"]
    spectrum = candidate["spectrum"]
    readiness = diagnose_tower_spectrum_readiness(spectra={framework: spectrum})
    framework_row = readiness["frameworks"][framework]
    validation = validate_tower_evidence(candidate["evidence"])
    schema_ready_and_tower_excluding = (
        validation["ready_for_framework_claim"]
        and framework_row["claimable_exclusion"]
    )
    return {
        "label": candidate["label"],
        "framework": framework,
        "framework_tower_verdict": framework_row["framework_tower_verdict"],
        "tower_claimable_by_math": framework_row["claimable_exclusion"],
        "evidence_validation": validation,
        "schema_ready_and_tower_excluding": schema_ready_and_tower_excluding,
        "claimable_now": False,
        "claim_guardrail": (
            "Synthetic fixture rows can prove wiring and schema behavior, but "
            "they are not current framework claims."
        ),
    }


def diagnose_tower_evidence_gate(
    candidates: list[dict[str, Any]] | None = None,
) -> dict:
    candidate_rows = [
        _candidate_row(candidate)
        for candidate in (candidates if candidates is not None else _default_candidates())
    ]
    return {
        "basis": ["TowerSpectrum", "TowerEvidence", "framework_verdict"],
        "candidate_count": len(candidate_rows),
        "schema_ready_and_tower_excluding_fixtures": [
            row["label"] for row in candidate_rows
            if row["schema_ready_and_tower_excluding"]
        ],
        "math_excluding_but_evidence_rejected": [
            row["label"] for row in candidate_rows
            if row["tower_claimable_by_math"]
            and not row["evidence_validation"]["ready_for_framework_claim"]
        ],
        "claimable_framework_exclusions_now": [],
        "candidates": candidate_rows,
        "literature_guardrail": {
            "claim": (
                "A tower verdict is not a framework-level quantum-gravity claim "
                "unless both the tower math and the evidence provenance gate pass. "
                "This audit uses synthetic fixtures, so it proves the gate rather "
                "than claiming an exclusion."
            ),
            "primary_sources": [
                {
                    "title": "Corvilain, Grimm, and Valenzuela, The Swampland Distance Conjecture for Kahler moduli",
                    "url": "https://arxiv.org/abs/1812.07548",
                },
            ],
        },
        "interpretation": (
            "v2.31 separates mathematical tower exclusion from evidential claim "
            "readiness. The current repo still has no non-synthetic evidence row "
            "for a registered framework."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.31/tower_evidence_gate.json")
    args = parser.parse_args()

    result = diagnose_tower_evidence_gate()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
