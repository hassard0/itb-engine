"""Canonical full-stack assembly for realism experiments.

Single source of truth for the constraint stack and frameworks used by the
prefactor-realism program (2026-06). Reproduces the v1.10/v1.20 intersection
roster (31 constraints) and exposes the six "knife-edge" O(1) prefactors as
tunable knobs so the stack can be rebuilt from a prefactor vector.

The motivating fact (README "Honest limitations" + v1.8 honest synthesis):
every constraint uses O(1) placeholder prefactors — "the right streets but the
wrong house numbers." The realism program asks: which framework verdicts
survive when we admit we only know the house numbers to within a factor of ~2?

CANONICAL holds the documented default for each tunable knob.
PLAUSIBLE_RANGES holds a defensible literature-uncertainty interval per knob
(roughly factor-of-two O(1) ignorance). These ranges are modeling assumptions,
stated openly, not published numbers.
"""

from itb.constraints.anomaly import AnomalyCancellation
from itb.constraints.anomaly_flow import GeneralizedAnomalyInflow, tHooftAnomalyMatching
from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.causality import CausalityBound
from itb.constraints.cft_flat_space import CFTFlatSpaceBound
from itb.constraints.complexity_cutoff import ComplexityCutoff
from itb.constraints.cubic_parity import ParityViolatingCubicBound
from itb.constraints.dispersion_tower import DispersionTowerCauchySchwarz, ScalarPositivityG8
from itb.constraints.distance_conjecture import DistanceConjecture
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.generalized_second_law import GeneralizedSecondLaw
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.graviton_forward_positivity import GravitonForwardPositivity
from itb.constraints.graviton_self_coupling import CubicCurvaturePositivity, CubicGravitonMatterBound
from itb.constraints.holographic_entropy import HolographicSubadditivity
from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
from itb.constraints.parity_violation import (
    LIGOBirefringenceBound,
    LeftHandedGravitonPositivity,
    ParityViolatingPositivity,
    RightHandedGravitonPositivity,
)
from itb.constraints.quantum_focusing import QuantumFocusingConjecture
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import ScalarPositivityG4, ScalarPositivityG6
from itb.constraints.spin_four_positivity import SpinFourPositivity
from itb.constraints.swampland import WeakGravityConjecture
from itb.constraints.swampland_variants import ScalarWGC
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.theory import Theory


