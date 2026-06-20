"""Gross-Witten K-factor ingestion attempt and source-record correction."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.141"


def source_record_attempts() -> list[dict[str, Any]]:
    return [
        {
            "attempt_id": "cern_record_170189_pdf",
            "url": "https://cds.cern.ch/record/170189/files/198608288.pdf",
            "retrieval_status": "downloaded_rendered_not_target_source",
            "downloaded_bytes": 473146,
            "local_pypdf_text_chars": 13,
            "vulcan_pdftotext_bytes": 14,
            "rendered_title": (
                "Higher Curvature Supergravity and Superstrings"
            ),
            "rendered_authors": ["S. Ferrara"],
            "target_title": "Superstring modifications of Einstein's equations",
            "is_gross_witten_target": False,
            "provides_machine_checkable_k_formula": False,
            "blocker": "wrong_cern_pdf_record_for_gross_witten",
            "interpretation": (
                "The previously downloaded CERN PDF is a Ferrara invited "
                "talk, not Gross-Witten. It cannot be used as the primary "
                "K-factor source."
            ),
        },
        {
            "attempt_id": "cern_record_166499_actual_gross_witten",
            "url": "https://cds.cern.ch/record/166499",
            "files_url": "https://cds.cern.ch/record/166499/files/",
            "retrieval_status": "metadata_record_found_no_file_link_exposed",
            "metadata_title": "Superstring modifications of Einstein's equations",
            "metadata_authors": ["David J. Gross", "Edward Witten"],
            "metadata_pages": 18,
            "files_endpoint_content_type": "text/html; charset=utf-8",
            "files_endpoint_bytes": 15578,
            "file_list_entries_found": 0,
            "is_gross_witten_target": True,
            "provides_machine_checkable_k_formula": False,
            "blocker": "gross_witten_cern_record_has_no_exposed_file",
            "interpretation": (
                "The real CERN record exists, but the public file tab did "
                "not expose a downloadable source/PDF file during this run."
            ),
        },
        {
            "attempt_id": "doi_record",
            "url": "https://doi.org/10.1016/0550-3213(86)90429-3",
            "retrieval_status": "bibliographic_primary_record_only",
            "metadata_title": "Superstring modifications of Einstein's equations",
            "metadata_authors": ["David J. Gross", "Edward Witten"],
            "is_gross_witten_target": True,
            "provides_machine_checkable_k_formula": False,
            "blocker": "doi_record_not_machine_formula_ingestion",
            "interpretation": (
                "The DOI identifies the primary article, but does not by "
                "itself supply a machine-checkable K expression."
            ),
        },
    ]


def k_factor_ingestion_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement": "target_source_identity_verified",
            "status": "satisfied",
            "evidence": "CERN record 166499 and DOI identify Gross-Witten.",
            "blocker": None,
        },
        {
            "requirement": "wrong_source_removed_from_route",
            "status": "satisfied",
            "evidence": (
                "CERN record 170189 PDF rendered as Ferrara, not Gross-Witten."
            ),
            "blocker": None,
        },
        {
            "requirement": "machine_checkable_k_formula",
            "status": "missing",
            "evidence": "No exposed Gross-Witten source/PDF text was ingested.",
            "blocker": "gross_witten_k_formula_not_ingested",
        },
        {
            "requirement": "k_plus_k_minus_projection",
            "status": "missing",
            "evidence": "Requires K formula or independent rederivation.",
            "blocker": "source_K_plus_K_minus_components_missing",
        },
    ]


def next_ingestion_routes() -> list[dict[str, Any]]:
    return [
        {
            "route": "obtain_gross_witten_article_pdf_from_library_or_elsevier",
            "status": "preferred_if_accessible",
            "acceptance_test": (
                "pdftotext or OCR yields enough text/formula content to "
                "locate the four-graviton K expression with page metadata."
            ),
        },
        {
            "route": "ocr_physical_scan_of_gross_witten_article",
            "status": "parallel_route",
            "acceptance_test": (
                "OCR output plus rendered page image identifies K without "
                "ambiguous manual transcription."
            ),
        },
        {
            "route": "rederive_k_from_string_polarization_tensors",
            "status": "fallback_route",
            "acceptance_test": (
                "Symbolic derivation projects a source-backed R4 tensor or "
                "kinematic factor into Bresciani K_plus/K_minus channels."
            ),
        },
    ]


def diagnose_gross_witten_k_factor_ingestion_attempt() -> dict[str, Any]:
    attempts = source_record_attempts()
    requirements = k_factor_ingestion_requirements()
    blockers = sorted({
        row["blocker"] for row in attempts + requirements
        if row["blocker"] is not None
    })
    verified_target_records = [
        row["attempt_id"] for row in attempts
        if row["is_gross_witten_target"]
    ]
    machine_k_sources = [
        row["attempt_id"] for row in attempts
        if row["provides_machine_checkable_k_formula"]
    ]
    satisfied_requirements = [
        row["requirement"] for row in requirements
        if row["status"] == "satisfied"
    ]
    missing_requirements = [
        row["requirement"] for row in requirements
        if row["status"] != "satisfied"
    ]
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.140_source_k_factor_helicity_decomposition_audit",
            "CERN_record_166499",
            "DOI_10.1016_0550-3213_86_90429-3",
        ],
        "source_record_attempts": attempts,
        "verified_gross_witten_records": verified_target_records,
        "machine_checkable_k_formula_sources": machine_k_sources,
        "requirements": requirements,
        "satisfied_requirements": satisfied_requirements,
        "missing_requirements": missing_requirements,
        "next_ingestion_routes": next_ingestion_routes(),
        "can_ingest_k_formula_now": bool(machine_k_sources),
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "gross_witten_record_corrected_k_formula_not_ingested",
        "selected_next_build_action": (
            "ocr_or_library_ingest_gross_witten_k_formula_or_rederive_k"
        ),
        "best_next_artifact": (
            "A page-anchored, machine-checkable K-factor expression from "
            "Gross-Witten, or a source-backed independent derivation that "
            "does not depend on the inaccessible scan."
        ),
        "interpretation": (
            "This iteration corrects the source trail: the accessible CERN "
            "PDF previously tried was the wrong paper. The real Gross-Witten "
            "record is identified, but no public file was exposed from CERN "
            "and no K formula has been ingested. The route remains active "
            "through OCR/library access or an independent derivation."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.141/"
            "gross_witten_k_factor_ingestion_attempt.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gross_witten_k_factor_ingestion_attempt()
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
