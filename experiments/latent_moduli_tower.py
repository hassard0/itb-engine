"""Latent moduli/tower diagnostic for the distance-prior bottleneck.

v2.18 showed that continuous tower/species norms are cleaner than the hard
coefficient max/min prior, but still redundant in the current basis. This
experiment inserts an explicit latent chain:

    Wilson coefficients -> inferred modulus distance -> tower mass -> species cutoff.

It is still a toy diagnostic. The point is to make the missing assumptions
inspectable before claiming a physical Swampland Distance Conjecture encoding.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, ".")
from experiments.phases import KEYS
from experiments.stack import build_stack
from experiments.tower_surrogate_distance import (
    _epsilon_to_zero_continuity,
    _framework_summary,
    _topology_diagnostic,
)
from experiments.tower_surrogate_overlap import (
    LEGACY_OVERLAP_CONSTRAINTS,
    _legacy_constraints,
    _targeted_samples,
)
from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.engine import check
from itb.predict import FRAMEWORKS
from itb.theory import Theory


CURVATURE_KEYS = ("g_R2", "g_C", "g_R3")
PARITY_KEYS = ("g_R2_parity", "g_R3_parity")
DEFAULT_NMAX_VALUES = (1.6, 1.8, 2.0, 2.2, 2.5, 3.0)


@dataclass(frozen=True)
class LatentTowerConfig:
    name: str
    reference: str
    transverse_weight: float
    parity_weight: float
    kappa: float = 1.5
    lambda_tower: float = 1.0
    tower_density: float = 1.0
    N_max: float = 3.0


DEFAULT_CONFIGS = (
    LatentTowerConfig(
        name="centroid_radial",
        reference="centroid_mean",
        transverse_weight=0.0,
        parity_weight=0.0,
    ),
    LatentTowerConfig(
        name="centroid_transverse",
        reference="centroid_mean",
        transverse_weight=2.0,
        parity_weight=0.5,
    ),
    LatentTowerConfig(
        name="data_driven_transverse",
        reference="discovered_data_driven",
        transverse_weight=2.0,
        parity_weight=0.5,
    ),
    LatentTowerConfig(
        name="string_transverse",
        reference="string_tree_eft",
        transverse_weight=2.0,
        parity_weight=0.5,
    ),
)


class LatentModuliTowerPrior(Constraint):
    """Toy latent-modulus tower prior.

    The reference direction represents a one-modulus trajectory in curvature
    coefficient space. The radial coordinate infers a field distance, transverse
    mismatch penalizes movement away from that trajectory, and the tower law uses
    m_tower = exp(-lambda*d). This is a diagnostic, not a canonical SDC.
    """

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, config: LatentTowerConfig, reference_vector: np.ndarray):
        self.config = config
        norm = float(np.linalg.norm(reference_vector))
        if norm <= 0.0:
            raise ValueError("reference_vector must be nonzero")
        self.reference_vector = reference_vector.astype(float)
        self.reference_direction = self.reference_vector / norm
        self.name = f"latent_moduli_tower_{config.name}"
        self.citation = "v2.19 latent moduli/tower diagnostic"

    def _curvature_vector(self, theory: Theory) -> np.ndarray:
        return np.array(
            [float(theory.coefficients.get(key, 0.0)) for key in CURVATURE_KEYS],
            dtype=float,
        )

    def _parity_vector(self, theory: Theory) -> np.ndarray:
        return np.array(
            [float(theory.coefficients.get(key, 0.0)) for key in PARITY_KEYS],
            dtype=float,
        )

    def latent_observables(self, theory: Theory) -> dict[str, float]:
        q = self._curvature_vector(theory)
        p = self._parity_vector(theory)
        radial = max(float(np.dot(q, self.reference_direction)), 0.0)
        transverse = float(np.linalg.norm(q - radial * self.reference_direction))
        parity_norm = float(np.linalg.norm(p))
        distance = math.log1p(self.config.kappa * radial)
        tower_mass = math.exp(-self.config.lambda_tower * distance)
        radial_species = 1.0 + self.config.tower_density * (
            math.exp(self.config.lambda_tower * distance) - 1.0
        )
        mismatch_species = (
            self.config.transverse_weight * transverse * transverse
            + self.config.parity_weight * parity_norm * parity_norm
        )
        species = radial_species + mismatch_species
        cutoff = 1.0 / math.sqrt(species)
        return {
            "radial_coordinate": radial,
            "transverse_mismatch": transverse,
            "parity_norm": parity_norm,
            "latent_distance": distance,
            "tower_mass": tower_mass,
            "N_tower": species,
            "species_cutoff": cutoff,
        }

    def tower_load(self, theory: Theory) -> float:
        return self.latent_observables(theory)["latent_distance"]

    def tower_species(self, theory: Theory) -> float:
        return self.latent_observables(theory)["N_tower"]

    def evaluate(self, theory: Theory) -> ConstraintResult:
        obs = self.latent_observables(theory)
        margin = self.config.N_max - obs["N_tower"]
        return ConstraintResult(
            self.name,
            margin >= 0.0,
            margin,
            margin,
            {
                **obs,
                "N_max": self.config.N_max,
                "reference": self.config.reference,
                "transverse_weight": self.config.transverse_weight,
                "parity_weight": self.config.parity_weight,
                "bound": "N_tower(d, transverse, parity) <= N_max",
                "tower_law": "m_tower = exp(-lambda_tower * latent_distance)",
            },
        )


def _json_default(value: Any) -> Any:
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _parse_float_list(raw: str) -> list[float]:
    return [float(part.strip()) for part in raw.split(",") if part.strip()]


def _theory(x: np.ndarray) -> Theory:
    return Theory(coefficients={k: float(v) for k, v in zip(KEYS, x)})


def _centroids(phases_doc: dict) -> list[np.ndarray]:
    return [
        np.array([phase["centroid"][k] for k in KEYS], dtype=float)
        for phase in phases_doc["phases"]
    ]


def _parity_zero(x: np.ndarray) -> np.ndarray:
    z = x.copy()
    z[KEYS.index("g_R2_parity")] = 0.0
    z[KEYS.index("g_R3_parity")] = 0.0
    return z


def _curvature_vector_from_coefficients(coefficients: dict[str, float]) -> np.ndarray:
    return np.array([float(coefficients.get(key, 0.0)) for key in CURVATURE_KEYS])


def _reference_vector(reference: str, centroids: list[np.ndarray]) -> np.ndarray:
    if reference == "centroid_mean":
        indices = [KEYS.index(key) for key in CURVATURE_KEYS]
        return np.mean([centroid[indices] for centroid in centroids], axis=0)
    if reference in FRAMEWORKS:
        return _curvature_vector_from_coefficients(FRAMEWORKS[reference].encode().coefficients)
    raise ValueError(f"unknown latent reference: {reference}")


def _base_stack() -> list[Constraint]:
    return build_stack(bnossw_mean="geometric", rfc_form="convex_hull")


def _reference_stack() -> list[Constraint]:
    return [
        constraint
        for constraint in _base_stack()
        if constraint.name not in {
            "swampland_distance_conjecture",
            "species_scale_bound",
        }
    ]


def _stack_with_prior(prior: Constraint) -> list[Constraint]:
    return _reference_stack() + [prior]


def _framework_latent_rows(prior: LatentModuliTowerPrior) -> dict[str, dict]:
    rows = {}
    for name, framework in FRAMEWORKS.items():
        theory = framework.encode()
        rows[name] = prior.latent_observables(theory)
    return rows


def _centroid_latent_rows(
    centroids: list[np.ndarray],
    prior: LatentModuliTowerPrior,
) -> list[dict]:
    rows = []
    for idx, centroid in enumerate(centroids):
        z = _parity_zero(centroid)
        rows.append({
            "component": idx,
            "centroid": prior.latent_observables(_theory(centroid)),
            "parity_zero_projection": prior.latent_observables(_theory(z)),
        })
    return rows


def _targeted_overlap(
    prior: LatentModuliTowerPrior,
    points: np.ndarray,
) -> dict:
    reference = _reference_stack()
    legacy = _legacy_constraints()
    reference_feasible = np.array([
        check(_theory(point), reference).feasible for point in points
    ])
    prior_satisfied = np.array([
        prior.evaluate(_theory(point)).satisfied for point in points
    ])
    candidate_feasible = reference_feasible & prior_satisfied
    prior_fail = ~prior_satisfied
    reference_gate = reference_feasible & prior_fail

    legacy_fail = {
        name: np.array([
            not constraint.evaluate(_theory(point)).satisfied for point in points
        ])
        for name, constraint in legacy.items()
    }
    gate_count = int(reference_gate.sum())
    all_prior_fail_count = int(prior_fail.sum())

    def fraction(count: int, denominator: int) -> float | None:
        return None if denominator == 0 else count / denominator

    return {
        "reference_feasible": int(reference_feasible.sum()),
        "candidate_feasible": int(candidate_feasible.sum()),
        "latent_gate_count": gate_count,
        "all_latent_prior_failures": all_prior_fail_count,
        "irreplaceability_growth_pct": (
            100.0 * (int(reference_feasible.sum()) / int(candidate_feasible.sum()) - 1.0)
            if int(candidate_feasible.sum()) else None
        ),
        "overlap_reference_gate": {
            name: {
                "count": int((reference_gate & failures).sum()),
                "fraction_of_reference_gate": fraction(
                    int((reference_gate & failures).sum()),
                    gate_count,
                ),
            }
            for name, failures in legacy_fail.items()
        },
        "overlap_all_latent_failures": {
            name: {
                "count": int((prior_fail & failures).sum()),
                "fraction_of_latent_failures": fraction(
                    int((prior_fail & failures).sum()),
                    all_prior_fail_count,
                ),
            }
            for name, failures in legacy_fail.items()
        },
    }


def _radial_monotonicity(prior: LatentModuliTowerPrior) -> dict:
    rows = []
    for scale in (0.0, 0.5, 1.0, 1.5, 2.0):
        q = prior.reference_vector * scale
        theory = Theory(
            coefficients={
                "g_R2": float(q[0]),
                "g_C": float(q[1]),
                "g_R3": float(q[2]),
                "g_R2_parity": 0.02,
                "g_R3_parity": 0.01,
            }
        )
        rows.append(prior.latent_observables(theory) | {"radial_scale": scale})
    distances = [row["latent_distance"] for row in rows]
    masses = [row["tower_mass"] for row in rows]
    species = [row["N_tower"] for row in rows]
    return {
        "rows": rows,
        "distance_non_decreasing": all(
            distances[i] <= distances[i + 1] + 1e-12
            for i in range(len(distances) - 1)
        ),
        "tower_mass_non_increasing": all(
            masses[i] >= masses[i + 1] - 1e-12 for i in range(len(masses) - 1)
        ),
        "species_non_decreasing": all(
            species[i] <= species[i + 1] + 1e-12
            for i in range(len(species) - 1)
        ),
        "species_cutoff_non_increasing": all(
            rows[i]["species_cutoff"] >= rows[i + 1]["species_cutoff"] - 1e-12
            for i in range(len(rows) - 1)
        ),
    }


def _candidate_result(
    config: LatentTowerConfig,
    reference_vector: np.ndarray,
    centroids: list[np.ndarray],
    zero_points: list[np.ndarray],
    points: np.ndarray,
    samples: int,
) -> dict:
    prior = LatentModuliTowerPrior(config=config, reference_vector=reference_vector)
    constraints = _stack_with_prior(prior)
    topology = _topology_diagnostic(centroids, zero_points, constraints, samples=samples)
    frameworks = _framework_summary(constraints, _reference_stack(), prior=prior)
    overlap = _targeted_overlap(prior, points)
    continuity = _epsilon_to_zero_continuity(
        centroids,
        constraints,
        prior,
    )
    accepted = (
        topology["all_connected_by_parity_zero_detour"]
        and not frameworks["additional_exclusions_vs_reference"]
        and not frameworks["prior_only_failures"]
        and not continuity["has_punctured_gap_near_zero"]
    )
    return {
        "config": config.__dict__,
        "accepted_basic_latent_gate": accepted,
        "reference_vector": {
            key: float(value) for key, value in zip(CURVATURE_KEYS, reference_vector)
        },
        "topology": topology,
        "frameworks": frameworks,
        "targeted_overlap": overlap,
        "epsilon_to_zero_continuity": continuity,
        "radial_monotonicity": _radial_monotonicity(prior),
        "centroid_latent_observables": _centroid_latent_rows(centroids, prior),
        "framework_latent_observables": _framework_latent_rows(prior),
    }


def _candidate_gate_summary(
    config: LatentTowerConfig,
    reference_vector: np.ndarray,
    centroids: list[np.ndarray],
    zero_points: list[np.ndarray],
    samples: int,
) -> dict:
    prior = LatentModuliTowerPrior(config=config, reference_vector=reference_vector)
    constraints = _stack_with_prior(prior)
    topology = _topology_diagnostic(centroids, zero_points, constraints, samples=samples)
    frameworks = _framework_summary(constraints, _reference_stack(), prior=prior)
    continuity = _epsilon_to_zero_continuity(centroids, constraints, prior)
    accepted = (
        topology["all_connected_by_parity_zero_detour"]
        and not frameworks["additional_exclusions_vs_reference"]
        and not frameworks["prior_only_failures"]
        and not continuity["has_punctured_gap_near_zero"]
    )
    return {
        "accepted_basic_latent_gate": accepted,
        "additional_framework_exclusions": frameworks["additional_exclusions_vs_reference"],
        "prior_only_framework_failures": frameworks["prior_only_failures"],
        "topology_connected": topology["all_connected_by_parity_zero_detour"],
        "punctured_gap_near_zero": continuity["has_punctured_gap_near_zero"],
    }


def _parameter_sensitivity(
    config: LatentTowerConfig,
    reference_vector: np.ndarray,
    centroids: list[np.ndarray],
) -> list[dict]:
    rows = []
    for lambda_tower in (0.5, 1.0, 1.5):
        for kappa in (1.0, 1.5, 2.0):
            for transverse_weight in (0.0, config.transverse_weight, 4.0):
                sensitivity_config = LatentTowerConfig(
                    **{
                        **config.__dict__,
                        "lambda_tower": lambda_tower,
                        "kappa": kappa,
                        "transverse_weight": transverse_weight,
                    }
                )
                prior = LatentModuliTowerPrior(
                    config=sensitivity_config,
                    reference_vector=reference_vector,
                )
                obs = [
                    prior.latent_observables(_theory(centroid))
                    for centroid in centroids
                ]
                rows.append({
                    "lambda_tower": lambda_tower,
                    "kappa": kappa,
                    "transverse_weight": transverse_weight,
                    "max_centroid_N_tower": max(row["N_tower"] for row in obs),
                    "max_centroid_distance": max(row["latent_distance"] for row in obs),
                    "min_centroid_tower_mass": min(row["tower_mass"] for row in obs),
                    "min_centroid_species_cutoff": min(
                        row["species_cutoff"] for row in obs
                    ),
                })
    return rows


def diagnose_latent_moduli_tower(
    phases_path: str | Path,
    samples: int = 101,
    targeted_samples: int = 20_000,
    seed: int = 31415,
    nmax_values: list[float] | None = None,
) -> dict:
    phases_doc = json.loads(Path(phases_path).read_text(encoding="utf-8"))
    centroids = _centroids(phases_doc)
    zero_points = [_parity_zero(centroid) for centroid in centroids]
    points = _targeted_samples(centroids, samples=targeted_samples, seed=seed)
    sweep_values = nmax_values or list(DEFAULT_NMAX_VALUES)

    configs = list(DEFAULT_CONFIGS)
    candidates = {}
    sweeps = {}
    parameter_sensitivity = {}
    for config in configs:
        ref = _reference_vector(config.reference, centroids)
        candidates[config.name] = _candidate_result(
            config,
            ref,
            centroids,
            zero_points,
            points,
            samples=samples,
        )
        parameter_sensitivity[config.name] = _parameter_sensitivity(
            config,
            ref,
            centroids,
        )
        rows = []
        for nmax in sweep_values:
            sweep_config = LatentTowerConfig(**{**config.__dict__, "N_max": float(nmax)})
            row = _candidate_gate_summary(
                sweep_config,
                ref,
                centroids,
                zero_points,
                samples=samples,
            )
            rows.append({
                "N_max": float(nmax),
                "accepted_basic_latent_gate": row["accepted_basic_latent_gate"],
                "additional_framework_exclusions": row["additional_framework_exclusions"],
                "prior_only_framework_failures": row["prior_only_framework_failures"],
                "topology_connected": row["topology_connected"],
                "punctured_gap_near_zero": row["punctured_gap_near_zero"],
            })
        sweeps[config.name] = {
            "rows": rows,
            "first_accepting_N_max": next(
                (
                    row["N_max"]
                    for row in rows
                    if row["accepted_basic_latent_gate"]
                ),
                None,
            ),
        }

    return {
        "input": str(phases_path),
        "basis": KEYS,
        "samples_per_segment": samples,
        "targeted_overlap_samples": targeted_samples,
        "seed": seed,
        "N_max_sweep": sweep_values,
        "legacy_overlap_constraints": LEGACY_OVERLAP_CONSTRAINTS,
        "literature_guardrail": {
            "claim": (
                "This diagnostic makes the moduli/tower assumptions explicit, but "
                "the latent coordinate is inferred from the same Wilson basis. It is "
                "a model audit, not a physical implementation or validation of the "
                "Swampland Distance Conjecture."
            ),
            "primary_sources": [
                {
                    "title": "Ooguri and Vafa, On the Geometry of the String Landscape and the Swampland",
                    "url": "https://arxiv.org/abs/hep-th/0605264",
                },
                {
                    "title": "van de Heisteeg, Vafa, and Wiesner, Bounds on Species Scale and the Distance Conjecture",
                    "url": "https://arxiv.org/abs/2303.13580",
                },
                {
                    "title": "van de Heisteeg, Vafa, Wiesner, and Wu, Moduli-dependent Species Scale",
                    "url": "https://arxiv.org/abs/2212.06841",
                },
            ],
        },
        "candidates_at_N_max_3": candidates,
        "N_max_sweeps": sweeps,
        "parameter_sensitivity": parameter_sensitivity,
        "interpretation": (
            "A latent model is interesting only if it removes the parity-zero "
            "artifact, preserves known framework representatives, and adds a "
            "targeted gate not wholly attributable to old aggregate curvature "
            "constraints. Passing these checks is still not an SDC solution."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="experiments/results/v2.13/phases_8d_1200.json")
    parser.add_argument("--out", default="experiments/results/v2.19/latent_moduli_tower.json")
    parser.add_argument("--samples", type=int, default=101)
    parser.add_argument("--targeted-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=31415)
    parser.add_argument(
        "--nmax-values",
        default=",".join(str(value) for value in DEFAULT_NMAX_VALUES),
        help="comma-separated N_max values for latent-model calibration",
    )
    args = parser.parse_args()

    result = diagnose_latent_moduli_tower(
        args.input,
        samples=args.samples,
        targeted_samples=args.targeted_samples,
        seed=args.seed,
        nmax_values=_parse_float_list(args.nmax_values),
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, default=_json_default), encoding="utf-8")
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
