"""Current-source recheck for the g8 high-moment route (v2.78)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


def _source_row(
    *,
    label: str,
    source_url: str,
    source_kind: str,
    relevance: str,
    external_numeric_measurement: bool,
    engine_g8_mapping: bool,
    public_likelihood: bool,
    framework_exclusion_math: bool,
    status: str,
    blockers: list[str],
) -> dict[str, Any]:
    ready = (
        external_numeric_measurement
        and engine_g8_mapping
        and public_likelihood
        and framework_exclusion_math
    )
    return {
        "label": label,
        "source_url": source_url,
        "source_kind": source_kind,
        "relevance": relevance,
        "external_numeric_measurement": external_numeric_measurement,
        "engine_g8_mapping": engine_g8_mapping,
        "public_likelihood": public_likelihood,
        "framework_exclusion_math": framework_exclusion_math,
        "claim_ready": ready,
        "status": status,
        "blockers": sorted(set(blockers)),
    }


def current_source_rows() -> list[dict[str, Any]]:
    return [
        _source_row(
            label="bresciani_levati_paradisi_partial_wave_unitarity",
            source_url="https://arxiv.org/abs/2504.12855",
            source_kind="theory_formalism",
            relevance=(
                "Generalized spinor-helicity partial-wave unitarity formalism "
                "covering spin-2 and higher-spin EFTs."
            ),
            external_numeric_measurement=False,
            engine_g8_mapping=False,
            public_likelihood=False,
            framework_exclusion_math=False,
            status="useful_theory_bridge_not_measurement_packet",
            blockers=[
                "theory_formalism_not_external_measurement",
                "no_engine_g8_normalization",
                "no_public_likelihood",
                "no_registered_framework_exclusion_math",
            ],
        ),
        _source_row(
            label="gravity_universal_cutoff_gravitational_eft_bounds",
            source_url="https://arxiv.org/abs/2408.06440",
            source_kind="theory_formalism",
            relevance=(
                "Discusses gravitational EFT Wilson coefficients and causality "
                "bounds in a universal-cutoff context."
            ),
            external_numeric_measurement=False,
            engine_g8_mapping=False,
            public_likelihood=False,
            framework_exclusion_math=False,
            status="gravitational_eft_theory_not_engine_g8_measurement",
            blockers=[
                "theory_formalism_not_external_measurement",
                "coefficient_basis_not_engine_g8",
                "no_public_likelihood",
                "no_registered_framework_exclusion_math",
            ],
        ),
        _source_row(
            label="cms_energy_correlator_measurements",
            source_url="https://arxiv.org/abs/2402.13864",
            source_kind="external_qcd_measurement",
            relevance=(
                "Real collider energy-correlator measurement and design seed for "
                "high-moment observables."
            ),
            external_numeric_measurement=True,
            engine_g8_mapping=False,
            public_likelihood=False,
            framework_exclusion_math=False,
            status="external_measurement_not_quantum_gravity_g8",
            blockers=[
                "qcd_jet_observable_not_qg_eft_g8",
                "no_engine_g8_normalization",
                "no_engine_usable_likelihood",
                "no_registered_framework_exclusion_math",
            ],
        ),
        _source_row(
            label="detectors_weakly_coupled_qft",
            source_url="https://arxiv.org/abs/2209.00008",
            source_kind="theory_formalism",
            relevance=(
                "Detector/light-ray observable framework that can inform a future "
                "high-moment adapter."
            ),
            external_numeric_measurement=False,
            engine_g8_mapping=False,
            public_likelihood=False,
            framework_exclusion_math=False,
            status="adapter_design_language_not_measurement_packet",
            blockers=[
                "theory_formalism_not_external_measurement",
                "no_engine_g8_normalization",
                "no_public_likelihood",
                "no_registered_framework_exclusion_math",
            ],
        ),
        _source_row(
            label="sharp_boundaries_for_the_swampland",
            source_url="https://arxiv.org/abs/2102.08951",
            source_kind="theory_formalism",
            relevance=(
                "Dispersive swampland boundary formalism for gravitational EFT "
                "constraints."
            ),
            external_numeric_measurement=False,
            engine_g8_mapping=False,
            public_likelihood=False,
            framework_exclusion_math=False,
            status="theory_constraint_context_not_measurement_packet",
            blockers=[
                "theory_formalism_not_external_measurement",
                "no_engine_g8_measurement_packet",
                "no_public_likelihood",
                "no_registered_framework_exclusion_math",
            ],
        ),
    ]


def diagnose_g8_current_source_recheck() -> dict[str, Any]:
    rows = current_source_rows()
    ready = [row for row in rows if row["claim_ready"]]
    theory_bridges = [
        row["label"] for row in rows
        if row["source_kind"] == "theory_formalism"
    ]
    external_measurements = [
        row["label"] for row in rows
        if row["external_numeric_measurement"]
    ]
    blocker_counts: dict[str, int] = {}
    for row in rows:
        for blocker in row["blockers"]:
            blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1

    return {
        "version": "v2.78",
        "basis": [
            "v2.77_post_gw_retirement_frontier",
            "v2.54_g8_high_moment_measurement_specification",
            "v2.55_g8_existing_measurement_packet_search",
            "current_primary_source_recheck_2026_06_19",
        ],
        "axis": "g_8",
        "candidate_count": len(rows),
        "theory_bridge_candidates": theory_bridges,
        "external_measurement_candidates": external_measurements,
        "claim_ready_routes": [row["label"] for row in ready],
        "claimable_discriminator_now": bool(ready),
        "blocker_counts": dict(sorted(blocker_counts.items())),
        "rows": rows,
        "route_status": "current_sources_no_engine_g8_measurement_packet",
        "best_next_artifact": (
            "Convert the partial-wave/detector theory bridges into a concrete "
            "adapter specification, or identify a public dataset with a "
            "source-backed g_8 projection and likelihood."
        ),
        "interpretation": (
            "The current source recheck adds a relevant 2025 partial-wave "
            "unitarity formalism, but it does not change the route status. The "
            "g8 path still lacks an external numerical measurement with an "
            "engine-normalized projection, public likelihood, and framework "
            "exclusion math."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.78/g8_current_source_recheck.json",
    )
    args = parser.parse_args()

    result = diagnose_g8_current_source_recheck()
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
