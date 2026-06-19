"""GW parity external measurement packet search (v2.60).

v2.59 moved the engine gravitational-parity route from CMB beta to GW
birefringence. This audit screens existing GW parity/birefringence analyses to
see whether any already supply a source-backed external packet for
g_R2_parity/g_R3_parity.
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
from itb.nontower import ExternalMeasurementEvidence, evaluate_nontower_promotion_guard


SOURCES = {
    "gwtc3_amplitude": {
        "title": "Ng et al., Constraining gravitational wave amplitude birefringence with GWTC-3",
        "url": "https://arxiv.org/abs/2305.05844",
    },
    "parameterized_parity": {
        "title": "Parameterized Parity Violation in Gravitational Wave Propagation",
        "url": "https://arxiv.org/abs/2305.10478",
    },
    "sgwb_nonobservation": {
        "title": (
            "A New Probe of Gravitational Parity Violation Through "
            "(Non-)Observation of the Stochastic Gravitational-Wave Background"
        ),
        "url": "https://arxiv.org/abs/2312.12532",
    },
    "gwtc3_param_constraints": {
        "title": (
            "Constraints on parity and Lorentz violations in gravity from GWTC-3 "
            "through a parametrization of modified gravitational wave propagations"
        ),
        "url": "https://arxiv.org/abs/2304.09025",
    },
    "coincident_grb_test": {
        "title": (
            "Testing gravitational parity violation with coincident gravitational "
            "waves and short gamma-ray bursts"
        ),
        "url": "https://arxiv.org/abs/1005.3310",
    },
}


def _candidate(
    *,
    label: str,
    source_key: str,
    measurement_kind: str,
    numerical_value: float | None,
    uncertainty: float | None,
    source_backed_theory: bool,
    external_bound_or_measurement: bool,
    maps_to_engine_axes: bool,
    public_likelihood: bool,
    frequency_normalization: str,
    framework_excluding_math: bool,
    status: str,
    notes: list[str],
) -> dict[str, Any]:
    source = SOURCES[source_key]
    evidence = ExternalMeasurementEvidence(
        axis="g_R2_parity/g_R3_parity",
        route=label,
        source_url=source["url"],
        source_type="primary_literature",
        measurement_kind=measurement_kind,
        numerical_value=numerical_value,
        uncertainty=uncertainty,
        axis_mapping_kind=(
            "source_backed_direct" if maps_to_engine_axes else "external_parameterization"
        ),
        systematics_status="bounded" if external_bound_or_measurement else "open",
        metadata={
            "source_backed_theory": source_backed_theory,
            "external_bound_or_measurement": external_bound_or_measurement,
            "maps_to_engine_axes": maps_to_engine_axes,
            "public_likelihood": public_likelihood,
            "frequency_normalization": frequency_normalization,
            "framework_excluding_math": framework_excluding_math,
        },
    )
    guard = evaluate_nontower_promotion_guard(
        evidence,
        discriminator_claimable_by_math=framework_excluding_math,
    )
    contract_failures = _contract_failures(
        evidence=evidence,
        source_backed_theory=source_backed_theory,
        external_bound_or_measurement=external_bound_or_measurement,
        maps_to_engine_axes=maps_to_engine_axes,
        public_likelihood=public_likelihood,
        frequency_normalization=frequency_normalization,
        framework_excluding_math=framework_excluding_math,
    )
    ready = not guard["blockers"] and not contract_failures
    return {
        "label": label,
        "source": source,
        "evidence": evidence.to_dict(),
        "guard": guard,
        "contract_failures": contract_failures,
        "ready_for_engine_gw_parity_claim": ready,
        "frontier_status": (
            "gw_parity_packet_ready"
            if ready
            else "gw_parity_packet_not_engine_claim_ready"
        ),
        "status": status,
        "notes": notes,
    }


def _contract_failures(
    *,
    evidence: ExternalMeasurementEvidence,
    source_backed_theory: bool,
    external_bound_or_measurement: bool,
    maps_to_engine_axes: bool,
    public_likelihood: bool,
    frequency_normalization: str,
    framework_excluding_math: bool,
) -> list[str]:
    failures = []
    if not source_backed_theory:
        failures.append("theory_not_source_backed")
    if (
        not external_bound_or_measurement
        or evidence.numerical_value is None
        or evidence.uncertainty is None
    ):
        failures.append("missing_external_numeric_gw_bound")
    if not maps_to_engine_axes:
        failures.append("missing_engine_axis_projection")
    if not public_likelihood:
        failures.append("missing_public_gw_likelihood")
    if frequency_normalization != "engine_usable":
        failures.append("frequency_normalization_not_engine_usable")
    if not framework_excluding_math:
        failures.append("no_framework_excluding_math")
    return failures


def candidate_rows() -> list[dict[str, Any]]:
    return [
        _candidate(
            label="gwtc3_amplitude_birefringence",
            source_key="gwtc3_amplitude",
            measurement_kind="external_upper_bound",
            numerical_value=None,
            uncertainty=None,
            source_backed_theory=True,
            external_bound_or_measurement=True,
            maps_to_engine_axes=False,
            public_likelihood=False,
            frequency_normalization="paper_parameterization",
            framework_excluding_math=False,
            status="external_bound_parameterized_not_engine_mapped",
            notes=[
                "Uses GWTC-3 to search for amplitude birefringence.",
                "The published parameterization is not yet projected to engine parity axes.",
            ],
        ),
        _candidate(
            label="parameterized_parity_violation_formalism",
            source_key="parameterized_parity",
            measurement_kind="theory_formalism",
            numerical_value=None,
            uncertainty=None,
            source_backed_theory=True,
            external_bound_or_measurement=False,
            maps_to_engine_axes=False,
            public_likelihood=False,
            frequency_normalization="formal_parameterization",
            framework_excluding_math=False,
            status="source_backed_formalism_not_measurement_packet",
            notes=[
                "Useful source-backed language for amplitude and velocity birefringence.",
                "It is not itself an external likelihood or bound.",
            ],
        ),
        _candidate(
            label="sgwb_nonobservation_parity_bound",
            source_key="sgwb_nonobservation",
            measurement_kind="external_upper_bound",
            numerical_value=0.1,
            uncertainty=None,
            source_backed_theory=True,
            external_bound_or_measurement=True,
            maps_to_engine_axes=False,
            public_likelihood=False,
            frequency_normalization="kappa_D_kappa_z_not_engine_axes",
            framework_excluding_math=False,
            status="external_sgwb_bound_not_engine_mapped",
            notes=[
                "Reports an order-0.1 joint constraint on generic SGWB birefringence parameters.",
                "The parameters are not g_R2_parity/g_R3_parity in engine normalization.",
            ],
        ),
        _candidate(
            label="gwtc3_modified_propagation_constraints",
            source_key="gwtc3_param_constraints",
            measurement_kind="external_upper_bound",
            numerical_value=None,
            uncertainty=None,
            source_backed_theory=True,
            external_bound_or_measurement=True,
            maps_to_engine_axes=False,
            public_likelihood=False,
            frequency_normalization="modified_propagation_parameterization",
            framework_excluding_math=False,
            status="external_constraints_not_engine_mapped",
            notes=[
                "Uses open GWTC-3 events to constrain parity/Lorentz-violating propagation.",
                "The constraints are not yet an engine parity likelihood.",
            ],
        ),
        _candidate(
            label="coincident_gw_grb_parity_test",
            source_key="coincident_grb_test",
            measurement_kind="design_probe",
            numerical_value=None,
            uncertainty=None,
            source_backed_theory=True,
            external_bound_or_measurement=False,
            maps_to_engine_axes=False,
            public_likelihood=False,
            frequency_normalization="proposal",
            framework_excluding_math=False,
            status="source_backed_test_concept_not_current_measurement",
            notes=[
                "Defines a multimessenger GW/GRB parity test concept.",
                "It requires suitable events and a current likelihood before promotion.",
            ],
        ),
    ]


def diagnose_gw_parity_measurement_packet_search() -> dict[str, Any]:
    rows = candidate_rows()
    ready = [row for row in rows if row["ready_for_engine_gw_parity_claim"]]
    external_candidates = [
        row for row in rows
        if row["evidence"]["metadata"]["external_bound_or_measurement"]
    ]
    failure_counts: dict[str, int] = {}
    for row in rows:
        for failure in row["contract_failures"]:
            failure_counts[failure] = failure_counts.get(failure, 0) + 1

    return {
        "basis": [
            "v2.59_parity_route_split",
            "web_primary_source_search_2026_06_19",
            "nontower_promotion_guard",
        ],
        "axis": "g_R2_parity/g_R3_parity",
        "candidate_count": len(rows),
        "external_bound_or_measurement_candidate_count": len(external_candidates),
        "claim_ready_routes": [row["label"] for row in ready],
        "claimable_discriminator_now": bool(ready),
        "contract_failure_counts": dict(sorted(failure_counts.items())),
        "rows": rows,
        "route_status": "gw_parity_external_bounds_not_engine_claim_ready",
        "best_next_artifact": (
            "An adapter from a published GW parity/birefringence likelihood to "
            "g_R2_parity/g_R3_parity, including frequency normalization and "
            "framework exclusion math."
        ),
        "interpretation": (
            "Existing GW parity analyses provide real source-backed constraints "
            "and useful parameterizations, but none is currently an engine-ready "
            "measurement packet for g_R2_parity/g_R3_parity."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.60/gw_parity_measurement_packet_search.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_measurement_packet_search()
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
