"""Evaluate pyRing quartic EFT QNM shifts at source-event remnant spins."""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_absolute_gamma_metadata import GWOSC_PARAMETER_SNAPSHOT
from experiments.r4_parspec_pyring_source_probe import (
    PYRING_BRANCH,
    PYRING_BRANCH_HEAD_SHA,
    PYRING_INITIALISE_SOURCE_URL,
    PYRING_QNM_PROBE_AXES,
    PYRING_QUARTIC_THEORIES,
    PYRING_SOURCE_DIRECTIONS,
    PYRING_TREE_URL,
    PYRING_WAVEFORM_SOURCE_URL,
    pyring_quartic_table_manifest,
)
from experiments.r4_parspec_qnm_deformation_jacobian import ENGINE_AXES, QNM_AXES
from experiments.r4_parspec_qnm_to_bresciani_gate import matrix_rank
from experiments.r4_parspec_pyring_tau_axis_jacobian import PARSPEC_HIGH_SPIN_TABLE


VERSION = "v2.203"
DEFAULT_OUT = Path(
    "experiments/results/v2.203/r4_parspec_pyring_event_spin_jacobian.json"
)

MODE_LABELS = ("220", "221")
EVENT_LABELS = ("GW150914", "GW200129")
EVENT_SPIN_ROWS = {
    "GW150914": {
        "spin": 0.6669526906700001,
        "source": "pyRing bundled GW150914_LAL_IMRPhenomP_O1_GWOSC_Mf_af_samples.txt",
        "sample_count": 17070,
        "sample_sha256": (
            "af11e39da06ee5ad9addbc15b7dc2fb4ef5c778ff87826225f2879753be49916"
        ),
        "summary": {
            "af_mean": 0.665174370082,
            "af_median": 0.66695269067,
            "af_p05": 0.61940334427,
            "af_p95": 0.705021230794,
        },
    },
    "GW200129": {
        "spin": 0.73,
        "source": "v2.199 GWOSC preferred parameter snapshot",
        "event_version": GWOSC_PARAMETER_SNAPSHOT["GW200129"]["event_version"],
        "selected_pe_record": GWOSC_PARAMETER_SNAPSHOT["GW200129"][
            "selected_pe_record"
        ],
        "summary": {
            "af_best": 0.73,
            "af_lower": 0.68,
            "af_upper": 0.79,
        },
    },
}

