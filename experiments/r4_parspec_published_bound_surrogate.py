"""Published-bound surrogate for the ParSpec qEFT source-axis attachment."""

from __future__ import annotations

import argparse
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_engine_axis_map_contract import (
    SOURCE_AXIS_WITH_UNIT,
    evaluate_parspec_engine_axis_map_packet,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    DEFAULT_OUT as DEFAULT_V2191_PATH,
    PARSPEC_EPRINT_URL,
    QEFT_EVENT_BOUNDS_KM_90,
    QEFT_POWER,
    parspec_qeft_source_package_assets,
    qeft_parspec_source_equation_facts,
    v2191_asset_enriched_parspec_axis_map_slot,
)
from experiments.r4_parspec_ringdown_source_bridge import (
    PARSPEC_ARXIV_DOI,
    PARSPEC_DOI,
    PARSPEC_SOURCE_URL,
    SOURCE_EVENTS,
    load_json,
)
from experiments.r4_parspec_source_event_covariance_export import (
    DEFAULT_OUT as DEFAULT_V2195_PATH,
)


VERSION = "v2.196"
DEFAULT_OUT = Path(
    "experiments/results/v2.196/r4_parspec_published_bound_surrogate.json"
)
HALF_NORMAL_90_Z = 1.6448536269514722
BOUND_GRID_FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25)


def half_normal_surrogate_from_upper_bound(
    label: str,
    upper_bound_km_90: float,
) -> dict[str, Any]:
    sigma_km = upper_bound_km_90 / HALF_NORMAL_90_Z
    variance_km2 = sigma_km * sigma_km
    grid = []
    for fraction in BOUND_GRID_FRACTIONS:
        ell = upper_bound_km_90 * fraction
        grid.append({
            "ell_qEFT_km": ell,
            "fraction_of_published_bound": fraction,
            "log_relative_surrogate_likelihood": -0.5 * (ell / sigma_km) ** 2,
        })
    return canonicalize_json_floats({
        "label": label,
        "surrogate_type": "half_normal_upper_limit_from_90_credible_bound",
        "source_axis": SOURCE_AXIS_WITH_UNIT,
        "upper_bound_km_90": upper_bound_km_90,
        "half_normal_sigma_km": sigma_km,
        "variance_km2": variance_km2,
        "normal_equivalent_quantile": HALF_NORMAL_90_Z,
        "cdf_at_published_bound": 0.9,
        "grid": grid,
        "is_public_likelihood_or_posterior_sample": False,
        "claim_use_allowed": False,
    })


def parspec_qeft_published_bound_surrogates() -> dict[str, Any]:
    rows = [
        half_normal_surrogate_from_upper_bound(label, bound)
        for label, bound in QEFT_EVENT_BOUNDS_KM_90.items()
    ]
    return canonicalize_json_floats({
        "surrogate_id": "parspec_qeft_published_bound_surrogate_v1",
        "source_axis": SOURCE_AXIS_WITH_UNIT,
        "source_axis_power": QEFT_POWER,
        "source_url": PARSPEC_SOURCE_URL,
        "source_doi": PARSPEC_DOI,
        "arxiv_doi": PARSPEC_ARXIV_DOI,
        "source_eprint_url": PARSPEC_EPRINT_URL,
        "source_refs": qeft_parspec_source_equation_facts()["source_refs"],
        "surrogates": rows,
        "machine_readable_public_likelihood_ready": False,
        "surrogate_ready_for_nonclaiming_attachment": True,
        "surrogate_scope": (
            "One-dimensional ell_qEFT source-axis upper-bound surrogate derived "
            "from the published 90% credible bounds only. It is not a public "
            "posterior-sample file, covariance object, or log-likelihood grid."
        ),
    })


