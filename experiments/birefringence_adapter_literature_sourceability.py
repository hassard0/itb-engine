"""Birefringence adapter literature sourceability audit (v2.58).

v2.56 and v2.57 showed that the engine needs a source-backed map from CMB
polarization rotation beta to the gravitational parity coefficients. This audit
checks the literature split: CMB beta is source-backed as an electromagnetic /
axion-photon rotation, while gravitational parity Chern-Simons couplings are
usually probed through gravitational waves. A universal bridge between the two
is not currently present in the engine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


SOURCES = {
    "alp_cmb_birefringence": {
        "title": "Murai, Isotropic cosmic birefringence from an oscillating axion-like field",
        "url": "https://arxiv.org/abs/2407.14162",
        "channel": "electromagnetic_axion_photon",
    },
    "eskilt_komatsu": {
        "title": (
            "Eskilt and Komatsu, Improved Constraints on Cosmic Birefringence "
            "from WMAP and Planck"
        ),
        "url": "https://arxiv.org/abs/2205.13962",
        "channel": "cmb_beta_measurement",
    },
    "act_dr6": {
        "title": "Diego-Palazuelos and Komatsu, ACT DR6 cosmic birefringence",
        "url": "https://arxiv.org/abs/2509.13654",
        "channel": "cmb_beta_measurement",
    },
    "axion_gravity_ligo": {
        "title": "Jung et al., Constraining the gravitational coupling of axion dark matter at LIGO",
        "url": "https://arxiv.org/abs/2003.02853",
        "channel": "gravitational_axion_chern_simons",
    },
    "axion_gravity_waves": {
        "title": "Chu, Soda, and Yoshida, Gravitational Waves in Axion Dark Matter",
        "url": "https://arxiv.org/abs/2002.04859",
        "channel": "gravitational_axion_chern_simons",
    },
}


def _row(
    *,
    label: str,
    source_key: str,
    supports_beta_measurement: bool,
    supports_em_axion_photon_map: bool,
    supports_gravitational_parity_map: bool,
    provides_universal_em_to_gravity_relation: bool,
    provides_engine_axis_normalization: bool,
    status: str,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "label": label,
        "source": SOURCES[source_key],
        "supports_beta_measurement": supports_beta_measurement,
        "supports_em_axion_photon_map": supports_em_axion_photon_map,
        "supports_gravitational_parity_map": supports_gravitational_parity_map,
        "provides_universal_em_to_gravity_relation": (
            provides_universal_em_to_gravity_relation
        ),
        "provides_engine_axis_normalization": provides_engine_axis_normalization,
        "status": status,
        "claim_ready_adapter_piece": (
            provides_universal_em_to_gravity_relation
            and provides_engine_axis_normalization
        ),
        "blockers": blockers,
    }


def literature_rows() -> list[dict[str, Any]]:
    return [
        _row(
            label="alp_photon_cmb_rotation_mechanism",
            source_key="alp_cmb_birefringence",
            supports_beta_measurement=False,
            supports_em_axion_photon_map=True,
            supports_gravitational_parity_map=False,
            provides_universal_em_to_gravity_relation=False,
            provides_engine_axis_normalization=False,
            status="source_backed_em_birefringence_mechanism",
            blockers=[
                "maps_beta_to_alp_photon_not_gravity_parity",
                "no_engine_g_R2_parity_normalization",
            ],
        ),
        _row(
            label="wmap_planck_beta_measurement",
            source_key="eskilt_komatsu",
            supports_beta_measurement=True,
            supports_em_axion_photon_map=False,
            supports_gravitational_parity_map=False,
            provides_universal_em_to_gravity_relation=False,
            provides_engine_axis_normalization=False,
            status="external_beta_hint_without_gravity_adapter",
            blockers=[
                "measurement_not_operator_adapter",
                "instrument_systematics_not_closed_for_claim",
            ],
        ),
        _row(
            label="act_dr6_beta_measurement",
            source_key="act_dr6",
            supports_beta_measurement=True,
            supports_em_axion_photon_map=False,
            supports_gravitational_parity_map=False,
            provides_universal_em_to_gravity_relation=False,
            provides_engine_axis_normalization=False,
            status="external_beta_hint_without_gravity_adapter",
            blockers=[
                "measurement_not_operator_adapter",
                "instrument_systematics_not_closed_for_claim",
            ],
        ),
        _row(
            label="ligo_axion_gravity_coupling_constraint",
            source_key="axion_gravity_ligo",
            supports_beta_measurement=False,
            supports_em_axion_photon_map=False,
            supports_gravitational_parity_map=True,
            provides_universal_em_to_gravity_relation=False,
            provides_engine_axis_normalization=False,
            status="source_backed_gravity_channel_not_cmb_beta_adapter",
            blockers=[
                "gravitational_parity_requires_gw_channel",
                "no_cmb_beta_to_gravity_coupling_relation",
            ],
        ),
        _row(
            label="axion_gravity_wave_birefringence_mechanism",
            source_key="axion_gravity_waves",
            supports_beta_measurement=False,
            supports_em_axion_photon_map=False,
            supports_gravitational_parity_map=True,
            provides_universal_em_to_gravity_relation=False,
            provides_engine_axis_normalization=False,
            status="source_backed_gravity_channel_not_cmb_beta_adapter",
            blockers=[
                "gravitational_birefringence_is_separate_observable",
                "no_cmb_beta_to_gravity_coupling_relation",
            ],
        ),
    ]


def diagnose_birefringence_adapter_literature_sourceability() -> dict[str, Any]:
    rows = literature_rows()
    claim_ready = [row for row in rows if row["claim_ready_adapter_piece"]]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "basis": [
            "v2.56_birefringence_adapter_requirements",
            "v2.57_prediction_noncircularity",
            "primary_literature_channel_split",
        ],
        "row_count": len(rows),
        "em_birefringence_source_backed": any(
            row["supports_em_axion_photon_map"] for row in rows
        ),
        "cmb_beta_measurement_source_backed": any(
            row["supports_beta_measurement"] for row in rows
        ),
        "gravitational_parity_channel_source_backed": any(
            row["supports_gravitational_parity_map"] for row in rows
        ),
        "universal_em_to_gravity_relation_found": any(
            row["provides_universal_em_to_gravity_relation"] for row in rows
        ),
        "engine_axis_normalization_found": any(
            row["provides_engine_axis_normalization"] for row in rows
        ),
        "claim_ready_adapter_pieces": [row["label"] for row in claim_ready],
        "claimable_discriminator_now": bool(claim_ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "cmb_beta_not_direct_gravitational_parity_adapter",
        "claim_blockers": [
            "cmb_beta_maps_to_photon_axion_not_engine_gravity_parity",
            "no_universal_em_gravity_coupling_relation",
            "gw_gravity_parity_is_separate_measurement_channel",
            "no_engine_axis_normalization",
            "birefringence_route_still_systematics_and_adapter_blocked",
        ],
        "best_next_artifact": (
            "Either a source-backed multimessenger axion model relating photon "
            "and gravity Chern-Simons couplings, or a pivot that treats CMB beta "
            "as an electromagnetic/axion route and uses GW birefringence for "
            "engine gravitational parity."
        ),
        "interpretation": (
            "The literature supports CMB beta as an electromagnetic axion-photon "
            "birefringence observable and separately supports gravitational "
            "Chern-Simons parity channels. It does not provide a universal, "
            "engine-normalized bridge from CMB beta to g_R2_parity/g_R3_parity. "
            "The direct beta-to-gravity-parity route should therefore remain "
            "blocked or be split into EM/axion and GW parity channels."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.58/"
            "birefringence_adapter_literature_sourceability.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_birefringence_adapter_literature_sourceability()
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
