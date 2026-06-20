"""Access probe for the Gross-Witten tree-level R4 primary source."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.152"
PROBE_DATE = "2026-06-20"


def gross_witten_metadata_sources() -> list[dict[str, Any]]:
    return [
        {
            "source_id": "cern_cds_166499",
            "url": "https://cds.cern.ch/record/166499",
            "metadata_status": "confirmed",
            "facts": {
                "title": "Superstring modifications of Einstein's equations",
                "authors": ["David J. Gross", "Edward Witten"],
                "publication_year": 1986,
                "record_type": "preprint",
                "pages": 18,
            },
            "file_status": "files_tab_disabled",
        },
        {
            "source_id": "inspire_227371",
            "url": "https://inspirehep.net/literature/227371",
            "metadata_status": "confirmed",
            "facts": {
                "title": "Superstring Modifications of Einstein's Equations",
                "journal": "Nucl.Phys.B 277 (1986) 1",
                "doi": "10.1016/0550-3213(86)90429-3",
            },
            "file_status": "metadata_only_in_probe",
        },
        {
            "source_id": "princeton_publication_page",
            "url": (
                "https://collaborate.princeton.edu/en/publications/"
                "superstring-modifications-of-einsteins-equations/"
            ),
            "metadata_status": "confirmed",
            "facts": {
                "abstract_scope": (
                    "tree-level gravitational scattering amplitudes determine "
                    "the effective gravitational action through quartic order "
                    "in the Riemann tensor"
                ),
            },
            "file_status": "metadata_only_in_probe",
        },
        {
            "source_id": "osti_etdeweb_7010259",
            "url": "https://www.osti.gov/etdeweb/biblio/7010259",
            "metadata_status": "confirmed",
            "facts": {
                "abstract_scope": (
                    "effective gravitational action through quartic order in "
                    "the Riemann tensor"
                ),
            },
            "file_status": "metadata_only_in_probe",
        },
    ]


def gross_witten_file_access_attempts() -> list[dict[str, Any]]:
    return [
        {
            "url": "https://cds.cern.ch/record/166499/files/",
            "observed_status": "200_text_html_directory_view",
            "machine_formula_ingested": False,
            "reason": "directory view returned no downloadable primary file",
        },
        {
            "url": "https://cds.cern.ch/record/166499/files/CM-P00062424.pdf",
            "observed_status": "404_not_found",
            "machine_formula_ingested": False,
            "reason": "common CDS PDF pattern did not match this record",
        },
        {
            "url": "https://cds.cern.ch/record/166499/files/198602063.pdf",
            "observed_status": "404_not_found",
            "machine_formula_ingested": False,
            "reason": "common preprint-number PDF pattern did not match",
        },
        {
            "url": "https://cds.cern.ch/record/166499/files/PRINT-86-0637.pdf",
            "observed_status": "404_not_found",
            "machine_formula_ingested": False,
            "reason": "common PRINT preprint PDF pattern did not match",
        },
        {
            "url": "https://cds.cern.ch/record/166499/files/CERN-TH-4380-86.pdf",
            "observed_status": "404_not_found",
            "machine_formula_ingested": False,
            "reason": "common CERN-TH PDF pattern did not match",
        },
    ]


def evaluate_gross_witten_source_access() -> dict[str, Any]:
    metadata = gross_witten_metadata_sources()
    attempts = gross_witten_file_access_attempts()
    metadata_confirmed = all(row["metadata_status"] == "confirmed" for row in metadata)
    machine_ingested = any(row["machine_formula_ingested"] for row in attempts)
    return canonicalize_json_floats({
        "probe_date": PROBE_DATE,
        "metadata_confirmed": metadata_confirmed,
        "primary_file_machine_ingested": machine_ingested,
        "k_formula_machine_ingested": False,
        "metadata_sources": metadata,
        "file_access_attempts": attempts,
        "claim_ready_now": False,
        "claim_blockers": [
            "gross_witten_primary_file_not_machine_ingested",
            "machine_readable_K_factor_formula_missing",
            "alpha_prime_to_engine_Lambda_R4_conversion_missing",
        ],
        "fallback_route": (
            "rederive_virasoro_shapiro_k_bridge_from_open_sources"
        ),
    })


def diagnose_gross_witten_source_access_probe() -> dict[str, Any]:
    evaluation = evaluate_gross_witten_source_access()
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.151_r4_claim_blocker_attack_plan",
            "Gross_Witten_1986_CERN_CDS_record_166499",
            "DOI_10.1016_0550_3213_86_90429_3",
        ],
        "evaluation": evaluation,
        "claimable_framework_exclusions_now": [],
        "ready_to_claim_now": False,
        "route_status": "gross_witten_metadata_confirmed_file_access_blocked",
        "selected_next_build_action": (
            "rederive_virasoro_shapiro_k_bridge_from_open_sources"
        ),
        "best_next_artifact": (
            "A rederivation workbench using open Russo/Kallosh/Virasoro-Shapiro "
            "normalizations to produce or reject a dimensionless K bridge and "
            "an alpha-prime to engine Lambda_R4 policy."
        ),
        "interpretation": (
            "The Gross-Witten source is confirmed as the primary target, but "
            "this probe did not obtain a machine-readable primary file or K "
            "formula. The route should move to an open-source rederivation "
            "instead of treating the missing PDF as a terminal blocker."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.152/gross_witten_source_access_probe.json",
    )
    args = parser.parse_args()

    result = diagnose_gross_witten_source_access_probe()
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
