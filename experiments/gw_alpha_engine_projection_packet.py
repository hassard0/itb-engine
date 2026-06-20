"""Add an explicit cubic-alpha engine projection to the v2.116 packet."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_cubic_source_native_adapter import (
    SOURCE_PARAMETERS,
    evaluate_gw_cubic_source_native_packet,
)
from experiments.gw_marginal_alpha_packet_export import (
    DEFAULT_MARGINAL_RESULT_PATH,
    marginal_alpha_source_native_packet,
)


VERSION = "v2.117"
DEFAULT_PACKET_EXPORT_PATH = Path(
    "experiments/results/v2.116/gw_marginal_alpha_packet_export.json"
)


def load_v2_116_packet(path: Path = DEFAULT_PACKET_EXPORT_PATH) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    return result["packet"]


def alpha_identity_engine_projection_strategy() -> dict[str, Any]:
    return {
        "status": "explicit_engine_projection",
        "target_axis": "gw_cubic_alpha",
        "source_parameters": list(SOURCE_PARAMETERS),
        "engine_parameters": list(SOURCE_PARAMETERS),
        "source_to_engine_jacobian": [[1.0, 0.0], [0.0, 1.0]],
        "normalization": "identity_in_paper_native_dimensionless_alpha_bar_basis",
        "projection_scope": (
            "source_native_cubic_alpha_axis_not_quadratic_curvature_or_g8"
        ),
    }


def packet_with_explicit_alpha_engine_projection(
    packet: dict[str, Any],
) -> dict[str, Any]:
    projected = deepcopy(packet)
    projected["label"] = "v2_117_projected_lalsuite_marginal_alpha_packet"
    projected["engine_axis_strategy"] = alpha_identity_engine_projection_strategy()
    projected["framework_projection_strategy"] = "framework_alpha_response_defined"
    projected["validation_reference"] = (
        "v2.117_alpha_identity_engine_projection_packet"
    )
    projected["projection_caveat"] = (
        "This is an identity projection from the source-native alpha_bar basis "
        "to an engine gw_cubic_alpha axis. It is not a projection to g8, g_C, "
        "or quadratic curvature axes."
    )
    return projected


def build_projected_packet_from_marginal_result(
    marginal_result_path: Path = DEFAULT_MARGINAL_RESULT_PATH,
) -> dict[str, Any]:
    result = json.loads(marginal_result_path.read_text(encoding="utf-8"))
    packet = marginal_alpha_source_native_packet(result)
    return packet_with_explicit_alpha_engine_projection(packet)


def evaluate_alpha_engine_projection_packet(
    packet: dict[str, Any],
) -> dict[str, Any]:
    adapter = evaluate_gw_cubic_source_native_packet(packet)
    projection = adapter["engine_projection_summary"]
    claim_blockers = set(adapter["claim_blockers"])
    removed = []
    if projection["engine_projection_ready"]:
        removed.append("engine_projection_not_ready")
        claim_blockers.discard("engine_projection_not_ready")
    return {
        "alpha_engine_projection_ready": projection["engine_projection_ready"],
        "target_axis": projection["target_axis"],
        "adapter_evaluation": adapter,
        "claim_ready": False,
        "removed_v2_116_blockers": removed,
        "remaining_claim_blockers_without_removed_projection": sorted(
            claim_blockers
        ),
        "remaining_nonclaiming_reasons": sorted(
            {
                "systematics_budget_missing_or_open",
                "g8_joint_component_missing",
                "likelihood_scale_not_calibrated_to_noise_evidence",
                "gw_cubic_alpha_axis_not_framework_discriminator_by_itself",
            }
        ),
    }


def diagnose_gw_alpha_engine_projection_packet(
    packet_export_path: Path = DEFAULT_PACKET_EXPORT_PATH,
) -> dict[str, Any]:
    packet = packet_with_explicit_alpha_engine_projection(
        load_v2_116_packet(packet_export_path)
    )
    evaluation = evaluate_alpha_engine_projection_packet(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.116_marginal_alpha_source_native_packet",
            "v2.102_source_native_alpha_adapter",
        ],
        "packet_export_path": str(packet_export_path),
        "packet": packet,
        "evaluation": evaluation,
        "claimable_discriminator_now": False,
        "route_status": (
            "alpha_engine_projection_packet_ready_nonclaiming"
            if evaluation["alpha_engine_projection_ready"]
            else "alpha_engine_projection_packet_not_ready"
        ),
        "selected_next_build_action": (
            "close_alpha_packet_systematics_budget"
        ),
        "best_next_artifact": (
            "Close or explicitly bound waveform, calibration, prior, EFT "
            "truncation, sampler convergence, and likelihood-scale systematics "
            "for the v2.117 alpha packet."
        ),
        "interpretation": (
            "The source-native alpha packet now has an explicit identity "
            "projection into an engine gw_cubic_alpha axis. The adapter no "
            "longer rejects it for missing engine projection, but the packet "
            "remains nonclaiming because systematics are open and no g8 joint "
            "component exists."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--packet-export",
        default=str(DEFAULT_PACKET_EXPORT_PATH),
    )
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.117/"
            "gw_alpha_engine_projection_packet.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_alpha_engine_projection_packet(Path(args.packet_export))
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
