"""Weyl/g8 discriminator frontier audit (v2.50).

v2.49 kept the birefringence route alive but one-observable dominated. This
audit asks whether the next non-tower directions, Weyl^2/g_C and the matter
high-moment g_8, can separate named frameworks or shrink the island without
pretending that internal PCA cuts are external measurements.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from explicit_tower_basis import _json_default
from stack import build_stack
from itb.holographic_ac import gC_from_gR2
from itb.predict import FRAMEWORKS
from itb.scope import engine_validity
from itb.theory import Theory


COEFFS = (
    "g_4",
    "g_6",
    "g_8",
    "g_R2",
    "g_R3",
    "g_C",
    "g_R2_parity",
    "g_R3_parity",
)
LO = np.array([0.05, 0.05, 0.05, 0.02, 0.0, 0.02, 0.0, 0.0])
HI = np.array([0.60, 0.60, 0.70, 0.45, 0.40, 0.60, 0.0, 0.0])
QUANTILES = (0.25, 0.50, 0.75)
STACK_CONFIG = {
    "bnossw_mean": "geometric",
    "rfc_form": "convex_hull",
}
ROBUSTNESS_SEEDS = (25050, 25051, 25052, 25053, 25054)
CLAIM_BLOCKERS = (
    "g_C_observables_are_structural_or_toy_mapped",
    "g_8_has_no_source_backed_measurement_program",
    "framework_exclusions_depend_on_internal_cut_choice",
    "pca_axes_are_internal_island_geometry_not_external_measurements",
)


def _theory_from_vector(x: Iterable[float]) -> Theory:
    return Theory(coefficients={k: float(v) for k, v in zip(COEFFS, x)})


def _framework_vector(name: str) -> np.ndarray:
    vector, _ = _framework_vector_and_g_c_source(name)
    return vector


def _framework_vector_and_g_c_source(name: str) -> tuple[np.ndarray, str]:
    coeffs = FRAMEWORKS[name].encode().coefficients
    g_r2 = coeffs.get("g_R2", 0.0)
    has_native_g_c = "g_C" in coeffs
    values = []
    for key in COEFFS:
        if key == "g_C":
            values.append(coeffs["g_C"] if has_native_g_c else gC_from_gR2(g_r2))
        else:
            values.append(coeffs.get(key, 0.0))
    return (
        np.array(values, dtype=float),
        "native" if has_native_g_c else "portrait_derived_from_g_R2",
    )


def sample_parity_even_island(
    sample_count: int = 120_000,
    *,
    seed: int = 25050,
) -> np.ndarray:
    """Sample the parity-even full-basis island used for the Weyl/g8 audit."""

    stack = build_stack(**STACK_CONFIG)
    rng = np.random.default_rng(seed)
    draws = LO + (HI - LO) * rng.random((sample_count, len(COEFFS)))
    survivors = []
    for row in draws:
        theory = _theory_from_vector(row)
        if all(constraint.evaluate(theory).satisfied for constraint in stack):
            survivors.append(row)
    return np.array(survivors, dtype=float).reshape(-1, len(COEFFS))


def _orient_direction(direction: np.ndarray) -> np.ndarray:
    oriented = np.array(direction, dtype=float)
    strongest = int(np.argmax(np.abs(oriented)))
    if oriented[strongest] < 0.0:
        oriented *= -1.0
    norm = float(np.linalg.norm(oriented))
    if norm == 0.0:
        raise ValueError("zero direction cannot be normalized")
    return oriented / norm


def _pca_directions(island: np.ndarray) -> tuple[np.ndarray, dict[str, Any]]:
    centered = island - island.mean(axis=0)
    covariance = np.cov(centered.T)
    evals, evecs = np.linalg.eigh(covariance)
    order = np.argsort(evals)[::-1]
    evals = np.clip(evals[order], 0.0, None)
    evecs = evecs[:, order]
    participation = float((evals.sum() ** 2) / np.square(evals).sum())

    directions = np.stack([
        _orient_direction(evecs[:, 0]),
        _orient_direction(evecs[:, 1]),
    ])
    pca = {
        "effective_dimension_raw_pca": participation,
        "variance_fraction": [
            float(value / evals.sum()) if evals.sum() else 0.0
            for value in evals[:4]
        ],
        "top2_loadings": {
            f"PC{i + 1}": {
                COEFFS[j]: round(float(directions[i, j]), 3)
                for j in range(len(COEFFS))
                if abs(directions[i, j]) >= 0.05
            }
            for i in range(2)
        },
    }
    return directions, pca


def _framework_rows(stack: list[Any]) -> list[dict[str, Any]]:
    rows = []
    for name in sorted(FRAMEWORKS):
        framework = FRAMEWORKS[name]
        vector, g_c_source = _framework_vector_and_g_c_source(name)
        theory = _theory_from_vector(vector)
        scope = engine_validity(framework)
        feasible = bool(
            all(constraint.evaluate(theory).satisfied for constraint in stack)
        )
        rows.append({
            "framework": name,
            "framework_feasibility_basis": "full_stack",
            "feasible_under_current_stack": feasible,
            "preexisting_full_stack_excluded": not feasible,
            "engine_scope": {
                "in_scope": bool(scope.in_scope),
                "violations": list(scope.violations),
                "note": scope.note,
            },
            "g_C_source": g_c_source,
            "coefficients": {
                key: round(float(vector[i]), 4)
                for i, key in enumerate(COEFFS)
            },
        })
    return rows


def _cut_row(
    *,
    label: str,
    threshold: float,
    projections: np.ndarray,
    direction: np.ndarray,
    frameworks: list[dict[str, Any]],
) -> dict[str, Any]:
    removed = projections > threshold
    excluded = []
    feasible_excluded = []
    preexisting_excluded = []
    for row in frameworks:
        vector = np.array([row["coefficients"][key] for key in COEFFS], dtype=float)
        if float(vector @ direction) > threshold:
            excluded.append(row["framework"])
            if row["feasible_under_current_stack"]:
                feasible_excluded.append(row["framework"])
            else:
                preexisting_excluded.append(row["framework"])
    return {
        "cut": label,
        "upper_threshold": threshold,
        "island_removed_fraction": float(np.mean(removed)),
        "island_retained_fraction": float(1.0 - np.mean(removed)),
        "frameworks_excluded": excluded,
        "feasible_frameworks_excluded": feasible_excluded,
        "preexisting_excluded_frameworks": preexisting_excluded,
    }


def _direction_audit(
    *,
    name: str,
    direction: np.ndarray,
    island: np.ndarray,
    frameworks: list[dict[str, Any]],
    favored_vector: np.ndarray,
    bootstrap_count: int,
    seed: int,
) -> dict[str, Any]:
    projections = island @ direction
    favored_projection = float(favored_vector @ direction)
    cuts = [
        _cut_row(
            label=f"q{int(q * 100)}",
            threshold=float(np.quantile(projections, q)),
            projections=projections,
            direction=direction,
            frameworks=frameworks,
        )
        for q in QUANTILES
    ]
    favored_safe_cut = _cut_row(
        label="tangent_discovered_data_driven",
        threshold=favored_projection,
        projections=projections,
        direction=direction,
        frameworks=frameworks,
    )
    cuts.append(favored_safe_cut)
    cuts.sort(
        key=lambda row: (
            -len(row["feasible_frameworks_excluded"]),
            -row["island_removed_fraction"],
            row["cut"],
        )
    )

    rng = np.random.default_rng(seed)
    boot_extents = []
    for _ in range(bootstrap_count):
        indices = rng.integers(0, len(projections), len(projections))
        boot_extents.append(float(np.std(projections[indices])))
    ci_low, ci_high = np.quantile(boot_extents, [0.025, 0.975])

    strongest = int(np.argmax(np.abs(direction)))
    return {
        "direction": name,
        "dominant_coefficient": COEFFS[strongest],
        "loadings": {
            COEFFS[i]: round(float(direction[i]), 3)
            for i in range(len(COEFFS))
            if abs(direction[i]) >= 0.05
        },
        "island_extent_std": float(np.std(projections)),
        "extent_bootstrap_95ci": [float(ci_low), float(ci_high)],
        "projection_range": [float(np.min(projections)), float(np.max(projections))],
        "favored_projection": favored_projection,
        "candidate_cuts_ranked": cuts,
        "best_internal_cut": cuts[0],
        "favored_safe_cut": favored_safe_cut,
    }


def _direction_geometry(island: np.ndarray) -> dict[str, Any]:
    pca_dirs, pca = _pca_directions(island)
    directions = {
        "single:g_C": _orient_direction(np.eye(len(COEFFS))[COEFFS.index("g_C")]),
        "single:g_8": _orient_direction(np.eye(len(COEFFS))[COEFFS.index("g_8")]),
        "PCA:PC1": pca_dirs[0],
        "PCA:PC2": pca_dirs[1],
    }
    extents = {
        name: float(np.std(island @ direction))
        for name, direction in directions.items()
    }
    ranked = sorted(extents, key=lambda name: -extents[name])
    top_single = [name for name in ranked if name.startswith("single:")]
    pc1_dominant = COEFFS[int(np.argmax(np.abs(pca_dirs[0])))]
    pc2_dominant = COEFFS[int(np.argmax(np.abs(pca_dirs[1])))]
    stable = (
        top_single[:2] == ["single:g_C", "single:g_8"]
        and pc1_dominant == "g_C"
        and pc2_dominant == "g_8"
    )
    return {
        "pca": pca,
        "pca_directions": pca_dirs,
        "directions": directions,
        "top_single_directions": top_single,
        "pc1_dominant": pc1_dominant,
        "pc2_dominant": pc2_dominant,
        "stable_weyl_g8_frontier": stable,
    }


def _robustness_matrix(
    *,
    sample_count: int,
    seeds: tuple[int, ...],
) -> dict[str, Any]:
    rows = []
    for seed in seeds:
        island = sample_parity_even_island(sample_count, seed=seed)
        if len(island) < 30:
            rows.append({
                "seed": seed,
                "sample_count": sample_count,
                "island_survivors": int(len(island)),
                "stable_weyl_g8_frontier": False,
                "failure": "insufficient_survivors",
            })
            continue
        geometry = _direction_geometry(island)
        rows.append({
            "seed": seed,
            "sample_count": sample_count,
            "island_survivors": int(len(island)),
            "top_single_directions": geometry["top_single_directions"][:2],
            "pc1_dominant": geometry["pc1_dominant"],
            "pc2_dominant": geometry["pc2_dominant"],
            "stable_weyl_g8_frontier": bool(geometry["stable_weyl_g8_frontier"]),
        })
    pass_fraction = (
        sum(1 for row in rows if row["stable_weyl_g8_frontier"]) / len(rows)
        if rows else 0.0
    )
    return {
        "basis": "seed_jackknife_over_parity_even_sampling",
        "minimum_pass_fraction": 0.8,
        "pass_fraction": float(pass_fraction),
        "passes_minimum_robustness": bool(pass_fraction >= 0.8),
        "rows": rows,
    }


def diagnose_weyl_g8_discriminator_frontier(
    sample_count: int = 120_000,
    *,
    seed: int = 25050,
    bootstrap_count: int = 80,
    robustness_sample_count: int = 20_000,
    robustness_seeds: tuple[int, ...] = ROBUSTNESS_SEEDS,
) -> dict[str, Any]:
    island = sample_parity_even_island(sample_count, seed=seed)
    if len(island) < 30:
        raise RuntimeError(
            f"insufficient island survivors: {len(island)} from {sample_count} samples"
        )

    stack = build_stack(**STACK_CONFIG)
    frameworks = _framework_rows(stack)
    favored = _framework_vector("discovered_data_driven")
    geometry = _direction_geometry(island)
    direction_rows = [
        _direction_audit(
            name=name,
            direction=direction,
            island=island,
            frameworks=frameworks,
            favored_vector=favored,
            bootstrap_count=bootstrap_count,
            seed=seed + index + 1,
        )
        for index, (name, direction) in enumerate(geometry["directions"].items())
    ]
    direction_rows.sort(key=lambda row: -row["island_extent_std"])
    top_single = geometry["top_single_directions"]
    robustness = _robustness_matrix(
        sample_count=robustness_sample_count,
        seeds=robustness_seeds,
    )

    return {
        "audit_configuration": {
            "coefficient_order": list(COEFFS),
            "sampling_box": {
                key: [float(LO[i]), float(HI[i])]
                for i, key in enumerate(COEFFS)
            },
            "parity_slice": "g_R2_parity = g_R3_parity = 0",
            "stack_config": STACK_CONFIG,
            "framework_feasibility_basis": "full_stack",
            "pca_basis": "raw covariance over sampled parity-even survivor vectors",
            "pca_orientation": (
                "principal component signs are flipped so the largest absolute "
                "loading is positive"
            ),
            "cut_semantics": "upper cuts remove points with projection > threshold",
        },
        "basis": [
            "parity_even_full_basis_island",
            "weyl_squared_g_C",
            "matter_high_moment_g_8",
            "internal_pca_geometry",
        ],
        "sample_count": sample_count,
        "island_survivors": int(len(island)),
        "island_survival_fraction": float(len(island) / sample_count),
        "pca": geometry["pca"],
        "frameworks": frameworks,
        "directions_ranked_by_extent": direction_rows,
        "top_single_directions": top_single,
        "geometry_status": (
            "weyl_g8_frontier_confirmed"
            if geometry["stable_weyl_g8_frontier"]
            else "weyl_g8_frontier_unstable"
        ),
        "robustness": robustness,
        "claimable_discriminator_now": False,
        "claim_blockers": list(CLAIM_BLOCKERS),
        "route_status": "frontier_alive_but_not_claimable",
        "interpretation": (
            "The parity-even island still points at g_C/Weyl^2 and g_8 as the "
            "widest non-tower directions. Internal cuts along those axes can "
            "separate named frameworks and shrink the island, but this is not a "
            "framework-level quantum-gravity discriminator until g_C and g_8 "
            "are tied to source-backed, externally measured observables."
        ),
        "honest": (
            "The cut sweep uses internal island geometry and toy observable "
            "mappings. It is an experiment-design frontier, not a discovery or "
            "exclusion claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=120_000)
    parser.add_argument("--seed", type=int, default=25050)
    parser.add_argument("--bootstrap-count", type=int, default=80)
    parser.add_argument("--robustness-samples", type=int, default=20_000)
    parser.add_argument(
        "--robustness-seeds",
        nargs="*",
        type=int,
        default=list(ROBUSTNESS_SEEDS),
    )
    parser.add_argument(
        "--out",
        default="experiments/results/v2.50/weyl_g8_discriminator_frontier.json",
    )
    args = parser.parse_args()

    result = diagnose_weyl_g8_discriminator_frontier(
        args.samples,
        seed=args.seed,
        bootstrap_count=args.bootstrap_count,
        robustness_sample_count=args.robustness_samples,
        robustness_seeds=tuple(args.robustness_seeds),
    )
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
