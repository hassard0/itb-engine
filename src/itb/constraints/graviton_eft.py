"""Mixed positivity bound coupling scalar EFT coefficients (g_4, g_6) to a
graviton-coupled higher-curvature operator (g_R2 = coefficient of R^2 in the
gravitational EFT).

For an EFT containing a scalar plus a graviton with R^2 coupling, dispersion
relations on amplitudes that mix scalar and graviton intermediate states give a
Cauchy-Schwarz-type bound:

    g_R2^2 <= g_4 * g_6      (in natural units, modulo numerical prefactors)

Equivalently, the coefficient of the spin-2 R^2 term cannot exceed the
geometric mean of the scalar positivity coefficients. This is the v0.4 step
out of the toy scalar EFT into actual graviton physics.

References:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin (2021-2024) on gravitational
  positivity bounds; the simplification here keeps the qualitative structure
  while remaining tractable in our localhost engine."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class GravitonMixedPositivity(Constraint):
    name = "graviton_mixed_positivity"
    citation = "Caron-Huot, Mazac, Rastelli, Simmons-Duffin (2021-2024) — simplified"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = g4 * g6 - gR2 * gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": "g_R2^2 <= g_4 * g_6",
                "g_4": g4, "g_6": g6, "g_R2": gR2, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out.setdefault("g_6", 0.0)
        out.setdefault("g_R2", 0.0)
        out["g_4"] = g6
        out["g_6"] = g4
        out["g_R2"] = -2.0 * gR2
        return out