# ---------------------------------------------------------------------------
# Tunable BNOSSW MMI proxy (harmonic- or geometric-mean form).
# ---------------------------------------------------------------------------
class TunableBNOSSWMonogamy(Constraint):
    """BNOSSW monogamy-of-mutual-information proxy with a tunable prefactor
    and a switchable mean form.

        harmonic:  prefactor * g4*g6/(g4+g6)        >= g_R2
        geometric: prefactor * sqrt(g4*g6)          >= g_R2

    MMI is an entropy-vector inequality; neither form is "the" published
    bound in a Wilson-coefficient basis — both are structural representatives.
    The point of making BOTH the prefactor and the mean form tunable is to
    test whether the LQG verdict is robust to BOTH choices."""

    constraint_class = ConstraintClass.B_INFORMATION

    def __init__(self, prefactor: float = 1.0, mean: str = "harmonic"):
        self.prefactor = float(prefactor)
        self.mean = mean
        self.name = "bnossw_monogamy"
        self.citation = (
            f"BNOSSW MMI proxy ({mean} mean, prefactor {prefactor:.3f})"
        )

    def _bound(self, g4: float, g6: float) -> float:
        if self.mean == "geometric":
            return (g4 * g6) ** 0.5 if (g4 > 0 and g6 > 0) else 0.0
        denom = g4 + g6
        return (g4 * g6) / denom if denom > 0 else 0.0

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        if g4 == 0.0 and g6 == 0.0 and gR2 == 0.0:
            return ConstraintResult(self.name, True, 0.0, 0.0, {"bound": "origin"})
        denom = g4 + g6
        if denom <= 0:
            margin = -abs(gR2) if gR2 != 0.0 else 0.0
            return ConstraintResult(self.name, margin >= 0, margin, margin,
                                    {"bound": "denom<=0"})
        margin = self.prefactor * self._bound(g4, g6) - gR2
        return ConstraintResult(
            self.name, margin >= 0, margin,
            self._signed_distance(margin, self.gradient(theory)),
            {"bound": f"{self.prefactor:.3f}*{self.mean}(g4,g6) >= g_R2",
             "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_R2"] = -1.0
        if self.mean == "geometric":
            if g4 > 0 and g6 > 0:
                root = (g4 * g6) ** 0.5
                out["g_4"] = self.prefactor * g6 / (2 * root)
                out["g_6"] = self.prefactor * g4 / (2 * root)
        else:
            denom = g4 + g6
            if denom > 0:
                d2 = denom * denom
                out["g_4"] = self.prefactor * (g6 * g6) / d2
                out["g_6"] = self.prefactor * (g4 * g4) / d2
        return out


class TunableRFC(Constraint):
    """Repulsive Force Conjecture with a switchable structural form.

    'matter_product' (the engine's v1.x encoding, flagged by Dr. M. as
        miscast):       g_4*g_6 - g_R2 - gamma*g_R2^2 >= 0
        — multiplies two MATTER-sector coefficients (g_4,g_6) against a
        graviton coefficient; the frameworks have g_4*g_6 ~ g_R2 by
        construction, so this is a near-universal excluder for any gamma>0.

    'convex_hull' (re-cast per RFC/WGC physics): the repulsive matter force
        must dominate gravitational attraction. In the toy basis this pits
        the matter charge-to-mass coupling g_4 against the graviton coupling
        g_R2 with a sub-extremal correction:
                        g_4 - g_R2 - gamma*g_R2^2 >= 0
        — no spurious product of two matter coefficients.
    """

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, gamma: float = 1.0, form: str = "matter_product"):
        self.gamma = float(gamma)
        self.form = form
        self.name = "repulsive_force_conjecture"
        self.citation = f"Heidenreich-Reece-Rudelius 2019 (RFC, {form} form)"

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        if self.form == "convex_hull":
            margin = g4 - gR2 - self.gamma * gR2 * gR2
        else:
            margin = g4 * g6 - gR2 - self.gamma * gR2 * gR2
        return ConstraintResult(
            self.name, margin >= 0, margin,
            self._signed_distance(margin, self.gradient(theory)),
            {"bound": f"RFC ({self.form}, gamma={self.gamma:.3f})", "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        if self.form == "convex_hull":
            out["g_4"] = 1.0
        else:
            out["g_4"] = g6
            out["g_6"] = g4
        out["g_R2"] = -1.0 - 2.0 * self.gamma * gR2
        return out


# ---------------------------------------------------------------------------
# Knife-edge prefactors: canonical values + plausible literature ranges.
# ---------------------------------------------------------------------------
CANONICAL: dict[str, float] = {
    "bnossw_pref": 1.0,        # BNOSSW MMI harmonic-mean coefficient
    "rfc_gamma": 1.0,          # repulsive force conjecture quadratic coeff
    "cubic_kappa": 1.0,        # cubic graviton-matter bound g_R3 <= kappa*g_4^2
    "complexity_cmax": 1.5,    # Susskind/Lloyd complexity cutoff scale
    "scalar_wgc_beta": 0.5,    # Palti scalar-WGC scalar-force coefficient
    "cft_alpha": 0.5,          # CFT-to-flat-space mapping coefficient
    "graviton_fwd_c": 1.2,     # forward-dispersion leading/cubic ratio (v1.24)
}

# Factor-of-~2 O(1) ignorance windows. Stated assumptions, not published numbers.
PLAUSIBLE_RANGES: dict[str, tuple[float, float]] = {
    "bnossw_pref": (0.5, 2.0),
    "rfc_gamma": (0.5, 2.0),
    "cubic_kappa": (0.5, 2.0),
    "complexity_cmax": (1.0, 2.5),
    "scalar_wgc_beta": (0.25, 1.0),
    "cft_alpha": (0.25, 1.0),
    "graviton_fwd_c": (0.8, 1.6),
}


def build_stack(prefactors: dict[str, float] | None = None,
                bnossw_mean: str = "harmonic",
                rfc_form: str = "matter_product") -> list[Constraint]:
    """Assemble the canonical 31-constraint stack, overriding the six tunable
    knife-edge prefactors with `prefactors` (missing keys fall back to
    CANONICAL)."""
    p = dict(CANONICAL)
    if prefactors:
        p.update(prefactors)
    return [
        # --- Class A: amplitude bootstrap ---
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=p["cubic_kappa"]),
        SpinFourPositivity(),
        CFTFlatSpaceBound(alpha=p["cft_alpha"]),
        GravitonForwardPositivity(c=p["graviton_fwd_c"]),  # v1.24

        # --- Class B: information-theoretic ---
        BekensteinTight(), HolographicSubadditivity(),
        TunableBNOSSWMonogamy(prefactor=p["bnossw_pref"], mean=bnossw_mean),
        QuantumFocusingConjecture(), GeneralizedSecondLaw(),
        # --- parity sector (class A) ---
        ParityViolatingPositivity(kappa=1.0),
        LeftHandedGravitonPositivity(kappa=1.0),
        RightHandedGravitonPositivity(kappa=1.0),
        ParityViolatingCubicBound(kappa=1.0),
        LIGOBirefringenceBound(bound=0.1),
        # --- Class C: gravitational universality / swampland ---
        EFTValidityBox(box=2.0), CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        GeneralizedAnomalyInflow(rho=0.06),
        tHooftAnomalyMatching(rho_match=0.5, slack=0.02),
        WeakGravityConjecture(alpha=1.0),
        ScalarWGC(beta=p["scalar_wgc_beta"]),
        TunableRFC(gamma=p["rfc_gamma"], form=rfc_form),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=p["complexity_cmax"]),
        DistanceConjecture(R_max=20.0),
    ]


def frameworks() -> list:
    return [PureGR(), StringTreeEFT(), AsymptoticSafety(),
            LQGInduced(), CausalDynamicalTriangulation()]


INTERSECTION_INITIAL = {
    "g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2,
    "g_R3": 0.15, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
}
