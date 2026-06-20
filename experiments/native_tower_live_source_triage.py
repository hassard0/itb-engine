"""Live-source triage for native tower adapters (v2.163)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.native_tower_ownership_frontier import (
    diagnose_native_tower_ownership_frontier,
)
from itb.predict import FRAMEWORKS


VERSION = "v2.163"
REGISTERED_FRAMEWORKS = set(FRAMEWORKS)


def _candidate(
    *,
    label: str,
    title: str,
    source_url: str,
    target_framework: str,
    registered_target_match: bool,
    source_class: str,
    observation: str,
    native_tower_spectrum_present: bool,
    native_tower_evidence_present: bool,
    framework_owned_endpoint: bool,
    framework_owned_displacement: bool,
    asymptotic_range: bool,
    adapter_normalization_present: bool,
    two_sigma_tower_exclusion_present: bool,
    source_specific_blockers: list[str],
) -> dict[str, Any]:
    blockers = set(source_specific_blockers)
    if target_framework not in REGISTERED_FRAMEWORKS:
        blockers.add("target_framework_not_registered")
    if not registered_target_match:
        blockers.add("source_does_not_target_registered_framework_adapter")
    if not native_tower_spectrum_present:
        blockers.add("missing_native_tower_spectrum")
    if not native_tower_evidence_present:
        blockers.add("missing_native_tower_evidence")
    if not framework_owned_endpoint:
        blockers.add("missing_framework_owned_endpoint")
    if not framework_owned_displacement:
        blockers.add("missing_framework_owned_displacement")
    if not asymptotic_range:
        blockers.add("missing_asymptotic_range_scope")
    if not adapter_normalization_present:
        blockers.add("adapter_normalization_missing")
    if not two_sigma_tower_exclusion_present:
        blockers.add("two_sigma_tower_exclusion_missing")

    return {
        "label": label,
        "title": title,
        "source_url": source_url,
        "target_framework": target_framework,
        "target_framework_registered": target_framework in REGISTERED_FRAMEWORKS,
        "registered_target_match": registered_target_match,
        "source_class": source_class,
        "observation": observation,
        "native_tower_spectrum_present": native_tower_spectrum_present,
        "native_tower_evidence_present": native_tower_evidence_present,
        "framework_owned_endpoint": framework_owned_endpoint,
        "framework_owned_displacement": framework_owned_displacement,
        "asymptotic_range": asymptotic_range,
        "adapter_normalization_present": adapter_normalization_present,
        "two_sigma_tower_exclusion_present": two_sigma_tower_exclusion_present,
        "native_adapter_triage_ready": not blockers,
        "claim_ready": False,
        "blockers": sorted(blockers),
    }


def live_native_tower_source_candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            label="asymptotic_safety_swampland_2025",
            title="Asymptotic safety, quantum gravity, and the swampland",
            source_url="https://arxiv.org/abs/2502.12290",
            target_framework="asymptotic_safety",
            registered_target_match=True,
            source_class="conceptual_swampland_assessment",
            observation=(
                "Reviews swampland ideas for asymptotic safety, but does not "
                "publish an asymptotic TowerSpectrum/TowerEvidence adapter."
            ),
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=False,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "conceptual_assessment_not_adapter",
            ],
        ),
        _candidate(
            label="absolute_swampland_review_2024",
            title="The Absolute Swampland",
            source_url="https://arxiv.org/abs/2405.20386",
            target_framework="asymptotic_safety",
            registered_target_match=True,
            source_class="review_and_research_directions",
            observation=(
                "Reviews string and asymptotic-safety swampland criteria; it is "
                "not a source-owned native tower adapter."
            ),
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=False,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "review_not_native_tower_source",
            ],
        ),
        _candidate(
            label="dark_dimension_swampland_2022",
            title="The Dark Dimension and the Swampland",
            source_url="https://arxiv.org/abs/2205.12293",
            target_framework="string_tree_eft",
            registered_target_match=False,
            source_class="dark_dimension_tower_scenario",
            observation=(
                "Discusses distance-conjecture towers and species scale, but "
                "does not expose a registered string_tree_eft adapter with "
                "owned endpoint and displacement metadata."
            ),
            native_tower_spectrum_present=True,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=True,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "scenario_tower_not_registered_framework_adapter",
            ],
        ),
        _candidate(
            label="horava_witten_dark_dimension_2026",
            title=(
                "Towards the Realization of the Dark Dimension Scenario in "
                "Horava-Witten Theory"
            ),
            source_url="https://arxiv.org/abs/2605.11068",
            target_framework="horava_lifshitz",
            registered_target_match=False,
            source_class="horava_witten_string_candidate",
            observation=(
                "Horava-Witten theory is a string/M-theory setup, not the "
                "registered Horava-Lifshitz framework; the paper is also "
                "speculative about the strong-coupling M-theory regime."
            ),
            native_tower_spectrum_present=True,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=True,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "horava_witten_not_horava_lifshitz",
                "strong_coupling_regime_speculative",
            ],
        ),
        _candidate(
            label="emergence_swampland_2018",
            title="Emergence and the Swampland Conjectures",
            source_url="https://arxiv.org/abs/1802.08698",
            target_framework="string_tree_eft",
            registered_target_match=False,
            source_class="general_sdc_derivation",
            observation=(
                "Derives an exponential tower condition from emergence "
                "assumptions, but does not provide a named registered-framework "
                "TowerSpectrum/TowerEvidence pair."
            ),
            native_tower_spectrum_present=True,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=True,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "universal_argument_not_framework_owned_adapter",
            ],
        ),
        _candidate(
            label="finite_complexity_landscape_2026",
            title=(
                "Tame Complexity of Effective Field Theories in the Quantum "
                "Gravity Landscape"
            ),
            source_url="https://arxiv.org/abs/2601.18863",
            target_framework="emergent_gravity",
            registered_target_match=False,
            source_class="landscape_complexity_constraint",
            observation=(
                "Constrains EFT description complexity, not a native tower "
                "spectrum for an engine registered framework."
            ),
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=False,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "complexity_constraint_not_tower_spectrum",
            ],
        ),
        _candidate(
            label="holographic_swampland_constraints_2025",
            title=(
                "Holography and the Swampland: Constraints on Quantum Gravity "
                "from Holographic Principles"
            ),
            source_url="https://arxiv.org/abs/2512.14389",
            target_framework="emergent_gravity",
            registered_target_match=False,
            source_class="holographic_swampland_constraints",
            observation=(
                "Maps holographic consistency ideas to swampland constraints, "
                "but does not publish a native tower adapter row."
            ),
            native_tower_spectrum_present=False,
            native_tower_evidence_present=False,
            framework_owned_endpoint=False,
            framework_owned_displacement=False,
            asymptotic_range=False,
            adapter_normalization_present=False,
            two_sigma_tower_exclusion_present=False,
            source_specific_blockers=[
                "holographic_constraint_not_native_tower_adapter",
            ],
        ),
    ]


def diagnose_native_tower_live_source_triage() -> dict[str, Any]:
    ownership = diagnose_native_tower_ownership_frontier()
    rows = live_native_tower_source_candidates()
    ready = [row["label"] for row in rows if row["native_adapter_triage_ready"]]
    framework_counts: dict[str, int] = {}
    blocker_counts: dict[str, int] = {}
    source_class_counts: dict[str, int] = {}
    for row in rows:
        framework = row["target_framework"]
        framework_counts[framework] = framework_counts.get(framework, 0) + 1
        source_class = row["source_class"]
        source_class_counts[source_class] = source_class_counts.get(source_class, 0) + 1
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": VERSION,
        "basis": [
            "v2.83_native_tower_current_source_audit",
            "v2.84_native_tower_route_decision",
            "live_primary_source_recheck_2026_06_20",
        ],
        "route": "framework_specific_native_tower_search",
        "query_scope": (
            "registered-framework native tower source triage after R4/g8 "
            "frontier routes remained external-packet blocked"
        ),
        "pass_condition": ownership["pass_condition"],
        "critical_phi_tower": ownership["critical_phi_tower"],
        "candidate_count": len(rows),
        "native_adapter_triage_ready_candidates": ready,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "target_framework_counts": dict(sorted(framework_counts.items())),
        "source_class_counts": dict(sorted(source_class_counts.items())),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "live_native_tower_sources_no_registered_adapter",
        "selected_next_build_action": (
            "derive_minimum_native_tower_adapter_requirements_per_registered_framework"
        ),
        "best_next_artifact": (
            "A per-framework adapter requirement sheet that names the endpoint, "
            "displacement, spectrum, evidence, normalization, and exclusion math "
            "each registered framework would need before native tower promotion."
        ),
        "interpretation": (
            "The live recheck found active primary-source material, but none "
            "supplies a registered-framework-owned native TowerSpectrum and "
            "TowerEvidence pair. The route remains scientifically relevant, yet "
            "all current rows are blocked by missing ownership, evidence, "
            "normalization, or target-framework match."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.163/"
            "native_tower_live_source_triage.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_native_tower_live_source_triage()
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
