"""Analytic KK tower benchmark scan (v2.38).

v2.37 found a large-volume benchmark whose sourced slope crosses the tower
threshold, but whose displacement is not framework-owned. This audit scans
analytic KK tower vectors from recent primary literature and records which
scoped decompactification benchmarks would cross the same threshold.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default
from experiments.tower_adapter_thresholds import diagnose_tower_adapter_thresholds


SOURCE = {
    "title": "Aoufia, Castellano, and Ibanez, Laplacians in Various Dimensions and the Swampland",
    "url": "https://arxiv.org/abs/2506.03253",
    "formula": "|zeta_KK,p| = sqrt((d + p - 2) / (p * (d - 2)))",
}


def kk_tower_vector_norm(dimension: int, internal_dimension: int) -> float:
    if dimension <= 2:
        raise ValueError("dimension must be greater than 2")
    if internal_dimension <= 0:
        raise ValueError("internal_dimension must be positive")
    return math.sqrt(
        (dimension + internal_dimension - 2.0)
        / (internal_dimension * (dimension - 2.0))
    )


def _benchmark_row(
    *,
    dimension: int,
    internal_dimension: int,
    critical_phi: float,
    delta_moduli: float,
) -> dict[str, Any]:
    alpha = kk_tower_vector_norm(dimension, internal_dimension)
    phi = alpha * delta_moduli
    return {
        "label": f"d{dimension}_p{internal_dimension}_kk_vector",
        "dimension": dimension,
        "internal_dimension": internal_dimension,
        "lambda_kk": alpha,
        "delta_moduli_benchmark": delta_moduli,
        "phi_tower_mean": phi,
        "phi_tower_sigma": 0.0,
        "tower_mass_gap": math.exp(-phi),
        "critical_phi_tower": critical_phi,
        "delta_moduli_required_for_exclusion": critical_phi / alpha,
        "benchmark_tower_verdict": (
            "benchmark_excluding" if phi > critical_phi else "benchmark_not_excluding"
        ),
        "claimable_now": False,
        "scope_blockers": [
            "analytic_tower_vector_not_registered_framework_evidence",
            "delta_moduli_benchmark_not_framework_owned_prediction",
            "decompactification_endpoint_not_selected_by_current_catalogue",
        ],
    }


def diagnose_analytic_kk_tower_benchmark(
    dimension: int = 4,
    internal_dimensions: list[int] | None = None,
    delta_moduli: float = 1.0,
) -> dict[str, Any]:
    if internal_dimensions is None:
        internal_dimensions = list(range(1, 7))
    thresholds = diagnose_tower_adapter_thresholds(sigma_values=[0.0])
    critical_phi = float(thresholds["critical_phi_tower"])
    rows = [
        _benchmark_row(
            dimension=dimension,
            internal_dimension=internal_dimension,
            critical_phi=critical_phi,
            delta_moduli=delta_moduli,
        )
        for internal_dimension in internal_dimensions
    ]
    excluding = [
        row["label"] for row in rows
        if row["benchmark_tower_verdict"] == "benchmark_excluding"
    ]
    registration_ready = [
        row["label"] for row in rows
        if row["benchmark_tower_verdict"] == "benchmark_excluding"
        and row["delta_moduli_required_for_exclusion"] <= delta_moduli
    ]
    return {
        "basis": ["analytic_KK_vector", "primary_literature", "benchmark_gate"],
        "source": SOURCE,
        "dimension": dimension,
        "delta_moduli_benchmark": delta_moduli,
        "critical_phi_tower": critical_phi,
        "candidate_count": len(rows),
        "benchmark_excluding_candidates": excluding,
        "registration_ready_if_scoped_candidates": registration_ready,
        "claimable_framework_exclusions_now": [],
        "candidates": rows,
        "literature_guardrail": {
            "claim": (
                "Analytic KK vector norms identify threshold-crossing benchmark "
                "rates, not current framework exclusions. Promotion still "
                "requires a scoped framework endpoint and displacement."
            ),
            "primary_sources": [SOURCE],
        },
        "interpretation": (
            "For d=4 and Delta_moduli=1, every scanned KK decompactification "
            "vector crosses the current tower threshold. This makes endpoint "
            "ownership, not rate size, the next limiting requirement."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="experiments/results/v2.38/analytic_kk_tower_benchmark.json",
    )
    parser.add_argument("--dimension", type=int, default=4)
    parser.add_argument("--max-p", type=int, default=6)
    parser.add_argument("--delta-moduli", type=float, default=1.0)
    args = parser.parse_args()

    result = diagnose_analytic_kk_tower_benchmark(
        dimension=args.dimension,
        internal_dimensions=list(range(1, args.max_p + 1)),
        delta_moduli=args.delta_moduli,
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
