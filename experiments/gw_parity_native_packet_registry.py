"""Native GW parity packet registry (v2.62).

v2.61 showed that Ng and Callister have public source-side material, while the
engine-axis adapter remains missing. This registry records those sources as
native, non-promoting packets.
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
from itb.gw_parity import GWParityNativePacket, validate_gw_parity_native_packet


def native_packets() -> list[GWParityNativePacket]:
    return [
        GWParityNativePacket(
            label="ng_gwtc3_kappa_at_100hz",
            source_url="https://arxiv.org/abs/2305.05844",
            parameter_basis="ng_kappa_at_100hz",
            measurement_kind="external_native_posterior",
            parameters={
                "kappa_Gpc_inv": -0.019,
                "kappa_plus_90": 0.038,
                "kappa_minus_90": 0.029,
                "f_ref_hz": 100.0,
                "M_PV_lower_bound_GeV": 6.8e-21,
            },
            public_code_url=(
                "https://github.com/thomasckng/"
                "Constraining-Birefringence-with-GWTC-3"
            ),
            public_data_url="https://zenodo.org/records/7935107",
            public_docs_url=(
                "https://github.com/thomasckng/"
                "Constraining-Birefringence-with-GWTC-3/blob/main/README.md"
            ),
            public_likelihood_url="https://zenodo.org/records/7935107",
            engine_projection_status="blocked_missing_engine_axis_adapter",
            notes=[
                "Source-side posterior material is public in the paper repository and Zenodo release.",
                "Keep native until kappa/M_PV is mapped through a PPV/operator adapter.",
            ],
        ),
        GWParityNativePacket(
            label="callister_sgwb_kappaD_kappaz",
            source_url="https://arxiv.org/abs/2312.12532",
            parameter_basis="sgwb_kappaD_kappaz",
            measurement_kind="external_native_posterior",
            parameters={
                "kappa_D_scale": 0.1,
                "kappa_z_scale": 0.1,
                "f_ref_hz": 100.0,
                "constraint_kind": "order_of_magnitude_joint_bound",
            },
            public_code_url="https://github.com/tcallister/stochastic-birefringence",
            public_data_url="https://zenodo.org/doi/10.5281/zenodo.10384997",
            public_docs_url="https://tcallister.github.io/stochastic-birefringence/",
            public_likelihood_url="https://zenodo.org/doi/10.5281/zenodo.10384997",
            engine_projection_status="blocked_missing_engine_axis_adapter",
            notes=[
                "Public repository, docs, and Zenodo data expose native SGWB parity material.",
                "Keep native until kappa_D/kappa_z are mapped to a source-backed engine basis.",
            ],
        ),
    ]


def _packet_row(packet: GWParityNativePacket) -> dict[str, Any]:
    validation = validate_gw_parity_native_packet(packet)
    return {
        "packet": packet.to_dict(),
        "validation": validation,
        "registry_status": (
            "native_source_ready_nonpromoting"
            if validation["native_packet_ready"] and not validation["engine_projection_ready"]
            else "not_registry_ready"
        ),
    }


def diagnose_gw_parity_native_packet_registry() -> dict[str, Any]:
    rows = [_packet_row(packet) for packet in native_packets()]
    native_ready = [
        row for row in rows
        if row["validation"]["native_packet_ready"]
    ]
    engine_ready = [
        row for row in rows
        if row["validation"]["engine_projection_ready"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["validation"]["projection_blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "basis": [
            "v2.61_gw_parity_adapter_readiness",
            "GWParityNativePacket",
            "validate_gw_parity_native_packet",
        ],
        "registry_packet_count": len(rows),
        "native_packet_ready_routes": [
            row["packet"]["label"] for row in native_ready
        ],
        "native_packet_ready_count": len(native_ready),
        "engine_projection_ready_routes": [
            row["packet"]["label"] for row in engine_ready
        ],
        "engine_projection_ready_count": len(engine_ready),
        "claimable_discriminator_now": bool(engine_ready),
        "projection_blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "native_gw_parity_packets_ready_projection_blocked",
        "best_next_artifact": (
            "A PPV/native-basis adapter specification mapping Ng kappa and "
            "Callister kappa_D/kappa_z into a shared source-backed propagation basis, "
            "without projecting to g_R2_parity/g_R3_parity yet."
        ),
        "interpretation": (
            "Ng and Callister can now be represented as native, public, "
            "non-promoting GW parity packets. Engine-axis projection remains "
            "blocked by missing operator, dimensional, frequency, and framework math."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.62/gw_parity_native_packet_registry.json",
    )
    args = parser.parse_args()

    result = diagnose_gw_parity_native_packet_registry()
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
