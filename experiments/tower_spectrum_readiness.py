"""Framework tower-spectrum readiness audit (v2.24).

v2.23 identified measurements that would reduce `phi_tower` assignment
ambiguity. This audit asks whether any current framework encoder can supply the
missing ingredient: a normalized tower-spectrum prediction with uncertainty.

The answer should remain conservative by default. A framework-level exclusion is
claimable only when a framework supplies an actionable tower prediction; absent
that prediction, the engine reports a wiring gap, not a physics verdict.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import ExplicitTowerModel, _critical_phi, _json_default
from experiments.tower_framework_scenarios import _framework_reference_verdicts
from itb.predict import FRAMEWORKS


REQUIRED_ACTIONABLE_FIELDS = (
    "tower_family",
    "phi_tower_mean",
    "phi_tower_sigma",
    "normalization",
    "source",
)


def _spectrum_to_dict(value: Any) -> dict | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return dict(to_dict())
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {
        "adapter_error": f"unsupported tower spectrum type: {type(value).__name__}",
    }


def _native_spectrum(framework: Any) -> dict | None:
    method = getattr(framework, "tower_spectrum", None)
    if callable(method):
        return _spectrum_to_dict(method())
    value = getattr(framework, "tower_spectrum_prediction", None)
    return _spectrum_to_dict(value)


def _phi_from_mass(model: ExplicitTowerModel, mass_gap: float | None) -> float | None:
    if mass_gap is None or mass_gap <= 0.0 or model.lambda_tower <= 0.0:
        return None
    if mass_gap > model.m0:
        return 0.0
    return -math.log(mass_gap / model.m0) / model.lambda_tower


def _normalize_prediction(
    framework_name: str,
    raw: dict | None,
    model: ExplicitTowerModel,
) -> dict:
    if raw is None:
        return {
            "framework": framework_name,
            "prediction_present": False,
            "actionable": False,
            "missing_fields": list(REQUIRED_ACTIONABLE_FIELDS),
            "tower_prediction": None,
        }

    prediction = dict(raw)
    if prediction.get("phi_tower_mean") is None:
        prediction["phi_tower_mean"] = _phi_from_mass(
            model,
            prediction.get("tower_mass_gap"),
        )

    missing = [
        field for field in REQUIRED_ACTIONABLE_FIELDS
        if prediction.get(field) in (None, "")
    ]
    actionable = len(missing) == 0
    return {
        "framework": framework_name,
        "prediction_present": True,
        "actionable": actionable,
        "missing_fields": missing,
        "tower_prediction": prediction,
    }


def _prediction_verdict(
    framework_name: str,
    normalized: dict,
    reference: dict[str, dict],
    model: ExplicitTowerModel,
) -> dict:
    ref_ok = bool(reference[framework_name]["reference_feasible"])
    base = {
        "framework": framework_name,
        "reference_feasible": ref_ok,
        **normalized,
    }
    if not normalized["actionable"]:
        return {
            **base,
            "two_sigma_phi_interval": None,
            "tower_allowed_at_mean": None,
            "framework_tower_verdict": "missing_actionable_tower_spectrum",
            "claimable_exclusion": False,
        }

    prediction = normalized["tower_prediction"]
    phi = float(prediction["phi_tower_mean"])
    sigma = max(float(prediction["phi_tower_sigma"]), 0.0)
    lower = phi - 2.0 * sigma
    upper = phi + 2.0 * sigma
    critical = _critical_phi(model)["critical_phi"]
    tower_allowed_at_mean = bool(model.observables(phi)["satisfied"])

    if critical is None:
        verdict = "critical_phi_unavailable"
        claimable = False
    elif ref_ok and lower > critical:
        verdict = "tower_excluded_by_predictive_spectrum"
        claimable = True
    elif ref_ok and upper <= critical:
        verdict = "tower_allowed_by_predictive_spectrum"
        claimable = False
    elif ref_ok:
        verdict = "tower_prediction_overlaps_threshold"
        claimable = False
    else:
        verdict = "reference_excluded_before_tower_prediction"
        claimable = False

    return {
        **base,
        "two_sigma_phi_interval": [lower, upper],
        "critical_phi_tower": critical,
        "tower_allowed_at_mean": tower_allowed_at_mean,
        "framework_tower_verdict": verdict,
        "claimable_exclusion": claimable,
    }


def _evaluate_framework_spectra(
    spectra: dict[str, Any] | None,
    model: ExplicitTowerModel,
) -> dict[str, dict]:
    reference = _framework_reference_verdicts()
    rows = {}
    for name, framework in FRAMEWORKS.items():
        raw = (
            _spectrum_to_dict(spectra.get(name))
            if spectra
            else _native_spectrum(framework)
        )
        normalized = _normalize_prediction(name, raw, model)
        rows[name] = _prediction_verdict(name, normalized, reference, model)
    return rows


def diagnose_tower_spectrum_readiness(
    spectra: dict[str, Any] | None = None,
) -> dict:
    model = ExplicitTowerModel(lambda_eft=0.65)
    rows = _evaluate_framework_spectra(spectra, model)
    reference_feasible = [
        name for name, row in rows.items() if row["reference_feasible"]
    ]
    present = [name for name, row in rows.items() if row["prediction_present"]]
    actionable = [name for name, row in rows.items() if row["actionable"]]
    claimable = [
        name for name, row in rows.items() if row["claimable_exclusion"]
    ]

    return {
        "basis": ["framework", "tower_spectrum", "phi_tower", "Lambda_species"],
        "model": model.__dict__,
        "critical_phi_tower": _critical_phi(model)["critical_phi"],
        "required_actionable_fields": list(REQUIRED_ACTIONABLE_FIELDS),
        "adapter_contract": {
            "tower_family": "string label such as KK, string_oscillator, species, or model_specific",
            "phi_tower_mean": "dimensionless tower coordinate in the v2.20 normalization",
            "phi_tower_sigma": "one-sigma uncertainty in the same normalization",
            "tower_mass_gap": "optional mass-gap input; converted to phi_tower if phi is absent",
            "normalization": "how the framework maps its physical scale into m0/lambda_tower units",
            "source": "literature, data product, or generator that justifies the spectrum",
        },
        "reference_feasible_frameworks": reference_feasible,
        "native_prediction_frameworks": present if spectra is None else [],
        "n_native_prediction_frameworks": len(present) if spectra is None else 0,
        "actionable_prediction_frameworks": actionable,
        "n_actionable_prediction_frameworks": len(actionable),
        "claimable_framework_exclusions": claimable,
        "frameworks": rows,
        "literature_guardrail": {
            "claim": (
                "This is a tower-spectrum readiness audit, not a quantum-gravity "
                "solution. Default missing spectra are wiring gaps; only an "
                "actionable, sourced, normalized framework prediction can create "
                "a claimable tower exclusion."
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
            "The current framework encoders produce Wilson coefficients but not "
            "tower spectra. v2.24 therefore blocks framework-level tower claims "
            "until a framework supplies the adapter contract above."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="experiments/results/v2.24/tower_spectrum_readiness.json")
    args = parser.parse_args()

    result = diagnose_tower_spectrum_readiness()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
