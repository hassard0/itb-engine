"""Weak Gravity Conjecture (WGC) — first real swampland constraint.

The WGC, in its original form (Arkani-Hamed-Motl-Nicolis-Vafa 2007), states
that any U(1) gauge theory coupled to gravity must contain at least one
charged particle whose charge-to-mass ratio is at least that of an extremal
black hole:

    q/m >= (q/m)_extremal

Translated to the EFT framework, this constrains the relative strength of
matter (gauge) couplings to gravity. For our toy basis with `g_4` (matter
self-interaction) and `g_R2` (graviton-mediated), the simplification is:

    g_R2 <= alpha_WGC * sqrt(g_4)

where alpha_WGC is an O(1) prefactor set by the precise form of the
extremal-mass relation in the relevant theory. We use alpha_WGC = 1 here,
which is roughly representative.

This constraint is a *gravitational universality* statement: it must hold in
any consistent theory of quantum gravity, regardless of the matter content.

References:
  Arkani-Hamed, Motl, Nicolis, Vafa. "The String Landscape, Black Holes and
  Gravity as the Weakest Force." JHEP 06 (2007) 060.
  Reviews: Palti (2019); Harlow et al (2022)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class WeakGravityConjecture(Constraint):
    name = "weak_gravity_conjecture"
    citation = "Arkani-Hamed, Motl, Nicolis, Vafa 2007 (toy form, alpha=1)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, alpha: float = 1.0):
        self.alpha = float(alpha)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        # WGC: g_R2 <= alpha * sqrt(g_4)
        # Margin: alpha * sqrt(g_4) - g_R2  (only defined for g_4 >= 0)
        if g4 < 0:
            margin = -1.0  # undefined / definitely violated when matter coefficient is negative
        else:
            margin = self.alpha * (g4 ** 0.5) - gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2 <= {self.alpha} * sqrt(g_4)",
                "g_4": g4, "g_R2": gR2, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R2"):
            out.setdefault(k, 0.0)
        if g4 > 0:
            out["g_4"] = self.alpha / (2.0 * (g4 ** 0.5))
        out["g_R2"] = -1.0
        return out