EVENT_SPIN_VALUE_SNAPSHOT = {
    "GW150914": {
        "220": {
            "spin": 0.6669526906700001,
            "berti_frequency_F": 0.5214875364939959,
            "berti_tau_dimensionless": 12.102356553155843,
            "parspec_frequency_F": 0.5178796242098723,
            "parspec_tau_dimensionless": 12.438521962283417,
            "directions": {
                "quartic_1_minus": {"df_fit": -0.7057280532347682, "domi_fit": 1.0182630943192719},
                "quartic_1_plus": {"df_fit": -1.7932703514341448, "domi_fit": -0.30193314204456373},
                "quartic_2_minus": {"df_fit": -1.734656943548799, "domi_fit": 0.8759309384888206},
                "quartic_2_plus": {"df_fit": -1.3003755671569561, "domi_fit": 0.1695746966794048},
                "quartic_3_minus": {"df_fit": -0.4036567038387552, "domi_fit": -0.1793809829092387},
                "quartic_3_plus": {"df_fit": 0.4036567038387552, "domi_fit": 0.1793809829092387},
            },
        },
        "221": {
            "spin": 0.6669526906700001,
            "berti_frequency_F": 0.5094500583211292,
            "berti_tau_dimensionless": 3.982710993908182,
            "parspec_frequency_F": 0.5054742334076994,
            "parspec_tau_dimensionless": 4.125286220597091,
            "directions": {
                "quartic_1_minus": {"df_fit": -3.807161527956978, "domi_fit": 2.3447354186591403},
                "quartic_1_plus": {"df_fit": -1.092712074657149, "domi_fit": -0.04323468705503384},
                "quartic_2_minus": {"df_fit": -4.3728765095637, "domi_fit": 1.2195483985834847},
                "quartic_2_plus": {"df_fit": -1.4568081130102204, "domi_fit": 0.756413306792831},
                "quartic_3_minus": {"df_fit": -0.012403898373476122, "domi_fit": -0.49713991331519214},
                "quartic_3_plus": {"df_fit": 0.012403898373476122, "domi_fit": 0.49713991331519214},
            },
        },
    },
    "GW200129": {
        "220": {
            "spin": 0.73,
            "berti_frequency_F": 0.5483341252148418,
            "berti_tau_dimensionless": 12.498645427403392,
            "parspec_frequency_F": 0.5432008671012916,
            "parspec_tau_dimensionless": 12.552164302987071,
            "directions": {
                "quartic_1_minus": {"df_fit": -1.2673275184369022, "domi_fit": 1.4002679859756588},
                "quartic_1_plus": {"df_fit": -2.3678221265745107, "domi_fit": -0.3872601752361533},
                "quartic_2_minus": {"df_fit": -2.0973318513452006, "domi_fit": 1.060904183646537},
                "quartic_2_plus": {"df_fit": -2.1393361148081143, "domi_fit": 0.04059154864963946},
                "quartic_3_minus": {"df_fit": -0.28055815117268007, "domi_fit": -0.22305093200550768},
                "quartic_3_plus": {"df_fit": 0.28055815117268007, "domi_fit": 0.22305093200550768},
            },
        },
        "221": {
            "spin": 0.73,
            "berti_frequency_F": 0.5382640155604229,
            "berti_tau_dimensionless": 4.124196200319079,
            "parspec_frequency_F": 0.5327443908647929,
            "parspec_tau_dimensionless": 4.23142515531754,
            "directions": {
                "quartic_1_minus": {"df_fit": -5.3657212968158365, "domi_fit": 2.9056731858161156},
                "quartic_1_plus": {"df_fit": -1.4479105468440374, "domi_fit": 0.00016518259124407002},
                "quartic_2_minus": {"df_fit": -5.160279750114034, "domi_fit": 2.0034791264527643},
                "quartic_2_plus": {"df_fit": -2.0125321002399468, "domi_fit": 0.32312206416905986},
                "quartic_3_minus": {"df_fit": 0.21266027980694507, "domi_fit": -0.2907526950632036},
                "quartic_3_plus": {"df_fit": -0.21266027980694507, "domi_fit": 0.2907526950632036},
            },
        },
    },
}


def fractional_frequency_derivative(df_fit: float, gr_frequency_f: float) -> float:
    if gr_frequency_f <= 0.0:
        raise ValueError("gr_frequency_f must be positive")
    return df_fit / gr_frequency_f


def fractional_tau_derivative(domi_fit: float, gr_tau_dimensionless: float) -> float:
    if gr_tau_dimensionless <= 0.0:
        raise ValueError("gr_tau_dimensionless must be positive")
    return -gr_tau_dimensionless * domi_fit


def exact_fractional_tau_shift(
    *,
    gamma: float,
    tau_gr_dimensionless: float,
    domi_fit: float,
) -> float:
    denominator = 1.0 + gamma * tau_gr_dimensionless * domi_fit
    if denominator == 0.0:
        raise ValueError("tau shift denominator is zero")
    return (1.0 / denominator) - 1.0


def finite_difference_tau_derivative(
    *,
    tau_gr_dimensionless: float,
    domi_fit: float,
    epsilon: float = 1e-7,
) -> float:
    plus = exact_fractional_tau_shift(
        gamma=epsilon,
        tau_gr_dimensionless=tau_gr_dimensionless,
        domi_fit=domi_fit,
    )
    minus = exact_fractional_tau_shift(
        gamma=-epsilon,
        tau_gr_dimensionless=tau_gr_dimensionless,
        domi_fit=domi_fit,
    )
    return (plus - minus) / (2.0 * epsilon)


def _normalization_delta(parspec_value: float, runtime_value: float) -> float:
    if runtime_value == 0.0:
        return parspec_value - runtime_value
    return (parspec_value - runtime_value) / runtime_value


