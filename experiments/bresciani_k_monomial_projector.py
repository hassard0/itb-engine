"""Project spinor-helicity K monomials onto Bresciani K components."""

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


VERSION = "v2.143"
TOLERANCE = 1e-12

K_PLUS_MONOMIALS = (
    "angle12^4_square34^4",
    "angle14^4_square23^4",
    "angle34^4_square12^4",
)
K_MINUS_MONOMIALS = (
    "angle12^4_angle34^4",
    "angle13^4_angle24^4",
    "angle14^4_angle23^4",
)
K_MINUS_CONJUGATE_MONOMIALS = (
    "square12^4_square34^4",
    "square13^4_square24^4",
    "square14^4_square23^4",
)


def bresciani_monomial_families() -> dict[str, list[str]]:
    return {
        "K_plus": list(K_PLUS_MONOMIALS),
        "K_minus": list(K_MINUS_MONOMIALS),
        "K_minus_conjugate": list(K_MINUS_CONJUGATE_MONOMIALS),
    }


def _complex_or_none(value: Any) -> complex | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return complex(float(value), 0.0)
    if isinstance(value, dict):
        real = value.get("real", 0.0)
        imag = value.get("imag", 0.0)
        if isinstance(real, bool) or isinstance(imag, bool):
            return None
        if isinstance(real, int | float) and isinstance(imag, int | float):
            return complex(float(real), float(imag))
    return None


def _json_complex(value: complex) -> dict[str, float]:
    return {
        "real": float(value.real),
        "imag": float(value.imag),
    }


def _family_projection(
    coefficients: dict[str, Any],
    monomials: tuple[str, ...],
) -> dict[str, Any]:
    values: list[complex] = []
    missing: list[str] = []
    nonnumeric: list[str] = []
    for monomial in monomials:
        if monomial not in coefficients:
            missing.append(monomial)
            continue
        value = _complex_or_none(coefficients[monomial])
        if value is None:
            nonnumeric.append(monomial)
            continue
        values.append(value)

    common = None
    equal = False
    if len(values) == len(monomials):
        common = sum(values) / len(values)
        equal = all(abs(value - common) <= TOLERANCE for value in values)
    return {
        "monomials": list(monomials),
        "missing": missing,
        "nonnumeric": nonnumeric,
        "values": [_json_complex(value) for value in values],
        "common_coefficient": _json_complex(common) if common is not None else None,
        "equal_within_tolerance": equal,
    }


def project_bresciani_k_components(packet: dict[str, Any]) -> dict[str, Any]:
    coefficients = packet.get("monomial_coefficients")
    if not isinstance(coefficients, dict):
        coefficients = {}

    plus = _family_projection(coefficients, K_PLUS_MONOMIALS)
    minus = _family_projection(coefficients, K_MINUS_MONOMIALS)
    minus_conjugate = _family_projection(coefficients, K_MINUS_CONJUGATE_MONOMIALS)

    blockers: set[str] = set()
    for label, row in {
        "K_plus": plus,
        "K_minus": minus,
        "K_minus_conjugate": minus_conjugate,
    }.items():
        if row["missing"]:
            blockers.add(f"{label}_monomials_missing")
        if row["nonnumeric"]:
            blockers.add(f"{label}_monomials_nonnumeric")
        if not row["equal_within_tolerance"]:
            blockers.add(f"{label}_coefficients_not_family_symmetric")

    k_plus_value = None
    k_minus_value = None
    k_minus_conj_value = None
    if plus["common_coefficient"] is not None:
        k_plus_value = complex(
            plus["common_coefficient"]["real"],
            plus["common_coefficient"]["imag"],
        )
        if abs(k_plus_value.imag) > TOLERANCE:
            blockers.add("K_plus_not_real")
    if minus["common_coefficient"] is not None:
        k_minus_value = complex(
            minus["common_coefficient"]["real"],
            minus["common_coefficient"]["imag"],
        )
    if minus_conjugate["common_coefficient"] is not None:
        k_minus_conj_value = complex(
            minus_conjugate["common_coefficient"]["real"],
            minus_conjugate["common_coefficient"]["imag"],
        )
    if k_minus_value is not None and k_minus_conj_value is not None:
        if abs(k_minus_conj_value - k_minus_value.conjugate()) > TOLERANCE:
            blockers.add("K_minus_conjugate_inconsistent")

    normalization = packet.get("normalization")
    overall = None
    if isinstance(normalization, dict):
        overall = _complex_or_none(normalization.get("overall_R4_factor"))
    if overall is None or abs(overall.imag) > TOLERANCE:
        blockers.add("overall_R4_factor_missing_or_not_real")
    if packet.get("source_backed_derivation") is not True:
        blockers.add("source_backed_derivation_missing")

    derived = None
    if not blockers:
        assert k_plus_value is not None
        assert k_minus_value is not None
        assert overall is not None
        derived = derive_bresciani_from_source_projection(
            overall_r4_factor=float(overall.real),
            k_plus=float(k_plus_value.real),
            k_minus_real=float(k_minus_value.real),
            k_minus_imag=float(k_minus_value.imag),
        )
        if not derived["positivity_summary"]["passed"]:
            blockers.add("bresciani_positivity_failed")

    return canonicalize_json_floats({
        "label": packet.get("label", "unnamed_bresciani_k_monomial_packet"),
        "families": {
            "K_plus": plus,
            "K_minus": minus,
            "K_minus_conjugate": minus_conjugate,
        },
        "projected_components": {
            "K_plus": _json_complex(k_plus_value) if k_plus_value is not None else None,
            "K_minus": _json_complex(k_minus_value) if k_minus_value is not None else None,
            "K_minus_conjugate": (
                _json_complex(k_minus_conj_value)
                if k_minus_conj_value is not None
                else None
            ),
            "overall_R4_factor": (
                float(overall.real)
                if overall is not None and abs(overall.imag) <= TOLERANCE
                else None
            ),
        },
        "derived_bresciani_projection": derived,
        "ready_for_k_factor_projection": not blockers,
        "blockers": sorted(blockers),
    })


