"""Ng GWTC-3 event-level Feather posterior parser probe (v2.72)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    NG_EVENT_LEVEL_FEATHER_FILENAME,
    load_ng_event_level_feather,
)

ZENODO_RECORD_URL = "https://zenodo.org/records/7935107"
ZENODO_API_URL = "https://zenodo.org/api/records/7935107"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.7338923"
ZENODO_VERSION_DOI = "10.5281/zenodo.7935107"
NG_EVENT_LEVEL_FEATHER_MD5 = "b60baf8bac203cb462943cc8e93f9a01"
NG_EVENT_LEVEL_FEATHER_SIZE = 636_846_658


def _md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - checksum verifies public artifact ID.
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_feather(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / NG_EVENT_LEVEL_FEATHER_FILENAME
    if out_path.exists() and _md5(out_path) == NG_EVENT_LEVEL_FEATHER_MD5:
        return out_path
    url = (
        "https://zenodo.org/api/records/7935107/files/"
        f"{NG_EVENT_LEVEL_FEATHER_FILENAME}/content"
    )
    urllib.request.urlretrieve(url, out_path)  # noqa: S310 - fixed public Zenodo URL.
    return out_path


def _compact_numeric_summary(
    parser_result: dict[str, Any],
    name: str,
) -> dict[str, Any]:
    summary = parser_result["numeric_summaries"][name]
    return {
        "min": summary["min"],
        "max": summary["max"],
        "mean": summary["mean"],
        "std": summary["std"],
        "p05": summary["p05"],
        "p50": summary["p50"],
        "p95": summary["p95"],
    }


def diagnose_gw_parity_ng_event_level_feather_parser(
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_ng_zenodo_7935107"
    feather_path = _download_feather(cache_dir)
    observed_md5 = _md5(feather_path)
    size_verified = feather_path.stat().st_size == NG_EVENT_LEVEL_FEATHER_SIZE
    md5_verified = observed_md5 == NG_EVENT_LEVEL_FEATHER_MD5
    artifact_blockers = [
        "restricted_global_kappa_likelihood_not_recomputed",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]

    if not (size_verified and md5_verified):
        return {
            "version": "v2.72",
            "basis": [
                "v2.71_gw_parity_ng_gaussian_posterior_parser",
                "Ng_Zenodo_10.5281_zenodo.7935107",
            ],
            "zenodo_record_url": ZENODO_RECORD_URL,
            "zenodo_api_url": ZENODO_API_URL,
            "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
            "zenodo_version_doi": ZENODO_VERSION_DOI,
            "source_file": NG_EVENT_LEVEL_FEATHER_FILENAME,
            "source_file_size_expected": NG_EVENT_LEVEL_FEATHER_SIZE,
            "source_file_size_observed": feather_path.stat().st_size,
            "source_file_size_verified": size_verified,
            "source_file_md5_expected": NG_EVENT_LEVEL_FEATHER_MD5,
            "source_file_md5_observed": observed_md5,
            "source_file_md5_verified": md5_verified,
            "parser_ready": False,
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
            "artifact_blockers": [
                "ng_event_level_feather_source_verification_failed",
                *artifact_blockers,
            ],
            "route_status": "ng_event_level_feather_source_verification_blocked",
        }

    parser_result = load_ng_event_level_feather(str(feather_path))
    parser_ready = parser_result["parser_ready"]
    return {
        "version": "v2.72",
        "basis": [
            "v2.71_gw_parity_ng_gaussian_posterior_parser",
            "Ng_Zenodo_10.5281_zenodo.7935107",
            "Ng_repository_sample_posterior_birefringence_release",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
        "zenodo_version_doi": ZENODO_VERSION_DOI,
        "source_file": NG_EVENT_LEVEL_FEATHER_FILENAME,
        "source_file_size_expected": NG_EVENT_LEVEL_FEATHER_SIZE,
        "source_file_size_observed": feather_path.stat().st_size,
        "source_file_size_verified": size_verified,
        "source_file_md5_expected": NG_EVENT_LEVEL_FEATHER_MD5,
        "source_file_md5_observed": observed_md5,
        "source_file_md5_verified": md5_verified,
        "pyarrow_dependency_declared": True,
        "parser_ready": parser_ready,
        "parser_result": {
            "schema": parser_result["schema"],
            "row_count": parser_result["row_count"],
            "column_count": parser_result["column_count"],
            "event_count": parser_result["event_count"],
            "event_sample_count_min": parser_result["event_sample_count_min"],
            "event_sample_count_max": parser_result["event_sample_count_max"],
            "event_counts_preview": parser_result["event_counts_preview"],
            "kappa": (
                _compact_numeric_summary(parser_result, "kappa")
                if parser_ready
                else {}
            ),
            "redshift": (
                _compact_numeric_summary(parser_result, "redshift")
                if parser_ready
                else {}
            ),
            "comoving_distance": (
                _compact_numeric_summary(parser_result, "comoving_distance")
                if parser_ready
                else {}
            ),
            "log_likelihood": (
                _compact_numeric_summary(parser_result, "log_likelihood")
                if parser_ready
                else {}
            ),
            "log_prior": (
                _compact_numeric_summary(parser_result, "log_prior")
                if parser_ready
                else {}
            ),
            "parser_blockers": parser_result["parser_blockers"],
            "projection_blockers": parser_result["projection_blockers"],
        },
        "event_level_kappa_samples_ready": parser_ready,
        "restricted_global_kappa_likelihood_ready": False,
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "route_status": "ng_event_level_feather_parser_ready_projection_blocked",
        "best_next_artifact": (
            "Recompute the restricted global kappa likelihood from the event-level "
            "posterior samples, then map it to source-declared beta_1_0 with a "
            "sign and frequency-normalization guard."
        ),
        "interpretation": (
            "The full Ng event-level posterior table is now verified and parsed "
            "as source-native kappa material. This closes the Feather ingestion "
            "blocker, but it still does not provide the restricted global kappa "
            "likelihood or an engine-axis quantum-gravity discriminator."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.72/"
            "gw_parity_ng_event_level_feather_parser.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ng_event_level_feather_parser(args.cache_dir)
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
