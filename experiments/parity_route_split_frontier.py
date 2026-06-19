"""Split CMB beta and gravitational parity routes (v2.59).

v2.58 blocked the direct CMB-beta -> gravitational-parity map. This audit turns
that blocker into a route split: CMB beta remains an EM/axion channel, while
engine gravitational parity should be tested by GW birefringence, PTA chirality,
or a source-backed multimessenger common-axion model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
sys.path.insert(0, "src")
from experiments.birefringence_adapter_literature_sourceability import (
    diagnose_birefringence_adapter_literature_sourceability,
)
from experiments.explicit_tower_basis import _json_default
from itb.frameworks.data_driven import DiscoveredDataDriven
from itb.gravitational_observables import GravitationalBirefringence


PARITY_PARAMS = ["g_R2_parity", "g_R3_parity"]


def _touches_parity_axes() -> list[str]:
    theory = DiscoveredDataDriven().encode()
    observable = GravitationalBirefringence(omegas=[1.0, 2.0])
    jacobian = observable.jacobian(theory, PARITY_PARAMS)
    return [
        key for index, key in enumerate(PARITY_PARAMS)
        if bool(np.any(np.abs(jacobian[:, index]) > 1e-12))
    ]


def _row(
    *,
    route: str,
    channel: str,
    target_axis: str,
    engine_gravity_parity_route: bool,
    implemented_observable: str | None,
    external_measurement_ready: bool,
    source_backed_theory: bool,
    current_status: str,
    blockers: list[str],
    next_required_artifact: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    claim_ready = (
        engine_gravity_parity_route
        and external_measurement_ready
        and source_backed_theory
        and not blockers
    )
    return {
        "route": route,
        "channel": channel,
        "target_axis": target_axis,
        "engine_gravity_parity_route": engine_gravity_parity_route,
        "implemented_observable": implemented_observable,
        "external_measurement_ready": external_measurement_ready,
        "source_backed_theory": source_backed_theory,
        "current_status": current_status,
        "claim_ready": claim_ready,
        "blockers": blockers,
        "next_required_artifact": next_required_artifact,
        "evidence": evidence,
    }


def split_rows() -> list[dict[str, Any]]:
    sourceability = diagnose_birefringence_adapter_literature_sourceability()
    return [
        _row(
            route="cmb_em_axion_beta",
            channel="electromagnetic_axion_photon",
            target_axis="axion_photon_coupling_or_field_history",
            engine_gravity_parity_route=False,
            implemented_observable=None,
            external_measurement_ready=False,
            source_backed_theory=True,
            current_status="external_em_hint_not_engine_gravity_discriminator",
            blockers=[
                "not_engine_gravity_parity_axis",
                "instrument_systematics_not_closed_for_claim",
                "no_registered_framework_em_axion_predictions",
            ],
            next_required_artifact=(
                "Treat CMB beta as a separate EM/axion observable with its own "
                "framework predictions and systematics closure."
            ),
            evidence={
                "sourceability_route_status": sourceability["route_status"],
                "cmb_beta_measurement_source_backed": sourceability[
                    "cmb_beta_measurement_source_backed"
                ],
                "em_birefringence_source_backed": sourceability[
                    "em_birefringence_source_backed"
                ],
            },
        ),
        _row(
            route="gw_gravitational_birefringence",
            channel="gravitational_wave_parity",
            target_axis="g_R2_parity,g_R3_parity",
            engine_gravity_parity_route=True,
            implemented_observable=(
                "src/itb/gravitational_observables.py:GravitationalBirefringence"
            ),
            external_measurement_ready=False,
            source_backed_theory=True,
            current_status="right_engine_axis_but_external_measurement_missing",
            blockers=[
                "no_external_gw_parity_measurement_packet",
                "toy_frequency_normalization",
                "no_framework_excluding_gw_likelihood",
            ],
            next_required_artifact=(
                "A public GW birefringence likelihood or bound mapped directly "
                "to g_R2_parity/g_R3_parity with frequency normalization."
            ),
            evidence={
                "implemented_axes_touched": _touches_parity_axes(),
                "sourceability_gravity_channel": sourceability[
                    "gravitational_parity_channel_source_backed"
                ],
            },
        ),
        _row(
            route="pta_chiral_sgwb",
            channel="gravitational_wave_chirality",
            target_axis="g_R2_parity,g_R3_parity",
            engine_gravity_parity_route=True,
            implemented_observable=None,
            external_measurement_ready=False,
            source_backed_theory=False,
            current_status="future_gravity_parity_probe_not_measurement_ready",
            blockers=[
                "no_external_pta_chirality_likelihood",
                "engine_prediction_is_order_of_magnitude",
                "no_source_backed_axis_normalization",
            ],
            next_required_artifact=(
                "A PTA circular-polarization or chiral Hellings-Downs likelihood "
                "with a source-backed projection to the engine parity axes."
            ),
            evidence={
                "role": "long-baseline gravity parity cross-check",
                "current_engine_status": "design_probe",
            },
        ),
        _row(
            route="multimessenger_common_axion",
            channel="em_plus_gravity_common_field",
            target_axis="coupled_axion_photon_and_axion_gravity_parameters",
            engine_gravity_parity_route=False,
            implemented_observable=None,
            external_measurement_ready=False,
            source_backed_theory=True,
            current_status="common_origin_hypothesis_not_adapter",
            blockers=[
                "no_source_backed_photon_gravity_coupling_relation",
                "requires_high_redshift_joint_em_gw_source",
                "ratio_not_clean_normalization_cancellation",
            ],
            next_required_artifact=(
                "A source-backed multimessenger model relating photon and gravity "
                "Chern-Simons couplings plus a high-redshift joint EM/GW event."
            ),
            evidence={
                "v1_56_status": "correlation_test_not_clean_ratio",
                "v2_58_best_next_artifact": sourceability["best_next_artifact"],
            },
        ),
    ]


def diagnose_parity_route_split_frontier() -> dict[str, Any]:
    rows = split_rows()
    claim_ready = [row for row in rows if row["claim_ready"]]
    gravity_routes = [row["route"] for row in rows if row["engine_gravity_parity_route"]]
    return {
        "basis": [
            "v2.58_birefringence_adapter_sourceability",
            "implemented_gravitational_birefringence_observable",
            "v1.56_multimessenger_caveat",
        ],
        "route_count": len(rows),
        "direct_cmb_beta_to_gravity_route_retired": True,
        "engine_gravity_parity_routes": gravity_routes,
        "claim_ready_routes": [row["route"] for row in claim_ready],
        "claimable_discriminator_now": bool(claim_ready),
        "rows": rows,
        "priority_order": [
            "gw_gravitational_birefringence",
            "multimessenger_common_axion",
            "cmb_em_axion_beta",
            "pta_chiral_sgwb",
        ],
        "route_status": "parity_routes_split_no_claim_ready_path",
        "interpretation": (
            "The overloaded birefringence route is now split. CMB beta remains "
            "a source-backed EM/axion hint, but it is retired as a direct "
            "engine-gravity-parity discriminator. The right engine axis is GW "
            "gravitational birefringence, currently blocked on an external "
            "likelihood and source-backed normalization."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.59/parity_route_split_frontier.json",
    )
    args = parser.parse_args()

    result = diagnose_parity_route_split_frontier()
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
