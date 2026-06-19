"""Ng GWTC-3 Gaussian hyperposterior parser probe (v2.71)."""

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
    NG_GAUSSIAN_NPZ_FILENAME,
    load_ng_gaussian_hyperposterior_npz,
)

ZENODO_RECORD_URL = "https://zenodo.org/records/7935107"
ZENODO_API_URL = "https://zenodo.org/api/records/7935107"
ZENODO_CONCEPT_DOI = "10.5281/zenodo.7338923"
ZENODO_VERSION_DOI = "10.5281/zenodo.7935107"
NG_GAUSSIAN_NPZ_MD5 = "4d8db1755415f92b7db821277c1ed04b"
NG_GAUSSIAN_NPZ_SIZE = 28_777_020


def _md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - checksum verifies public artifact ID.
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_npz(cache_dir: Path) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / NG_GAUSSIAN_NPZ_FILENAME
    if out_path.exists() and _md5(out_path) == NG_GAUSSIAN_NPZ_MD5:
        return out_path
    url = (
        "https://zenodo.org/api/records/7935107/files/"
        f"{NG_GAUSSIAN_NPZ_FILENAME}/content"
    )
    urllib.request.urlretrieve(url, out_path)  # noqa: S310 - fixed public Zenodo URL.
    return out_path


def _compact_parameter_summary(parser_result: dict[str, Any], name: str) -> dict[str, Any]:
    summary = parser_result["parameter_summaries"][name]
    return {
        "min": summary["min"],
        "max": summary["max"],
        "mean": summary["mean"],
        "std": summary["std"],
        "p05": summary["p05"],
        "p50": summary["p50"],
        "p95": summary["p95"],
    }


def diagnose_gw_parity_ng_gaussian_posterior_parser(
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_ng_zenodo_7935107"
    npz_path = _download_npz(cache_dir)
    observed_md5 = _md5(npz_path)
    parser_result = load_ng_gaussian_hyperposterior_npz(str(npz_path))
    parser_ready = parser_result["parser_ready"]
    artifact_blockers = [
        "ng_gaussian_hyperposterior_not_restricted_global_kappa_likelihood",
        "full_event_level_feather_table_not_ingested",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]

    return {
        "version": "v2.71",
        "basis": [
            "v2.70_gw_parity_ppv_convention_audit",
            "Ng_Zenodo_10.5281_zenodo.7935107",
            "Ng_repository_showyourwork_dataset_manifest",
            "Ng_repository_kappa_constraint_generic_script",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
        "zenodo_version_doi": ZENODO_VERSION_DOI,
        "source_file": NG_GAUSSIAN_NPZ_FILENAME,
        "source_file_size_expected": NG_GAUSSIAN_NPZ_SIZE,
        "source_file_size_observed": npz_path.stat().st_size,
        "source_file_size_verified": npz_path.stat().st_size == NG_GAUSSIAN_NPZ_SIZE,
        "source_file_md5_expected": NG_GAUSSIAN_NPZ_MD5,
        "source_file_md5_observed": observed_md5,
        "source_file_md5_verified": observed_md5 == NG_GAUSSIAN_NPZ_MD5,
        "parser_ready": parser_ready,
        "parser_result": {
            "schema": parser_result["schema"],
            "chain_shape": parser_result["chain_shape"],
            "log_prob_shape": parser_result["log_prob_shape"],
            "local_accs_shape": parser_result["local_accs_shape"],
            "global_accs_shape": parser_result["global_accs_shape"],
            "sample_count": parser_result["sample_count"],
            "parameter_names": parser_result["parameter_names"],
            "mu": _compact_parameter_summary(parser_result, "mu") if parser_ready else {},
            "sigma": (
                _compact_parameter_summary(parser_result, "sigma")
                if parser_ready
                else {}
            ),
            "parser_blockers": parser_result["parser_blockers"],
            "projection_blockers": parser_result["projection_blockers"],
        },
        "ng_beta10_candidate_ready": parser_ready,
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "route_status": "ng_gaussian_hyperposterior_parser_ready_projection_blocked",
        "best_next_artifact": (
            "Build a sign-harmonized beta_1_0 likelihood adapter and decide whether "
            "to add pyarrow for the full event-level Feather posterior table."
        ),
        "interpretation": (
            "The Ng Gaussian hyperposterior product is now a verified, parsed "
            "source-native release artifact. It summarizes the population-level "
            "mu/sigma distribution of event kappas, not the restricted global "
            "kappa likelihood and not an engine-axis quantum-gravity discriminator."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.71/"
            "gw_parity_ng_gaussian_posterior_parser.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ng_gaussian_posterior_parser(args.cache_dir)
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
