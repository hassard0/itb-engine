"""Framework tower-adapter threshold requirements (v2.25).

v2.24 added the optional framework tower-spectrum contract but found no native
predictions. This audit computes the numerical thresholds a future adapter must
cross before the tower axis can support a claimable framework verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import ExplicitTowerModel, _critical_phi, _json_default
from experiments.tower_framework_scenarios import _framework_reference_verdicts
from itb.predict import FRAMEWORKS


DEFAULT_SIGMA_VALUES = (0.0, 0.01, 0.05, 0.10, 0.20)


def _threshold_row(model: ExplicitTowerModel, critical_phi: float, sigma: float) -> dict:
    exclusion_phi_min = critical_phi + 2.0 * sigma
    allowed_phi_max = critical_phi - 2.0 * sigma
    return {
        "phi_tower_sigma": sigma,
        "claimable_exclusion_requires_phi_mean_gt": exclusion_phi_min,
        "claimable_exclusion_requires_mass_gap_mean_lt": model.tower_mass(exclusion_phi_min),
        "claimable_allowance_requires_phi_mean_lte": (
            allowed_phi_max if allowed_phi_max >= 0.0 else None
        ),
        "claimable_allowance_requires_mass_gap_mean_gte": (
            model.tower_mass(allowed_phi_max) if allowed_phi_max >= 0.0 else None
        ),
        "overlap_zone": [
            max(allowed_phi_max, 0.0),
            exclusion_phi_min,
        ],
        "verdict_rule": (
            "For a two-sigma interval, tower exclusion is claimable only if "
            "phi_mean - 2*sigma is above critical_phi. Tower allowance is "
            "claimable only if phi_mean + 2*sigma is at or below critical_phi."
        ),
    }


def _framework_row(
    name: str,
    model: ExplicitTowerModel,
    critical_phi: float,
    sigma_values: list[float],
    reference: dict[str, dict],
) -> dict:
    spectrum = FRAMEWORKS[name].tower_spectrum()
    ref_ok = bool(reference[name]["reference_feasible"])
    return {
        "reference_feasible": ref_ok,
        "reference_binding": reference[name]["binding"],
        "native_tower_spectrum_present": spectrum is not None,
        "current_claim_status": (
            "blocked_missing_tower_spectrum"
            if ref_ok and spectrum is None
            else "reference_excluded_before_tower_adapter"
            if not ref_ok
            else "native_tower_spectrum_available"
        ),
        "sigma_thresholds": [
            _threshold_row(model, critical_phi, sigma)
            for sigma in sigma_values
        ],
    }


def diagnose_tower_adapter_thresholds(
    sigma_values: list[float] | None = None,
) -> dict:
    model = ExplicitTowerModel(lambda_eft=0.65)
    critical = _critical_phi(model)
    critical_phi = float(critical["critical_phi"])
    sigmas = sigma_values if sigma_values is not None else list(DEFAULT_SIGMA_VALUES)
    reference = _framework_reference_verdicts()
    frameworks = {
        name: _framework_row(name, model, critical_phi, sigmas, reference)
        for name in FRAMEWORKS
    }
    reference_feasible = [
        name for name, row in frameworks.items() if row["reference_feasible"]
    ]
    missing_adapter = [
        name
        for name in reference_feasible
        if not row_has_native_spectrum(frameworks[name])
    ]

    return {
        "basis": ["TowerSpectrum", "phi_tower", "tower_mass", "Lambda_species"],
        "model": model.__dict__,
        "critical_phi_tower": critical_phi,
        "critical_tower_mass": critical["tower_mass"],
        "critical_species_cutoff": critical["species_cutoff"],
        "sigma_values": sigmas,
        "reference_feasible_frameworks": reference_feasible,
        "reference_excluded_before_tower_adapter": [
            name for name, row in frameworks.items() if not row["reference_feasible"]
        ],
        "frameworks_missing_native_tower_adapter": missing_adapter,
        "claimable_framework_exclusions_now": [],
        "frameworks": frameworks,
        "literature_guardrail": {
            "claim": (
                "These are future adapter thresholds, not framework predictions. "
                "They quantify what a sourced TowerSpectrum must show before the "
                "tower gate can support a framework-level verdict."
            ),
            "primary_sources": [
                {
                    "title": "Dvali and Redi, Black Hole Bound on the Number of Species and Quantum Gravity at LHC",
                    "url": "https://arxiv.org/abs/0710.4344",
                },
                {
                    "title": "van de Heisteeg, Vafa, and Wiesner, Bounds on Species Scale and the Distance Conjecture",
                    "url": "https://arxiv.org/abs/2303.13580",
                },
            ],
        },
        "interpretation": (
            "A future framework adapter can create a tower verdict only by placing "
            "its two-sigma phi_tower interval entirely on one side of the critical "
            "threshold. The current engine has no such native spectra, so there "
            "are no framework-level tower exclusions now."
        ),
    }


def row_has_native_spectrum(row: dict) -> bool:
    return bool(row["native_tower_spectrum_present"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.25/tower_adapter_thresholds.json")
    args = parser.parse_args()

    result = diagnose_tower_adapter_thresholds()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
