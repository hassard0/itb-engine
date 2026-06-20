"""Bridge source string R4 coefficients into the engine R4 normalization."""

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
from experiments.supersymmetric_r4_shape_projection import (
    kallosh_bresciani_shape_packet,
)


VERSION = "v2.145"
ZETA_3 = 1.2020569031595942
RUSSO_TREE_R4_CONTACT_SCALAR = 2.0 * ZETA_3


def normalization_bridge_requirements() -> list[dict[str, Any]]:
    return [
        {
            "field": "source_contact_scalar",
            "required_status": "source_backed",
            "source_value": "2*zeta(3)",
            "reason": (
                "Russo's type-IIB four-graviton tree expansion fixes the "
                "R4 contact scalar multiplying K."
            ),
        },
        {
            "field": "k_convention_bridge",
            "required_status": "source_backed",
            "source_value": "K_Russo / Kallosh_R4_shape",
            "reason": (
                "The source K factor must be normalized against the v2.144 "
                "helicity shape before a numeric engine coefficient is real."
            ),
        },
        {
            "field": "engine_lambda_r4_unit_conversion",
            "required_status": "source_backed",
            "source_value": "alpha_prime/string_scale units to Lambda_R4 units",
            "reason": (
                "The engine axis is dimensionless in Lambda_R4 units, so "
                "alpha-prime and Planck/string-frame factors must be fixed."
            ),
        },
    ]