def public_likelihood_acquisition_snapshot() -> dict[str, Any]:
    assets = parspec_qeft_source_package_assets()
    return {
        "snapshot_id": "parspec_qeft_public_likelihood_acquisition_snapshot_v1",
        "source_url": PARSPEC_SOURCE_URL,
        "source_doi": PARSPEC_DOI,
        "arxiv_eprint_url": PARSPEC_EPRINT_URL,
        "source_package_top_level_files": assets["top_level_files"],
        "detected_machine_readable_likelihood_assets": assets[
            "detected_machine_readable_likelihood_assets"
        ],
        "audited_public_surfaces": [
            {
                "surface": "arxiv_abs",
                "url": PARSPEC_SOURCE_URL,
                "result": "abstract_and_tex_source_available",
            },
            {
                "surface": "arxiv_eprint_source_package",
                "url": PARSPEC_EPRINT_URL,
                "result": "tex_and_pdf_figures_only",
            },
            {
                "surface": "published_article",
                "url": PARSPEC_DOI,
                "result": "published_bounds_and_figures_only",
            },
            {
                "surface": "public_web_search",
                "queries": [
                    "2205.05132 ParSpec qEFT posterior samples likelihood GitHub",
                    "Silva Ghosh Buonanno ParSpec qEFT data release likelihood samples",
                    "\"qeft_posteriors_combined\" \"paper_alt_theory_bounds\"",
                ],
                "result": "no_public_machine_readable_samples_or_likelihood_found",
            },
        ],
        "machine_readable_public_likelihood_ready": False,
        "published_bound_surrogate_available": True,
    }


def event_aligned_published_bound_packet(
    v2195_path: Path = DEFAULT_V2195_PATH,
) -> dict[str, Any]:
    v2195 = load_json(v2195_path)
    source_events = v2195["source_event_covariance_export"]["source_events"]
    packet = deepcopy(v2191_asset_enriched_parspec_axis_map_slot())
    packet["packet_id"] = "v2196_event_aligned_published_bound_surrogate_slot"
    packet["event_set_policy"] = {
        "status": "aligned",
        "source_events": list(SOURCE_EVENTS),
        "engine_events": source_events,
        "same_event_set": tuple(source_events) == SOURCE_EVENTS,
        "engine_event_covariance_artifact": Path(v2195_path).as_posix(),
    }
    packet["likelihood_reference"] = {
        "status": "published_bound_surrogate",
        "source_axis": SOURCE_AXIS_WITH_UNIT,
        "events": list(SOURCE_EVENTS),
        "posterior_or_likelihood_exported": False,
        "available_in_source": "published_90_credible_upper_bounds_only",
        "published_bound_surrogate": parspec_qeft_published_bound_surrogates(),
        "needed": (
            "A public posterior-sample file, covariance matrix, or "
            "log-likelihood grid on ell_qEFT_km."
        ),
    }
    packet["claim_controls"] = {
        **packet["claim_controls"],
        "claim_use_allowed": False,
        "framework_claim_allowed": False,
        "published_bound_surrogate_not_claim_evidence": True,
    }
    return canonicalize_json_floats(packet)


