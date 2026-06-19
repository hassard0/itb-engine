"""g_8 direct measurement route decision after feasibility audit (v2.90)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


def _decision_row(
    *,
    route: str,
    status: str,
    retained: bool,
    claim_ready: bool,
    reason: str,
    next_action: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "route": route,
        "status": status,
        "retained": retained,
        "claim_ready": claim_ready,
        "reason": reason,
        "next_action": next_action,
        "blockers": sorted(set(blockers)),
    }


def route_decision_rows() -> list[dict[str, Any]]:
    return [
        _decision_row(
            route="direct_spin4_detector_measurement_in_repo_execution",
            status="retired_for_current_in_repo_run",
            retained=False,
            claim_ready=False,
            reason=(
                "v2.89 shows the repo can validate a g_8 packet but cannot "
                "create the external spin-4/detector measurement, public "
                "likelihood, or systematics release."
            ),
            next_action=(
                "Do not keep attempting to manufacture the measurement in repo; "
                "seek external data or reprioritize."
            ),
            blockers=[
                "external_measurement_missing",
                "public_likelihood_release_missing",
                "external_systematics_budget_missing",
                "external_eft_domain_missing",
            ],
        ),
        _decision_row(
            route="synthetic_g8_measurement_fixture_as_claim",
            status="retired_as_invalid_claim_route",
            retained=False,
            claim_ready=False,
            reason=(
                "Synthetic fixtures prove the adapter accepts a well-shaped row, "
                "but they are not external physics evidence."
            ),
            next_action="Use fixtures only for tests and schema validation.",
            blockers=[
                "synthetic_fixture_not_real_source",
                "external_measurement_missing",
            ],
        ),
        _decision_row(
            route="external_spin4_detector_measurement_request",
            status="retained_external_dependency",
            retained=True,
            claim_ready=False,
            reason=(
                "A real external measurement remains the cleanest g_8 path, but "
                "it is outside the repo's executable capabilities."
            ),
            next_action=(
                "Specify the packet requirements for an outside measurement or "
                "watch for a public release."
            ),
            blockers=[
                "external_experimental_program_required",
                "external_public_release_required",
                "external_systematics_budget_missing",
            ],
        ),
        _decision_row(
            route="future_public_g8_measurement_ingestion",
            status="retained_ingestion_route",
            retained=True,
            claim_ready=False,
            reason=(
                "Once a public packet exists, the repo can ingest and test it "
                "through the v2.79 acceptance harness."
            ),
            next_action=(
                "Implement parser/adapter only after a concrete public data "
                "product exists."
            ),
            blockers=[
                "future_public_g8_packet_missing",
                "blocked_until_external_packet_exists",
            ],
        ),
        _decision_row(
            route="g8_measurement_schema_archive",
            status="retained_as_nonpromoting_design_material",
            retained=True,
            claim_ready=False,
            reason=(
                "The measurement contract and acceptance harness remain useful "
                "for future data even though the current run lacks the packet."
            ),
            next_action="Keep the schema and fixtures; do not claim from them.",
            blockers=[
                "schema_not_measurement",
                "source_archive_not_framework_claim",
            ],
        ),
    ]


def diagnose_g8_direct_measurement_route_decision() -> dict[str, Any]:
    rows = route_decision_rows()
    retired = [row["route"] for row in rows if row["status"].startswith("retired")]
    retained = [row["route"] for row in rows if row["retained"]]
    claim_ready = [row["route"] for row in rows if row["claim_ready"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.90",
        "basis": [
            "v2.89_g8_direct_measurement_feasibility_audit",
            "v2.88_post_g8_derivation_route_decision_frontier",
            "v2.79_g8_adapter_acceptance_harness",
        ],
        "decision_scope": "direct_g8_measurement_current_in_repo_run",
        "route_count": len(rows),
        "retired_routes": retired,
        "retained_nonpromoting_routes": retained,
        "claim_ready_routes": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "direct_g8_measurement_execution_retired_external_dependency",
        "best_next_artifact": (
            "Reprioritize the frontier with direct g_8 measurement marked as an "
            "external dependency, or obtain a real external packet."
        ),
        "interpretation": (
            "The direct g_8 measurement route is not false, but it cannot be "
            "completed inside this run without external experimental data. "
            "Schema, synthetic fixtures, and source audits remain non-promoting."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.90/"
            "g8_direct_measurement_route_decision.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_g8_direct_measurement_route_decision()
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
