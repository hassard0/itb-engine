"""v1.15 — Cross-framework convergence analysis.

After v1.14 projection, each framework has both an 'original' set of
Wilson coefficients (its toy encoded values) and a 'projected' set
(the L2-nearest feasible point). Compute pairwise distances between:

  1. Original framework values
  2. Projected framework values

If projected distances are systematically smaller than original
distances, the engine is *converging* the candidate UV completions
toward a common region — a real convergence prediction.

If projected distances are similar to or larger than original, the
constraint set isn't pulling frameworks together; they remain distinct.

This is the engine's first analysis comparing pre/post-projection
clustering."""

from pathlib import Path

import numpy as np

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow, tHooftAnomalyMatching,
)
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.complexity_cutoff import ComplexityCutoff
from itb.constraints.cubic_parity import ParityViolatingCubicBound
from itb.constraints.dispersion_tower import (
    DispersionTowerCauchySchwarz, ScalarPositivityG8,
)
from itb.constraints.distance_conjecture import DistanceConjecture
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.generalized_second_law import GeneralizedSecondLaw
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.graviton_self_coupling import (
    CubicCurvaturePositivity, CubicGravitonMatterBound,
)
from itb.constraints.holographic_entropy import (
    BNOSSWMonogamy, HolographicSubadditivity,
)
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.parity_violation import (
    LIGOBirefringenceBound, LeftHandedGravitonPositivity,
    ParityViolatingPositivity, RightHandedGravitonPositivity,
)
from itb.constraints.quantum_focusing import QuantumFocusingConjecture
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4, ScalarPositivityG6,
)
from itb.constraints.spin_four_positivity import SpinFourPositivity
from itb.constraints.swampland import WeakGravityConjecture
from itb.constraints.swampland_variants import (
    RepulsiveForceConjecture, ScalarWGC,
)
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.projection import project_framework_to_feasible


def _l2(a: dict[str, float], b: dict[str, float]) -> float:
    keys = sorted(set(a) | set(b))
    diff = np.array([a.get(k, 0.0) - b.get(k, 0.0) for k in keys])
    return float(np.sqrt(np.sum(diff ** 2)))


