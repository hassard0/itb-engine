"""ParSpec quartic-EFT ringdown source bridge for the R4 route."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_lalsuite_waveform_likelihood_posterior import (
    AXES,
    DEFAULT_OUT as DEFAULT_V2187_PATH,
)


VERSION = "v2.188"
DEFAULT_OUT = Path(
    "experiments/results/v2.188/r4_parspec_ringdown_source_bridge.json"
)
PARSPEC_SOURCE_URL = "https://arxiv.org/abs/2205.05132"
PARSPEC_DOI = "https://doi.org/10.1103/PhysRevD.107.044030"
PARSPEC_ARXIV_DOI = "https://doi.org/10.48550/arXiv.2205.05132"
PARSPEC_QEFT_BOUND_KM_90 = 51.3
PARSPEC_CEFT_BOUND_KM_90 = 38.2
PARSPEC_DCS_BOUND_KM_90 = 38.7
SOURCE_EVENTS = ("GW150914", "GW200129")
CURRENT_V2187_EVENT = "GW170608"
BRIDGE_REQUIRED_FIELDS = (
    "source_url",
    "source_doi",
    "theory_family",
    "source_ringdown_model_available",
    "quartic_eft_bound_available",
    "events",
    "engine_axes",
    "axis_map_to_engine_r4",
    "source_likelihood_or_posterior",
    "systematics",
    "claim_controls",
)
REMAINING_BRIDGE_BLOCKERS = (
    "engine_r4_axes_to_parspec_qeft_length_map_missing",
    "public_parspec_qeft_likelihood_or_posterior_samples_missing",
    "event_set_mismatch_gw170608_vs_gw150914_gw200129",
    "full_source_owned_r4_imr_sampler_not_integrated",
    "calibration_and_waveform_systematics_not_exported",
    "external_adversarial_review_missing",
)


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parspec_quartic_eft_source() -> dict[str, Any]:
    return {
        "source_url": PARSPEC_SOURCE_URL,
        "source_doi": PARSPEC_DOI,
        "arxiv_doi": PARSPEC_ARXIV_DOI,
        "title": "Black-hole ringdown as a probe of higher-curvature gravity theories",
        "authors": ["Hector O. Silva", "Abhirup Ghosh", "Alessandra Buonanno"],
        "journal_reference": "Phys. Rev. D 107, 044030 (2023)",
        "theory_family": "quartic_order_effective_field_theory_of_general_relativity",
        "method_summary": (
            "Effective-one-body IMR waveform augmented with a parametrized "
            "ringdown expansion in final black-hole spin, with theory-by-theory "
            "quasinormal-mode frequency inputs."
        ),
        "source_ringdown_model_available": True,
        "source_owned_full_imr_sampler_export_available": False,
        "public_code_or_samples_found": False,
        "quartic_eft_bound_available": True,
        "bounds_90_credible_km": {
            "quartic_eft_length_scale": PARSPEC_QEFT_BOUND_KM_90,
            "cubic_eft_length_scale": PARSPEC_CEFT_BOUND_KM_90,
            "dynamical_chern_simons_length_scale": PARSPEC_DCS_BOUND_KM_90,
        },
        "events": list(SOURCE_EVENTS),
        "source_claim_scope": (
            "Ringdown constraints on higher-curvature length scales for selected "
            "loud events; not an engine-normalized Bresciani R4-axis posterior."
        ),
    }


def current_v2187_summary(path: str | Path = DEFAULT_V2187_PATH) -> dict[str, Any]:
    result = load_json(path)
    posterior = result["network_likelihood"]["posterior"]
    return canonicalize_json_floats({
        "path": Path(path).as_posix(),
        "version": result["version"],
        "route_status": result["route_status"],
        "ready": result["evaluation"]["r4_waveform_likelihood_posterior_ready"],
        "event": CURRENT_V2187_EVENT,
        "engine_axes": list(AXES),
        "posterior_mean": posterior["posterior_mean"],
        "posterior_covariance": posterior["posterior_covariance"],
        "claim_blockers": result["evaluation"]["claim_blockers"],
    })


def parspec_r4_bridge_packet(
    *,
    v2187_path: str | Path = DEFAULT_V2187_PATH,
) -> dict[str, Any]:
    source = parspec_quartic_eft_source()
    frontier = current_v2187_summary(v2187_path)
    return canonicalize_json_floats({
        "packet_id": "parspec_quartic_eft_ringdown_to_engine_r4_bridge_v1",
        "source_url": source["source_url"],
        "source_doi": source["source_doi"],
        "arxiv_doi": source["arxiv_doi"],
        "theory_family": source["theory_family"],
        "source_ringdown_model_available": source[
            "source_ringdown_model_available"
        ],
        "quartic_eft_bound_available": source["quartic_eft_bound_available"],
        "events": source["events"],
        "engine_axes": list(AXES),
        "v2_187_frontier": frontier,
        "source_evidence": source,
        "axis_map_to_engine_r4": {
            "status": "missing",
            "needed": (
                "Map the ParSpec quartic-EFT length-scale posterior or likelihood "
                "onto engine-normalized Bresciani axes g_R4_c1, g_R4_c2, g_R4_c3."
            ),
            "engine_axes": list(AXES),
            "source_axis": "ell_qEFT_km",
        },
        "source_likelihood_or_posterior": {
            "status": "missing_public_export",
            "available_in_source": "published_bound_only",
            "needed": (
                "Public likelihood samples, log-likelihood grid, or covariance "
                "for the quartic-EFT ringdown parameter, with event metadata."
            ),
        },
        "systematics": {
            "status": "source_mentions_eft_and_waveform_systematics_but_no_engine_export",
            "needed": [
                "waveform_systematics_budget",
                "calibration_prior",
                "event_selection_policy",
                "glitch_and_data_quality_policy",
                "eft_validity_domain",
            ],
        },
        "event_bridge": {
            "source_events": source["events"],
            "current_engine_event": CURRENT_V2187_EVENT,
            "same_event_set": CURRENT_V2187_EVENT in source["events"],
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "source_bridge_only_not_claim_evidence": True,
        },
    })


def evaluate_parspec_r4_bridge(packet: dict[str, Any]) -> dict[str, Any]:
    missing = [
        field for field in BRIDGE_REQUIRED_FIELDS
        if packet.get(field) in (None, "", {}, [], ())
    ]
    blockers: set[str] = set()
    if missing:
        blockers.add("bridge_required_fields_missing")
    if packet.get("source_url") != PARSPEC_SOURCE_URL:
        blockers.add("parspec_primary_source_url_missing")
    if packet.get("source_doi") != PARSPEC_DOI:
        blockers.add("parspec_published_doi_missing")
    if packet.get("theory_family") != (
        "quartic_order_effective_field_theory_of_general_relativity"
    ):
        blockers.add("source_theory_family_not_quartic_eft")
    if packet.get("source_ringdown_model_available") is not True:
        blockers.add("source_ringdown_model_not_available")
    if packet.get("quartic_eft_bound_available") is not True:
        blockers.add("quartic_eft_bound_not_available")
    if set(packet.get("engine_axes", [])) != set(AXES):
        blockers.add("engine_r4_axes_mismatch")

    axis_map = packet.get("axis_map_to_engine_r4", {})
    if axis_map.get("status") != "ready":
        blockers.add("engine_r4_axes_to_parspec_qeft_length_map_missing")
    likelihood = packet.get("source_likelihood_or_posterior", {})
    if likelihood.get("status") not in {
        "public_likelihood_samples",
        "public_log_likelihood_grid",
        "public_covariance_matrix",
    }:
        blockers.add("public_parspec_qeft_likelihood_or_posterior_samples_missing")
    event_bridge = packet.get("event_bridge", {})
    if event_bridge.get("same_event_set") is not True:
        blockers.add("event_set_mismatch_gw170608_vs_gw150914_gw200129")
    systematics = packet.get("systematics", {})
    if systematics.get("status") != "engine_export_ready":
        blockers.add("calibration_and_waveform_systematics_not_exported")

    controls = packet.get("claim_controls", {})
    if controls.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")
    if controls.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")

    source_bridge_ready = not (
        {
            "bridge_required_fields_missing",
            "parspec_primary_source_url_missing",
            "parspec_published_doi_missing",
            "source_theory_family_not_quartic_eft",
            "source_ringdown_model_not_available",
            "quartic_eft_bound_not_available",
            "engine_r4_axes_mismatch",
        }
        & blockers
    )
    sampler_ready = not blockers
    claim_blockers = set(REMAINING_BRIDGE_BLOCKERS)
    if not sampler_ready:
        claim_blockers.add("parspec_bridge_not_claim_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "source_bridge_ready": source_bridge_ready,
        "source_owned_full_imr_sampler_ready": sampler_ready,
        "ready_for_framework_claim": False,
        "bridge_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "parspec_bound_imported": {
            "quartic_eft_length_scale_90_credible_km": (
                PARSPEC_QEFT_BOUND_KM_90
            ),
            "events": list(SOURCE_EVENTS),
        },
        "split_v2_187_blocker": {
            "previous": "full_r4_modified_imr_merger_ringdown_completion_missing",
            "now_resolved_subpiece": (
                "primary_parspec_quartic_eft_ringdown_source_identified"
            ),
            "remaining_subpieces": [
                "engine_r4_axes_to_parspec_qeft_length_map_missing",
                "public_parspec_qeft_likelihood_or_posterior_samples_missing",
                "event_set_mismatch_gw170608_vs_gw150914_gw200129",
                "full_source_owned_r4_imr_sampler_not_integrated",
            ],
        },
        "route_status": (
            "parspec_r4_ringdown_source_bridge_ready_nonclaiming"
            if source_bridge_ready
            else "parspec_r4_ringdown_source_bridge_blocked"
        ),
    })


def malformed_parspec_r4_bridge_packet() -> dict[str, Any]:
    packet = parspec_r4_bridge_packet()
    packet["source_url"] = "https://example.invalid/not-a-source"
    packet["quartic_eft_bound_available"] = False
    packet["engine_axes"] = ["g_R4_c1"]
    packet["claim_controls"]["claim_use_allowed"] = True
    return packet


def diagnose_r4_parspec_ringdown_source_bridge(
    *,
    v2187_path: str | Path = DEFAULT_V2187_PATH,
) -> dict[str, Any]:
    packet = parspec_r4_bridge_packet(v2187_path=v2187_path)
    evaluation = evaluate_parspec_r4_bridge(packet)
    malformed = evaluate_parspec_r4_bridge(malformed_parspec_r4_bridge_packet())
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.187_r4_lalsuite_waveform_likelihood_posterior",
            "Silva_Ghosh_Buonanno_2023_ParSpec_higher_curvature_ringdown",
            "PhysRevD_107_044030",
        ],
        "bridge_packet": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "source_bridge_ready": evaluation["source_bridge_ready"],
        "source_owned_full_imr_sampler_ready": evaluation[
            "source_owned_full_imr_sampler_ready"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "map_parspec_qeft_length_likelihood_to_engine_r4_axes_or_find_public_samples"
        ),
        "best_next_artifact": (
            "A ParSpec/qEFT source packet with public posterior samples or a "
            "likelihood grid, plus a source-backed map from ell_qEFT to the "
            "engine R4 axes g_R4_c1, g_R4_c2, and g_R4_c3."
        ),
        "interpretation": (
            "The v2.187 source-owned IMR blocker has been split. A primary "
            "ParSpec higher-curvature ringdown source exists for quartic EFT "
            "and provides a published length-scale bound, but it is not yet an "
            "engine-normalized R4 posterior or sampler. This is a concrete "
            "source bridge, not claim evidence."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2187", default=str(DEFAULT_V2187_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_ringdown_source_bridge(
        v2187_path=Path(args.v2187)
    )
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
