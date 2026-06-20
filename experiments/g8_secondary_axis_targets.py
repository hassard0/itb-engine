"""Secondary-axis targets for g8 near-degenerate framework pairs (v2.97)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.g8_measurement_sensitivity_targets import (
    Z_SCORE,
    diagnose_g8_measurement_sensitivity_targets,
)
from itb.holographic_ac import gC_from_gR2
from itb.predict import FRAMEWORKS


VERSION = "v2.97"
NEAR_G8_SEPARATION = 0.01
COEFFICIENT_AXES = (
    "g_4",
    "g_6",
    "g_8",
    "g_R2",
    "g_R3",
    "g_C",
    "g_R2_parity",
    "g_R3_parity",
)
SECONDARY_AXES = tuple(axis for axis in COEFFICIENT_AXES if axis != "g_8")
WEYL_G8_FRONTIER_SECONDARY_AXES = ("g_C",)


def _coefficients(framework_name: str) -> dict[str, float]:
    return dict(FRAMEWORKS[framework_name].encode().coefficients)


def _axis_value(framework_name: str, axis: str) -> float:
    coefficients = _coefficients(framework_name)
    if axis == "g_C" and axis not in coefficients:
        return float(gC_from_gR2(coefficients.get("g_R2", 0.0)))
    return float(coefficients.get(axis, 0.0))


def _axis_provenance(framework_name: str, axis: str) -> str:
    coefficients = _coefficients(framework_name)
    if axis in coefficients:
        return "native"
    if axis == "g_C":
        return "portrait_derived_from_g_R2"
    return "absent_zero"


def _axis_rows(framework_a: str, framework_b: str) -> list[dict[str, Any]]:
    rows = []
    for axis in SECONDARY_AXES:
        value_a = _axis_value(framework_a, axis)
        value_b = _axis_value(framework_b, axis)
        separation = abs(value_b - value_a)
        rows.append(
            {
                "axis": axis,
                "value_a": value_a,
                "value_b": value_b,
                "separation": separation,
                "required_total_sigma_for_2sigma_distinguishability": (
                    None if separation == 0.0 else separation / Z_SCORE
                ),
                "provenance_a": _axis_provenance(framework_a, axis),
                "provenance_b": _axis_provenance(framework_b, axis),
                "is_weyl_g8_frontier_secondary_axis": (
                    axis in WEYL_G8_FRONTIER_SECONDARY_AXES
                ),
                "is_parity_axis": axis in {"g_R2_parity", "g_R3_parity"},
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -(
                row["required_total_sigma_for_2sigma_distinguishability"]
                or 0.0
            ),
            row["axis"],
        ),
    )


def _named_axis(rows: list[dict[str, Any]], axis: str) -> dict[str, Any]:
    return next(row for row in rows if row["axis"] == axis)


def _pair_rows() -> list[dict[str, Any]]:
    g8_targets = diagnose_g8_measurement_sensitivity_targets()
    rows = []
    for pair in g8_targets["eligible_pairwise_separations"]:
        framework_a = pair["framework_a"]
        framework_b = pair["framework_b"]
        axes = _axis_rows(framework_a, framework_b)
        nonzero_axes = [
            row
            for row in axes
            if row["required_total_sigma_for_2sigma_distinguishability"]
            is not None
        ]
        rows.append(
            {
                "framework_a": framework_a,
                "framework_b": framework_b,
                "g8_separation": pair["separation"],
                "g8_required_total_sigma_for_2sigma_distinguishability": pair[
                    "required_total_sigma_for_2sigma_distinguishability"
                ],
                "near_g8_degenerate": pair["separation"] <= NEAR_G8_SEPARATION,
                "secondary_axes_ranked_by_tolerance": axes,
                "best_secondary_axis_by_tolerance": (
                    nonzero_axes[0] if nonzero_axes else None
                ),
                "weyl_g8_frontier_secondary_axis": _named_axis(axes, "g_C"),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            not row["near_g8_degenerate"],
            row["g8_separation"],
            row["framework_a"],
            row["framework_b"],
        ),
    )


def diagnose_g8_secondary_axis_targets() -> dict[str, Any]:
    pairs = _pair_rows()
    near_pairs = [row for row in pairs if row["near_g8_degenerate"]]

    return {
        "version": VERSION,
        "basis": [
            "v2.96_g8_measurement_sensitivity_targets",
            "itb.predict.FRAMEWORKS",
            "itb.holographic_ac.gC_from_gR2",
            "v2.50_weyl_g8_discriminator_frontier",
        ],
        "route": "g8_joint_secondary_axis_measurement_design",
        "route_status": "secondary_axis_targets_defined_no_joint_packet",
        "claimable_discriminator_now": False,
        "external_joint_packet_present": False,
        "z_score": Z_SCORE,
        "near_g8_separation_threshold": NEAR_G8_SEPARATION,
        "coefficient_axes": list(COEFFICIENT_AXES),
        "secondary_axes": list(SECONDARY_AXES),
        "pair_count": len(pairs),
        "near_g8_pair_count": len(near_pairs),
        "near_g8_pair_targets": near_pairs,
        "all_eligible_pair_targets": pairs,
        "recommended_joint_targets": [
            {
                "frameworks": [row["framework_a"], row["framework_b"]],
                "g8_required_total_sigma": row[
                    "g8_required_total_sigma_for_2sigma_distinguishability"
                ],
                "best_secondary_axis_by_tolerance": row[
                    "best_secondary_axis_by_tolerance"
                ],
                "weyl_g8_frontier_secondary_axis": row[
                    "weyl_g8_frontier_secondary_axis"
                ],
            }
            for row in near_pairs
        ],
        "claim_blockers": [
            "real_engine_normalized_g8_packet_missing",
            "source_backed_secondary_axis_packet_missing",
            "joint_likelihood_and_covariance_missing",
            "shared_eft_domain_bounds_missing",
            "secondary_axis_observable_normalization_missing",
        ],
        "best_next_artifact": (
            "A real joint packet for g_8 plus one source-backed secondary axis. "
            "For the tightest eligible pair, g_R2 gives the widest numeric "
            "tolerance, while g_C aligns with the existing Weyl/g8 frontier."
        ),
        "interpretation": (
            "The tightest eligible g_8 pair does not require giving up on the "
            "route. It requires either a very precise one-axis g_8 packet or a "
            "joint packet with a secondary axis such as g_R2 or g_C. This is "
            "still only a design target until those external measurements exist."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.97/g8_secondary_axis_targets.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_secondary_axis_targets()
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
