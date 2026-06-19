"""Ng restricted global-kappa likelihood reproduction probe (v2.73)."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_parity_ng_event_level_feather_parser import (
    NG_EVENT_LEVEL_FEATHER_MD5,
    NG_EVENT_LEVEL_FEATHER_SIZE,
    ZENODO_API_URL,
    ZENODO_CONCEPT_DOI,
    ZENODO_RECORD_URL,
    ZENODO_VERSION_DOI,
    _download_feather,
    _md5,
)
from itb.gw_parity import (
    GW_PARITY_PROJECTION_BLOCKERS,
    NG_EVENT_LEVEL_FEATHER_FILENAME,
    load_ng_restricted_global_kappa_likelihood_from_feather,
)

NG_REPOSITORY_URL = "https://github.com/thomasckng/constraining-birefringence-with-gwtc-3"
NG_REPOSITORY_COMMIT = "447fc5eaee71995cfc046c99dc41754716249d47"
NG_RESTRICTED_SCRIPT_PATH = "src/scripts/kappa_constraint_restricted.py"
PUBLISHED_MEDIAN_ROUNDED = -0.019
PUBLISHED_PLUS_90_ROUNDED = 0.038
PUBLISHED_MINUS_90_ROUNDED = 0.029


def _rounded_constraint_match(likelihood: dict[str, Any]) -> dict[str, Any]:
    observed = {
        "median": round(likelihood["restricted_kappa_median"], 3),
        "plus_90": round(likelihood["restricted_kappa_plus_90"], 3),
        "minus_90": round(likelihood["restricted_kappa_minus_90"], 3),
    }
    expected = {
        "median": PUBLISHED_MEDIAN_ROUNDED,
        "plus_90": PUBLISHED_PLUS_90_ROUNDED,
        "minus_90": PUBLISHED_MINUS_90_ROUNDED,
    }
    return {
        "expected": expected,
        "observed": observed,
        "matches_published_rounding": observed == expected,
    }


def diagnose_gw_parity_ng_restricted_likelihood(
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_ng_zenodo_7935107"
    feather_path = _download_feather(cache_dir)
    observed_md5 = _md5(feather_path)
    size_verified = feather_path.stat().st_size == NG_EVENT_LEVEL_FEATHER_SIZE
    md5_verified = observed_md5 == NG_EVENT_LEVEL_FEATHER_MD5
    artifact_blockers = [
        "ppv_beta1_sign_frequency_guard_not_applied",
        *GW_PARITY_PROJECTION_BLOCKERS,
    ]

    if not (size_verified and md5_verified):
        return {
            "version": "v2.73",
            "basis": [
                "v2.72_gw_parity_ng_event_level_feather_parser",
                "Ng_Zenodo_10.5281_zenodo.7935107",
                "Ng_repository_kappa_constraint_restricted_script",
            ],
            "source_file": NG_EVENT_LEVEL_FEATHER_FILENAME,
            "source_file_size_expected": NG_EVENT_LEVEL_FEATHER_SIZE,
            "source_file_size_observed": feather_path.stat().st_size,
            "source_file_size_verified": size_verified,
            "source_file_md5_expected": NG_EVENT_LEVEL_FEATHER_MD5,
            "source_file_md5_observed": observed_md5,
            "source_file_md5_verified": md5_verified,
            "restricted_global_kappa_likelihood_ready": False,
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
            "artifact_blockers": [
                "ng_event_level_feather_source_verification_failed",
                *artifact_blockers,
            ],
            "route_status": "ng_restricted_global_kappa_source_verification_blocked",
        }

    likelihood = load_ng_restricted_global_kappa_likelihood_from_feather(
        str(feather_path)
    )
    rounded_match = _rounded_constraint_match(likelihood) if likelihood["ready"] else {}
    return {
        "version": "v2.73",
        "basis": [
            "v2.72_gw_parity_ng_event_level_feather_parser",
            "Ng_Zenodo_10.5281_zenodo.7935107",
            "Ng_repository_kappa_constraint_restricted_script",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
        "zenodo_version_doi": ZENODO_VERSION_DOI,
        "ng_repository_url": NG_REPOSITORY_URL,
        "ng_repository_commit": NG_REPOSITORY_COMMIT,
        "ng_restricted_script_path": NG_RESTRICTED_SCRIPT_PATH,
        "source_file": NG_EVENT_LEVEL_FEATHER_FILENAME,
        "source_file_size_expected": NG_EVENT_LEVEL_FEATHER_SIZE,
        "source_file_size_observed": feather_path.stat().st_size,
        "source_file_size_verified": size_verified,
        "source_file_md5_expected": NG_EVENT_LEVEL_FEATHER_MD5,
        "source_file_md5_observed": observed_md5,
        "source_file_md5_verified": md5_verified,
        "restricted_global_kappa_likelihood_ready": likelihood["ready"],
        "likelihood": {
            "schema": likelihood["schema"],
            "sample_count": likelihood.get("sample_count", 0),
            "event_count": likelihood.get("event_count", 0),
            "event_sample_count_min": likelihood.get("event_sample_count_min", 0),
            "event_sample_count_max": likelihood.get("event_sample_count_max", 0),
            "grid_min": likelihood.get("grid_min"),
            "grid_max": likelihood.get("grid_max"),
            "grid_size": likelihood.get("grid_size"),
            "density_norm": likelihood.get("density_norm"),
            "maximum_likelihood_kappa": likelihood.get("maximum_likelihood_kappa"),
            "restricted_kappa_5": likelihood.get("restricted_kappa_5"),
            "restricted_kappa_median": likelihood.get("restricted_kappa_median"),
            "restricted_kappa_95": likelihood.get("restricted_kappa_95"),
            "restricted_kappa_plus_90": likelihood.get("restricted_kappa_plus_90"),
            "restricted_kappa_minus_90": likelihood.get("restricted_kappa_minus_90"),
            "credible_level_at_zero": likelihood.get("credible_level_at_zero"),
            "absolute_kappa_68": likelihood.get("absolute_kappa_68"),
            "absolute_kappa_90": likelihood.get("absolute_kappa_90"),
            "parser_blockers": likelihood["parser_blockers"],
            "projection_blockers": likelihood["projection_blockers"],
        },
        "published_constraint_rounding_check": rounded_match,
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "artifact_blockers": artifact_blockers,
        "route_status": "ng_restricted_global_kappa_likelihood_reproduced_projection_blocked",
        "best_next_artifact": (
            "Wrap the reproduced source-native kappa likelihood in a PPV beta_1_0 "
            "candidate packet with explicit sign, frequency, and dimensional guards."
        ),
        "interpretation": (
            "The Ng restricted global kappa likelihood is now reproduced from the "
            "public event-level samples and matches the published rounded median "
            "and 90 percent interval. It remains a source-native GW attenuation "
            "constraint, not an engine-axis quantum-gravity discriminator."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument(
        "--out",
        default="experiments/results/v2.73/gw_parity_ng_restricted_likelihood.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ng_restricted_likelihood(args.cache_dir)
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
