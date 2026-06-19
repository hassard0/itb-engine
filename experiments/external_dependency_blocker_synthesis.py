"""External-dependency blocker synthesis for the current frontier (v2.95)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.current_external_packet_probe import (
    diagnose_current_external_packet_probe,
)
from experiments.explicit_tower_basis import _json_default
from experiments.external_evidence_intake_gate import (
    diagnose_external_evidence_intake_gate,
)
from experiments.external_evidence_packet_contract import (
    diagnose_external_evidence_packet_contract,
)
from experiments.post_g8_direct_measurement_frontier import (
    diagnose_post_g8_direct_measurement_frontier,
)


UNBLOCK_CONDITIONS = (
    {
        "route": "future_public_g8_measurement_ingestion",
        "condition": (
            "A real engine-normalized g_8 packet passes the v2.93 intake gate "
            "with public likelihood, closed component systematics, bounded EFT "
            "domain, and framework-exclusion math."
        ),
    },
    {
        "route": "framework_specific_native_tower_search",
        "condition": (
            "A registered framework supplies native tower spectra, ownership "
            "metadata, adapter normalization, uncertainty model, and excluding "
            "tower evidence."
        ),
    },
    {
        "route": "gw_parity_operator_normalization_search",
        "condition": (
            "A source-backed PPV-to-engine parity operator bridge supplies "
            "normalization, sign convention, engine axis target, and framework "
            "projection."
        ),
    },
    {
        "route": "weyl_g8_joint_frontier",
        "condition": (
            "Engine-normalized g_C and g_8 packets become available with a "
            "joint likelihood and shared EFT domain."
        ),
    },
)


def diagnose_external_dependency_blocker_synthesis() -> dict[str, Any]:
    frontier = diagnose_post_g8_direct_measurement_frontier()
    contract = diagnose_external_evidence_packet_contract()
    intake = diagnose_external_evidence_intake_gate()
    source_probe = diagnose_current_external_packet_probe()

    claim_ready_sources = source_probe["claim_ready_candidates"]
    schema_ready_sources = source_probe["schema_ready_candidates"]
    promotion_ready_routes = frontier["current_in_repo_promotion_ready_routes"]
    claim_ready_sample_packets = intake["claim_ready_sample_packets"]

    blocked = (
        not claim_ready_sources
        and not schema_ready_sources
        and not promotion_ready_routes
        and not claim_ready_sample_packets
    )

    return {
        "version": "v2.95",
        "basis": [
            "v2.91_post_g8_direct_measurement_frontier",
            "v2.92_external_evidence_packet_contract",
            "v2.93_external_evidence_intake_gate",
            "v2.94_current_external_packet_probe",
        ],
        "blocker_scope": "defensible_discriminator_claim_current_run",
        "frontier_route_status": frontier["route_status"],
        "contract_route_status": contract["route_status"],
        "intake_route_status": intake["route_status"],
        "source_probe_route_status": source_probe["route_status"],
        "external_dependency_routes": frontier["external_dependency_routes"],
        "contract_route_count": contract["route_count"],
        "current_source_candidate_count": source_probe["candidate_count"],
        "current_schema_ready_candidates": schema_ready_sources,
        "current_claim_ready_candidates": claim_ready_sources,
        "current_in_repo_promotion_ready_routes": promotion_ready_routes,
        "claim_ready_sample_packets": claim_ready_sample_packets,
        "claimable_discriminator_now": False,
        "repeated_blocker": "real_engine_normalized_external_packet_missing",
        "blocked_for_current_run": blocked,
        "unblock_conditions": list(UNBLOCK_CONDITIONS),
        "allowed_nonclaim_work": [
            "monitor_current_sources",
            "ingest_and_validate_real_external_packet",
            "maintain_acceptance_contracts",
        ],
        "disallowed_next_steps": [
            "synthetic_fixture_as_physics_claim",
            "source_incomplete_adapter_promotion",
            "additional_internal_route_ranking_as_claim_substitute",
        ],
        "route_status": "research_frontier_blocked_pending_external_evidence",
        "best_next_artifact": (
            "Obtain or supply a real external packet satisfying one unblock "
            "condition; otherwise only nonclaim maintenance work remains."
        ),
        "interpretation": (
            "The current run cannot honestly promote a defensible quantum-gravity "
            "discriminator. The in-repo frontier is externally gated: contracts "
            "and intake validation are ready, but no current public source "
            "provides a complete packet that passes the gate."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.95/"
            "external_dependency_blocker_synthesis.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_external_dependency_blocker_synthesis()
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