def main() -> None:
    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0),
        SpinFourPositivity(),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        QuantumFocusingConjecture(),
        GeneralizedSecondLaw(),
        ParityViolatingPositivity(kappa=1.0),
        LeftHandedGravitonPositivity(kappa=1.0),
        RightHandedGravitonPositivity(kappa=1.0),
        ParityViolatingCubicBound(kappa=1.0),
        LIGOBirefringenceBound(bound=0.1),
        EFTValidityBox(box=2.0), CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        GeneralizedAnomalyInflow(rho=0.06),
        tHooftAnomalyMatching(rho_match=0.5, slack=0.02),
        WeakGravityConjecture(alpha=1.0),
        ScalarWGC(beta=1.0),
        RepulsiveForceConjecture(gamma=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
        DistanceConjecture(R_max=20.0),
    ]
    frameworks = [PureGR(), StringTreeEFT(), AsymptoticSafety(),
                  LQGInduced(), CausalDynamicalTriangulation()]

    projections = {}
    for fw in frameworks:
        proj = project_framework_to_feasible(fw, constraints, max_iters=1000)
        projections[fw.name] = proj

    # Pairwise distance matrices
    names = [fw.name for fw in frameworks]
    n = len(names)

    D_orig = np.zeros((n, n))
    D_proj = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D_orig[i, j] = _l2(
                projections[names[i]].original_coefficients,
                projections[names[j]].original_coefficients,
            )
            D_proj[i, j] = _l2(
                projections[names[i]].projected_coefficients,
                projections[names[j]].projected_coefficients,
            )

    print("Pairwise distance matrices (5 frameworks):\n")
    print("ORIGINAL:")
    print("           " + "  ".join(f"{n:>10}" for n in names))
    for i, ni in enumerate(names):
        row = "  ".join(f"{D_orig[i, j]:10.4f}" for j in range(n))
        print(f"  {ni:<10} {row}")
    print("\nPROJECTED:")
    print("           " + "  ".join(f"{n:>10}" for n in names))
    for i, ni in enumerate(names):
        row = "  ".join(f"{D_proj[i, j]:10.4f}" for j in range(n))
        print(f"  {ni:<10} {row}")

    # Convergence ratio: projected / original
    print("\nCONVERGENCE RATIOS (projected/original):")
    print("           " + "  ".join(f"{n:>10}" for n in names))
    for i, ni in enumerate(names):
        row = []
        for j in range(n):
            if i == j or D_orig[i, j] < 1e-9:
                row.append(f"{'   --   ':>10}")
            else:
                ratio = D_proj[i, j] / D_orig[i, j]
                row.append(f"{ratio:10.4f}")
        print(f"  {ni:<10} {'  '.join(row)}")

    # Mean ratio for non-trivial pairs (excluding pure_gr from comparison
    # since its projected = original = origin, ratio always 1.0).
    nontrivial = [i for i, n in enumerate(names) if n != "pure_gr"]
    ratios = []
    for i in nontrivial:
        for j in nontrivial:
            if i < j and D_orig[i, j] > 1e-9:
                ratios.append(D_proj[i, j] / D_orig[i, j])

    print(f"\nMean convergence ratio (non-trivial pairs only): {np.mean(ratios):.4f}")
    print(f"  if < 1.0: the engine is *converging* frameworks toward each other")
    print(f"  if > 1.0: projection separates frameworks more than originally")

    md = []
    md.append("# v1.15 - Cross-framework convergence analysis\n")
    md.append("Pairwise L2 distances in 7D coefficient space, before and after\n")
    md.append("projection onto the 30-constraint feasible region.\n\n")

    md.append("## Distance matrices\n")
    md.append("**Original** (encoded toy values):\n")
    md.append("| | " + " | ".join(names) + " |")
    md.append("|---|" + "|".join(["---"] * n) + "|")
    for i, ni in enumerate(names):
        row = "| " + ni + " | " + " | ".join(
            f"{D_orig[i, j]:.4f}" for j in range(n)
        ) + " |"
        md.append(row)
    md.append("\n**Projected** (L2-nearest feasible):\n")
    md.append("| | " + " | ".join(names) + " |")
    md.append("|---|" + "|".join(["---"] * n) + "|")
    for i, ni in enumerate(names):
        row = "| " + ni + " | " + " | ".join(
            f"{D_proj[i, j]:.4f}" for j in range(n)
        ) + " |"
        md.append(row)

    md.append("\n## Convergence ratios (projected / original)\n")
    md.append("| | " + " | ".join(names) + " |")
    md.append("|---|" + "|".join(["---"] * n) + "|")
    for i, ni in enumerate(names):
        cells = []
        for j in range(n):
            if i == j or D_orig[i, j] < 1e-9:
                cells.append("--")
            else:
                cells.append(f"{D_proj[i, j] / D_orig[i, j]:.3f}")
        md.append(f"| {ni} | " + " | ".join(cells) + " |")
    md.append(f"\n**Mean ratio (non-trivial pairs):** {np.mean(ratios):.4f}\n")

    md.append("## Reading\n")
    if np.mean(ratios) < 0.95:
        md.append(
            f"With mean ratio {np.mean(ratios):.3f} < 1.0, the engine is "
            f"**converging** the candidate UV completions toward each other "
            f"under the constraint stack. Pairs that drop most are the most "
            f"strongly aligned by the constraints.\n"
        )
    elif np.mean(ratios) > 1.05:
        md.append(
            f"With mean ratio {np.mean(ratios):.3f} > 1.0, projection is "
            f"actually *separating* the frameworks. The constraint set "
            f"resolves them more sharply than their toy values do.\n"
        )
    else:
        md.append(
            f"Mean ratio {np.mean(ratios):.3f} is near 1.0 — projection "
            f"preserves the framework geometry without strong convergence "
            f"or separation.\n"
        )

    out = Path("docs/results/2026-05-08-v1.15-convergence-analysis.md")
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
