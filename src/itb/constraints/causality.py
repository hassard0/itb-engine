"""Causality / refractive-index bound (class A amplitude).

Forward propagation in an EFT must be subluminal: the refractive index
seen by any mode in any background state must satisfy n >= 1 (group
velocity ≤ c). For our toy EFT, the leading correction to the index from
g_R2 takes the form:

    n - 1 ∝ -g_R2 * (background curvature)

For positive background curvature, causality requires g_R2 ≤ some bound
that depends on the matter sector. Here we encode a representative form:

    g_4 - g_R2 * γ >= 0    with γ = 1 in natural units

This is class A because it derives from the same dispersion-relation
machinery as positivity bounds, and is qualitatively the Adams-Arkani-Hamed
"causality + analyticity" obstruction at fixed t.

References: Adams et al 2006 §3 (causality side); de Rham, Tolley (2014)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class CausalityBound(Constraint):
    name = "causality_bound"
    citation = "Adams et al 2006 (causality from analyticity); de Rham-Tolley 2014"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, gamma: float = 1.0):
        self.gamma = float(gamma)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = g4 - self.gamma * gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": f"g_4 - {self.gamma} * g_R2 >= 0", "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_4"] = 1.0
        out["g_R2"] = -self.gamma
        return out
