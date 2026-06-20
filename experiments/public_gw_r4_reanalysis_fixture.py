"""Public-GW R4 reanalysis fixture wired to the Bresciani axis dictionary."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_r4_axis_dictionary import (
    bresciani_r4_axis_dictionary,
    bresciani_r4_axis_mapping_sidecar,
    evaluate_bresciani_r4_axis_dictionary,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.gw_public_strain_connector import (
    gw170608_v3_event_record,
    gw170608_v3_strain_records,
    summarize_strain_records,
)
from experiments.r4_shape_likelihood_ingestion_adapter import (
    evaluate_r4_shape_likelihood_ingestion_packet,
)
from experiments.r4_shape_likelihood_packet_manifest import (
    TARGET_AXES,
    evaluate_r4_shape_likelihood_packet,
)


VERSION = "v2.176"
EVENT = "GW170608"
FIXTURE_PACKET_ID = "gw170608_public_r4_shape_reanalysis_fixture_v1"
R4_LIKELIHOOD_AXES = ("g_R4_c1", "g_R4_c2", "g_R4_c3")
SOURCE_URLS = (
    "https://gwosc.org/api/v2/event-versions/GW170608-v3",
    "https://gwosc.org/eventapi/html/GWTC/",
    "https://arxiv.org/abs/2504.12855",
    "https://arxiv.org/abs/2407.08929",
)
REAL_REANALYSIS_BLOCKERS = (
    "r4_waveform_response_model_is_fixture",
    "public_r4_reanalysis_samples_missing",
    "waveform_systematics_not_closed_for_r4",
    "external_adversarial_review_missing",
)


def gw170608_r4_reanalysis_source_package() -> dict[str, Any]:
    records = gw170608_v3_strain_records()
    return canonicalize_json_floats({
        "event": EVENT,
        "event_record": gw170608_v3_event_record(),
        "strain_summary": summarize_strain_records(records),
        "strain_records": records,
        "source_urls": list(SOURCE_URLS),
        "public_inputs_declared": True,
        "required_reanalysis_steps": [
            "load_h1_l1_32s_public_strain",
            "build_gr_reference_waveform_and_nuisance_grid",
            "inject_linearized_r4_shape_response",
            "sample_or_grid_g_R4_c1_c2_c3",
            "export_v2_160_r4_shape_likelihood_packet",
        ],
        "fixture_boundary": {
            "public_strain_inputs": True,
            "r4_waveform_response_is_synthetic_fixture": True,
            "public_r4_likelihood_release": False,
        },
    })


def linearized_r4_waveform_parameterization() -> dict[str, Any]:
    sidecar = bresciani_r4_axis_mapping_sidecar()
    return canonicalize_json_floats({
        "status": "fixture_parameterization_ready",
        "event": EVENT,
        "source_coordinates": [
            "delta_K_plus",
            "delta_Re_K_minus",
            "delta_Im_K_minus",
        ],
        "engine_axes": list(R4_LIKELIHOOD_AXES),
        "source_to_engine_jacobian_for_overall_R4_factor_8": [
            [0.5, 0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.0, 0.0, 1.0],
        ],
        "axis_mapping_sidecar": sidecar,
        "response_model": {
            "kind": "linearized_post_inspiral_phase_fixture",
            "real_waveform_code_attached": False,
            "lalsuite_r4_waveform_plugin": "missing",
            "purpose": (
                "exercise packet covariance wiring before real R4 waveform "
                "generation exists"
            ),
        },
        "normalization": {
            "scope": "shape_likelihood_only",
            "uses_numeric_lambda_r4_scale": False,
            "dictionary_id": sidecar["dictionary_id"],
        },
    })


def synthetic_public_gw_r4_reanalysis_packet() -> dict[str, Any]:
    source_package = gw170608_r4_reanalysis_source_package()
    axis_dictionary = bresciani_r4_axis_dictionary()
    sidecar = axis_dictionary["packet_builder_exports"]["axis_mapping"]
    return canonicalize_json_floats({
        "packet_id": FIXTURE_PACKET_ID,
        "source_url": source_package["event_record"]["event_version_url"],
        "source_type": "public_gw_reanalysis_fixture",
        "target_axes": list(TARGET_AXES),
        "likelihood": {
            "status": "public_covariance_matrix",
            "central_values": {
                "g_R4_c1": 0.51,
                "g_R4_c2": 0.49,
                "g_R4_c3": 0.02,
            },
            "covariance": [
                [0.25, 0.03, 0.0],
                [0.03, 0.25, 0.0],
                [0.0, 0.0, 0.09],
            ],
            "axes": list(R4_LIKELIHOOD_AXES),
            "generation": "deterministic_fixture_covariance",
        },
        "axis_mapping": sidecar,
        "normalization": {
            "axis_normalization_declared": True,
            "uses_numeric_lambda_r4_scale": False,
            "normalization_scope": "shape_likelihood_only",
            "axis_dictionary_id": axis_dictionary["dictionary_id"],
            "axis_dictionary_version": axis_dictionary["version"],
        },
        "domain": {
            "status": "bounded_for_qg_eft",
            "shared_domain_with_query_row": True,
            "event": EVENT,
            "domain_notes": [
                "dimensionless_r4_shape_axes_only",
                "no_numeric_lambda_r4_scale_claim",
            ],
        },
        "systematics": {
            "status": "declared",
            "items": [
                "fixture_linearized_r4_waveform_response",
                "public_strain_urls_declared_not_redownloaded_by_fixture",
                "calibration_prior_and_sampler_systematics_open",
                "no_external_adversarial_review",
            ],
        },
        "provenance": {
            "reproducible_data_or_code": True,
            "public_likelihood_or_covariance": True,
            "synthetic_control": True,
            "public_data_inputs_declared": True,
            "public_r4_reanalysis_output": False,
            "source_urls": list(SOURCE_URLS),
            "source_package": source_package,
            "waveform_parameterization": linearized_r4_waveform_parameterization(),
        },
        "discriminator_math": "excludes_registered_framework",
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
            "synthetic_control_not_claim_evidence": True,
        },
    })


def evaluate_public_gw_r4_reanalysis_fixture(
    packet: dict[str, Any],
) -> dict[str, Any]:
    manifest = evaluate_r4_shape_likelihood_packet(packet)
    ingestion = evaluate_r4_shape_likelihood_ingestion_packet(packet)
    axis_dictionary = bresciani_r4_axis_dictionary()
    axis_evaluation = evaluate_bresciani_r4_axis_dictionary(axis_dictionary)
    source_package = packet.get("provenance", {}).get("source_package", {})
    strain_summary = source_package.get("strain_summary", {})
    waveform = packet.get("provenance", {}).get("waveform_parameterization", {})

    blockers: set[str] = set()
    if manifest["ready_for_engine_likelihood_packet"] is not True:
        blockers.add("manifest_packet_gate_failed")
    if ingestion["adapter_ingestion_ready"] is not True:
        blockers.add("r4_ingestion_adapter_failed")
    if axis_evaluation["ready_for_r4_shape_packet_axis_mapping"] is not True:
        blockers.add("axis_dictionary_not_ready")
    if strain_summary.get("public_strain_urls_ready") is not True:
        blockers.add("public_strain_urls_not_ready")
    response = waveform.get("response_model", {})
    if not isinstance(response, dict) or response.get("real_waveform_code_attached"):
        blockers.add("fixture_response_boundary_not_preserved")

    synthetic = bool(
        packet.get("provenance", {}).get("synthetic_control")
        or packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence")
    )
    claim_blockers = set(REAL_REANALYSIS_BLOCKERS)
    if synthetic:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if blockers:
        claim_blockers.add("fixture_packet_not_engine_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "manifest_evaluation": manifest,
        "ingestion_evaluation": ingestion,
        "axis_dictionary_evaluation": axis_evaluation,
        "fixture_packet_engine_ready": not blockers,
        "ready_for_shape_likelihood_diagnostic": (
            ingestion["ready_for_shape_likelihood_diagnostic"]
        ),
        "ready_for_real_public_r4_reanalysis": False,
        "ready_for_framework_claim": False,
        "synthetic_control": synthetic,
        "fixture_blockers": sorted(blockers),
        "real_reanalysis_blockers": sorted(REAL_REANALYSIS_BLOCKERS),
        "claim_blockers": sorted(claim_blockers),
        "shape_score": ingestion["shape_score"],
        "route_status": (
            "public_gw_r4_reanalysis_fixture_engine_ready_nonclaiming"
            if not blockers
            else "public_gw_r4_reanalysis_fixture_blocked"
        ),
    })


def malformed_public_gw_r4_reanalysis_packet() -> dict[str, Any]:
    packet = deepcopy(synthetic_public_gw_r4_reanalysis_packet())
    packet["packet_id"] = "malformed_public_gw_r4_reanalysis_fixture"
    packet["axis_mapping"]["mapped_axes"].remove("g_R4_minus_abs")
    packet["likelihood"]["covariance"][1][1] = 0.0
    packet["provenance"]["source_package"]["strain_summary"][
        "public_strain_urls_ready"
    ] = False
    return packet


def diagnose_public_gw_r4_reanalysis_fixture() -> dict[str, Any]:
    fixture = synthetic_public_gw_r4_reanalysis_packet()
    malformed = malformed_public_gw_r4_reanalysis_packet()
    fixture_eval = evaluate_public_gw_r4_reanalysis_fixture(fixture)
    malformed_eval = evaluate_public_gw_r4_reanalysis_fixture(malformed)
    ready_fixtures = [
        row["packet_id"] for row in [fixture_eval, malformed_eval]
        if row["fixture_packet_engine_ready"]
    ]

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.162_r4_shape_likelihood_ingestion_adapter",
            "v2.160_r4_shape_likelihood_packet_manifest",
            "v2.106_gw_public_strain_connector",
            "GWOSC_GW170608_v3_public_strain",
        ],
        "source_package": gw170608_r4_reanalysis_source_package(),
        "waveform_parameterization": linearized_r4_waveform_parameterization(),
        "fixture_packet": fixture,
        "fixture_evaluation": fixture_eval,
        "malformed_control_evaluation": malformed_eval,
        "engine_ready_fixture_packets": ready_fixtures,
        "ready_real_public_r4_reanalysis_packets_now": [],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "public_gw_r4_reanalysis_fixture_ready_nonclaiming",
        "selected_next_build_action": (
            "replace_fixture_response_with_lalsuite_r4_waveform_reanalysis"
        ),
        "best_next_artifact": (
            "A real LALSuite-compatible R4 waveform response that reuses this "
            "packet export path but replaces the synthetic covariance with "
            "public GW170608 posterior samples or a reproducible likelihood grid."
        ),
        "interpretation": (
            "The public-GW R4 route now has an ingestable, manifest-complete "
            "fixture packet wired through the Bresciani axis dictionary and "
            "shape scorer. It proves the software path, not the physics result: "
            "the waveform response and covariance are synthetic controls."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.176/"
            "public_gw_r4_reanalysis_fixture.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_public_gw_r4_reanalysis_fixture()
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
