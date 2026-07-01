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
from itb.constraints.bh_entropy_positivity import WaldEntropyPositivity
from itb.constraints.causality import CausalityBound
from itb.constraints.cemz_causality import CEMZCausality
from itb.constraints.cft_flat_space import CFTFlatSpaceBound
from itb.constraints.cross_sector_efthedron import CrossSectorEFThedron
from itb.constraints.complexity_cutoff import ComplexityCutoff
from itb.constraints.cubic_parity import ParityViolatingCubicBound
from itb.constraints.dispersion_tower import DispersionTowerCauchySchwarz, ScalarPositivityG8
from itb.constraints.curvature_dispersion_tower import (
    CurvatureRiemann4Positivity,
    CurvatureMomentTowerMandate,
)
from itb.constraints.distance_conjecture import DistanceConjecture
from itb.constraints.eft_validity import EFTValidityBox
from itb.constraints.generalized_second_law import GeneralizedSecondLaw
from itb.constraints.graviton_eft import GravitonMixedPositivity
from itb.constraints.gw_dispersion import GWDispersionBound
from itb.constraints.gw_speed import GWSpeedBound
from itb.constraints.graviton_forward_positivity import GravitonForwardPositivity
from itb.constraints.graviton_self_coupling import CubicCurvaturePositivity, CubicGravitonMatterBound
from itb.constraints.hofman_maldacena import HofmanMaldacenaWedge
from itb.constraints.holographic_entropy import HolographicSubadditivity
from itb.constraints.matter_s3_positivity import MatterS3Positivity
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
from itb.constraints.species_scale import SpeciesScaleBound
from itb.constraints.spin_four_positivity import SpinFourPositivity
from itb.constraints.cosmic_birefringence import CosmicBirefringenceData
from itb.constraints.submm_gravity import SubmmGravityYukawaBound
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
    "matter_s3_cm": 1.0,       # matter s^3 forward-moment ratio (v1.25)
    "anomaly_rho": 0.06,       # gravitational anomaly-inflow coefficient (v1.26)
    "cemz_kappa": 0.8,         # CEMZ graviton-causality prefactor (v1.61)
    "efthedron_alpha": 1.1,    # cross-sector dim-8 EFThedron prefactor (v1.61, Dr. M.)
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
    "matter_s3_cm": (0.8, 1.4),
    "anomaly_rho": (0.03, 0.12),
    "cemz_kappa": (0.6, 1.2),
    "efthedron_alpha": (0.8, 1.5),
}


def build_stack(prefactors: dict[str, float] | None = None,
                bnossw_mean: str = "harmonic",
                rfc_form: str = "matter_product",
                include_data: bool = False,
                submm_screened: bool = False,
                include_birefringence: bool = False,
                birefringence_mode: str = "hint",
                birefringence_nsigma: float = 2.0,
                include_gw_speed: bool = False,
                gw_speed_low_cutoff: bool = True,
                include_gw_dispersion: bool = False,
                gw_dispersion_low_cutoff: bool = True,
                include_curvature_tower: bool = False) -> list[Constraint]:
    """Assemble the canonical constraint stack, overriding the tunable knife-edge
    prefactors with `prefactors` (missing keys fall back to CANONICAL).

    All default constraints are THEORETICAL axioms. DATA-sourced constraints are
    opt-in and default OFF (so the theoretical-only stack is unchanged):
      - `include_data=True`: Eot-Wash sub-mm gravity Yukawa bound (v1.77, matter
        sector); `submm_screened=True` makes it vacuous.
      - `include_birefringence=True`: cosmic-birefringence band (v1.78, parity
        sector; Minami-Komatsu beta=0.34+/-0.09 deg) -- PREFERS nonzero parity.
        `birefringence_mode` in {hint, confirmed, ignore}, `birefringence_nsigma`."""
    p = dict(CANONICAL)
    if prefactors:
        p.update(prefactors)
    stack = [
        # --- Class A: amplitude bootstrap ---
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=p["cubic_kappa"]),
        SpinFourPositivity(),
        CFTFlatSpaceBound(alpha=p["cft_alpha"]),
        GravitonForwardPositivity(c=p["graviton_fwd_c"]),  # v1.24
        MatterS3Positivity(c_m=p["matter_s3_cm"]),          # v1.25
        CEMZCausality(kappa=p["cemz_kappa"]),               # v1.61 (causality)
        CrossSectorEFThedron(alpha=p["efthedron_alpha"]),   # v1.61 (cross-sector, Dr. M.)
        HofmanMaldacenaWedge(),                             # v1.71 (a/c collider wedge)

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
        GeneralizedAnomalyInflow(rho=p["anomaly_rho"]),
        tHooftAnomalyMatching(rho_match=0.5, slack=0.02),
        WeakGravityConjecture(alpha=1.0),
        WaldEntropyPositivity(),                            # v1.82 (CLR/WGC, BH entropy)
        ScalarWGC(beta=p["scalar_wgc_beta"]),
        TunableRFC(gamma=p["rfc_gamma"], form=rfc_form),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=p["complexity_cmax"]),
        DistanceConjecture(R_max=20.0),
        SpeciesScaleBound(nu=2.0, N_max=3.0),               # v1.96 (species scale / tower)
    ]
    if include_data:
        # --- DATA: first experiment-sourced constraint (v1.77, matter sector) ---
        stack.append(SubmmGravityYukawaBound(screened=submm_screened))
    if include_birefringence:
        # --- DATA: second experiment (v1.78, parity sector) ---
        stack.append(CosmicBirefringenceData(mode=birefringence_mode,
                                             n_sigma=birefringence_nsigma))
    if include_gw_speed:
        # --- DATA: third experiment (v1.84, tensor-propagation sector, speed) ---
        stack.append(GWSpeedBound(low_cutoff=gw_speed_low_cutoff))
    if include_gw_dispersion:
        # --- DATA: fourth experiment (v1.85, tensor dispersion, the proper probe) ---
        stack.append(GWDispersionBound(low_cutoff=gw_dispersion_low_cutoff))
    if include_curvature_tower:
        # --- v2.292: the g_R4 (Riemann^4) curvature dispersion tower (opt-in core-engine extension) ---
        stack.append(CurvatureRiemann4Positivity())
        stack.append(CurvatureMomentTowerMandate())
    return stack


