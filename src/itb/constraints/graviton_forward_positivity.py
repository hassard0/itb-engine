"""Forward-limit graviton dispersion positivity.

For 2->2 graviton scattering, analyticity + unitarity + crossing give
dispersive sum rules in which the low-energy Wilson coefficients are
expressed as spectral integrals over a positive density (the imaginary part
of the amplitude, weighted by the partial-wave / Gegenbauer structure). After
subtracting the graviton t-channel pole (Caron-Huot & Van Duong 2021;
Caron-Huot, Mazac, Rastelli, Simmons-Duffin 2021; Cheung-Remmen / CEMZ), the
*leading* curvature coupling and the *subleading* cubic coupling are both
controlled by the SAME positive integral. Because that integral is dominated
by its leading-energy behaviour, the leading coupling must dominate the
subleading one: the two-sided bounds take the schematic form

    g_R2  >=  c * g_R3                      (c an O(1) forward-dispersion ratio)

i.e. the dimension-4 curvature-squared coupling g_R2 (which sets the s^2 term
of the forward amplitude) cannot be smaller than an O(1) multiple of the cubic
curvature coupling g_R3. A theory whose cubic coupling rivals its leading
coupling sits outside the dispersive cone.

This is a genuinely independent class-A bound: it is a LOWER bound on g_R2
(unlike the existing graviton positivity constraints, which bound it from
above or mix it with matter), and it pins the minimum magnitude of the leading
graviton coupling relative to the cubic.

Honest note: the precise value of c requires evaluating the literal two-sided
bound (the ratio of two Gegenbauer-weighted spectral integrals), which depends
on the spectral assumptions. The STRUCTURAL content — leading dominates cubic —
is robust; c ~ O(1) is the canonical placeholder, swept in the realism program.

References:
  Caron-Huot, Van Duong. "Extremal Effective Field Theories." JHEP 05 (2021) 280.
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin. "Sharp Boundaries for the
  Swampland." JHEP 07 (2021) 110.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class GravitonForwardPositivity(Constraint):
    """Forward-limit dispersion: leading curvature coupling dominates cubic.

        g_R2 - c * g_R3 >= 0
    """

    name = "graviton_forward_positivity"
    citation = "Caron-Huot-Van Duong 2021 (forward-limit graviton dispersion, two-sided)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, c: float = 1.2):
        self.c = float(c)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        margin = gR2 - self.c * gR3
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2 >= {self.c}*g_R3 (forward dispersion)",
                "g_R2": gR2, "g_R3": gR3, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_R2", "g_R3"):
            out.setdefault(k, 0.0)
        out["g_R2"] = 1.0
        out["g_R3"] = -self.c
        return out
