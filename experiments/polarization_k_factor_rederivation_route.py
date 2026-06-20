"""Route and validator for rederiving the R4 K-factor helicity components."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.four_dimensional_r4_projection_derivation_workbench import (
    derive_bresciani_from_source_projection,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats


VERSION = "v2.142"
PRIMARY_SOURCE_PREFIXES = ("https://arxiv.org/", "https://doi.org/")
VALID_FRAME_POLICIES = {
    "four_dimensional_on_shell_weyl_ricci_flat",
    "four_dimensional_on_shell_riemann_with_eom_terms_removed",
}
REQUIRED_DERIVATION_PACKET_FIELDS = (
    "source_urls",
    "source_equation_refs",
    "four_dimensional_policy",
    "polarization_dictionary",
    "source_k_formula",
    "helicity_components",
    "normalization",
    "source_backed_derivation",
)


def rederivation_stages() -> list[dict[str, Any]]:
    return [
        {
            "stage": "fix_four_dimensional_policy",
            "required_output": "four_dimensional_policy",
            "acceptance_test": (
                "Policy is one of the explicit on-shell Weyl/Riemann options."
            ),
        },
        {
            "stage": "define_polarization_dictionary",
            "required_output": "polarization_dictionary",
            "acceptance_test": (
                "Maps graviton helicity states to spinor-helicity Weyl "
                "building blocks used by the source K expression."
            ),
        },
        {
            "stage": "state_source_k_formula",
            "required_output": "source_k_formula",
            "acceptance_test": (
                "Formula is page/equation anchored to a primary source or "
                "derived algebraically from source tensor contractions."
            ),
        },
        {
            "stage": "project_helicity_components",
            "required_output": "K_plus, Re(K_minus), Im(K_minus)",
            "acceptance_test": (
                "Components match Bresciani same-helicity and complex "
                "helicity-flip monomial families."
            ),
        },
        {
            "stage": "normalize_to_engine_lambda_r4",
            "required_output": "overall_R4_factor",
            "acceptance_test": (
                "Normalization is dimensionless in the engine Lambda_R4 "
                "convention and tied to source alpha-prime units."
            ),
        },
        {
            "stage": "invert_and_check_positivity",
            "required_output": "g_R4_c1, g_R4_c2, g_R4_c3",
            "acceptance_test": (
                "v2.139 inversion is applied and the Bresciani positivity "
                "residual is computed."
            ),
        },
    ]


def _missing(value: Any) -> bool:
    return value in (None, "", [], {})


def _primary_urls(urls: Any) -> bool:
    if not isinstance(urls, list) or not urls:
        return False
    return all(str(url).startswith(PRIMARY_SOURCE_PREFIXES) for url in urls)


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def evaluate_k_rederivation_packet(packet: dict[str, Any]) -> dict[str, Any]:
    missing = [
        field for field in REQUIRED_DERIVATION_PACKET_FIELDS
        if _missing(packet.get(field))
    ]
    blockers: set[str] = set()
    if missing:
        blockers.add("missing_required_fields")
    if not _primary_urls(packet.get("source_urls")):
        blockers.add("source_urls_not_primary")
    if packet.get("four_dimensional_policy") not in VALID_FRAME_POLICIES:
        blockers.add("four_dimensional_policy_invalid")
    if not isinstance(packet.get("polarization_dictionary"), dict):
        blockers.add("polarization_dictionary_missing_or_invalid")
    if not isinstance(packet.get("source_k_formula"), dict):
        blockers.add("source_k_formula_missing_or_invalid")

    components = packet.get("helicity_components")
    if not isinstance(components, dict):
        components = {}
    k_plus = _numeric(components.get("K_plus"))
    k_minus_real = _numeric(components.get("K_minus_real"))
    k_minus_imag = _numeric(components.get("K_minus_imag"))
    if None in (k_plus, k_minus_real, k_minus_imag):
        blockers.add("k_plus_k_minus_components_missing_or_nonnumeric")

    normalization = packet.get("normalization")
    overall = None
    if isinstance(normalization, dict):
        overall = _numeric(normalization.get("overall_R4_factor"))
    if overall is None:
        blockers.add("overall_r4_factor_missing_or_nonnumeric")
    if packet.get("source_backed_derivation") is not True:
        blockers.add("source_backed_derivation_missing")

    derived = None
    if not blockers:
        assert overall is not None
        assert k_plus is not None
        assert k_minus_real is not None
        assert k_minus_imag is not None
        derived = derive_bresciani_from_source_projection(
            overall_r4_factor=overall,
            k_plus=k_plus,
            k_minus_real=k_minus_real,
            k_minus_imag=k_minus_imag,
        )
        if not derived["positivity_summary"]["passed"]:
            blockers.add("bresciani_positivity_failed")

    return canonicalize_json_floats({
        "label": packet.get("label", "unnamed_k_rederivation_packet"),
        "missing_fields": missing,
        "source_urls_primary": _primary_urls(packet.get("source_urls")),
        "four_dimensional_policy_valid": (
            packet.get("four_dimensional_policy") in VALID_FRAME_POLICIES
        ),
        "k_components": {
            "K_plus": k_plus,
            "K_minus_real": k_minus_real,
            "K_minus_imag": k_minus_imag,
        },
        "overall_R4_factor": overall,
        "derived_bresciani_projection": derived,
        "ready_for_k_factor_projection": not blockers,
        "blockers": sorted(blockers),
    })


def empty_rederivation_packet() -> dict[str, Any]:
    return {
        "label": "empty_source_backed_k_rederivation_packet",
        "source_urls": [],
        "source_equation_refs": {},
        "four_dimensional_policy": "",
        "polarization_dictionary": {},
        "source_k_formula": {},
        "helicity_components": {},
        "normalization": {},
        "source_backed_derivation": False,
    }


def synthetic_control_packet() -> dict[str, Any]:
    return {
        "label": "synthetic_k_rederivation_control",
        "source_urls": ["https://arxiv.org/abs/2504.12855"],
        "source_equation_refs": {"synthetic": ["not_a_source_derivation"]},
        "four_dimensional_policy": "four_dimensional_on_shell_weyl_ricci_flat",
        "polarization_dictionary": {
            "negative_helicity_weyl_spinor": "lambda^4",
            "positive_helicity_weyl_spinor": "tilde_lambda^4",
        },
        "source_k_formula": {
            "status": "synthetic_control_not_source_formula",
            "formula": "K_plus=0.3, K_minus=0.1+0.05i",
        },
        "helicity_components": {
            "K_plus": 0.3,
            "K_minus_real": 0.1,
            "K_minus_imag": 0.05,
        },
        "normalization": {
            "overall_R4_factor": 8.0,
            "status": "synthetic_unit_normalization",
        },
        "source_backed_derivation": False,
    }


def diagnose_polarization_k_factor_rederivation_route() -> dict[str, Any]:
    evaluations = {
        "empty_packet": evaluate_k_rederivation_packet(empty_rederivation_packet()),
        "synthetic_control": evaluate_k_rederivation_packet(synthetic_control_packet()),
    }
    blockers = sorted({
        blocker for row in evaluations.values() for blocker in row["blockers"]
    })
    ready_packets = [
        label for label, row in evaluations.items()
        if row["ready_for_k_factor_projection"]
    ]
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.141_gross_witten_k_factor_ingestion_attempt",
            "v2.139_four_dimensional_r4_projection_derivation_workbench",
            "Bresciani_helicity_matching_contract",
        ],
        "required_derivation_packet_fields": list(REQUIRED_DERIVATION_PACKET_FIELDS),
        "valid_four_dimensional_policies": sorted(VALID_FRAME_POLICIES),
        "rederivation_stages": rederivation_stages(),
        "evaluations": evaluations,
        "ready_k_factor_projection_packets": ready_packets,
        "current_blockers": blockers,
        "claimable_framework_exclusions_now": [],
        "route_status": "polarization_k_factor_rederivation_route_specified_no_source_packet",
        "selected_next_build_action": (
            "derive_or_ingest_source_backed_k_rederivation_packet"
        ),
        "best_next_artifact": (
            "A source-backed K rederivation packet that passes this validator "
            "and feeds v2.139 with K_plus, K_minus, and overall_R4_factor."
        ),
        "interpretation": (
            "The fallback route now has executable acceptance tests. Synthetic "
            "components are rejected unless a source-backed derivation is "
            "present, so the engine can safely evaluate future K-factor "
            "rederivations without promoting fixtures."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.142/"
            "polarization_k_factor_rederivation_route.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_polarization_k_factor_rederivation_route()
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
