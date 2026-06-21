"""Public-likelihood acquisition gate for the ParSpec qEFT bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_engine_axis_map_contract import SOURCE_AXIS_WITH_UNIT
from experiments.r4_parspec_published_bound_surrogate import (
    parspec_qeft_published_bound_surrogates,
    public_likelihood_acquisition_snapshot,
)
from experiments.r4_parspec_qeft_source_asset_audit import (
    PARSPEC_EPRINT_URL,
    PARSPEC_SOURCE_PACKAGE_SHA256,
    QEFT_CDF_FIGURE_SHA256,
    QEFT_EVENT_BOUNDS_KM_90,
    QEFT_POSTERIORS_FIGURE_SHA256,
    QEFT_TEX_SHA256,
    parspec_qeft_source_package_assets,
    qeft_parspec_source_equation_facts,
)
from experiments.r4_parspec_ringdown_source_bridge import (
    PARSPEC_ARXIV_DOI,
    PARSPEC_DOI,
    PARSPEC_SOURCE_URL,
    SOURCE_EVENTS,
)


VERSION = "v2.206"
DEFAULT_OUT = Path(
    "experiments/results/v2.206/r4_parspec_public_likelihood_packet.json"
)
PUBLIC_LIKELIHOOD_ACCEPTANCE_CRITERIA = (
    "machine_readable_public_url",
    "posterior_samples_or_covariance_or_log_likelihood_grid",
    "ell_qeft_or_qnm_axis_schema",
    "source_event_rows_or_combined_policy",
    "prior_and_threshold_policy",
    "waveform_sampler_version_metadata",
    "calibration_and_systematics_policy",
    "content_hashes_and_license",
)
ALLOWED_PUBLIC_LIKELIHOOD_ASSET_TYPES = (
    "posterior_samples",
    "covariance_matrix",
    "log_likelihood_grid",
)
QNM_AXIS_SCHEMA = (
    "delta_omega_qeft_0",
    "delta_tau_qeft_0",
    "delta_omega_qeft_1",
    "delta_tau_qeft_1",
)
PUBLIC_RECHECK_QUERIES = (
    '"2205.05132" "posterior samples" qEFT ParSpec',
    '"Tests of general relativity with GW150914 and GW200129" "data"',
    '"qeft_posteriors_combined" "paper_alt_theory_bounds"',
    '"Silva" "Ghosh" "Buonanno" "ParSpec" "GitHub"',
    '"2205.05132" "github.com"',
    '"paper_alt_theory_bounds" github',
    '"qeft_posteriors_combined.pdf"',
    '"ell_qEFT" "posterior"',
)


def public_likelihood_acceptance_criteria() -> list[dict[str, Any]]:
    return [
        {
            "criterion": "machine_readable_public_url",
            "required": True,
            "description": (
                "A public URL or DOI-backed landing page must expose the "
                "machine-readable object, not only a plotted figure."
            ),
        },
        {
            "criterion": "posterior_samples_or_covariance_or_log_likelihood_grid",
            "required": True,
            "description": (
                "The object must be posterior samples, a covariance matrix, or "
                "a log-likelihood grid for the qEFT source axis."
            ),
        },
        {
            "criterion": "ell_qeft_or_qnm_axis_schema",
            "required": True,
            "description": (
                "The schema must identify ell_qEFT_km or the four ParSpec qNM "
                "deformation axes used by the engine bridge."
            ),
        },
        {
            "criterion": "source_event_rows_or_combined_policy",
            "required": True,
            "description": (
                "The packet must name GW150914/GW200129 rows or a source-backed "
                "combined-event policy."
            ),
        },
        {
            "criterion": "prior_and_threshold_policy",
            "required": True,
            "description": (
                "The prior, EFT threshold, and credible-bound policy must be "
                "recoverable from the packet."
            ),
        },
        {
            "criterion": "waveform_sampler_version_metadata",
            "required": True,
            "description": (
                "The waveform family, sampler, and version metadata must be "
                "recorded so the likelihood can be reproduced."
            ),
        },
        {
            "criterion": "calibration_and_systematics_policy",
            "required": True,
            "description": (
                "Calibration, detector topology, and waveform-systematics "
                "policy must be explicit."
            ),
        },
        {
            "criterion": "content_hashes_and_license",
            "required": True,
            "description": (
                "The released object must carry content hashes and an access or "
                "license statement."
            ),
        },
    ]


def _absent_public_likelihood_candidate() -> dict[str, Any]:
    return {
        "status": "absent",
        "asset_type": "none",
        "machine_readable": False,
        "public_url": "",
        "source_axis_schema": [],
        "event_scope": [],
        "combined_event_policy": "",
        "prior_policy": "",
        "threshold_policy": "",
        "waveform_sampler_metadata": {},
        "calibration_systematics_policy": {},
        "content_hash_sha256": "",
        "license_or_access_statement": "",
        "source_note": (
            "No public posterior sample file, covariance object, or "
            "log-likelihood grid for ell_qEFT_km was found."
        ),
    }


def public_likelihood_surface_recheck() -> dict[str, Any]:
    snapshot = public_likelihood_acquisition_snapshot()
    return {
        "checked_on": "2026-06-21",
        "snapshot_id": "parspec_qeft_public_likelihood_surface_recheck_v2",
        "source_package_top_level_files": snapshot["source_package_top_level_files"],
        "queries": list(PUBLIC_RECHECK_QUERIES),
        "surfaces": [
            {
                "surface": "arxiv_abs",
                "url": PARSPEC_SOURCE_URL,
                "result": (
                    "paper, PDF, and TeX source links visible; no code/data "
                    "landing page for qEFT posterior samples."
                ),
            },
            {
                "surface": "arxiv_eprint_source_package",
                "url": PARSPEC_EPRINT_URL,
                "result": (
                    "TeX/Bib/Bbl plus figure PDFs only; no h5, txt, csv, dat, "
                    "npy, json, posterior chain, covariance, or likelihood grid."
                ),
            },
            {
                "surface": "published_article",
                "url": PARSPEC_DOI,
                "result": (
                    "Published bounds and figures are available; no visible "
                    "machine-readable supplemental qEFT likelihood packet."
                ),
            },
            {
                "surface": "arxiv_doi",
                "url": PARSPEC_ARXIV_DOI,
                "result": "redirects to the arXiv paper/source surface.",
            },
            {
                "surface": "lvk_gwtc2_tests_of_gr_zenodo",
                "url": "https://zenodo.org/records/5172704",
                "result": (
                    "Generic LVK tests-of-GR posterior products are public, but "
                    "not a Silva/Ghosh/Buonanno ell_qEFT likelihood release."
                ),
            },
            {
                "surface": "lvk_gwtc3_tests_of_gr_zenodo",
                "url": "https://zenodo.org/records/7007370",
                "result": (
                    "Generic LVK tests-of-GR posterior products are public, but "
                    "not the required qEFT source-axis likelihood packet."
                ),
            },
            {
                "surface": "author_and_public_code_surfaces",
                "url": "https://github.com/hosilva",
                "result": (
                    "No paper-specific public repository or data release for "
                    "the qEFT posterior/likelihood surfaced in exact searches."
                ),
            },
            {
                "surface": "public_web_search",
                "queries": list(PUBLIC_RECHECK_QUERIES),
                "result": (
                    "No public machine-readable samples, covariance, or "
                    "log-likelihood grid found."
                ),
            },
        ],
        "detected_machine_readable_likelihood_assets": [],
        "machine_readable_public_likelihood_ready": False,
    }


def parspec_public_likelihood_packet_candidate() -> dict[str, Any]:
    assets = parspec_qeft_source_package_assets()
    facts = qeft_parspec_source_equation_facts()
    surrogate = parspec_qeft_published_bound_surrogates()
    return canonicalize_json_floats({
        "packet_id": "v2206_parspec_public_likelihood_packet_candidate",
        "source_identity": {
            "paper": "Silva_Ghosh_Buonanno_2023",
            "source_url": PARSPEC_SOURCE_URL,
            "source_doi": PARSPEC_DOI,
            "arxiv_doi": PARSPEC_ARXIV_DOI,
            "source_eprint_url": PARSPEC_EPRINT_URL,
        },
        "acceptance_criteria": public_likelihood_acceptance_criteria(),
        "source_package_hashes": {
            "source_package_sha256": PARSPEC_SOURCE_PACKAGE_SHA256,
            "qeft_tex_sha256": QEFT_TEX_SHA256,
            "qeft_posterior_figure_sha256": QEFT_POSTERIORS_FIGURE_SHA256,
            "qeft_cdf_figure_sha256": QEFT_CDF_FIGURE_SHA256,
        },
        "source_facts_preserved": {
            "source_axis": SOURCE_AXIS_WITH_UNIT,
            "qeft_power": facts["parspec_gamma_relation"]["qeft_power"],
            "qnm_deformation_coefficients": facts[
                "qnm_deformation_coefficients"
            ],
            "event_bounds_90_credible_km": QEFT_EVENT_BOUNDS_KM_90,
            "source_events": list(SOURCE_EVENTS),
        },
        "available_public_assets": {
            "top_level_files": assets["top_level_files"],
            "audited_assets": assets["audited_assets"],
            "detected_machine_readable_likelihood_assets": assets[
                "detected_machine_readable_likelihood_assets"
            ],
            "machine_readable_likelihood_ready": assets[
                "machine_readable_likelihood_ready"
            ],
        },
        "public_surface_recheck": public_likelihood_surface_recheck(),
        "public_likelihood_candidate": _absent_public_likelihood_candidate(),
        "published_bound_surrogate_reference": {
            "surrogate_id": surrogate["surrogate_id"],
            "source_axis": surrogate["source_axis"],
            "source_axis_power": surrogate["source_axis_power"],
            "event_labels": [row["label"] for row in surrogate["surrogates"]],
            "machine_readable_public_likelihood_ready": surrogate[
                "machine_readable_public_likelihood_ready"
            ],
            "surrogate_ready_for_nonclaiming_attachment": surrogate[
                "surrogate_ready_for_nonclaiming_attachment"
            ],
            "claim_use_allowed": False,
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "public_likelihood_required_for_claim": True,
            "published_bound_surrogate_not_claim_evidence": True,
        },
    })


def _criterion_status(candidate: dict[str, Any]) -> dict[str, bool]:
    axis_schema = set(candidate.get("source_axis_schema", []))
    event_scope = set(candidate.get("event_scope", []))
    metadata = candidate.get("waveform_sampler_metadata", {})
    systematics = candidate.get("calibration_systematics_policy", {})
    return {
        "machine_readable_public_url": bool(
            candidate.get("machine_readable") and candidate.get("public_url")
        ),
        "posterior_samples_or_covariance_or_log_likelihood_grid": (
            candidate.get("asset_type") in ALLOWED_PUBLIC_LIKELIHOOD_ASSET_TYPES
            and bool(candidate.get("machine_readable"))
        ),
        "ell_qeft_or_qnm_axis_schema": (
            SOURCE_AXIS_WITH_UNIT in axis_schema
            or set(QNM_AXIS_SCHEMA).issubset(axis_schema)
        ),
        "source_event_rows_or_combined_policy": (
            set(SOURCE_EVENTS).issubset(event_scope)
            or bool(candidate.get("combined_event_policy"))
        ),
        "prior_and_threshold_policy": bool(
            candidate.get("prior_policy") and candidate.get("threshold_policy")
        ),
        "waveform_sampler_version_metadata": all(
            metadata.get(key) for key in ("waveform_model", "sampler", "version")
        ),
        "calibration_and_systematics_policy": all(
            systematics.get(key)
            for key in (
                "detector_topology",
                "calibration_policy",
                "waveform_systematics_policy",
            )
        ),
        "content_hashes_and_license": (
            isinstance(candidate.get("content_hash_sha256"), str)
            and len(candidate["content_hash_sha256"]) == 64
            and bool(candidate.get("license_or_access_statement"))
        ),
    }


def evaluate_public_likelihood_packet(
    packet: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = packet or parspec_public_likelihood_packet_candidate()
    candidate = packet["public_likelihood_candidate"]
    statuses = _criterion_status(candidate)
    criteria = {
        row["criterion"]: row["required"]
        for row in packet["acceptance_criteria"]
    }
    missing = [
        criterion
        for criterion in PUBLIC_LIKELIHOOD_ACCEPTANCE_CRITERIA
        if criteria.get(criterion) is not True or statuses[criterion] is not True
    ]
    blockers = [f"{criterion}_missing" for criterion in missing]
    public_ready = not blockers
    claim_blockers = set(blockers)
    claim_blockers.update({
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "pyring_quartic_direction_to_bresciani_axis_orientation_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    })
    if not public_ready:
        claim_blockers.add(
            "public_parspec_qeft_likelihood_or_posterior_samples_missing"
        )

    return canonicalize_json_floats({
        "acceptance_gate_documented": True,
        "criterion_status": statuses,
        "public_likelihood_packet_ready": public_ready,
        "machine_readable_public_likelihood_ready": public_ready,
        "published_bound_surrogate_retained": packet[
            "published_bound_surrogate_reference"
        ]["surrogate_ready_for_nonclaiming_attachment"],
        "published_bound_surrogate_claim_use_allowed": False,
        "blockers": blockers,
        "claim_blockers": sorted(claim_blockers),
        "ready_for_framework_claim": False,
        "claimable_framework_exclusions_now": [],
        "route_status": (
            "parspec_public_likelihood_packet_ready_claim_gate_still_blocked"
            if public_ready
            else "parspec_public_likelihood_packet_absent_bound_surrogate_retained"
        ),
    })


def malformed_public_likelihood_packet_candidate() -> dict[str, Any]:
    packet = parspec_public_likelihood_packet_candidate()
    packet["public_likelihood_candidate"] = {
        "status": "present_but_incomplete_control",
        "asset_type": "posterior_samples",
        "machine_readable": True,
        "public_url": "https://example.invalid/qeft-samples.h5",
        "source_axis_schema": [SOURCE_AXIS_WITH_UNIT],
        "event_scope": ["GW150914"],
        "combined_event_policy": "",
        "prior_policy": "",
        "threshold_policy": "",
        "waveform_sampler_metadata": {
            "waveform_model": "SEOBNRv4HM_PA",
            "sampler": "LALInferenceMCMC",
        },
        "calibration_systematics_policy": {
            "detector_topology": "H1L1",
            "calibration_policy": "",
            "waveform_systematics_policy": "",
        },
        "content_hash_sha256": "",
        "license_or_access_statement": "",
        "source_note": (
            "Positive control: a URL-shaped object is insufficient without "
            "events, priors, threshold policy, versions, hashes, license, and "
            "systematics metadata."
        ),
    }
    return packet


def diagnose_r4_parspec_public_likelihood_packet() -> dict[str, Any]:
    packet = parspec_public_likelihood_packet_candidate()
    evaluation = evaluate_public_likelihood_packet(packet)
    malformed = evaluate_public_likelihood_packet(
        malformed_public_likelihood_packet_candidate()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.191_r4_parspec_qeft_source_asset_audit",
            "v2.196_r4_parspec_published_bound_surrogate",
            "v2.205_r4_parspec_pyring_to_bresciani_orientation",
            "public_source_recheck_2026_06_21",
        ],
        "public_likelihood_packet": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed,
        "public_likelihood_packet_ready": evaluation[
            "public_likelihood_packet_ready"
        ],
        "machine_readable_public_likelihood_ready": evaluation[
            "machine_readable_public_likelihood_ready"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": evaluation["route_status"],
        "selected_next_build_action": (
            "build_reproducible_qeft_likelihood_rerun_packet_or_find_new_"
            "source_backed_qnm_to_bresciani_sensitivity"
        ),
        "interpretation": (
            "The public-source recheck preserves the same conclusion as the "
            "source-package audit: the ParSpec qEFT paper exposes source TeX "
            "and plotted posterior/CDF figures, and the engine can retain the "
            "published-bound surrogate for nonclaiming continuity. It still "
            "does not have a public machine-readable posterior sample, "
            "covariance matrix, or log-likelihood grid on ell_qEFT_km, so the "
            "claim gate remains closed."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_public_likelihood_packet()
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
