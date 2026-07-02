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
