"""Tower evidence sourceability from current framework encoders (v2.33).

v2.32 identified the next required artifact: a sourced TowerEvidence row for a
reference-feasible, in-scope framework. This audit asks whether that row can be
derived from the framework catalogue as currently encoded, without importing new
physics or external compactification data.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.discriminator_frontier import diagnose_discriminator_frontier
from experiments.explicit_tower_basis import _json_default
from itb.predict import FRAMEWORKS


TOWER_INPUT_KEYS = (
    "phi_tower",
    "phi_tower_mean",
    "phi_tower_sigma",
    "tower_mass_gap",
    "radius_ratio",
    "radius_ratio_mean",
    "delta_moduli",
    "delta_moduli_mean",
    "lambda_sdc",
)


def _encoded_tower_inputs(name: str) -> dict:
    framework = FRAMEWORKS[name]
    theory = framework.encode()
    coefficients = theory.coefficients
    metadata = theory.metadata
    attr_hits = [
        key for key in TOWER_INPUT_KEYS
        if getattr(framework, key, None) is not None
    ]
    coeff_hits = [
        key for key in TOWER_INPUT_KEYS
        if coefficients.get(key) is not None
    ]
    metadata_hits = [
        key for key in TOWER_INPUT_KEYS
        if metadata.get(key) is not None
    ]
    return {
        "coefficient_hits": coeff_hits,
        "metadata_hits": metadata_hits,
        "framework_attribute_hits": attr_hits,
        "has_any_tower_input": bool(coeff_hits or metadata_hits or attr_hits),
        "encoded_coefficient_keys": sorted(coefficients),
        "metadata_keys": sorted(metadata),
    }


def _required_next_data(name: str) -> str:
    if name == "pure_gr":
        return (
            "A UV-completion or null-baseline decision with sourced tower evidence; "
            "pure GR Wilson coefficients alone are not quantum-gravity tower data."
        )
    if name == "string_tree_eft":
        return (
            "A compactification-specific R/R0 or Delta_moduli with uncertainty, "
            "normalization, and primary source."
        )
    if name == "asymptotic_safety":
        return (
            "A sourced RG-to-tower map or scale spectrum with phi_tower normalization "
            "and uncertainty."
        )
    if name == "cdt":
        return (
            "A sourced continuum-limit geometric spectrum mapped to a tower mass, "
            "radius ratio, or moduli distance with uncertainty."
        )
    if name.startswith("discovered_"):
        return (
            "External evidence or a reproducible computed-spectrum artifact; "
            "engine-generated Wilson coefficients alone are not an allowed source."
        )
    return "A sourced TowerEvidence row with normalization and uncertainty."


def _row(name: str, frontier_row: dict) -> dict:
    encoded_inputs = _encoded_tower_inputs(name)
    target = (
        frontier_row["reference_feasible"]
        and frontier_row["engine_scope"]["in_scope"]
    )
    sourceable = target and encoded_inputs["has_any_tower_input"]
    if not frontier_row["reference_feasible"]:
        status = "not_target_reference_excluded"
    elif not frontier_row["engine_scope"]["in_scope"]:
        status = "not_target_scope_limited"
    elif sourceable:
        status = "encoded_tower_inputs_present_needs_evidence_validation"
    else:
        status = "not_sourceable_from_current_encoder"
    return {
        "framework": name,
        "reference_feasible": frontier_row["reference_feasible"],
        "engine_in_scope": frontier_row["engine_scope"]["in_scope"],
        "frontier_status": frontier_row["frontier_status"],
        "encoded_tower_inputs": encoded_inputs,
        "sourceable_from_current_encoder": sourceable,
        "sourceability_status": status,
        "required_next_data": _required_next_data(name),
    }


def diagnose_tower_evidence_sourceability() -> dict:
    frontier = diagnose_discriminator_frontier()
    rows = {
        name: _row(name, frontier["frameworks"][name])
        for name in FRAMEWORKS
    }
    in_scope_reference_feasible = [
        name for name, row in rows.items()
        if row["reference_feasible"] and row["engine_in_scope"]
    ]
    sourceable = [
        name for name, row in rows.items()
        if row["sourceable_from_current_encoder"]
    ]
    status_counts = {
        status: sum(1 for row in rows.values() if row["sourceability_status"] == status)
        for status in sorted({row["sourceability_status"] for row in rows.values()})
    }
    return {
        "basis": ["framework_encoder", "Theory", "TowerEvidence"],
        "registered_framework_count": len(rows),
        "in_scope_reference_feasible_frameworks": in_scope_reference_feasible,
        "sourceable_from_current_encoder": sourceable,
        "sourceability_status_counts": status_counts,
        "claimable_framework_exclusions_now": [],
        "frameworks": rows,
        "literature_guardrail": {
            "claim": (
                "This is an encoder sourceability audit, not a literature "
                "exhaustion proof. It only says whether the current repository "
                "already encodes the tower inputs needed for TowerEvidence."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "Corvilain, Grimm, and Valenzuela, The Swampland Distance Conjecture for Kahler moduli",
                    "url": "https://arxiv.org/abs/1812.07548",
                },
            ],
        },
        "interpretation": (
            "No in-scope reference-feasible framework currently encodes phi_tower, "
            "tower_mass_gap, R/R0, Delta_moduli, or lambda_sdc. A non-synthetic "
            "TowerEvidence row therefore requires new sourced data, not a local "
            "reinterpretation of existing Wilson coefficients."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.33/tower_evidence_sourceability.json")
    args = parser.parse_args()

    result = diagnose_tower_evidence_sourceability()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
