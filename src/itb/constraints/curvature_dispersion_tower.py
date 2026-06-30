"""Curvature dispersion tower: the Riemann^4 (g_R4) operator and its mandated positivity.

NEW ENGINE THEORY (v2.292, the authorized g_R4 core-engine extension). The matter sector already
carries a dispersion tower g_{2n}^2 <= g_{2n-2} g_{2n+2} (dispersion_tower.py: g_6^2 <= g_4 g_8). The
CURVATURE sector has the exact analog. The leading curvature operators g_R2 (Ricci^2), g_R3 (Ricci^3)
and g_R4 (Riemann^4, dim-8) are forward-limit moments of a positive spectral density, so by the same
twice-subtracted dispersion / Cauchy-Schwarz argument (the Stieltjes moment structure of v2.261) they
obey

    g_R4 >= 0                          (curvature positivity at the quartic order)
    g_R3^2 <= g_R2 * g_R4              (Cauchy-Schwarz between adjacent curvature moments)

The second is the v2.234 MANDATE: a consistent UV completion with nonzero g_R2, g_R3 is FORCED to carry
a nonzero Riemann^4 coefficient g_R4 >= g_R3^2/g_R2. g_R4 is the FIRST ringdown-active curvature
operator (v2.233: Schwarzschild is Ricci-flat, so g_R2/g_R3 are ringdown-blind and the quartic Riemann
contraction is the leading operator that deforms the QNM spectrum). Adding it makes the engine's
ringdown phenomenology internal rather than imported.

References:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin, JHEP 07 (2021) 110 (the moment / EFT-hedron tower).
  this repo: v2.234 (the g_R4 mandate), v2.261 (curvature couplings as a Stieltjes moment sequence),
             v2.233 (Riemann^4 is the first ringdown-active curvature operator)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class CurvatureRiemann4Positivity(Constraint):
    """g_R4 >= 0 -- the Riemann^4 coefficient is a positive forward-limit moment."""

    name = "curvature_riemann4_positivity"
    citation = "Caron-Huot et al 2021 (curvature-sector forward positivity); this repo v2.261"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR4 = theory.coefficients.get("g_R4", 0.0)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=gR4 >= 0,
            margin=gR4,
            signed_distance_margin=self._signed_distance(gR4, self.gradient(theory)),
            details={"bound": "g_R4 >= 0", "value": gR4},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R4", 0.0)
        out["g_R4"] = 1.0
        return out


class CurvatureMomentTowerMandate(Constraint):
    """g_R3^2 <= g_R2 * g_R4 -- the curvature Cauchy-Schwarz; mandates g_R4 >= g_R3^2/g_R2 (v2.234)."""

    name = "curvature_moment_tower_g_R4_mandate"
    citation = "this repo v2.234 / v2.261 (curvature dispersion tower); Caron-Huot et al 2021"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        gR4 = theory.coefficients.get("g_R4", 0.0)
        margin = gR2 * gR4 - gR3 * gR3        # >= 0  <=>  g_R3^2 <= g_R2 g_R4
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, self.gradient(theory)),
            details={"bound": "g_R3^2 <= g_R2 * g_R4 (g_R4 >= g_R3^2/g_R2)",
                     "g_R2": gR2, "g_R3": gR3, "g_R4": gR4, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        gR4 = theory.coefficients.get("g_R4", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_R2", "g_R3", "g_R4"):
            out.setdefault(k, 0.0)
        out["g_R2"] = gR4
        out["g_R4"] = gR2
        out["g_R3"] = -2.0 * gR3
        return out
