"""Source-route graph for the missing ParSpec qNM-to-Bresciani bridge."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_r4_axis_dictionary import (
    BRESCIANI_SOURCE_URL,
)
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_public_likelihood_packet import (
    DEFAULT_OUT as DEFAULT_V2206_PATH,
)
from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH,
    PYRING_BRANCH_HEAD_SHA,
    PYRING_TREE_URL,
    PYRING_WAVEFORM_SOURCE_URL,
    ROTATING_QNM_SOURCE_URL,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    PARSPEC_EPRINT_URL,
    PARSPEC_SOURCE_URL,
)
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES, QNM_AXES
from experiments.r4_parspec_qnm_to_bresciani_gate import matrix_rank
from experiments.r4_parspec_ringdown_source_bridge import PARSPEC_DOI, load_json


VERSION = "v2.207"
DEFAULT_OUT = Path(
    "experiments/results/v2.207/r4_parspec_qnm_bresciani_source_route_graph.json"
)
PYRING_EFT_RINGDOWN_ANALYSIS_URL = "https://arxiv.org/abs/2411.17893"
PARSPEC_FOUNDATION_URL = "https://arxiv.org/abs/1910.12893"
PARSPEC_EFT_SCALE_URL = "https://arxiv.org/abs/2102.05939"
CANO_QUARTIC_QNM_URL = "https://arxiv.org/abs/2110.11378"

REQUIRED_SENSITIVITY_EDGES = (
    "source_qnm_deformation_axis_schema",
    "qnm_deformation_to_operator_coordinate_map",
    "operator_coordinate_to_bresciani_K_map",
    "bresciani_K_to_engine_axis_projection",
    "finite_3x4_sensitivity_matrix",
    "field_redefinition_policy",
    "axis_normalization_policy",
)
CLAIM_STAGE_REQUIREMENTS = (
    *REQUIRED_SENSITIVITY_EDGES,
    "public_or_reproducible_likelihood_export",
    "claim_grade_systematics_export",
    "external_adversarial_review",
)


def _source_registry() -> dict[str, dict[str, Any]]:
    return {
        "silva_ghosh_buonanno_2023": {
            "url": PARSPEC_SOURCE_URL,
            "doi": PARSPEC_DOI,
            "source_eprint_url": PARSPEC_EPRINT_URL,
            "role": "ParSpec qEFT ringdown source and published qEFT bounds",
            "provides": [
                "ell_qEFT_km source axis",
                "qEFT power p=6",
                "qEFT gamma-to-qNM deformation ray",
                "GW150914/GW200129 published bounds",
            ],
            "does_not_provide": [
                "three-axis Bresciani R4 operator basis",
                "machine-readable likelihood packet",
            ],
        },
        "maselli_cardoso_et_al_2020_parspec": {
            "url": PARSPEC_FOUNDATION_URL,
            "role": "ParSpec ringdown-parameterization foundation",
            "provides": [
                "frequency and damping-time deformation-axis schema",
                "spin expansion convention for qNM deviations",
            ],
            "does_not_provide": [
                "higher-curvature amplitude coefficient map",
                "Bresciani K coordinate orientation",
            ],
        },
        "parspec_eft_scale_framework_2021": {
            "url": PARSPEC_EFT_SCALE_URL,
            "role": "ParSpec EFT scaling and gamma policy source",
            "provides": [
                "gamma scaling convention for beyond-GR ringdown deformations",
                "EFT mass-scale interpretation",
            ],
            "does_not_provide": [
                "spin-2 R4 amplitude basis normalization",
                "qNM-to-Bresciani sensitivity matrix",
            ],
        },
        "cano_et_al_2021_quartic_qnm_shifts": {
            "url": CANO_QUARTIC_QNM_URL,
            "role": "slow-rotation quartic-EFT QNM shift source",
            "provides": [
                "forward QNM sensitivities to quartic EFT couplings",
                "plus/minus branch and parity-breaking branch structure",
            ],
            "does_not_provide": [
                "Bresciani K_plus/Re(K_minus)/Im(K_minus) normalization",
                "source-backed inverse from qNM axes to amplitude axes",
            ],
        },
        "cano_fransen_hertog_maenaut_2023": {
            "url": ROTATING_QNM_SOURCE_URL,
            "role": "higher-derivative rotating black-hole QNM shifts",
            "provides": [
                "quartic EFT QNM shift calculations",
                "polar/axial plus-minus branch semantics",
                "pyRing table provenance",
            ],
            "does_not_provide": [
                "Bresciani K_plus/Re(K_minus)/Im(K_minus) orientation",
                "field-redefinition policy into the Bresciani amplitude basis",
            ],
        },
        "bresciani_levati_paradisi_2026": {
            "url": BRESCIANI_SOURCE_URL,
            "role": "spin-2 R4 amplitude/unitarity source",
            "provides": [
                "Bresciani K coordinate basis",
                "engine projection axes g_R4_c1/g_R4_c2/g_R4_c3",
            ],
            "does_not_provide": [
                "ringdown qNM deformation sensitivity",
                "pyRing quartic branch identity",
            ],
        },
        "pyring_eft_qnms_branch": {
            "url": PYRING_TREE_URL,
            "waveform_url": PYRING_WAVEFORM_SOURCE_URL,
            "branch": PYRING_BRANCH,
            "branch_head_sha": PYRING_BRANCH_HEAD_SHA,
            "role": "public implementation of EFT QNM coefficient tables",
            "provides": [
                "hash-pinned quartic_1/2/3 plus/minus QNM branch tables",
                "runtime table-loading convention",
            ],
            "does_not_provide": [
                "operator-basis orientation to Bresciani K coordinates",
                "claim-grade public likelihood export",
            ],
        },
        "maenaut_2024_pyring_eft_ringdown_analysis": {
            "url": PYRING_EFT_RINGDOWN_ANALYSIS_URL,
            "role": "pyRing EFT ringdown analysis path for GWTC-3 events",
            "provides": [
                "time-domain pyRing EFT template path",
                "uniform-prior and event-selection description",
                "candidate rerun route for a reproducible likelihood packet",
            ],
            "does_not_provide": [
                "machine-readable posterior bundle in the current repo",
                "Bresciani K coordinate orientation",
            ],
        },
    }


def _route(
    *,
    route_id: str,
    source_ids: list[str],
    provided_edges: list[str],
    missing_edges: list[str],
    local_matrix: list[list[float]] | None,
    route_kind: str,
    interpretation: str,
    next_action: str,
    synthetic: bool = False,
) -> dict[str, Any]:
    rank = matrix_rank(local_matrix) if local_matrix else 0
    return canonicalize_json_floats({
        "route_id": route_id,
        "route_kind": route_kind,
        "source_ids": source_ids,
        "provided_edges": provided_edges,
        "missing_edges": missing_edges,
        "local_matrix_shape": (
            [len(local_matrix), len(local_matrix[0])] if local_matrix else []
        ),
        "local_matrix_rank": rank,
        "synthetic": synthetic,
        "source_backed_edges_only": not synthetic,
        "sensitivity_ready": (
            not synthetic
            and set(REQUIRED_SENSITIVITY_EDGES).issubset(provided_edges)
            and rank >= len(ENGINE_AXES)
            and not missing_edges
        ),
        "interpretation": interpretation,
        "next_action": next_action,
    })


def qnm_bresciani_source_routes() -> list[dict[str, Any]]:
    return [
        _route(
            route_id="parspec_qeft_ray_plus_bresciani_dictionary",
            route_kind="source_combination_attempt",
            source_ids=[
                "maselli_cardoso_et_al_2020_parspec",
                "parspec_eft_scale_framework_2021",
                "silva_ghosh_buonanno_2023",
                "bresciani_levati_paradisi_2026",
            ],
            provided_edges=[
                "source_qnm_deformation_axis_schema",
                "bresciani_K_to_engine_axis_projection",
                "axis_normalization_policy",
            ],
            missing_edges=[
                "qnm_deformation_to_operator_coordinate_map",
                "operator_coordinate_to_bresciani_K_map",
                "finite_3x4_sensitivity_matrix",
                "field_redefinition_policy",
            ],
            local_matrix=[[-0.2114], [-0.6070], [-1.5263], [171.35]],
            interpretation=(
                "ParSpec qEFT supplies a one-dimensional gamma-to-qNM ray. "
                "Bresciani supplies K-to-engine axes. The missing edge is the "
                "source-backed map from qNM deformation coordinates to "
                "Bresciani K coordinates."
            ),
            next_action=(
                "Find a theory-coordinate source relating ParSpec qNM shifts "
                "to the Bresciani spin-2 R4 amplitude basis."
            ),
        ),
        _route(
            route_id="pyring_quartic_tables_plus_bresciani_dictionary",
            route_kind="source_combination_attempt",
            source_ids=[
                "cano_et_al_2021_quartic_qnm_shifts",
                "cano_fransen_hertog_maenaut_2023",
                "pyring_eft_qnms_branch",
                "bresciani_levati_paradisi_2026",
            ],
            provided_edges=[
                "source_qnm_deformation_axis_schema",
                "bresciani_K_to_engine_axis_projection",
                "axis_normalization_policy",
            ],
            missing_edges=[
                "qnm_deformation_to_operator_coordinate_map",
                "operator_coordinate_to_bresciani_K_map",
                "finite_3x4_sensitivity_matrix",
                "field_redefinition_policy",
            ],
            local_matrix=[
                [-0.079381, 0.057608, -0.600495, -0.473316],
                [-0.166139, 0.244369, -0.428423, 1.23114],
                [-0.199007, 0.35232, -0.777659, 1.258555],
                [0.0, 0.0, 0.0, 0.0],
                [-0.073712, 0.136392, -0.169775, 0.741556],
                [0.073712, -0.136392, 0.169775, -0.741556],
            ],
            interpretation=(
                "The pyRing table slice has local QNM branch-column rank, but "
                "rank in branch coordinates is not an operator-basis "
                "orientation into Bresciani K axes."
            ),
            next_action=(
                "Keep pyRing runtime coordinates for reruns unless a separate "
                "field-redefinition source identifies the branch directions "
                "with Bresciani operator coordinates."
            ),
        ),
        _route(
            route_id="bresciani_amplitude_dictionary_only",
            route_kind="single_source_edge",
            source_ids=["bresciani_levati_paradisi_2026"],
            provided_edges=["bresciani_K_to_engine_axis_projection"],
            missing_edges=[
                "source_qnm_deformation_axis_schema",
                "qnm_deformation_to_operator_coordinate_map",
                "operator_coordinate_to_bresciani_K_map",
                "finite_3x4_sensitivity_matrix",
                "field_redefinition_policy",
                "axis_normalization_policy",
            ],
            local_matrix=[
                [0.5, 0.5, 0.0],
                [0.5, -0.5, 0.0],
                [0.0, 0.0, 1.0],
            ],
            interpretation=(
                "The amplitude dictionary is complete for K-to-engine "
                "projection but contains no ringdown/QNM edge."
            ),
            next_action=(
                "Use this dictionary only downstream of a real qNM-to-K source."
            ),
        ),
        _route(
            route_id="pyring_eft_likelihood_rerun_route",
            route_kind="next_likelihood_build_candidate",
            source_ids=[
                "maenaut_2024_pyring_eft_ringdown_analysis",
                "pyring_eft_qnms_branch",
            ],
            provided_edges=[
                "source_qnm_deformation_axis_schema",
                "axis_normalization_policy",
            ],
            missing_edges=[
                "public_or_reproducible_likelihood_export",
                "claim_grade_systematics_export",
                "operator_coordinate_to_bresciani_K_map",
                "finite_3x4_sensitivity_matrix",
                "field_redefinition_policy",
            ],
            local_matrix=None,
            interpretation=(
                "This is not a Bresciani sensitivity source. It is the best "
                "nonclaiming path toward a reproducible likelihood export in "
                "pyRing runtime coordinates."
            ),
            next_action=(
                "Build a rerun packet with event configs, priors, pyRing "
                "commit, sampler settings, hashes, and explicit nonclaiming "
                "coordinate scope."
            ),
        ),
    ]


def qnm_bresciani_source_route_graph() -> dict[str, Any]:
    return canonicalize_json_floats({
        "graph_id": "r4_parspec_qnm_bresciani_source_route_graph_v1",
        "version": VERSION,
        "target_sensitivity": {
            "rows": list(ENGINE_AXES),
            "columns": list(QNM_AXES),
            "required_rank": len(ENGINE_AXES),
            "required_edges": list(REQUIRED_SENSITIVITY_EDGES),
        },
        "claim_stage_requirements": list(CLAIM_STAGE_REQUIREMENTS),
        "source_registry": _source_registry(),
        "routes": qnm_bresciani_source_routes(),
        "disallowed_inferences": [
            "rank_only_branch_projection",
            "label_overlap_as_operator_identity",
            "synthetic_qnm_to_K_matrix",
            "published_bound_surrogate_as_likelihood",
        ],
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "synthetic_sensitivity_allowed": False,
            "route_graph_only_not_claim_evidence": True,
        },
    })


def evaluate_qnm_bresciani_source_route_graph(
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    graph = graph or qnm_bresciani_source_route_graph()
    blockers: set[str] = set()
    warnings: set[str] = set()
    source_registry = graph.get("source_registry", {})
    routes = graph.get("routes", [])

    if graph.get("graph_id") != "r4_parspec_qnm_bresciani_source_route_graph_v1":
        blockers.add("graph_id_mismatch")
    if tuple(graph.get("target_sensitivity", {}).get("rows", [])) != ENGINE_AXES:
        blockers.add("target_rows_mismatch")
    if tuple(graph.get("target_sensitivity", {}).get("columns", [])) != QNM_AXES:
        blockers.add("target_columns_mismatch")
    if tuple(graph.get("target_sensitivity", {}).get("required_edges", [])) != (
        REQUIRED_SENSITIVITY_EDGES
    ):
        blockers.add("required_edges_changed")
    if tuple(graph.get("claim_stage_requirements", [])) != CLAIM_STAGE_REQUIREMENTS:
        blockers.add("claim_stage_requirements_changed")
    if not isinstance(routes, list) or not routes:
        blockers.add("routes_missing")

    ready_routes: list[str] = []
    rerun_candidate_routes: list[str] = []
    for route in routes:
        route_id = route.get("route_id", "unknown_route")
        source_ids = route.get("source_ids", [])
        missing_sources = [
            source_id for source_id in source_ids if source_id not in source_registry
        ]
        if missing_sources:
            blockers.add(f"{route_id}_source_registry_missing")
        provided = set(route.get("provided_edges", []))
        missing = set(route.get("missing_edges", []))
        overlap = provided & missing
        if overlap:
            blockers.add(f"{route_id}_provided_missing_edge_overlap")
        if route.get("synthetic") is True:
            blockers.add(f"{route_id}_synthetic_route_present")
        if route.get("sensitivity_ready") is True:
            if not set(REQUIRED_SENSITIVITY_EDGES).issubset(provided):
                blockers.add(f"{route_id}_ready_without_required_edges")
            if missing:
                blockers.add(f"{route_id}_ready_with_missing_edges")
            if route.get("local_matrix_rank", 0) < len(ENGINE_AXES):
                blockers.add(f"{route_id}_ready_with_rank_deficiency")
            ready_routes.append(route_id)
        if route.get("route_kind") == "next_likelihood_build_candidate":
            if "public_or_reproducible_likelihood_export" in missing:
                rerun_candidate_routes.append(route_id)
            else:
                warnings.add(f"{route_id}_likelihood_export_unexpectedly_ready")

    controls = graph.get("claim_controls", {})
    if controls.get("claim_use_allowed") is not False:
        blockers.add("claim_use_not_disabled")
    if controls.get("framework_claim_allowed") is not False:
        blockers.add("framework_claim_not_disabled")
    if controls.get("synthetic_sensitivity_allowed") is not False:
        blockers.add("synthetic_sensitivity_not_forbidden")
    if controls.get("route_graph_only_not_claim_evidence") is not True:
        blockers.add("route_graph_not_marked_nonclaiming")

    sensitivity_ready = len(ready_routes) > 0 and not blockers
    claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if blockers:
        claim_blockers.add("qnm_bresciani_source_route_graph_not_clean")

    return canonicalize_json_floats({
        "source_route_graph_ready": not blockers,
        "qnm_to_bresciani_sensitivity_ready": sensitivity_ready,
        "ready_sensitivity_routes": ready_routes,
        "next_likelihood_build_candidate_routes": rerun_candidate_routes,
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "blockers": sorted(blockers),
        "warnings": sorted(warnings),
        "remaining_claim_blockers": sorted(claim_blockers),
        "route_status": (
            "source_route_graph_ready_sensitivity_missing"
            if not blockers and not sensitivity_ready
            else "source_route_graph_not_ready"
        ),
    })


def malformed_synthetic_source_route_graph() -> dict[str, Any]:
    graph = copy.deepcopy(qnm_bresciani_source_route_graph())
    graph["routes"].append(
        _route(
            route_id="synthetic_qnm_to_bresciani_matrix",
            route_kind="synthetic_control",
            source_ids=["silva_ghosh_buonanno_2023"],
            provided_edges=list(REQUIRED_SENSITIVITY_EDGES),
            missing_edges=[],
            local_matrix=[
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
            ],
            synthetic=True,
            interpretation="Malformed positive control.",
            next_action="reject",
        )
    )
    graph["claim_controls"]["synthetic_sensitivity_allowed"] = True
    return graph


def diagnose_r4_parspec_qnm_bresciani_source_route_graph(
    *,
    v2206_path: str | Path = DEFAULT_V2206_PATH,
) -> dict[str, Any]:
    graph = qnm_bresciani_source_route_graph()
    evaluation = evaluate_qnm_bresciani_source_route_graph(graph)
    malformed = evaluate_qnm_bresciani_source_route_graph(
        malformed_synthetic_source_route_graph()
    )
    v2206 = load_json(v2206_path)
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.200_qnm_to_bresciani_gate",
            "v2.205_pyring_to_bresciani_orientation_audit",
            "v2.206_public_likelihood_packet_gate",
            "public_source_route_recheck_2026_06_21",
        ],
        "source_route_graph": graph,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "v2206_public_likelihood_status": {
            "route_status": v2206["route_status"],
            "machine_readable_public_likelihood_ready": v2206[
                "machine_readable_public_likelihood_ready"
            ],
        },
        "qnm_to_bresciani_sensitivity_ready": evaluation[
            "qnm_to_bresciani_sensitivity_ready"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "build_pyring_eft_likelihood_rerun_packet_or_find_primary_"
            "qnm_to_bresciani_operator_source"
        ),
        "interpretation": (
            "v2.207 records the source-route graph rather than manufacturing "
            "a sensitivity matrix. ParSpec, pyRing/Cano, and Bresciani each "
            "supply useful source-backed edges, but no current public source "
            "supplies the field-redefinition/operator edge from qNM "
            "deformations into Bresciani K coordinates. The best executable "
            "next route is therefore a pyRing EFT likelihood-rerun packet in "
            "runtime coordinates, while the Bresciani map gate remains closed."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2206", default=str(DEFAULT_V2206_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_qnm_bresciani_source_route_graph(
        v2206_path=Path(args.v2206)
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