# --- Rigor classification (v2.411): make the toy-vs-real distinction first-class. -----------------
# Every constraint is tagged by how much its FORM depends on toy O(1) input:
#   "rigorous"      : source-exact amplitude positivity / causality / bootstrap bound. The inequality
#                     structure is the published result (Adams-Nicolis-Rattazzi, Caron-Huot et al,
#                     CEMZ, Hofman-Maldacena, Arkani-Hamed EFThedron); only overall units/prefactor are
#                     simplified. A conclusion resting on these alone needs ZERO toy input.
#   "sourced_proxy" : a real conjecture/theorem (WGC, swampland distance/species, anomaly matching,
#                     GSL/Bekenstein/QFC, complexity) encoded via a toy O(1) proxy FORM -- the physics
#                     is real, the specific inequality is a placeholder.
#   "data"          : a real measurement, but mapped to the couplings through an O(1) observable map.
RIGOR = {
    # --- rigorous: source-exact amplitude positivity / causality / bootstrap (19) ---
    "scalar_positivity_g4": "rigorous", "scalar_positivity_g6": "rigorous",
    "scalar_positivity_g8": "rigorous", "scalar_convexity_g6_vs_g4": "rigorous",
    "dispersion_tower_g6_squared_bound": "rigorous", "graviton_forward_positivity": "rigorous",
    "graviton_mixed_positivity": "rigorous", "matter_s3_positivity": "rigorous",
    "spin_four_positivity": "rigorous", "cubic_curvature_positivity": "rigorous",
    "cubic_graviton_matter_bound": "rigorous", "cross_sector_efthedron": "rigorous",
    "cemz_causality": "rigorous", "hofman_maldacena_wedge": "rigorous",
    "cft_flat_space_bound": "rigorous", "parity_violating_positivity": "rigorous",
    "left_handed_graviton_positivity": "rigorous", "right_handed_graviton_positivity": "rigorous",
    "parity_violating_cubic_bound": "rigorous",
    # --- sourced_proxy: real conjecture/theorem via a toy O(1) proxy form (17) ---
    "weak_gravity_conjecture": "sourced_proxy", "scalar_wgc": "sourced_proxy",
    "swampland_distance_conjecture": "sourced_proxy", "species_scale_bound": "sourced_proxy",
    "repulsive_force_conjecture": "sourced_proxy", "anomaly_cancellation": "sourced_proxy",
    "generalized_anomaly_inflow": "sourced_proxy", "t_hooft_anomaly_matching": "sourced_proxy",
    "bekenstein_tight": "sourced_proxy", "holographic_subadditivity": "sourced_proxy",
    "bnossw_monogamy": "sourced_proxy", "quantum_focusing_conjecture": "sourced_proxy",
    "generalized_second_law": "sourced_proxy", "wald_entropy_positivity": "sourced_proxy",
    "complexity_cutoff": "sourced_proxy", "causality_bound": "sourced_proxy",
    "eft_validity_box": "sourced_proxy",
    # --- data: real measurement mapped through an O(1) observable map (6) ---
    "cosmic_birefringence_data": "data", "gw_speed_bound": "data", "gw_dispersion_bound": "data",
    "ligo_birefringence_bound": "data", "ligo_graviton_mass_bound": "data",
    "submm_gravity_yukawa_bound": "data",
}


