"""Non-circular framework beta prediction audit (v2.57).

v2.56 showed that the cosmic-birefringence route needs a source-backed adapter
from beta to the engine parity axes. This audit asks a narrower question: which
registered frameworks predict beta independently of the beta input, and which
only match it because the measurement was used to construct the framework?
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.explicit_tower_basis import _json_default
from experiments.stack import build_stack
from itb.constraints.cosmic_birefringence import BETA_MEAS_DEG, BETA_SIGMA_DEG, KAPPA_BETA
from itb.predict import FRAMEWORKS


DISCOVERED_FRAMEWORKS = {
    "discovered_novel",
    "discovered_parity_violating",
    "discovered_high_g8",
}
DATA_DRIVEN_FRAMEWORKS = {"discovered_data_driven"}
CATALOGUED_FRAMEWORKS = set(FRAMEWORKS) - DISCOVERED_FRAMEWORKS - DATA_DRIVEN_FRAMEWORKS
_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")


def _passes_stack(framework_name: str) -> bool:
    theory = FRAMEWORKS[framework_name].encode()
    return all(constraint.evaluate(theory).satisfied for constraint in _STACK)


def _provenance(framework_name: str) -> str:
    if framework_name in DATA_DRIVEN_FRAMEWORKS:
        return "data_driven_from_birefringence_input"
    if framework_name in DISCOVERED_FRAMEWORKS:
        return "engine_discovered_internal_search"
    return "catalogued_framework_representative"


def _prediction_row(framework_name: str) -> dict[str, Any]:
    theory = FRAMEWORKS[framework_name].encode()
    coeffs = theory.coefficients
    g_r2_parity = float(coeffs.get("g_R2_parity", 0.0))
    g_r3_parity = float(coeffs.get("g_R3_parity", 0.0))
    beta_pred = KAPPA_BETA * g_r2_parity
    residual_sigma = (beta_pred - BETA_MEAS_DEG) / BETA_SIGMA_DEG
    provenance = _provenance(framework_name)
    uses_beta_input = provenance == "data_driven_from_birefringence_input"
    independent_of_beta_input = not uses_beta_input
    source_backed_beta_adapter = False
    stack_pass = _passes_stack(framework_name)
    claim_ready = (
        independent_of_beta_input
        and source_backed_beta_adapter
        and stack_pass
        and abs(residual_sigma) <= 2.0
    )
    blockers = []
    if uses_beta_input:
        blockers.append("prediction_reuses_beta_input")
    if not source_backed_beta_adapter:
        blockers.append("missing_source_backed_beta_adapter")
    if not stack_pass:
        blockers.append("framework_fails_current_stack")
    if abs(residual_sigma) > 2.0:
        blockers.append("beta_prediction_not_within_hint_band")
    if not claim_ready:
        blockers.append("not_claim_ready")

    return {
        "framework": framework_name,
        "provenance": provenance,
        "g_R2_parity": g_r2_parity,
        "g_R3_parity": g_r3_parity,
        "beta_pred_deg_toy_map": beta_pred,
        "beta_residual_sigma_toy_map": residual_sigma,
        "matches_beta_hint_2sigma_under_toy_map": abs(residual_sigma) <= 2.0,
        "independent_of_beta_input": independent_of_beta_input,
        "uses_beta_input": uses_beta_input,
        "source_backed_beta_adapter": source_backed_beta_adapter,
        "passes_current_stack": stack_pass,
        "claim_ready": claim_ready,
        "blockers": sorted(set(blockers)),
    }


def diagnose_birefringence_prediction_noncircularity_audit() -> dict[str, Any]:
    rows = [_prediction_row(name) for name in sorted(FRAMEWORKS)]
    claim_ready = [row for row in rows if row["claim_ready"]]
    independent_matches = [
        row["framework"] for row in rows
        if row["independent_of_beta_input"]
        and row["matches_beta_hint_2sigma_under_toy_map"]
    ]
    data_driven_matches = [
        row["framework"] for row in rows
        if row["uses_beta_input"]
        and row["matches_beta_hint_2sigma_under_toy_map"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "basis": [
            "v2.56_birefringence_parity_adapter_requirements",
            "registered_framework_coefficients",
            "current_theory_stack_point_evaluation",
        ],
        "framework_count": len(rows),
        "catalogued_framework_count": len(CATALOGUED_FRAMEWORKS),
        "engine_discovered_framework_count": len(DISCOVERED_FRAMEWORKS),
        "data_driven_framework_count": len(DATA_DRIVEN_FRAMEWORKS),
        "toy_beta_map": {
            "formula": "beta_pred_deg = KAPPA_BETA * g_R2_parity",
            "kappa_beta": KAPPA_BETA,
            "status": "toy_order_of_magnitude_not_source_backed",
            "beta_meas_deg": BETA_MEAS_DEG,
            "beta_sigma_deg": BETA_SIGMA_DEG,
        },
        "independent_toy_map_matches_2sigma": independent_matches,
        "data_driven_toy_map_matches_2sigma": data_driven_matches,
        "claim_ready_frameworks": [row["framework"] for row in claim_ready],
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "no_non_circular_source_backed_beta_prediction",
        "best_next_artifact": (
            "For any beta-matching framework, provide a source-backed beta adapter "
            "and independent framework parity prediction not fitted to the beta input."
        ),
        "interpretation": (
            "Several registered rows can match the beta hint under the engine's toy "
            "map, but none has a source-backed beta adapter. The data-driven row "
            "matches because it uses the beta input, so it cannot validate the "
            "same measurement. No framework currently supplies a non-circular, "
            "claim-ready beta prediction."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.57/"
            "birefringence_prediction_noncircularity_audit.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_birefringence_prediction_noncircularity_audit()
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
