"""v1.17 - Bayesian posterior over Wilson coefficients per framework.

For each framework, draw 5000 samples from a Gaussian prior centered at
the framework's encoded values, with sigma=0.05. Accept samples that
satisfy the v1.16 constraint set. Report posterior mean, std, and
acceptance rate per coefficient."""

from pathlib import Path

from itb.bayesian_posterior import sample_posterior
from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import (
    GeneralizedAnomalyInflow, tHooftAnomalyMatching,
)
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.cft_flat_space import CFTFlatSpaceBound
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
from itb.frameworks.string_tree_eft import StringTreeEFT


def main() -> None:
    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0), SpinFourPositivity(),
        CFTFlatSpaceBound(alpha=0.5),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        QuantumFocusingConjecture(), GeneralizedSecondLaw(),
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
        ScalarWGC(beta=1.0), RepulsiveForceConjecture(gamma=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
        DistanceConjecture(R_max=20.0),
    ]
    frameworks = [StringTreeEFT(), AsymptoticSafety(), CausalDynamicalTriangulation(), LQGInduced()]

    md = []
    md.append("# v1.17 - Bayesian posterior per framework\n")
    md.append("Rejection sampling: 5000 draws from Gaussian prior centered at "
              "encoded values, sigma=0.05. Posterior = those satisfying "
              "all 31 v1.16 constraints.\n")

    for fw in frameworks:
        prior = fw.encode().coefficients
        post = sample_posterior(prior, constraints, sigma=0.05, n_samples=5000)
        print(f"\n{fw.name}:")
        print(f"  acceptance rate: {post.acceptance_rate:.3%} ({post.n_samples_accepted} of 5000)")
        if post.n_samples_accepted > 0:
            for k in sorted(prior.keys()):
                shift = post.posterior_mean[k] - prior[k]
                if abs(shift) > 0.005:
                    print(f"  {k:<15} prior={prior[k]:.4f}  posterior={post.posterior_mean[k]:.4f}  shift={shift:+.4f}  std={post.posterior_std[k]:.4f}")

        md.append(f"## {fw.name}\n")
        md.append(f"- Acceptance rate: **{post.acceptance_rate:.2%}** ({post.n_samples_accepted}/5000)\n")
        md.append("| coefficient | prior (encoded) | posterior mean | shift | posterior std |")
        md.append("|---|---|---|---|---|")
        for k in sorted(prior.keys()):
            if post.n_samples_accepted == 0:
                md.append(f"| {k} | {prior[k]:.4f} | (no samples) | -- | -- |")
            else:
                shift = post.posterior_mean[k] - prior[k]
                md.append(f"| {k} | {prior[k]:.4f} | {post.posterior_mean[k]:.4f} | {shift:+.4f} | {post.posterior_std[k]:.4f} |")
        md.append("")

    out = Path("docs/results/2026-05-08-v1.17-bayesian-posterior.md")
    out.write_text("\n".join(md), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
