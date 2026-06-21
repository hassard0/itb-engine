"""Contract for mapping ParSpec qEFT length scale onto engine R4 axes."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_lalsuite_waveform_likelihood_posterior import AXES
from experiments.r4_parspec_ringdown_source_bridge import (
    CURRENT_V2187_EVENT,
    DEFAULT_OUT as DEFAULT_V2188_PATH,
    PARSPEC_DOI,
    PARSPEC_SOURCE_URL,
    SOURCE_EVENTS,
    load_json,
)


VERSION = "v2.190"
DEFAULT_OUT = Path(
    "experiments/results/v2.190/r4_parspec_engine_axis_map_contract.json"
)
SOURCE_AXIS = "ell_qEFT"
SOURCE_AXIS_WITH_UNIT = "ell_qEFT_km"
SOURCE_AXIS_UNITS = "km"
REQUIRED_PACKET_FIELDS = (
    "packet_id",
    "source_url",
    "source_doi",
    "source_type",
    "source_theory_family",
    "source_axis",
    "source_axis_units",
    "target_engine_axes",
    "source_axis_power_policy",
    "operator_basis_map",
    "engine_axis_map",
    "axis_normalization",
    "likelihood_reference",
    "event_set_policy",
    "systematics",
    "claim_controls",
)
VALID_SOURCE_TYPES = {
    "unit_test_control",
    "source_backed_parspec_qeft_axis_map",
}
VALID_LIKELIHOOD_STATUSES = {
    "public_covariance_matrix",
    "public_likelihood_samples",
    "public_log_likelihood_grid",
}
MAP_BLOCKERS = (
    "source_axis_power_policy_missing",
    "operator_basis_map_missing",
    "engine_axis_orientation_missing",
    "axis_normalization_missing",
)
ATTACHMENT_BLOCKERS = (
    "public_parspec_qeft_likelihood_or_posterior_samples_missing",
    "event_set_mismatch_gw170608_vs_gw150914_gw200129",
    "calibration_and_waveform_systematics_not_exported",
)


def parspec_engine_axis_map_contract() -> dict[str, Any]:
    return {
        "version": VERSION,
        "contract_id": "parspec_qeft_to_engine_r4_axis_map_contract_v1",
        "source_axis": SOURCE_AXIS_WITH_UNIT,
        "target_engine_axes": list(AXES),
        "required_packet_fields": list(REQUIRED_PACKET_FIELDS),
        "valid_source_types": sorted(VALID_SOURCE_TYPES),
        "valid_likelihood_statuses": sorted(VALID_LIKELIHOOD_STATUSES),
        "claim_rule": (
            "A ParSpec qEFT length-scale posterior can touch engine R4 "
            "likelihood logic only after a source-backed length-power policy, "
            "operator-basis map, engine-axis orientation, absolute or "
            "equivalent normalization, public likelihood object, event-set "
            "policy, and systematics export are all present. Framework claims "
            "remain disabled until adversarial review."
        ),
    }


def synthetic_ready_parspec_engine_axis_map_packet() -> dict[str, Any]:
    """Complete positive control; not evidence for the real qEFT map."""

    return {
        "packet_id": "synthetic_parspec_qeft_to_engine_r4_axis_map_v1",
        "source_url": PARSPEC_SOURCE_URL,
        "source_doi": PARSPEC_DOI,
        "source_type": "unit_test_control",
        "source_theory_family": (
            "quartic_order_effective_field_theory_of_general_relativity"
        ),
        "source_axis": SOURCE_AXIS,
        "source_axis_units": SOURCE_AXIS_UNITS,
        "target_engine_axes": list(AXES),
        "source_axis_power_policy": {
            "status": "source_backed",
            "length_axis": SOURCE_AXIS_WITH_UNIT,
            "length_power_declared": True,
            "length_power": 4,
            "power_scope": "synthetic_contract_control_not_source_claim",
        },
        "operator_basis_map": {
            "status": "source_backed",
            "source_operator_family": "quartic_eft_ringdown",
            "target_basis": "bresciani_r4_axis_dictionary_v1",
            "field_redefinition_policy": "closed_for_packet",
            "target_axes": list(AXES),
        },
        "engine_axis_map": {
            "status": "ready",
            "map_kind": "length_power_to_engine_axis_vector",
            "source_axis": SOURCE_AXIS_WITH_UNIT,
            "target_axes": list(AXES),
            "axis_vector": {
                "g_R4_c1": "A_qeft_c1 * ell_qEFT_km^4 / Lambda_R4^8",
                "g_R4_c2": "A_qeft_c2 * ell_qEFT_km^4 / Lambda_R4^8",
                "g_R4_c3": "A_qeft_c3 * ell_qEFT_km^4 / Lambda_R4^8",
            },
            "jacobian_available": True,
            "covariance_pushforward_available": True,
        },
        "axis_normalization": {
            "status": "source_backed",
            "normalization_scope": "absolute_length_to_engine_r4_axes",
            "uses_numeric_lambda_r4_scale_or_equivalent": True,
            "unit_conversion": "km_to_engine_R4_axis_units",
            "normalization_uncertainty_exported": True,
        },
        "likelihood_reference": {
            "status": "public_covariance_matrix",
            "source_axis": SOURCE_AXIS_WITH_UNIT,
            "events": list(SOURCE_EVENTS),
            "covariance": [[1.0]],
            "posterior_or_likelihood_exported": True,
        },
        "event_set_policy": {
            "status": "aligned",
            "source_events": list(SOURCE_EVENTS),
            "engine_events": list(SOURCE_EVENTS),
            "same_event_set": True,
        },
        "systematics": {
            "status": "engine_export_ready",
            "items": [
                "waveform_systematics_budget",
                "calibration_prior",
                "event_selection_policy",
                "eft_validity_domain",
            ],
        },
        "claim_controls": {
            "claim_use_allowed": False,
            "framework_claim_allowed": False,
            "external_adversarial_review_complete": False,
            "synthetic_control_not_claim_evidence": True,
        },
    }


def current_v2188_parspec_axis_map_slot(
    path: str | Path = DEFAULT_V2188_PATH,
) -> dict[str, Any]:
    bridge = load_json(path)["bridge_packet"]
    return {
        "packet_id": "current_v2188_parspec_qeft_axis_map_slot",
        "source_url": bridge["source_url"],
        "source_doi": bridge["source_doi"],
        "source_type": "source_backed_parspec_qeft_axis_map",
        "source_theory_family": bridge["theory_family"],
        "source_axis": SOURCE_AXIS,
        "source_axis_units": SOURCE_AXIS_UNITS,
        "target_engine_axes": list(AXES),
        "source_axis_power_policy": {},
        "operator_basis_map": {},
        "engine_axis_map": bridge["axis_map_to_engine_r4"],
        "axis_normalization": {},
        "likelihood_reference": bridge["source_likelihood_or_posterior"],
        "event_set_policy": {
            "status": "mismatch",
            "source_events": bridge["event_bridge"]["source_events"],
            "engine_events": [CURRENT_V2187_EVENT],
            "same_event_set": False,
        },
        "systematics": bridge["systematics"],
        "claim_controls": bridge["claim_controls"],
    }


def malformed_parspec_engine_axis_map_packet() -> dict[str, Any]:
    packet = synthetic_ready_parspec_engine_axis_map_packet()
    packet["source_url"] = "https://example.invalid/not-parspec"
    packet["source_axis_units"] = "meters"
    packet["target_engine_axes"] = ["g_R4_c1"]
    packet["engine_axis_map"]["axis_vector"].pop("g_R4_c3")
    packet["claim_controls"]["claim_use_allowed"] = True
    return packet


def _missing(value: Any) -> bool:
    return value in (None, "", [], {}, ())


def _finite_positive(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if not isinstance(value, int | float):
        return False
    numeric = float(value)
    return math.isfinite(numeric) and numeric > 0.0


def _axis_component_ready(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, bool):
        return False
    if isinstance(value, int | float):
        return math.isfinite(float(value))
    return False


def _valid_covariance(value: Any) -> bool:
    if not isinstance(value, list) or len(value) != 1:
        return False
    row = value[0]
    if not isinstance(row, list) or len(row) != 1:
        return False
    return _finite_positive(row[0])


def evaluate_parspec_engine_axis_map_packet(
    packet: dict[str, Any],
) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_PACKET_FIELDS
        if _missing(packet.get(field))
    ]
    blockers: set[str] = set(missing_fields)

    if packet.get("source_url") != PARSPEC_SOURCE_URL:
        blockers.add("parspec_primary_source_url_missing")
    if packet.get("source_doi") != PARSPEC_DOI:
        blockers.add("parspec_published_doi_missing")
    if packet.get("source_type") not in VALID_SOURCE_TYPES:
        blockers.add("source_type_not_allowed")
    if packet.get("source_theory_family") != (
        "quartic_order_effective_field_theory_of_general_relativity"
    ):
        blockers.add("source_theory_family_not_quartic_eft")
    if packet.get("source_axis") != SOURCE_AXIS:
        blockers.add("source_axis_not_ell_qeft")
    if packet.get("source_axis_units") != SOURCE_AXIS_UNITS:
        blockers.add("source_axis_units_not_km")
    if set(packet.get("target_engine_axes") or []) != set(AXES):
        blockers.add("target_engine_axes_mismatch")

    power = packet.get("source_axis_power_policy")
    if not isinstance(power, dict) or _missing(power):
        blockers.add("source_axis_power_policy_missing")
    else:
        if power.get("status") != "source_backed":
            blockers.add("source_axis_power_policy_not_source_backed")
        if power.get("length_axis") != SOURCE_AXIS_WITH_UNIT:
            blockers.add("source_axis_power_axis_mismatch")
        if power.get("length_power_declared") is not True:
            blockers.add("source_axis_power_not_declared")
        if not _finite_positive(power.get("length_power")):
            blockers.add("source_axis_power_value_missing")

    basis = packet.get("operator_basis_map")
    if not isinstance(basis, dict) or _missing(basis):
        blockers.add("operator_basis_map_missing")
    else:
        if basis.get("status") != "source_backed":
            blockers.add("operator_basis_map_not_source_backed")
        if basis.get("target_basis") != "bresciani_r4_axis_dictionary_v1":
            blockers.add("operator_basis_target_not_bresciani_r4")
        if basis.get("field_redefinition_policy") != "closed_for_packet":
            blockers.add("operator_basis_field_redefinition_not_closed")
        if set(basis.get("target_axes") or []) != set(AXES):
            blockers.add("operator_basis_target_axes_mismatch")

    axis_map = packet.get("engine_axis_map")
    if not isinstance(axis_map, dict) or _missing(axis_map):
        blockers.add("engine_axis_orientation_missing")
    else:
        if axis_map.get("status") != "ready":
            blockers.add("engine_axis_orientation_missing")
            blockers.add("engine_axis_map_not_ready")
        if axis_map.get("source_axis") != SOURCE_AXIS_WITH_UNIT:
            blockers.add("engine_axis_map_source_axis_mismatch")
        if set(axis_map.get("target_axes") or []) != set(AXES):
            blockers.add("engine_axis_map_target_axes_mismatch")
        vector = axis_map.get("axis_vector")
        if not isinstance(vector, dict):
            blockers.add("engine_axis_orientation_missing")
            blockers.add("engine_axis_vector_missing")
        else:
            missing_axes = [axis for axis in AXES if axis not in vector]
            if missing_axes:
                blockers.add("engine_axis_vector_incomplete")
            if any(not _axis_component_ready(vector.get(axis)) for axis in AXES):
                blockers.add("engine_axis_vector_components_not_ready")
        if axis_map.get("jacobian_available") is not True:
            blockers.add("engine_axis_map_jacobian_missing")
        if axis_map.get("covariance_pushforward_available") is not True:
            blockers.add("engine_axis_map_covariance_pushforward_missing")

    normalization = packet.get("axis_normalization")
    if not isinstance(normalization, dict) or _missing(normalization):
        blockers.add("axis_normalization_missing")
    else:
        if normalization.get("status") != "source_backed":
            blockers.add("axis_normalization_not_source_backed")
        if normalization.get("normalization_scope") != (
            "absolute_length_to_engine_r4_axes"
        ):
            blockers.add("axis_normalization_scope_not_absolute")
        if normalization.get("uses_numeric_lambda_r4_scale_or_equivalent") is not True:
            blockers.add("numeric_lambda_r4_or_equivalent_normalization_missing")
        if normalization.get("normalization_uncertainty_exported") is not True:
            blockers.add("axis_normalization_uncertainty_missing")

    likelihood = packet.get("likelihood_reference")
    if not isinstance(likelihood, dict) or _missing(likelihood):
        blockers.add("public_parspec_qeft_likelihood_or_posterior_samples_missing")
    else:
        if likelihood.get("status") not in VALID_LIKELIHOOD_STATUSES:
            blockers.add("public_parspec_qeft_likelihood_or_posterior_samples_missing")
        if likelihood.get("source_axis") not in {SOURCE_AXIS, SOURCE_AXIS_WITH_UNIT}:
            blockers.add("parspec_likelihood_source_axis_mismatch")
        if likelihood.get("status") == "public_covariance_matrix":
            if not _valid_covariance(likelihood.get("covariance")):
                blockers.add("parspec_likelihood_covariance_invalid")
        if likelihood.get("posterior_or_likelihood_exported") is not True:
            blockers.add("parspec_likelihood_export_not_confirmed")

    events = packet.get("event_set_policy")
    if not isinstance(events, dict) or _missing(events):
        blockers.add("event_set_policy_missing")
    else:
        if events.get("same_event_set") is not True:
            blockers.add("event_set_mismatch_gw170608_vs_gw150914_gw200129")
        if not set(SOURCE_EVENTS).issubset(set(events.get("source_events") or [])):
            blockers.add("source_events_missing_from_event_policy")

    systematics = packet.get("systematics")
    if not isinstance(systematics, dict) or _missing(systematics):
        blockers.add("systematics_missing")
    elif systematics.get("status") != "engine_export_ready":
        blockers.add("calibration_and_waveform_systematics_not_exported")

    controls = packet.get("claim_controls")
    if not isinstance(controls, dict) or _missing(controls):
        blockers.add("claim_controls_missing")
    else:
        if controls.get("claim_use_allowed") is not False:
            blockers.add("claim_use_not_disabled")
        if controls.get("framework_claim_allowed") is not False:
            blockers.add("framework_claim_not_disabled")
        if controls.get("external_adversarial_review_complete") is True:
            blockers.add("external_review_unexpectedly_complete")

    map_blockers = sorted(set(MAP_BLOCKERS) & blockers)
    attachment_blockers = sorted(set(ATTACHMENT_BLOCKERS) & blockers)
    axis_map_ready = not map_blockers and not {
        blocker for blocker in blockers
        if blocker.startswith("engine_axis_")
        or blocker.startswith("operator_basis_")
        or blocker.startswith("source_axis_power")
        or blocker.startswith("axis_normalization")
        or blocker.startswith("numeric_lambda")
    }
    likelihood_attachment_ready = axis_map_ready and not attachment_blockers
    synthetic = bool(
        packet.get("claim_controls", {}).get("synthetic_control_not_claim_evidence")
    )
    claim_blockers = {
        "framework_claim_controls_disabled",
        "external_adversarial_review_missing",
    }
    if synthetic:
        claim_blockers.add("synthetic_control_not_claim_evidence")
    if not likelihood_attachment_ready:
        claim_blockers.add("parspec_engine_axis_likelihood_attachment_not_ready")

    return canonicalize_json_floats({
        "packet_id": packet.get("packet_id"),
        "source_bridge_ready": not (
            {
                "parspec_primary_source_url_missing",
                "parspec_published_doi_missing",
                "source_theory_family_not_quartic_eft",
                "source_axis_not_ell_qeft",
                "source_axis_units_not_km",
                "target_engine_axes_mismatch",
            }
            & blockers
        ),
        "axis_map_ready": axis_map_ready,
        "likelihood_attachment_ready": likelihood_attachment_ready,
        "ready_for_framework_claim": False,
        "synthetic_control": synthetic,
        "missing_required_fields": sorted(missing_fields),
        "map_blockers": map_blockers,
        "attachment_blockers": attachment_blockers,
        "all_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "split_v2_188_axis_map_blocker": {
            "previous": "engine_r4_axes_to_parspec_qeft_length_map_missing",
            "contract_subpieces": [
                "source_axis_power_policy",
                "operator_basis_map",
                "engine_axis_orientation",
                "axis_normalization",
                "covariance_pushforward",
            ],
        },
        "route_status": (
            "parspec_engine_axis_map_packet_ready_nonclaiming"
            if likelihood_attachment_ready
            else "parspec_engine_axis_map_packet_blocked"
        ),
    })


def diagnose_r4_parspec_engine_axis_map_contract(
    *,
    v2188_path: str | Path = DEFAULT_V2188_PATH,
) -> dict[str, Any]:
    synthetic_packet = synthetic_ready_parspec_engine_axis_map_packet()
    current_packet = current_v2188_parspec_axis_map_slot(v2188_path)
    synthetic = evaluate_parspec_engine_axis_map_packet(synthetic_packet)
    current = evaluate_parspec_engine_axis_map_packet(current_packet)
    malformed = evaluate_parspec_engine_axis_map_packet(
        malformed_parspec_engine_axis_map_packet()
    )

    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.170_r4_symbolic_scale_resolution_contract",
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.188_r4_parspec_ringdown_source_bridge",
            "v2.189_r4_research_continuity_ledger",
        ],
        "contract": parspec_engine_axis_map_contract(),
        "synthetic_ready_packet": synthetic_packet,
        "current_v2188_packet": current_packet,
        "synthetic_control_evaluation": synthetic,
        "current_v2188_evaluation": current,
        "malformed_control_evaluation": malformed,
        "contract_ready": True,
        "current_axis_map_ready": current["axis_map_ready"],
        "current_likelihood_attachment_ready": current[
            "likelihood_attachment_ready"
        ],
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "route_status": "parspec_engine_axis_map_contract_ready_nonclaiming",
        "selected_next_build_action": (
            "derive_source_backed_parspec_qeft_axis_map_or_acquire_public_likelihood"
        ),
        "best_next_artifact": (
            "A real ParSpec/qEFT packet satisfying this contract: source-backed "
            "ell_qEFT length-power policy, Bresciani-axis orientation, "
            "normalization into engine R4 units, covariance pushforward, public "
            "likelihood object, event-set alignment, and systematics export."
        ),
        "interpretation": (
            "v2.190 does not invent the missing qEFT map. It turns the v2.188 "
            "axis-map blocker into a concrete packet contract, proves the pass "
            "branch with a synthetic control, and records exactly why the "
            "current ParSpec bridge remains blocked."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v2188", default=str(DEFAULT_V2188_PATH))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_engine_axis_map_contract(
        v2188_path=Path(args.v2188)
    )
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
