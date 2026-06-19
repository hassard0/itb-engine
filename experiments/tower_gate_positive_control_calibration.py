"""Tower-gate calibration against known string-compatible controls (v2.39).

v2.37 and v2.38 found primary-source benchmarks that cross the current tower
threshold. This audit treats those benchmarks as positive controls for stringy
decompactification behavior. A discriminator that rejects its positive controls
is not yet calibrated for framework exclusions.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.analytic_kk_tower_benchmark import diagnose_analytic_kk_tower_benchmark
from experiments.explicit_tower_basis import _json_default
from experiments.large_volume_sdc_benchmark import diagnose_large_volume_sdc_benchmark


def _large_volume_control() -> dict[str, Any]:
    candidate = diagnose_large_volume_sdc_benchmark()["candidate"]
    return {
        "label": candidate["label"],
        "source_family": "large_volume_calabi_yau_sdc",
        "known_qg_positive_control": True,
        "math_excluded_by_current_gate": bool(candidate["tower_claimable_by_math"]),
        "gate_verdict": candidate["framework_tower_verdict"],
        "two_sigma_phi_interval": candidate["two_sigma_phi_interval"],
        "critical_phi_tower": candidate["critical_phi_tower"],
        "calibration_verdict": (
            "positive_control_rejected_by_tower_gate"
            if candidate["tower_claimable_by_math"]
            else "positive_control_passes_tower_gate"
        ),
        "scope": (
            "asymptotic large-volume Calabi-Yau benchmark with audit-supplied "
            "Delta_moduli=1"
        ),
    }


def _analytic_kk_controls() -> list[dict[str, Any]]:
    benchmark = diagnose_analytic_kk_tower_benchmark()
    rows = []
    for candidate in benchmark["candidates"]:
        rejected = candidate["benchmark_tower_verdict"] == "benchmark_excluding"
        rows.append({
            "label": candidate["label"],
            "source_family": "analytic_kk_decompactification_vector",
            "known_qg_positive_control": True,
            "math_excluded_by_current_gate": rejected,
            "gate_verdict": candidate["benchmark_tower_verdict"],
            "phi_tower_mean": candidate["phi_tower_mean"],
            "phi_tower_sigma": candidate["phi_tower_sigma"],
            "critical_phi_tower": candidate["critical_phi_tower"],
            "calibration_verdict": (
                "positive_control_rejected_by_tower_gate"
                if rejected
                else "positive_control_passes_tower_gate"
            ),
            "scope": (
                "analytic KK decompactification vector with audit-supplied "
                "Delta_moduli=1"
            ),
        })
    return rows


def diagnose_tower_gate_positive_control_calibration() -> dict[str, Any]:
    controls = [_large_volume_control(), *_analytic_kk_controls()]
    rejected = [
        row for row in controls
        if row["calibration_verdict"] == "positive_control_rejected_by_tower_gate"
    ]
    status = (
        "tower_gate_fails_positive_control_calibration"
        if rejected
        else "tower_gate_passes_positive_control_calibration"
    )
    return {
        "basis": ["tower_gate", "known_qg_positive_control", "calibration_audit"],
        "positive_control_count": len(controls),
        "positive_controls_rejected_by_gate": [row["label"] for row in rejected],
        "positive_control_rejection_count": len(rejected),
        "calibration_status": status,
        "calibrated_discriminator_ready": False,
        "tower_discriminator_candidates_now": [],
        "claimable_framework_exclusions_now": [],
        "controls": controls,
        "action_required": (
            "Do not promote tower-gate math exclusions into framework exclusions "
            "until the gate is recalibrated or scope-limited so it does not reject "
            "known string-compatible decompactification controls."
        ),
        "literature_guardrail": {
            "claim": (
                "This is an adversarial calibration audit. Positive-control "
                "rejection is evidence against the current gate as a universal "
                "quantum-gravity discriminator, not evidence for a solution claim."
            ),
            "primary_sources": [
                {
                    "title": (
                        "Blumenhagen, Klaewer, Schlechter, and Wolf, The Refined "
                        "Swampland Distance Conjecture in Calabi-Yau Moduli Spaces"
                    ),
                    "url": "https://arxiv.org/abs/1803.04989",
                },
                {
                    "title": (
                        "Aoufia, Castellano, and Ibanez, Laplacians in Various "
                        "Dimensions and the Swampland"
                    ),
                    "url": "https://arxiv.org/abs/2506.03253",
                },
            ],
        },
        "interpretation": (
            "The current tower gate is useful as a benchmark stress test, but it "
            "cannot support framework exclusions while it rejects string-compatible "
            "large-volume and analytic KK positive controls."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.39/tower_gate_positive_control_calibration.json",
    )
    args = parser.parse_args()

    result = diagnose_tower_gate_positive_control_calibration()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
