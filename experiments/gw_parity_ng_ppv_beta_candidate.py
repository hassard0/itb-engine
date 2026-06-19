"""Ng PPV beta_1_0 candidate packet probe (v2.74)."""

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
from experiments.gw_parity_ng_restricted_likelihood import (
    NG_REPOSITORY_COMMIT,
    NG_REPOSITORY_URL,
    NG_RESTRICTED_SCRIPT_PATH,
)
from itb.gw_parity import (
    NG_EVENT_LEVEL_FEATHER_FILENAME,
    build_ng_ppv_beta10_candidate_packet,
    load_ng_restricted_global_kappa_likelihood_from_feather,
)

JENKS_PPV_URL = "https://arxiv.org/abs/2305.10478"


def _packet_summary(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": packet["schema"],
        "candidate_ready": packet["candidate_ready"],
        "source_parameter": packet.get("source_parameter"),
        "target_ppv_parameter": packet.get("target_ppv_parameter"),
        "source_declared_mapping_ready": packet.get("source_declared_mapping_ready"),
        "source_native_likelihood_ready": packet.get("source_native_likelihood_ready"),
        "ppv_beta10_candidate_likelihood_ready": packet.get(
            "ppv_beta10_candidate_likelihood_ready"
        ),
        "canonical_engine_beta10_ready": packet.get("canonical_engine_beta10_ready"),
        "frequency_reference_hz": packet.get("frequency_reference_hz"),
        "distance_factor": packet.get("distance_factor"),
        "candidate_formula": packet.get("candidate_formula"),
        "candidate_coefficient_units": packet.get("candidate_coefficient_units"),
        "candidate_coefficient_basis": packet.get("candidate_coefficient_basis"),
        "source_native_constraint": packet.get("source_native_constraint", {}),
        "sign_conventions": packet.get("sign_conventions", {}),
        "readiness": packet.get("readiness", {}),
        "parser_blockers": packet.get("parser_blockers", []),
        "projection_blockers": packet["projection_blockers"],
        "blockers": packet["blockers"],
    }


def diagnose_gw_parity_ng_ppv_beta_candidate(
    cache_dir: Path | None = None,
) -> dict[str, Any]:
    if cache_dir is None:
        cache_dir = Path(tempfile.gettempdir()) / "itb_ng_zenodo_7935107"
    feather_path = _download_feather(cache_dir)
    observed_md5 = _md5(feather_path)
    size_verified = feather_path.stat().st_size == NG_EVENT_LEVEL_FEATHER_SIZE
    md5_verified = observed_md5 == NG_EVENT_LEVEL_FEATHER_MD5

    if not (size_verified and md5_verified):
        return {
            "version": "v2.74",
            "basis": [
                "v2.73_gw_parity_ng_restricted_likelihood",
                "v2.70_gw_parity_ppv_convention_audit",
            ],
            "source_file": NG_EVENT_LEVEL_FEATHER_FILENAME,
            "source_file_size_expected": NG_EVENT_LEVEL_FEATHER_SIZE,
            "source_file_size_observed": feather_path.stat().st_size,
            "source_file_size_verified": size_verified,
            "source_file_md5_expected": NG_EVENT_LEVEL_FEATHER_MD5,
            "source_file_md5_observed": observed_md5,
            "source_file_md5_verified": md5_verified,
            "candidate_packet_ready": False,
            "engine_projection_ready": False,
            "claimable_discriminator_now": False,
            "artifact_blockers": [
                "ng_event_level_feather_source_verification_failed",
            ],
            "route_status": "ng_ppv_beta10_candidate_source_verification_blocked",
        }

    likelihood = load_ng_restricted_global_kappa_likelihood_from_feather(
        str(feather_path)
    )
    packet = build_ng_ppv_beta10_candidate_packet(likelihood)
    return {
        "version": "v2.74",
        "basis": [
            "v2.73_gw_parity_ng_restricted_likelihood",
            "v2.70_gw_parity_ppv_convention_audit",
            "Ng_restricted_kappa_source_likelihood",
            "Jenks_source_declared_beta_1_0_mapping",
        ],
        "zenodo_record_url": ZENODO_RECORD_URL,
        "zenodo_api_url": ZENODO_API_URL,
        "zenodo_concept_doi": ZENODO_CONCEPT_DOI,
        "zenodo_version_doi": ZENODO_VERSION_DOI,
        "ng_repository_url": NG_REPOSITORY_URL,
        "ng_repository_commit": NG_REPOSITORY_COMMIT,
        "ng_restricted_script_path": NG_RESTRICTED_SCRIPT_PATH,
        "jenks_ppv_url": JENKS_PPV_URL,
        "source_file": NG_EVENT_LEVEL_FEATHER_FILENAME,
        "source_file_size_expected": NG_EVENT_LEVEL_FEATHER_SIZE,
        "source_file_size_observed": feather_path.stat().st_size,
        "source_file_size_verified": size_verified,
        "source_file_md5_expected": NG_EVENT_LEVEL_FEATHER_MD5,
        "source_file_md5_observed": observed_md5,
        "source_file_md5_verified": md5_verified,
        "restricted_global_kappa_likelihood_ready": likelihood["ready"],
        "candidate_packet_ready": packet["candidate_ready"],
        "source_native_ppv_candidate_ready": packet["candidate_ready"],
        "ppv_beta10_candidate_likelihood_ready": packet.get(
            "ppv_beta10_candidate_likelihood_ready",
            False,
        ),
        "canonical_engine_beta10_ready": packet.get(
            "canonical_engine_beta10_ready",
            False,
        ),
        "packet": _packet_summary(packet),
        "closed_blockers": [
            "restricted_global_kappa_likelihood_not_recomputed",
            "ng_public_posterior_parser_not_implemented",
        ],
        "artifact_blockers": packet["blockers"],
        "ppv_beta1_projection_ready": False,
        "engine_projection_ready": False,
        "claimable_discriminator_now": False,
        "route_status": "ng_ppv_beta10_candidate_packet_ready_engine_blocked",
        "best_next_artifact": (
            "Define the engine-canonical helicity sign and dimensional PPV beta "
            "normalization, or prove that the source-native beta candidate cannot "
            "be mapped into any current engine parity axis."
        ),
        "interpretation": (
            "Ng now supplies a reproduced source-native kappa likelihood and a "
            "source-declared PPV beta_1_0 candidate packet. The packet is useful "
            "for bookkeeping and future adapters, but still blocks all engine "
            "projection because the canonical sign and dimensionless beta "
            "normalization are not owned by the engine."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-dir", type=Path, default=None)
    parser.add_argument(
        "--out",
        default="experiments/results/v2.74/gw_parity_ng_ppv_beta_candidate.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_ng_ppv_beta_candidate(args.cache_dir)
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
