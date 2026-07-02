"""Cosmological-constant / dark-energy sector (v2.422, core extension CC1).

The engine had no vacuum-energy coupling -- the one big quantum-gravity problem it never touched. This module
adds a dimensionless vacuum-energy parameter g_Lambda (the dark-energy density in cutoff-scale units, positive =
de Sitter / dark energy, negative = anti-de Sitter, zero = Minkowski) and a first swampland constraint on it.

**The refined de Sitter Swampland Conjecture** (Ooguri-Palti-Shiu-Vafa 2018, refining Obied-Ooguri-Spodyneiko-
Vafa 2018): a scalar potential with V > 0 (a de Sitter / dark-energy vacuum) is in the swampland UNLESS it is
sufficiently steep or tachyonic --

    M_Pl |grad V| / V >= c    OR    M_Pl^2 min(grad grad V) / V <= -c'      (c, c' ~ O(1)).

A positive cosmological constant sitting at a potential extremum (grad V = 0) can only be consistent via the
SECOND condition: the potential must be sufficiently CONCAVE (tachyonic) relative to its height. The candidate's
dark energy is carried by the Starobinsky R^2 scalaron (g_R2 is the R^2 inflaton, this repo v1.86), whose plateau
IS concave -- so the refined-dS second condition maps, in this basis, to the scalaron potential curvature (set by
g_R2) bounding the vacuum energy:

    g_Lambda <= g_R2 / c_dS      (for g_Lambda > 0 ; trivially satisfied for g_Lambda <= 0, i.e. AdS/Minkowski).

This is a FIRST PROXY encoding: the refined dS conjecture is itself conjectural, and the map from the abstract
V''/V condition to the engine's dimensionless g_R2 is order-of-magnitude (the scalaron mass^2 ~ 1/(6 g_R2) in the
usual Starobinsky normalization, so larger curvature coupling = flatter potential = LESS able to support dS; the
sign/rough-scaling is the robust content, the exact c_dS is O(1)). It is tagged 'sourced_proxy' in the rigor
registry accordingly -- a conjectural swampland statement, not a source-exact positivity bound.

Reference: Ooguri, Palti, Shiu, Vafa. "Distance and de Sitter Conjectures on the Swampland." Phys. Lett. B 788
(2019) 180. Obied, Ooguri, Spodyneiko, Vafa. "De Sitter Space and the Swampland." (2018)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class DeSitterConjecture(Constraint):
    """Refined de Sitter conjecture (proxy): positive vacuum energy bounded by the scalaron curvature.

    g_Lambda <= g_R2 / c_dS   for g_Lambda > 0;   g_Lambda <= 0 (AdS/Minkowski) trivially satisfied.
    """

    name = "de_sitter_conjecture"
    citation = "Ooguri-Palti-Shiu-Vafa 2018 (refined dS swampland conjecture; toy scalaron-curvature proxy)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, c_dS: float = 1.0):
        self.c_dS = float(c_dS)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gL = theory.coefficients.get("g_Lambda", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        if gL <= 0.0:
            # AdS / Minkowski: no de Sitter tension.
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=True,
                margin=abs(gL) + 1e-6,
                signed_distance_margin=self._signed_distance(abs(gL) + 1e-6, grad),
                details={"bound": "g_Lambda <= 0 (AdS/Minkowski): refined-dS trivially satisfied",
                         "g_Lambda": gL, "g_R2": gR2},
            )
        bound = gR2 / self.c_dS
        margin = bound - gL
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": f"g_Lambda <= g_R2 / c_dS = {bound:.4f} (refined dS, c_dS={self.c_dS})",
                     "g_Lambda": gL, "g_R2": gR2, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        gL = theory.coefficients.get("g_Lambda", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_Lambda", 0.0)
        out.setdefault("g_R2", 0.0)
        if gL > 0.0:
            # margin = g_R2/c_dS - g_Lambda
            out["g_Lambda"] = -1.0
            out["g_R2"] = 1.0 / self.c_dS
        else:
            out["g_Lambda"] = 1.0  # margin = |g_Lambda| increases as g_Lambda -> more negative
        return out


class AdSDistanceConjecture(Constraint):
    """AdS distance conjecture (v2.423, CC2): a small |vacuum energy| requires a light tower.

    Lust-Palti-Vafa 2019: as |Lambda| -> 0 a tower of states becomes light, m_tower <= c |Lambda|^alpha
    (strong version alpha = 1/2). With the tower at the species scale Lambda_species = 1 / sqrt(N) (Dvali; the
    same N = 1 + nu*(|g_R2|+|g_C|+|g_R3|) the species-scale bound counts), the conjecture becomes a FLOOR on the
    vacuum-energy magnitude set by the tower:

        |g_Lambda| >= c_AdS * Lambda_species^(1/alpha) = c_AdS * (1/N)^(1/(2 alpha))   (alpha=1/2 -> c_AdS / N).

    So a bounded (not-parametrically-light) tower forbids a parametrically small cosmological constant -- the
    swampland form of the CC naturalness puzzle. Applied to the AdS branch (g_Lambda < 0), where the conjecture
    is on firmest footing; the g_Lambda >= 0 (dS/Minkowski) branch is left to the refined-dS constraint and is
    trivially satisfied here. Tagged 'sourced_proxy' (conjectural + O(1) c_AdS + the tower<->species identification).

    Reference: Lust, Palti, Vafa. "AdS and the Swampland." Phys. Lett. B 797 (2019) 134867."""

    name = "ads_distance_conjecture"
    citation = "Lust-Palti-Vafa 2019 (AdS distance conjecture; species-scale tower, O(1) c_AdS proxy)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, c_AdS: float = 1.0, nu: float = 2.0, alpha: float = 0.5):
        self.c_AdS = float(c_AdS)
        self.nu = float(nu)
        self.alpha = float(alpha)

    def _N(self, theory: Theory) -> float:
        gR2 = abs(theory.coefficients.get("g_R2", 0.0))
        gC = abs(theory.coefficients.get("g_C", 0.0))
        gR3 = abs(theory.coefficients.get("g_R3", 0.0))
        return 1.0 + self.nu * (gR2 + gC + gR3)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gL = theory.coefficients.get("g_Lambda", 0.0)
        N = self._N(theory)
        # Lambda_species = 1/sqrt(N); floor = c_AdS * Lambda_species^(1/alpha)
        floor = self.c_AdS * (1.0 / (N ** 0.5)) ** (1.0 / self.alpha)
        if gL >= 0.0:
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=True,
                margin=floor + 1e-6,
                signed_distance_margin=self._signed_distance(floor + 1e-6, grad),
                details={"bound": "g_Lambda >= 0: AdS-distance trivially satisfied (dS/Minkowski branch)",
                         "g_Lambda": gL, "N_species": N, "ads_floor": floor},
            )
        margin = abs(gL) - floor   # |g_Lambda| >= floor
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": f"|g_Lambda| >= c_AdS*(1/N)^(1/(2a)) = {floor:.4f} (AdS branch; N={N:.3f})",
                     "g_Lambda": gL, "N_species": N, "ads_floor": floor, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        gL = theory.coefficients.get("g_Lambda", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_Lambda", 0.0)
        if gL < 0.0:
            out["g_Lambda"] = -1.0   # margin = |g_Lambda| - floor; d/dg_Lambda = -1 for gL<0
        else:
            out["g_Lambda"] = 0.0
        return out