def synthetic_monomial_packet(*, source_backed: bool = False) -> dict[str, Any]:
    coefficients: dict[str, Any] = {}
    for monomial in K_PLUS_MONOMIALS:
        coefficients[monomial] = 0.3
    for monomial in K_MINUS_MONOMIALS:
        coefficients[monomial] = {"real": 0.1, "imag": 0.05}
    for monomial in K_MINUS_CONJUGATE_MONOMIALS:
        coefficients[monomial] = {"real": 0.1, "imag": -0.05}
    return {
        "label": "synthetic_bresciani_k_monomial_control",
        "source_urls": ["https://arxiv.org/abs/2504.12855"],
        "monomial_coefficients": coefficients,
        "normalization": {
            "overall_R4_factor": 8.0,
            "status": "synthetic_unit_normalization",
        },
        "source_backed_derivation": source_backed,
    }


def malformed_monomial_packet() -> dict[str, Any]:
    packet = synthetic_monomial_packet(source_backed=True)
    packet["label"] = "malformed_bresciani_k_monomial_packet"
    packet["monomial_coefficients"]["angle13^4_angle24^4"] = {
        "real": 0.2,
        "imag": 0.05,
    }
    packet["monomial_coefficients"]["square14^4_square23^4"] = {
        "real": 0.1,
        "imag": 0.05,
    }
    return packet


def diagnose_bresciani_k_monomial_projector() -> dict[str, Any]:
    evaluations = {
        "synthetic_control": project_bresciani_k_components(
            synthetic_monomial_packet(source_backed=False)
        ),
        "source_backed_shape_control": project_bresciani_k_components(
            synthetic_monomial_packet(source_backed=True)
        ),
        "malformed_shape_control": project_bresciani_k_components(
            malformed_monomial_packet()
        ),
    }
    ready_packets = [
        label for label, row in evaluations.items()
        if row["ready_for_k_factor_projection"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in evaluations.values():
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.142_polarization_k_factor_rederivation_route",
            "v2.139_four_dimensional_r4_projection_derivation_workbench",
            "Bresciani_eq_amplitude_monomial_families",
        ],
        "tolerance": TOLERANCE,
        "bresciani_monomial_families": bresciani_monomial_families(),
        "evaluations": evaluations,
        "ready_k_factor_projection_packets": ready_packets,
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "claimable_framework_exclusions_now": [],
        "route_status": "bresciani_k_monomial_projector_ready_no_source_formula",
        "selected_next_build_action": (
            "fill_projector_with_source_backed_k_monomial_coefficients"
        ),
        "best_next_artifact": (
            "A source-backed monomial coefficient packet from Gross-Witten "
            "OCR/library access or an independent polarization derivation."
        ),
        "interpretation": (
            "The mechanical K projection is now implemented. Given source-backed "
            "coefficients for the Bresciani monomial families, it extracts "
            "K_plus and complex K_minus, checks symmetry and conjugacy, then "
            "feeds the v2.139 Bresciani inversion. The only ready packet is a "
            "source-backed shape control, not a physics claim."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.143/"
            "bresciani_k_monomial_projector.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_bresciani_k_monomial_projector()
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
