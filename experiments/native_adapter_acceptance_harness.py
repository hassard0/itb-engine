"""Native adapter acceptance harness (v2.47).

v2.46 showed that live frameworks lack native tower adapters. This harness
temporarily installs synthetic adapters into the live frontier path to prove
which future native row would become claim-ready and which would remain blocked.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.discriminator_frontier import diagnose_discriminator_frontier
from experiments.explicit_tower_basis import _json_default
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.predict import FRAMEWORKS
from itb.tower import TowerEvidence, TowerSpectrum


def _synthetic_spectrum(*, owned_scope: bool) -> TowerSpectrum:
    metadata = {
        "range_scope": "asymptotic",
        "source_family": "synthetic_native_adapter_acceptance_fixture",
    }
    if owned_scope:
        metadata.update({
            "native_framework_endpoint": "synthetic endpoint owned by string_tree_eft",
            "native_framework_displacement": (
                "synthetic displacement owned by string_tree_eft"
            ),
        })
    return TowerSpectrum(
        tower_family="synthetic_native_string_tree_kk",
        phi_tower_mean=1.0,
        phi_tower_sigma=0.02,
        tower_mass_gap=math.exp(-1.0),
        normalization="synthetic v2.47 native adapter acceptance normalization",
        source="synthetic acceptance harness row, not a physics source",
        metadata=metadata,
    )


def _synthetic_evidence(*, owned_scope: bool) -> TowerEvidence:
    metadata = {
        "range_scope": "asymptotic",
        "source_family": "synthetic_native_adapter_acceptance_fixture",
        "fixture": True,
    }
    if owned_scope:
        metadata.update({
            "native_framework_endpoint": "synthetic endpoint owned by string_tree_eft",
            "native_framework_displacement": (
                "synthetic displacement owned by string_tree_eft"
            ),
        })
    return TowerEvidence(
        framework="string_tree_eft",
        spectrum=_synthetic_spectrum(owned_scope=owned_scope),
        adapter_kind="synthetic_native_acceptance_fixture",
        source_url="https://arxiv.org/abs/1812.07548",
        source_type="primary_literature",
        derivation_kind="synthetic_acceptance_fixture",
        uncertainty_kind="exact_fixture_sigma_zero",
        normalization_reference="synthetic fixture normalization",
        metadata=metadata,
    )


class _SyntheticStringTreeTowerAdapter(StringTreeEFT):
    def __init__(self, *, owned_scope: bool) -> None:
        self._owned_scope = owned_scope

    def tower_spectrum(self) -> TowerSpectrum:
        return _synthetic_spectrum(owned_scope=self._owned_scope)

    def tower_evidence(self) -> TowerEvidence:
        return _synthetic_evidence(owned_scope=self._owned_scope)


def _with_synthetic_string_tree_adapter(*, owned_scope: bool) -> dict[str, Any]:
    original = FRAMEWORKS["string_tree_eft"]
    FRAMEWORKS["string_tree_eft"] = _SyntheticStringTreeTowerAdapter(
        owned_scope=owned_scope,
    )
    try:
        result = diagnose_discriminator_frontier()
    finally:
        FRAMEWORKS["string_tree_eft"] = original
    return result


def _case(label: str, *, owned_scope: bool) -> dict[str, Any]:
    frontier = _with_synthetic_string_tree_adapter(owned_scope=owned_scope)
    row = frontier["frameworks"]["string_tree_eft"]
    guard = row["tower_generic_claim_guard"]
    return {
        "label": label,
        "owned_scope": owned_scope,
        "frontier_status": row["frontier_status"],
        "tower_claimable_by_math": row["tower_claimable_by_math"],
        "promotion_guard_ready": row["tower_promotion_guard"]["ready_for_promotion"],
        "generic_claim_guard_ready": guard["ready_for_generic_framework_claim"],
        "generic_claim_guard_blockers": guard["blockers"],
        "source_scope": guard["source_scope"],
        "tower_discriminator_claim_ready": frontier["tower_discriminator_claim_ready"],
        "claimable_now": False,
    }


def diagnose_native_adapter_acceptance_harness() -> dict[str, Any]:
    cases = [
        _case("owned_scope_acceptance_fixture", owned_scope=True),
        _case("missing_ownership_fixture", owned_scope=False),
    ]
    live_after_restore = diagnose_discriminator_frontier()["frameworks"]["string_tree_eft"]
    return {
        "basis": [
            "synthetic_native_adapter",
            "discriminator_frontier",
            "generic_framework_claim_guard",
        ],
        "cases": cases,
        "claim_ready_synthetic_fixtures": [
            row["label"] for row in cases
            if row["frontier_status"] == "tower_discriminator_claim_ready"
        ],
        "generic_claim_blocked_synthetic_fixtures": [
            row["label"] for row in cases
            if row["frontier_status"] == "tower_generic_claim_guard_blocked"
        ],
        "claimable_framework_exclusions_now": [],
        "registry_restored_after_harness": (
            live_after_restore["native_tower_spectrum_present"] is False
            and live_after_restore["native_tower_evidence_present"] is False
        ),
        "literature_guardrail": {
            "claim": (
                "This is a synthetic acceptance harness. It proves wiring for a "
                "future native adapter but does not provide a framework-level "
                "quantum-gravity exclusion."
            ),
            "primary_sources": [],
        },
        "interpretation": (
            "A future native adapter will only reach discriminator claim readiness "
            "when it is mathematically excluding and carries owned endpoint and "
            "displacement metadata. Missing ownership remains blocked even when "
            "the spectrum is excluding and promotion-ready."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.47/native_adapter_acceptance_harness.json",
    )
    args = parser.parse_args()

    result = diagnose_native_adapter_acceptance_harness()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