def evaluate_published_bound_surrogate(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = result or diagnose_r4_parspec_published_bound_surrogate()
    surrogate = result["published_bound_surrogate"]
    packet_eval = result["event_aligned_packet_evaluation"]
    blockers: set[str] = set()

    labels = tuple(row["label"] for row in surrogate["surrogates"])
    if labels != tuple(QEFT_EVENT_BOUNDS_KM_90):
        blockers.add("published_bound_surrogate_labels_mismatch")
    for row in surrogate["surrogates"]:
        if row.get("source_axis") != SOURCE_AXIS_WITH_UNIT:
            blockers.add(f"{row.get('label', 'unknown')}_source_axis_mismatch")
        bound = row.get("upper_bound_km_90")
        sigma = row.get("half_normal_sigma_km")
        if not isinstance(bound, int | float) or bound <= 0:
            blockers.add(f"{row.get('label', 'unknown')}_published_bound_invalid")
            continue
        if not isinstance(sigma, int | float) or sigma <= 0:
            blockers.add(f"{row.get('label', 'unknown')}_surrogate_sigma_invalid")
            continue
        recovered_bound = float(sigma) * HALF_NORMAL_90_Z
        if not math.isclose(recovered_bound, float(bound), rel_tol=0.0, abs_tol=1e-9):
            blockers.add(
                f"{row.get('label', 'unknown')}_surrogate_quantile_mismatch"
            )
        if row.get("is_public_likelihood_or_posterior_sample") is not False:
            blockers.add(
                f"{row.get('label', 'unknown')}_public_likelihood_flag_unexpected"
            )

    resolved_v2191_blockers = sorted(
        set(result["v2191_asset_enriched_evaluation"]["all_blockers"])
        - set(packet_eval["all_blockers"])
    )
    claim_blockers = set(packet_eval["claim_blockers"])
    claim_blockers.update({
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "published_bound_surrogate_not_public_likelihood",
        "operator_basis_map_missing",
        "engine_axis_orientation_missing",
        "axis_normalization_missing",
        "claim_grade_systematics_export_missing",
    })
    if blockers:
        claim_blockers.add("published_bound_surrogate_not_ready")

    return canonicalize_json_floats({
        "published_bound_surrogate_ready": not blockers,
        "event_set_alignment_ready": (
            "event_set_mismatch_gw170608_vs_gw150914_gw200129"
            not in packet_eval["all_blockers"]
        ),
        "machine_readable_public_likelihood_ready": False,
        "ready_for_framework_claim": False,
        "surrogate_blockers": sorted(blockers),
        "resolved_v2191_attachment_blockers": resolved_v2191_blockers,
        "remaining_packet_blockers": packet_eval["all_blockers"],
        "claim_blockers": sorted(claim_blockers),
        "claimable_framework_exclusions_now": [],
        "route_status": (
            "parspec_published_bound_surrogate_ready_axis_map_and_public_likelihood_missing"
            if not blockers
            else "parspec_published_bound_surrogate_not_ready"
        ),
    })


def base_published_bound_surrogate_result(
    *,
    v2191_path: Path = DEFAULT_V2191_PATH,
    v2195_path: Path = DEFAULT_V2195_PATH,
) -> dict[str, Any]:
    v2191 = load_json(v2191_path)
    v2195 = load_json(v2195_path)
    packet = event_aligned_published_bound_packet(v2195_path)
    packet_eval = evaluate_parspec_engine_axis_map_packet(packet)
    return {
        "version": VERSION,
        "basis": [
            "v2.191_r4_parspec_qeft_source_asset_audit",
            "v2.195_r4_parspec_source_event_covariance_export",
            "published_qeft_90_credible_upper_bounds",
        ],
        "source_event_covariance_export": {
            "version": v2195["version"],
            "route_status": v2195["route_status"],
            "source_event_specific_nuisance_covariance_export_ready": v2195[
                "source_event_specific_nuisance_covariance_export_ready"
            ],
        },
        "public_likelihood_acquisition_snapshot": (
            public_likelihood_acquisition_snapshot()
        ),
        "published_bound_surrogate": parspec_qeft_published_bound_surrogates(),
        "event_aligned_published_bound_packet": packet,
        "v2191_asset_enriched_evaluation": v2191[
            "v2191_asset_enriched_evaluation"
        ],
        "event_aligned_packet_evaluation": packet_eval,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_source_backed_axis_map_or_acquire_machine_readable_qeft_likelihood"
        ),
        "interpretation": (
            "The ParSpec route now has an event-aligned source-axis surrogate "
            "derived from the published qEFT 90% credible bounds. This removes "
            "the stale event-set mismatch and source-axis-likelihood mismatch "
            "subpieces, but it is not a public posterior sample, covariance, or "
            "log-likelihood grid and therefore cannot close the claim-grade "
            "public-likelihood blocker."
        ),
    }


def malformed_published_bound_surrogate(
    v2191_path: Path = DEFAULT_V2191_PATH,
    v2195_path: Path = DEFAULT_V2195_PATH,
) -> dict[str, Any]:
    result = base_published_bound_surrogate_result(
        v2191_path=v2191_path,
        v2195_path=v2195_path,
    )
    result["published_bound_surrogate"]["surrogates"][0][
        "half_normal_sigma_km"
    ] = 1.0
    result["published_bound_surrogate"]["surrogates"][1][
        "is_public_likelihood_or_posterior_sample"
    ] = True
    result["published_bound_surrogate"]["surrogates"].pop()
    return result


def diagnose_r4_parspec_published_bound_surrogate(
    *,
    v2191_path: Path = DEFAULT_V2191_PATH,
    v2195_path: Path = DEFAULT_V2195_PATH,
) -> dict[str, Any]:
    result = base_published_bound_surrogate_result(
        v2191_path=v2191_path,
        v2195_path=v2195_path,
    )
    evaluation = evaluate_published_bound_surrogate(result)
    malformed = evaluate_published_bound_surrogate(
        malformed_published_bound_surrogate(v2191_path, v2195_path)
    )
    result["evaluation"] = evaluation
    result["malformed_control_evaluation"] = malformed
    result["published_bound_surrogate_ready"] = evaluation[
        "published_bound_surrogate_ready"
    ]
    result["route_status"] = evaluation["route_status"]
    return canonicalize_json_floats(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2191", default=str(DEFAULT_V2191_PATH))
    parser.add_argument("--v2195", default=str(DEFAULT_V2195_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_published_bound_surrogate(
        v2191_path=Path(args.v2191),
        v2195_path=Path(args.v2195),
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
