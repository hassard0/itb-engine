"""Direct spin-4/detector g_8 measurement feasibility audit (v2.89)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


def _capability_row(
    *,
    capability: str,
    available_in_repo: bool,
    can_create_external_measurement: bool,
    role: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "capability": capability,
        "available_in_repo": available_in_repo,
        "can_create_external_measurement": can_create_external_measurement,
        "role": role,
        "blockers": sorted(set(blockers)),
    }


def _requirement_row(
    *,
    requirement: str,
    satisfied_now: bool,
    satisfiable_by_repo_only: bool,
    needed_artifact: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "requirement": requirement,
        "satisfied_now": satisfied_now,
        "satisfiable_by_repo_only": satisfiable_by_repo_only,
        "needed_artifact": needed_artifact,
        "blockers": sorted(set(blockers)),
    }


def repo_capability_rows() -> list[dict[str, Any]]:
    return [
        _capability_row(
            capability="measurement_contract_and_acceptance_gate",
            available_in_repo=True,
            can_create_external_measurement=False,
            role="Defines packet schema and rejects incomplete packets.",
            blockers=["schema_not_measurement"],
        ),
        _capability_row(
            capability="mock_or_synthetic_fixture_generation",
            available_in_repo=True,
            can_create_external_measurement=False,
            role="Tests plumbing and positive/negative guard branches.",
            blockers=["synthetic_fixture_not_real_source"],
        ),
        _capability_row(
            capability="public_source_and_data_product_audit",
            available_in_repo=True,
            can_create_external_measurement=False,
            role="Finds and classifies public sources and datasets.",
            blockers=["source_audit_cannot_generate_new_data"],
        ),
        _capability_row(
            capability="external_spin4_detector_experiment",
            available_in_repo=False,
            can_create_external_measurement=True,
            role="Would produce the missing external numerical g_8 packet.",
            blockers=["external_experimental_program_required"],
        ),
        _capability_row(
            capability="public_likelihood_and_systematics_release",
            available_in_repo=False,
            can_create_external_measurement=True,
            role="Would release covariance, likelihood, and systematics budget.",
            blockers=["external_public_release_required"],
        ),
    ]


def measurement_requirement_rows() -> list[dict[str, Any]]:
    return [
        _requirement_row(
            requirement="external_numeric_spin4_or_detector_observable",
            satisfied_now=False,
            satisfiable_by_repo_only=False,
            needed_artifact=(
                "Published numerical spin-4 partial-wave, detector-moment, or "
                "source-projected high-moment observable."
            ),
            blockers=["external_measurement_missing"],
        ),
        _requirement_row(
            requirement="public_g8_likelihood_or_covariance",
            satisfied_now=False,
            satisfiable_by_repo_only=False,
            needed_artifact="Public likelihood/covariance containing engine g_8.",
            blockers=["public_likelihood_release_missing"],
        ),
        _requirement_row(
            requirement="component_level_systematics_budget",
            satisfied_now=False,
            satisfiable_by_repo_only=False,
            needed_artifact=(
                "Angular acceptance, calibration, backgrounds, EFT truncation, "
                "and running/renormalization systematics."
            ),
            blockers=["external_systematics_budget_missing"],
        ),
        _requirement_row(
            requirement="bounded_low_energy_qg_eft_domain",
            satisfied_now=False,
            satisfiable_by_repo_only=False,
            needed_artifact="Published validity domain for the measured observable.",
            blockers=["external_eft_domain_missing"],
        ),
        _requirement_row(
            requirement="registered_framework_exclusion_math",
            satisfied_now=False,
            satisfiable_by_repo_only=True,
            needed_artifact=(
                "Engine exclusion calculation after the external packet exists."
            ),
            blockers=["blocked_until_external_packet_exists"],
        ),
    ]


def diagnose_g8_direct_measurement_feasibility_audit() -> dict[str, Any]:
    capabilities = repo_capability_rows()
    requirements = measurement_requirement_rows()
    repo_can_create_packet = any(
        row["available_in_repo"] and row["can_create_external_measurement"]
        for row in capabilities
    )
    unsatisfied = [row for row in requirements if not row["satisfied_now"]]
    external_required = [
        row["requirement"] for row in requirements
        if not row["satisfiable_by_repo_only"]
    ]
    blocker_counts: dict[str, int] = {}
    for group in (capabilities, requirements):
        for row in group:
            for blocker in row["blockers"]:
                blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.89",
        "basis": [
            "v2.88_post_g8_derivation_route_decision_frontier",
            "v2.79_g8_adapter_acceptance_harness",
            "v2.54_g8_high_moment_measurement_specification",
        ],
        "route": "new_spin4_or_detector_g8_measurement",
        "repo_can_create_external_measurement_packet": repo_can_create_packet,
        "unsatisfied_requirement_count": len(unsatisfied),
        "external_required_requirements": external_required,
        "claim_ready_routes": [],
        "claimable_discriminator_now": False,
        "capabilities": capabilities,
        "requirements": requirements,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "route_status": "direct_g8_measurement_requires_external_experiment",
        "best_next_artifact": (
            "Either obtain an external published spin-4/detector g_8 packet, or "
            "retire this route for the current in-repo run and reprioritize."
        ),
        "interpretation": (
            "The repo can define, validate, and consume a g_8 measurement packet, "
            "but cannot create the external measurement, public likelihood, or "
            "component systematics required for one. This is an external-state "
            "blocker, not an implementation gap in the adapter harness."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.89/"
            "g8_direct_measurement_feasibility_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_direct_measurement_feasibility_audit()
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