def _numeric(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _source_backed(row: Any) -> bool:
    return isinstance(row, dict) and row.get("status") == "source_backed"


def evaluate_string_r4_normalization_bridge(packet: dict[str, Any]) -> dict[str, Any]:
    blockers: set[str] = set()
    source_contact = packet.get("source_contact_scalar")
    k_bridge = packet.get("k_convention_bridge")
    lambda_bridge = packet.get("engine_lambda_r4_unit_conversion")

    contact_value = None
    if _source_backed(source_contact):
        contact_value = _numeric(source_contact.get("value"))
    if contact_value is None:
        blockers.add("source_contact_scalar_missing_or_not_source_backed")

    k_bridge_value = None
    if _source_backed(k_bridge):
        k_bridge_value = _numeric(k_bridge.get("value"))
    if k_bridge_value is None:
        blockers.add("k_convention_bridge_missing_or_not_source_backed")

    lambda_bridge_value = None
    if _source_backed(lambda_bridge):
        lambda_bridge_value = _numeric(lambda_bridge.get("value"))
    if lambda_bridge_value is None:
        blockers.add("engine_lambda_r4_unit_conversion_missing_or_not_source_backed")

    if packet.get("source_backed_normalization") is not True:
        blockers.add("source_backed_normalization_missing")

    candidate = None
    if None not in (contact_value, k_bridge_value, lambda_bridge_value):
        assert contact_value is not None
        assert k_bridge_value is not None
        assert lambda_bridge_value is not None
        overall = contact_value * k_bridge_value * lambda_bridge_value
        candidate = derive_bresciani_from_source_projection(
            overall_r4_factor=overall,
            k_plus=1.0,
            k_minus_real=0.0,
            k_minus_imag=0.0,
        )

    return canonicalize_json_floats({
        "label": packet.get("label", "unnamed_string_r4_normalization_packet"),
        "source_contact_scalar": contact_value,
        "k_convention_bridge": k_bridge_value,
        "engine_lambda_r4_unit_conversion": lambda_bridge_value,
        "candidate_projection": candidate,
        "ready_for_engine_normalized_r4_projection": not blockers,
        "blockers": sorted(blockers),
    })


def source_fixed_partial_packet() -> dict[str, Any]:
    return {
        "label": "russo_kallosh_source_fixed_partial_normalization",
        "source_urls": [
            "https://arxiv.org/abs/hep-th/9707241",
            "https://arxiv.org/abs/0811.3417",
        ],
        "shape_packet": kallosh_bresciani_shape_packet()["label"],
        "source_contact_scalar": {
            "status": "source_backed",
            "value": RUSSO_TREE_R4_CONTACT_SCALAR,
            "expression": "2*zeta(3)",
            "source_ref": "Russo hep-th/9707241 eqs. A4/A4^0 expansion",
        },
        "k_convention_bridge": {
            "status": "missing",
            "value": None,
            "needed_ref": "machine-checkable K_Russo to Kallosh R4 shape bridge",
        },
        "engine_lambda_r4_unit_conversion": {
            "status": "missing",
            "value": None,
            "needed_ref": "repository Lambda_R4 convention for alpha-prime units",
        },
        "source_backed_normalization": False,
    }


def synthetic_unit_bridge_packet() -> dict[str, Any]:
    packet = source_fixed_partial_packet()
    packet["label"] = "synthetic_unit_string_r4_normalization_bridge"
    packet["k_convention_bridge"] = {
        "status": "synthetic",
        "value": 1.0,
        "warning": "unit bridge is an algebra fixture, not source-backed",
    }
    packet["engine_lambda_r4_unit_conversion"] = {
        "status": "synthetic",
        "value": 1.0,
        "warning": "unit conversion is an algebra fixture, not source-backed",
    }
    packet["source_backed_normalization"] = False
    return packet


def source_backed_unit_shape_control_packet() -> dict[str, Any]:
    packet = source_fixed_partial_packet()
    packet["label"] = "source_backed_unit_shape_control"
    packet["control_only"] = True
    packet["k_convention_bridge"] = {
        "status": "source_backed",
        "value": 1.0,
        "scope": "shape-control convention only",
    }
    packet["engine_lambda_r4_unit_conversion"] = {
        "status": "source_backed",
        "value": 1.0,
        "scope": "shape-control convention only",
    }
    packet["source_backed_normalization"] = True
    return packet


def diagnose_string_r4_normalization_bridge() -> dict[str, Any]:
    packets = {
        "source_fixed_partial_packet": source_fixed_partial_packet(),
        "synthetic_unit_bridge_packet": synthetic_unit_bridge_packet(),
        "source_backed_unit_shape_control": source_backed_unit_shape_control_packet(),
    }
    evaluations = {
        label: evaluate_string_r4_normalization_bridge(packet)
        for label, packet in packets.items()
    }
    ready = [
        label for label, row in evaluations.items()
        if (
            row["ready_for_engine_normalized_r4_projection"]
            and not packets[label].get("control_only", False)
        )
    ]
    ready_controls = [
        label for label, row in evaluations.items()
        if (
            row["ready_for_engine_normalized_r4_projection"]
            and packets[label].get("control_only", False)
        )
    ]
    blockers = sorted({
        blocker
        for row in evaluations.values()
        for blocker in row["blockers"]
    })
    naive_unit_projection = evaluations[
        "source_backed_unit_shape_control"
    ]["candidate_projection"]

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.144_supersymmetric_r4_shape_projection",
            "Russo_arXiv_hep-th_9707241_type_IIB_R4_contact_scalar",
            "v2.133_gravity_r4_projection_guard_schema",
        ],
        "normalization_bridge_requirements": normalization_bridge_requirements(),
        "source_fixed_terms": {
            "R4_contact_scalar": {
                "expression": "2*zeta(3)",
                "value": RUSSO_TREE_R4_CONTACT_SCALAR,
            },
            "shape": {
                "K_plus": 1.0,
                "K_minus_real": 0.0,
                "K_minus_imag": 0.0,
            },
        },
        "bridge_equation": (
            "overall_R4_factor = 2*zeta(3) * "
            "k_convention_bridge * engine_lambda_r4_unit_conversion"
        ),
        "evaluations": evaluations,
        "ready_normalization_packets": ready,
        "ready_control_packets": ready_controls,
        "current_blockers": blockers,
        "unit_bridge_shape_control_projection": naive_unit_projection,
        "claimable_framework_exclusions_now": [],
        "route_status": "string_r4_normalization_equation_ready_bridge_missing",
        "selected_next_build_action": (
            "source_k_convention_bridge_or_define_engine_lambda_r4_unit"
        ),
        "best_next_artifact": (
            "A source-backed value for K_Russo/Kallosh_R4_shape and the "
            "engine Lambda_R4 unit conversion, after which the v2.133 guard "
            "can receive a real string_tree_eft R4 projection packet."
        ),
        "interpretation": (
            "The string R4 normalization problem is now an executable equation. "
            "The source fixes the scalar contact term 2*zeta(3) and v2.144 "
            "fixes the helicity shape, but the current repo still lacks the "
            "source-backed K-convention bridge and Lambda_R4 unit conversion "
            "needed for a real framework-normalized claim."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.145/"
            "string_r4_normalization_bridge.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_string_r4_normalization_bridge()
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
