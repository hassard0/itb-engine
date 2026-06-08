"""CEMZ graviton-causality bound on the cubic curvature coupling.

Camanho, Edelstein, Maldacena, Zhiboedov (2014) showed that a higher-curvature
(cubic) correction to the graviton three-point function induces a *time advance*
in high-energy gravitational scattering, violating causality — unless an infinite
tower of higher-spin states enters at a scale set by the coupling. The low-energy
consequence is a bound on the cubic curvature coupling: it cannot be arbitrarily
large relative to the leading (quadratic) curvature coupling and the matter sector
that sources the scattering.

In the toy 7-coefficient basis we encode the structural form

    |g_R3| <= kappa * sqrt(g_4 * g_R2)

i.e. the cubic graviton self-coupling is bounded by the geometric mean of the
matter coupling g_4 (what scatters) and the leading curvature coupling g_R2 (the
graviton self-interaction), with kappa an O(1) causality prefactor. This rests on
CAUSALITY (no time advance), a *different* physical principle from the
analyticity/unitarity behind the dispersive positivity bounds, and has a distinct
functional form from forward positivity (g_R2 >= c*g_R3). Its value is to test
whether causality *independently* disfavours the large-cubic frameworks.

Honest: the geometric-mean form and kappa~O(1) are representative; the literal
CEMZ bound is a statement about the required higher-spin scale. The structural
content (causality bounds the cubic relative to the available couplings) is robust.
"""

import math

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class CEMZCausality(Constraint):
    """|g_R3| <= kappa * sqrt(g_4 * g_R2)  (graviton time-advance causality)."""

    name = "cemz_causality"
    citation = "Camanho-Edelstein-Maldacena-Zhiboedov 2014 (graviton causality / time-advance)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, kappa: float = 0.8):
        self.kappa = float(kappa)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        if g4 < 0 or gR2 < 0:
            margin = -abs(gR3)          # ill-defined bound -> treat as violated
        else:
            margin = self.kappa * math.sqrt(g4 * gR2) - abs(gR3)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"|g_R3| <= {self.kappa}*sqrt(g_4*g_R2)",
                "g_R3": gR3, "rhs": (self.kappa * math.sqrt(g4 * gR2)
                                     if (g4 >= 0 and gR2 >= 0) else None),
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R2", "g_R3"):
            out.setdefault(k, 0.0)
        if g4 > 0 and gR2 > 0:
            root = math.sqrt(g4 * gR2)
            out["g_4"] = self.kappa * gR2 / (2 * root)
            out["g_R2"] = self.kappa * g4 / (2 * root)
        out["g_R3"] = -1.0 if gR3 >= 0 else 1.0
        return out
