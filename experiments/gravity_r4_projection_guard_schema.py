"""R4 framework projection guard and schema (v2.133)."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gravity_r4_axis_extension_candidate import candidate_equations
from experiments.gravity_r4_framework_projection_requirements import (
    REQUIRED_R4_COEFFICIENTS,
    R4_METADATA_KEYS,
    diagnose_gravity_r4_framework_projection_requirements,
    r4_framework_projection_schema,
)
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from itb.predict import FRAMEWORKS
from itb.scope import engine_validity


VERSION = "v2.133"

REQUIRED_R4_PROJECTION_FIELDS = (
    "framework",
    "axis_family",
    "source_url",
    "source_type",
    "source_version",
    "adapter_kind",
    "basis",
    "coefficients",
    "derived",
    "normalization",
    "operator_projection_matrix",
    "valid_energy_domain",
    "uncertainty_or_covariance",
    "ownership_metadata",
    "unitarity_bound",
    "positivity_status",
    "discriminator_math",
)

VALID_SOURCE_TYPES = {
    "primary_literature",
    "computed_framework_projection",
    "validated_measurement",
}
VALID_NORMALIZATION_STATUSES = {
    "source_backed_cutoff",
    "engine_lambda_r4_defined",
}
VALID_UNCERTAINTY_STATUSES = {
    "public_covariance_matrix",
    "public_likelihood_samples",
    "bounded_systematic_envelope",
}
LIKELIHOOD_STATUSES = {
    "public_engine_usable",
    "public_covariance_matrix",
    "public_likelihood_samples",
}
OWNERSHIP_MARKERS = (
    "framework_owned_derivation",
    "native_framework_r4_projection",
    "source_owned_by_framework",
)
DERIVED_TOLERANCE = 1e-9


def _is_missing(value: Any) -> bool:
    return value in (None, "", {}, [], ())


def _status_value(value: Any) -> str:
    if isinstance(value, dict):
        status = value.get("status")
        return str(status) if status is not None else ""
    return str(value) if value is not None else ""


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _truthy_marker_present(value: Any, markers: tuple[str, ...]) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key).lower()
            if any(marker in key_text for marker in markers) and item not in (
                False,
                None,
                "",
                [],
                {},
                (),
            ):
                return True
            if _truthy_marker_present(item, markers):
                return True
    if isinstance(value, (list, tuple, set)):
        return any(_truthy_marker_present(item, markers) for item in value)
    return False


def _coefficient_summary(packet: dict[str, Any]) -> dict[str, Any]:
    coefficients = packet.get("coefficients")
    if not isinstance(coefficients, dict):
        return {
            "coefficient_values": {},
            "missing_or_nonnumeric": list(REQUIRED_R4_COEFFICIENTS),
            "positivity_passed": False,
            "positivity_residual": None,
        }

    values = {
        axis: _float_or_none(coefficients.get(axis))
        for axis in REQUIRED_R4_COEFFICIENTS
    }
    missing = [
        axis for axis, value in values.items()
        if value is None
    ]
    positivity_passed = False
    residual = None
    if not missing:
        c1 = values["g_R4_c1"]
        c2 = values["g_R4_c2"]
        c3 = values["g_R4_c3"]
        assert c1 is not None
        assert c2 is not None
        assert c3 is not None
        residual = float(4.0 * c1 * c2 - c3**2)
        positivity_passed = c1 >= 0.0 and c2 >= 0.0 and residual >= -DERIVED_TOLERANCE

    return {
        "coefficient_values": values,
        "missing_or_nonnumeric": missing,
        "positivity_passed": positivity_passed,
        "positivity_residual": residual,
    }


def _derived_summary(packet: dict[str, Any], coefficients: dict[str, Any]) -> dict[str, Any]:
    derived = packet.get("derived")
    if not isinstance(derived, dict):
        return {
            "missing_or_nonnumeric": ["g_R4_plus", "g_R4_minus_abs"],
            "expected": None,
            "provided": {},
            "consistent": False,
        }
    c1 = coefficients["coefficient_values"].get("g_R4_c1")
    c2 = coefficients["coefficient_values"].get("g_R4_c2")
    c3 = coefficients["coefficient_values"].get("g_R4_c3")
    plus = _float_or_none(derived.get("g_R4_plus"))
    minus_abs = _float_or_none(derived.get("g_R4_minus_abs"))
    missing = [
        axis for axis, value in {
            "g_R4_plus": plus,
            "g_R4_minus_abs": minus_abs,
        }.items()
        if value is None
    ]
    expected = None
    consistent = False
    if not missing and None not in (c1, c2, c3):
        expected_plus = float(c1 + c2)
        expected_minus_abs = float(math.hypot(c1 - c2, c3))
        expected = {
            "g_R4_plus": expected_plus,
            "g_R4_minus_abs": expected_minus_abs,
        }
        consistent = (
            abs(plus - expected_plus) <= DERIVED_TOLERANCE
            and abs(minus_abs - expected_minus_abs) <= DERIVED_TOLERANCE
        )
    return {
        "missing_or_nonnumeric": missing,
        "expected": expected,
        "provided": {
            "g_R4_plus": plus,
            "g_R4_minus_abs": minus_abs,
        },
        "consistent": consistent,
    }


def _dict_status_summary(packet: dict[str, Any], field: str, valid: set[str]) -> dict[str, Any]:
    value = packet.get(field)
    status = _status_value(value)
    return {
        "present": isinstance(value, dict) and bool(value),
        "status": status,
        "status_valid": status in valid,
    }


def _axes_cover_required(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    axes = value.get("axes") or value.get("dimensions") or []
    return set(REQUIRED_R4_COEFFICIENTS).issubset(set(axes))


def evaluate_r4_projection_packet(packet: dict[str, Any]) -> dict[str, Any]:
    missing = [
        field for field in REQUIRED_R4_PROJECTION_FIELDS
        if _is_missing(packet.get(field))
    ]
    projection_blockers: set[str] = set()
    claim_blockers: set[str] = set()
    if missing:
        projection_blockers.add("missing_required_fields")

    framework = packet.get("framework")
    framework_registered = framework in FRAMEWORKS
    if not framework_registered:
        projection_blockers.add("framework_not_registered")
        scope_summary = {
            "in_scope": False,
            "violations": ["framework_not_registered"],
            "note": "framework is not registered in itb.predict.FRAMEWORKS",
        }
    else:
        scope = engine_validity(FRAMEWORKS[framework])
        scope_summary = {
            "in_scope": scope.in_scope,
            "violations": scope.violations,
            "note": scope.note,
        }
        if not scope.in_scope:
            projection_blockers.add("framework_outside_current_r4_gate")

    if packet.get("axis_family") != "gravity_R4_Riemann4":
        projection_blockers.add("axis_family_not_gravity_r4_riemann4")
    if packet.get("adapter_kind") != "framework_native_r4_projection":
        projection_blockers.add("adapter_kind_not_framework_native_r4_projection")
    if packet.get("basis") != "Bresciani_c_i_spin2_Riemann4":
        projection_blockers.add("basis_not_bresciani_spin2_riemann4")

    source_url = str(packet.get("source_url") or "")
    source_url_valid = source_url.startswith(("https://arxiv.org/", "https://doi.org/"))
    if source_url and not source_url_valid:
        projection_blockers.add("source_url_not_primary_allowed")
    if packet.get("source_type") not in VALID_SOURCE_TYPES:
        projection_blockers.add("source_type_not_allowed")

    coefficients = _coefficient_summary(packet)
    if coefficients["missing_or_nonnumeric"]:
        projection_blockers.add("r4_coefficients_missing_or_nonnumeric")
    elif not coefficients["positivity_passed"]:
        projection_blockers.add("r4_source_positivity_failed")

    derived = _derived_summary(packet, coefficients)
    if derived["missing_or_nonnumeric"]:
        projection_blockers.add("r4_derived_coordinates_missing_or_nonnumeric")
    elif not derived["consistent"]:
        projection_blockers.add("r4_derived_coordinates_inconsistent")

    normalization = _dict_status_summary(
        packet,
        "normalization",
        VALID_NORMALIZATION_STATUSES,
    )
    if not normalization["present"] or not normalization["status_valid"]:
        projection_blockers.add("r4_normalization_not_source_backed")

    operator_projection = _dict_status_summary(
        packet,
        "operator_projection_matrix",
        {"source_backed"},
    )
    if not operator_projection["present"] or not operator_projection["status_valid"]:
        projection_blockers.add("r4_operator_projection_matrix_not_source_backed")

    domain = _dict_status_summary(
        packet,
        "valid_energy_domain",
        {"bounded_for_qg_eft"},
    )
    if not domain["present"] or not domain["status_valid"]:
        projection_blockers.add("r4_valid_energy_domain_not_bounded")

    uncertainty = _dict_status_summary(
        packet,
        "uncertainty_or_covariance",
        VALID_UNCERTAINTY_STATUSES,
    )
    uncertainty_axes_ready = _axes_cover_required(
        packet.get("uncertainty_or_covariance")
    )
    if (
        not uncertainty["present"]
        or not uncertainty["status_valid"]
        or not uncertainty_axes_ready
    ):
        projection_blockers.add("r4_uncertainty_or_covariance_incomplete")

    ownership = packet.get("ownership_metadata")
    source_owned = _truthy_marker_present(ownership, OWNERSHIP_MARKERS)
    if not source_owned:
        projection_blockers.add("r4_framework_source_ownership_missing")

    unitarity = _dict_status_summary(packet, "unitarity_bound", {"source_backed"})
    uses_spin2_bound = bool(
        isinstance(packet.get("unitarity_bound"), dict)
        and packet["unitarity_bound"].get("uses_bresciani_spin2_bound") is True
    )
    if not unitarity["present"] or not unitarity["status_valid"] or not uses_spin2_bound:
        projection_blockers.add("r4_unitarity_bound_not_source_backed")

    if _status_value(packet.get("positivity_status")) not in {"checked", "source_backed"}:
        projection_blockers.add("r4_positivity_status_not_checked")
    if packet.get("synthetic_fixture") is True:
        projection_blockers.add("synthetic_fixture_not_real_source")

    likelihood = _dict_status_summary(
        packet,
        "measurement_likelihood",
        LIKELIHOOD_STATUSES,
    )
    likelihood_axes_ready = _axes_cover_required(packet.get("measurement_likelihood"))
    if not likelihood["present"] or not likelihood["status_valid"] or not likelihood_axes_ready:
        claim_blockers.add("measurement_likelihood_missing_or_incomplete")
    if packet.get("discriminator_math") != "excludes_registered_framework":
        claim_blockers.add("discriminator_math_not_excluding")

    claim_blockers.update(projection_blockers)
    return canonicalize_json_floats({
        "framework": framework,
        "framework_registered": framework_registered,
        "engine_scope": scope_summary,
        "missing_required_fields": sorted(set(missing)),
        "source_url_valid": source_url_valid,
        "source_type_valid": packet.get("source_type") in VALID_SOURCE_TYPES,
        "coefficient_summary": coefficients,
        "derived_summary": derived,
        "normalization_summary": normalization,
        "operator_projection_summary": operator_projection,
        "energy_domain_summary": domain,
        "uncertainty_summary": {
            **uncertainty,
            "axes_cover_required": uncertainty_axes_ready,
        },
        "ownership_summary": {
            "framework_source_owned": source_owned,
        },
        "unitarity_summary": {
            **unitarity,
            "uses_bresciani_spin2_bound": uses_spin2_bound,
        },
        "likelihood_summary": {
            **likelihood,
            "axes_cover_required": likelihood_axes_ready,
        },
        "ready_for_framework_projection": not projection_blockers,
        "ready_for_framework_claim": not claim_blockers,
        "projection_blockers": sorted(projection_blockers),
        "claim_blockers": sorted(claim_blockers),
    })


def _current_framework_packet(name: str) -> dict[str, Any]:
    return {
        "framework": name,
        "axis_family": "gravity_R4_Riemann4",
        "source_url": "",
        "source_type": "",
        "source_version": "",
        "adapter_kind": "framework_native_r4_projection",
        "basis": "Bresciani_c_i_spin2_Riemann4",
        "coefficients": {},
        "derived": {},
        "normalization": {},
        "operator_projection_matrix": {},
        "valid_energy_domain": {},
        "uncertainty_or_covariance": {},
        "ownership_metadata": {},
        "unitarity_bound": {},
        "positivity_status": "not_checked",
        "discriminator_math": "projection_only",
    }


def diagnose_gravity_r4_projection_guard_schema() -> dict[str, Any]:
    requirements = diagnose_gravity_r4_framework_projection_requirements()
    guard_rows = {
        name: evaluate_r4_projection_packet(_current_framework_packet(name))
        for name in FRAMEWORKS
    }
    ready_projection = [
        name for name, row in guard_rows.items()
        if row["ready_for_framework_projection"]
    ]
    ready_claim = [
        name for name, row in guard_rows.items()
        if row["ready_for_framework_claim"]
    ]
    blocker_counts = {
        blocker: sum(
            1 for row in guard_rows.values()
            if blocker in row["projection_blockers"]
        )
        for blocker in sorted({
            blocker
            for row in guard_rows.values()
            for blocker in row["projection_blockers"]
        })
    }
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.132_gravity_r4_framework_projection_requirements",
            "Bresciani_Levati_Paradisi_arXiv_2504_12855_v2",
            "registered_FRAMEWORKS_from_itb.predict",
        ],
        "source_equations": candidate_equations(),
        "r4_framework_projection_schema": r4_framework_projection_schema(),
        "required_packet_fields": list(REQUIRED_R4_PROJECTION_FIELDS),
        "required_metadata_keys": list(R4_METADATA_KEYS),
        "registered_framework_count": requirements["registered_framework_count"],
        "ready_framework_projection_packets": ready_projection,
        "claim_ready_framework_packets": ready_claim,
        "projection_blocker_counts": blocker_counts,
        "current_framework_guard_results": guard_rows,
        "claimable_framework_exclusions_now": [],
        "route_status": "r4_projection_guard_schema_ready_no_current_adapter",
        "selected_next_build_action": "search_string_r4_basis_translation_source",
        "best_next_artifact": (
            "A source-backed string R4 basis translation audit, because "
            "string_tree_eft is the highest-priority candidate from v2.132 "
            "and the new guard can now reject incomplete adapters."
        ),
        "interpretation": (
            "The guard is executable and rejects every current framework "
            "projection packet because no encoder supplies R4 coefficients, "
            "Bresciani derived coordinates, source metadata, normalization, "
            "uncertainty, or ownership. It can accept future complete "
            "projection packets without making a framework claim unless a "
            "measurement likelihood and excluding discriminator math are also "
            "present."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.133/"
            "gravity_r4_projection_guard_schema.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gravity_r4_projection_guard_schema()
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