def rigor_of(name: str) -> str:
    """Rigor tier of a constraint by name; unknown -> 'sourced_proxy' (conservative)."""
    return RIGOR.get(name, "sourced_proxy")


def filter_by_rigor(stack: list, tiers) -> list:
    """Keep only constraints whose rigor tier is in `tiers` (a set/list of tier strings)."""
    tiers = set(tiers)
    return [c for c in stack if rigor_of(getattr(c, "name", "")) in tiers]


def rigorous_core_stack(**build_kwargs) -> list:
    """The rigorous core: only the source-exact amplitude/causality/bootstrap constraints -- ZERO toy input.

    Accepts the same kwargs as build_stack(); data/birefringence flags are irrelevant here since data
    constraints are excluded by tier, but they are passed through so callers can reuse one kwargs dict.
    """
    return filter_by_rigor(build_stack(**build_kwargs), {"rigorous"})


# --- Rigorous-IMPLIED constraints (v2.412): sourced_proxy/data constraints whose CUT is already made by the
# rigorous core -- empirically, ~100% of rigorous-core-feasible points satisfy them, so their conclusions are
# secretly rigorous (their toy prefactor does not matter: the source-exact positivity/causality already implies
# the inequality). Determined by the v2.412 redundancy scan over the rigorous-feasible region. Notably the WGC
# (matter dominance's gravity ceiling) and the Wald-entropy / extremal-BH-decay bound are here -- so those
# results are rigorous, not toy. (submm-in-screened-mode and gw_speed are redundant only because they are
# trivially satisfied / non-binding; the physically meaningful promotions are positivity-implies-swampland.)
IMPLIED_BY_RIGOROUS = frozenset({
    "weak_gravity_conjecture", "wald_entropy_positivity", "generalized_second_law",
    "quantum_focusing_conjecture", "holographic_subadditivity", "t_hooft_anomaly_matching",
    "causality_bound", "eft_validity_box", "species_scale_bound",
    "submm_gravity_yukawa_bound", "gw_speed_bound",
})


def effective_rigorous_stack(**build_kwargs) -> list:
    """Source-exact core PLUS the constraints the core already implies (v2.412) -- the effective zero-toy stack.

    A conclusion resting only on this set needs no toy prefactor: it is either a source-exact bound or a bound
    the source-exact bounds already force.
    """
    stack = build_stack(**build_kwargs)
    return [c for c in stack if rigor_of(getattr(c, "name", "")) == "rigorous"
            or getattr(c, "name", "") in IMPLIED_BY_RIGOROUS]


# --- Harmless-speculative vs load-bearing toy (v2.413): of the constraints that add genuine information beyond
# the rigorous+implied set, WHICH does the candidate actually depend on? Full-stack leverage scan (drop each,
# measure how much the local feasible region opens):
#   complexity_cutoff              1.11x   nearly redundant  -> HARMLESS (research-grade conjecture, but unused)
#   swampland_distance_conjecture  1.11x   nearly redundant  -> HARMLESS (toy aspect-ratio proxy, but unused)
#   anomaly_cancellation           1.36x   LOAD-BEARING      -> the genuine toy dependence
#   generalized_anomaly_inflow     2.43x   LOAD-BEARING      -> the genuine toy dependence
#   cosmic_birefringence_data      7.36x   LOAD-BEARING      -> real DATA (v2.408), not toy
# So the candidate's real toy dependence (beyond real data) is the ANOMALY SECTOR alone; the two most
# speculative proxies (complexity, SDC) do not shape the result.
HARMLESS_SPECULATIVE = frozenset({"complexity_cutoff", "swampland_distance_conjecture"})
LOAD_BEARING_TOY = frozenset({"anomaly_cancellation", "generalized_anomaly_inflow"})


def frameworks() -> list:
    return [PureGR(), StringTreeEFT(), AsymptoticSafety(),
            LQGInduced(), CausalDynamicalTriangulation()]


INTERSECTION_INITIAL = {
    "g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2,
    "g_R3": 0.15, "g_R2_parity": 0.0, "g_R3_parity": 0.0,
}
