"""Cubic-order parity-violating gravitational EFT constraint.

The Wilson coefficient g_R3_parity controls the parity-violating analog of
the cube-of-Riemann operator (e.g. ε^μνρσ R_μνρσ × R^αβγδ R_αβγδ couplings).
In the dispersion-tower structure, the parity-decomposed cubic bound reads:

    |g_R3|^2 + |g_R3_parity|^2 <= κ * g_4^2

— the same shape as the v1.4 quadratic parity bound, scaled up to cubic
order. UV completions producing large parity-odd cubic curvature without
correspondingly large matter coupling are inconsistent.

References:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin, Tolley, Zhou — extended
  parity decomposition (2023-2024)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ParityViolatingCubicBound(Constraint):
    name = "parity_violating_cubic_bound"
    citation = "Caron-Huot et al 2024 (parity-decomposed cubic positivity)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, kappa: float = 1.0):
        self.kappa = float(kappa)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        gR3p = theory.coefficients.get("g_R3_parity", 0.0)
        margin = self.kappa * g4 * g4 - (gR3 * gR3 + gR3p * gR3p)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R3^2 + g_R3_parity^2 <= {self.kappa} * g_4^2",
                "g_R3": gR3, "g_R3_parity": gR3p, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        gR3p = theory.coefficients.get("g_R3_parity", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R3", "g_R3_parity"):
            out.setdefault(k, 0.0)
        out["g_4"] = 2.0 * self.kappa * g4
        out["g_R3"] = -2.0 * gR3
        out["g_R3_parity"] = -2.0 * gR3p
        return out
