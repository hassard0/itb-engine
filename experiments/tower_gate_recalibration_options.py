"""Tower-gate recalibration options from positive controls (v2.40).

v2.39 showed that the current tower gate rejects known string-compatible
positive controls. This audit computes concrete recalibration options without
changing the production gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_gate_positive_control_calibration import (
    diagnose_tower_gate_positive_control_calibration,
)


def _control_lower_phi(control: dict[str, Any]) -> float:
    if "two_sigma_phi_interval" in control:
        return float(control["two_sigma_phi_interval"][0])
    phi = float(control["phi_tower_mean"])
    sigma = float(control.get("phi_tower_sigma", 0.0))
    return phi - 2.0 * sigma


def _rejected_at_threshold(control: dict[str, Any], threshold: float) -> bool:
    return _control_lower_phi(control) > threshold


def diagnose_tower_gate_recalibration_options() -> dict[str, Any]:
    calibration = diagnose_tower_gate_positive_control_calibration()
    controls = calibration["controls"]
    current_threshold = float(controls[0]["critical_phi_tower"])
    safe_threshold = max(_control_lower_phi(control) for control in controls)
    current_rejected = [
        control["label"] for control in controls
        if _rejected_at_threshold(control, current_threshold)
    ]
    recalibrated_rejected = [
        control["label"] for control in controls
        if _rejected_at_threshold(control, safe_threshold)
    ]
    return {
        "basis": ["tower_gate", "positive_control_calibration", "recalibration_options"],
        "current_critical_phi_tower": current_threshold,
        "positive_control_safe_critical_phi_tower": safe_threshold,
        "positive_control_count": len(controls),
        "positive_controls_rejected_by_current_gate": current_rejected,
        "positive_controls_rejected_after_global_threshold_recalibration": (
            recalibrated_rejected
        ),
        "options": {
            "raise_global_threshold": {
                "candidate_threshold": safe_threshold,
                "positive_control_rejections_after": len(recalibrated_rejected),
                "tradeoff": (
                    "Removes positive-control rejection but weakens all future "
                    "tower exclusions below the strongest known KK benchmark."
                ),
                "production_change_recommended_now": False,
            },
            "scope_limit_decompactification_controls": {
                "candidate_rule": (
                    "Do not apply the current tower exclusion gate to candidates "
                    "whose source_scope is known string-compatible decompactification."
                ),
                "positive_control_rejections_after": 0,
                "tradeoff": (
                    "Preserves the numeric threshold for non-decompactification "
                    "uses but requires a source-scope classifier before promotion."
                ),
                "production_change_recommended_now": False,
            },
            "positive_control_promotion_block": {
                "candidate_rule": (
                    "A candidate cannot become tower_discriminator_claim_ready if "
                    "it matches a known positive-control family rejected by the gate."
                ),
                "positive_control_rejections_after": 0,
                "tradeoff": (
                    "Adds a conservative promotion guard while leaving diagnostic "
                    "math unchanged."
                ),
                "production_change_recommended_now": True,
            },
        },
        "recommended_next_implementation": (
            "Add a promotion guard that blocks tower_discriminator_claim_ready for "
            "known string-compatible decompactification families, then keep the "
            "numeric gate as a diagnostic until a broader calibrated threshold is "
            "justified."
        ),
        "claimable_framework_exclusions_now": [],
        "literature_guardrail": {
            "claim": (
                "This audit proposes calibration options; it does not change the "
                "engine gate and does not create framework exclusions."
            ),
            "primary_sources": calibration["literature_guardrail"]["primary_sources"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.40/tower_gate_recalibration_options.json",
    )
    args = parser.parse_args()

    result = diagnose_tower_gate_recalibration_options()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