def event_spin_jacobian_packet(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or EVENT_SPIN_VALUE_SNAPSHOT
    event_rows = []
    normalization_deltas = []
    derivative_checks = []
    for event in EVENT_LABELS:
        event_payload = snapshot[event]
        rows = []
        for mode in MODE_LABELS:
            mode_payload = event_payload[mode]
            berti_f = float(mode_payload["berti_frequency_F"])
            berti_tau = float(mode_payload["berti_tau_dimensionless"])
            parspec_f = float(mode_payload["parspec_frequency_F"])
            parspec_tau = float(mode_payload["parspec_tau_dimensionless"])
            normalization_deltas.append({
                "event": event,
                "mode": mode,
                "frequency_parspec_vs_pyring_runtime_fractional_delta": (
                    _normalization_delta(parspec_f, berti_f)
                ),
                "tau_parspec_vs_pyring_runtime_fractional_delta": (
                    _normalization_delta(parspec_tau, berti_tau)
                ),
            })
            rows.extend([
                {
                    "row": f"{event}_delta_omega_{mode}_runtime_frac",
                    "mode": mode,
                    "normalization": "pyRing_QNM_EFT_runtime_Berti_frequency",
                    "values": [
                        fractional_frequency_derivative(
                            float(mode_payload["directions"][direction]["df_fit"]),
                            berti_f,
                        )
                        for direction in PYRING_SOURCE_DIRECTIONS
                    ],
                },
                {
                    "row": f"{event}_delta_tau_{mode}_runtime_frac",
                    "mode": mode,
                    "normalization": "pyRing_QNM_EFT_runtime_Berti_tau",
                    "values": [
                        fractional_tau_derivative(
                            float(mode_payload["directions"][direction]["domi_fit"]),
                            berti_tau,
                        )
                        for direction in PYRING_SOURCE_DIRECTIONS
                    ],
                },
                {
                    "row": f"{event}_delta_omega_{mode}_parspec_high_spin_frac",
                    "mode": mode,
                    "normalization": "ParSpec_high_spin_frequency_polynomial",
                    "values": [
                        fractional_frequency_derivative(
                            float(mode_payload["directions"][direction]["df_fit"]),
                            parspec_f,
                        )
                        for direction in PYRING_SOURCE_DIRECTIONS
                    ],
                },
                {
                    "row": f"{event}_delta_tau_{mode}_parspec_high_spin_frac",
                    "mode": mode,
                    "normalization": "ParSpec_high_spin_tau_polynomial",
                    "values": [
                        fractional_tau_derivative(
                            float(mode_payload["directions"][direction]["domi_fit"]),
                            parspec_tau,
                        )
                        for direction in PYRING_SOURCE_DIRECTIONS
                    ],
                },
            ])
            for direction in PYRING_SOURCE_DIRECTIONS:
                domi_fit = float(mode_payload["directions"][direction]["domi_fit"])
                derivative_checks.append({
                    "event": event,
                    "mode": mode,
                    "source_direction": direction,
                    "normalization": "pyRing_QNM_EFT_runtime_Berti_tau",
                    "linearized_derivative": fractional_tau_derivative(
                        domi_fit,
                        berti_tau,
                    ),
                    "finite_difference_derivative": finite_difference_tau_derivative(
                        tau_gr_dimensionless=berti_tau,
                        domi_fit=domi_fit,
                    ),
                })
        event_rows.append({
            "event": event,
            "event_spin": EVENT_SPIN_ROWS[event],
            "rows": [row["row"] for row in rows],
            "columns": list(PYRING_SOURCE_DIRECTIONS),
            "matrix": [row["values"] for row in rows],
            "row_metadata": rows,
            "rank": matrix_rank([row["values"] for row in rows]),
        })

    return canonicalize_json_floats({
        "packet_id": "pyring_event_spin_frequency_tau_jacobian_v1",
        "events": list(EVENT_LABELS),
        "modes": list(MODE_LABELS),
        "columns": list(PYRING_SOURCE_DIRECTIONS),
        "columns_are_branch_splitting_directions": True,
        "columns_are_independent_operator_axes": False,
        "event_rows": event_rows,
        "normalization_comparison": normalization_deltas,
        "max_abs_frequency_normalization_delta": max(
            abs(row["frequency_parspec_vs_pyring_runtime_fractional_delta"])
            for row in normalization_deltas
        ),
        "max_abs_tau_normalization_delta": max(
            abs(row["tau_parspec_vs_pyring_runtime_fractional_delta"])
            for row in normalization_deltas
        ),
        "derivative_checks": derivative_checks,
        "source_formulae": {
            "runtime_fractional_frequency": "d(freq_EFT/freq_GR-1)/d gamma = df_EFT_fit/F_Berti(a)",
            "runtime_fractional_tau": "d(tau_EFT/tau_GR-1)/d gamma = -tau_Berti_dimensionless(a)*domi_EFT_fit",
            "parspec_high_spin_comparison": (
                "The same pyRing df/domi fits are also divided by the ParSpec "
                "high-spin F(a) and tau(a) polynomials to expose the remaining "
                "normalization-policy difference."
            ),
        },
    })


def evaluate_event_spin_jacobian(
    snapshot: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    snapshot = snapshot or EVENT_SPIN_VALUE_SNAPSHOT
    blockers: set[str] = set()
    for event in EVENT_LABELS:
        if event not in snapshot:
            blockers.add(f"{event}_event_missing")
            continue
        if event not in EVENT_SPIN_ROWS:
            blockers.add(f"{event}_spin_source_missing")
        spin = EVENT_SPIN_ROWS[event]["spin"]
        if not isinstance(spin, int | float) or not 0.0 <= float(spin) < 1.0:
            blockers.add(f"{event}_spin_nonphysical")
        for mode in MODE_LABELS:
            if mode not in snapshot[event]:
                blockers.add(f"{event}_{mode}_mode_missing")
                continue
            mode_payload = snapshot[event][mode]
            for key in (
                "berti_frequency_F",
                "berti_tau_dimensionless",
                "parspec_frequency_F",
                "parspec_tau_dimensionless",
            ):
                if float(mode_payload.get(key, 0.0)) <= 0.0:
                    blockers.add(f"{event}_{mode}_{key}_not_positive")
            if tuple(mode_payload.get("directions", {})) != PYRING_SOURCE_DIRECTIONS:
                blockers.add(f"{event}_{mode}_direction_set_mismatch")

    packet = event_spin_jacobian_packet(snapshot)
    for event_row in packet["event_rows"]:
        if event_row["rank"] < 4:
            blockers.add(f"{event_row['event']}_event_spin_matrix_rank_deficient")
    for check in packet["derivative_checks"]:
        if not math.isclose(
            float(check["linearized_derivative"]),
            float(check["finite_difference_derivative"]),
            rel_tol=1e-8,
            abs_tol=1e-8,
        ):
            blockers.add(
                f"{check['event']}_{check['mode']}_{check['source_direction']}_tau_finite_diff_mismatch"
            )

    ready = not blockers
    remaining_claim_blockers = {
        "qnm_deformation_to_bresciani_engine_r4_map_missing",
        "pyring_plus_minus_branches_not_independent_operator_axes",
        "pyring_quartic_direction_to_bresciani_axis_orientation_missing",
        "pyring_runtime_to_parspec_high_spin_normalization_policy_missing",
        "public_parspec_qeft_likelihood_or_posterior_samples_missing",
        "claim_grade_systematics_export_missing",
        "external_adversarial_review_missing",
    }
    if not ready:
        remaining_claim_blockers.add("pyring_event_spin_jacobian_not_ready")

    return canonicalize_json_floats({
        "pyring_event_spin_jacobian_ready": ready,
        "pyring_runtime_fractional_axes_ready": ready,
        "parspec_high_spin_comparison_ready": ready,
        "parspec_axis_normalization_policy_ready": False,
        "qnm_to_bresciani_sensitivity_ready": False,
        "public_likelihood_ready": False,
        "ready_for_framework_claim": False,
        "source_intake_blockers": sorted(blockers),
        "resolved_v2202_subpieces": (
            [
                "pyring_event_spin_runtime_frequency_tau_jacobian_defined",
                "gw150914_final_spin_source_attached",
            ]
            if ready
            else []
        ),
        "remaining_claim_blockers": sorted(remaining_claim_blockers),
        "route_status": (
            "pyring_event_spin_jacobian_ready_normalization_policy_missing"
            if ready
            else "pyring_event_spin_jacobian_not_ready"
        ),
    })


def malformed_event_spin_snapshot() -> dict[str, dict[str, Any]]:
    snapshot = copy.deepcopy(EVENT_SPIN_VALUE_SNAPSHOT)
    for mode in MODE_LABELS:
        snapshot["GW150914"][mode]["directions"] = {
            direction: {"df_fit": 0.0, "domi_fit": 0.0}
            for direction in PYRING_SOURCE_DIRECTIONS
        }
    return snapshot


def diagnose_r4_parspec_pyring_event_spin_jacobian() -> dict[str, Any]:
    packet = event_spin_jacobian_packet()
    evaluation = evaluate_event_spin_jacobian()
    malformed_evaluation = evaluate_event_spin_jacobian(
        malformed_event_spin_snapshot()
    )
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.199_absolute_gamma_metadata",
            "v2.201_pyring_source_probe",
            "v2.202_pyring_tau_axis_jacobian",
            "public_pyring_EFT_QNMs_branch",
        ],
        "source_manifest": {
            "branch": PYRING_BRANCH,
            "branch_head_sha": PYRING_BRANCH_HEAD_SHA,
            "tree_url": PYRING_TREE_URL,
            "waveform_source_url": PYRING_WAVEFORM_SOURCE_URL,
            "initialise_source_url": PYRING_INITIALISE_SOURCE_URL,
            "pyring_quartic_tables": pyring_quartic_table_manifest()["tables"],
            "parspec_high_spin_table": PARSPEC_HIGH_SPIN_TABLE,
            "gw150914_spin_source": EVENT_SPIN_ROWS["GW150914"],
            "gw200129_spin_source": EVENT_SPIN_ROWS["GW200129"],
            "source_line_refs": {
                "pyring_table_ingest": "waveform.pyx:72-80",
                "pyring_runtime_frequency_formula": "waveform.pyx:526-532",
                "pyring_runtime_tau_formula": "waveform.pyx:534-540",
                "pyring_berti_gr_fit": "waveform.pyx:34-39,252-254",
                "parspec_high_spin_fit": "waveform.pyx:61-69",
            },
        },
        "engine_target_axes": list(ENGINE_AXES),
        "parspec_qnm_axes": list(QNM_AXES),
        "pyring_probe_axes": list(PYRING_QNM_PROBE_AXES),
        "pyring_quartic_theories": list(PYRING_QUARTIC_THEORIES),
        "pyring_source_directions": list(PYRING_SOURCE_DIRECTIONS),
        "event_spin_value_snapshot": EVENT_SPIN_VALUE_SNAPSHOT,
        "event_spin_jacobian": packet,
        "evaluation": evaluation,
        "malformed_control_evaluation": malformed_evaluation,
        "pyring_event_spin_jacobian_ready": evaluation[
            "pyring_event_spin_jacobian_ready"
        ],
        "qnm_to_bresciani_sensitivity_ready": False,
        "claimable_framework_exclusions_now": [],
        "ready_for_framework_claim": False,
        "selected_next_build_action": (
            "derive_pyring_runtime_to_parspec_high_spin_normalization_policy_or_"
            "pyring_quartic_direction_to_bresciani_axis_orientation"
        ),
        "route_status": evaluation["route_status"],
        "interpretation": (
            "v2.203 evaluates the pyRing quartic EFT frequency and damping-time "
            "rows at source-event remnant spins. The runtime pyRing QNM_EFT "
            "normalization uses Berti GR fits, while the ParSpec high-spin "
            "polynomial normalization differs at the few-percent level for the "
            "checked rows. This is a useful event-spin Jacobian, not a "
            "Bresciani operator-axis map or public likelihood."
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_r4_parspec_pyring_event_spin_jacobian()
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
