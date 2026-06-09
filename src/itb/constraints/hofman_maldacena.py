"""Hofman-Maldacena conformal-collider wedge on the a/c central charges (v1.71).

This is the constraint that v1.70 said the engine could not feel until the basis
resolved the two curvature-squared anomalies. The 4d Weyl anomaly is

        <T^mu_mu> = c * Weyl^2 - a * Euler ,

with TWO central charges: a (Euler density) and c (Weyl^2). The toy basis used a
single coupling g_R2 for both; we now add a second curvature-squared coupling
g_C so the basis separates them:

        g_R2  <->  a   (Euler / Gauss-Bonnet coefficient)
        g_C   <->  c   (Weyl^2 coefficient)

Hofman-Maldacena (2008) energy-flux positivity at a conformal collider bounds the
ratio a/c for any unitary 4d CFT with a stress tensor:

        1/3  <=  a/c  <=  31/18 ,

the lower bound saturated by a free real scalar (a/c = 1/3) and the upper by a
free Maxwell vector (a/c = 31/18 ~ 1.722). With a proportional g_R2 and c
proportional g_C (same constant, so a/c = g_R2/g_C, and c = g_C > 0 for
unitarity) the wedge is the conjunction of two linear bounds:

        3 g_R2 - g_C       >= 0      (a/c >= 1/3)
        31 g_C - 18 g_R2   >= 0      (a/c <= 31/18)

equivalently (18/31) g_R2 <= g_C <= 3 g_R2, plus c = g_C > 0.

This is a genuinely NEW, TWO-SIDED bound of independent (conformal-collider /
ANEC) origin. It is the ONLY constraint in the stack that touches the new c-axis
g_C, so by construction it carries information no existing constraint encodes.

Frameworks default g_C = g_R2 (a/c = 1) -- the generic HOLOGRAPHIC expectation
(two-derivative Einstein duals force a = c; higher-derivative bulk corrections
shift c - a). A point at a/c = 1 sits dead-center in the wedge, so the bound does
not bite the default framework points; it bites theory-space points whose a/c is
far from 1. See the v1.71 results note.

Reference:
  Hofman, Maldacena. "Conformal collider physics: Energy and charge
  correlations." JHEP 05 (2008) 012.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory

AC_UPPER = 31.0 / 18.0   # ~1.7222


class HofmanMaldacenaWedge(Constraint):
    """1/3 <= a/c <= 31/18, with a = g_R2 (Euler), c = g_C (Weyl^2).

    g_C falls back to g_R2 (a/c = 1, the holographic a = c default) when a
    framework does not carry an explicit Weyl^2 coupling.
    """

    name = "hofman_maldacena_wedge"
    citation = "Hofman-Maldacena 2008 (conformal collider, 1/3 <= a/c <= 31/18)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def _coeffs(self, theory: Theory):
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gC = theory.coefficients.get("g_C", gR2)   # default a = c (holographic)
        return gR2, gC

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2, gC = self._coeffs(theory)
        # No curvature-squared sector at all (e.g. pure two-derivative GR):
        # a = c = 0, the theory is not a CFT with higher-curvature anomalies, so
        # the conformal-collider bound is INAPPLICABLE -> vacuously satisfied.
        if gR2 == 0.0 and gC == 0.0:
            return ConstraintResult(
                self.name, True, 0.0, 0.0,
                {"bound": "inapplicable (no curvature-squared sector)",
                 "a_over_c": 1.0, "g_R2": gR2, "g_C": gC, "binding": "none"},
            )
        # unitarity: c = g_C > 0 (a positive curvature-squared central charge)
        if gC <= 0.0:
            margin = gC if gC < 0 else -1e-12
            return ConstraintResult(
                self.name, False, margin,
                self._signed_distance(margin, {"g_C": 1.0}),
                {"bound": "c = g_C > 0 (unitarity)", "g_C": gC},
            )
        lower = 3.0 * gR2 - gC            # a/c >= 1/3
        upper = 31.0 * gC - 18.0 * gR2    # a/c <= 31/18
        margin = min(lower, upper)
        ac = gR2 / gC
        binding = "lower(a/c>=1/3)" if lower <= upper else "upper(a/c<=31/18)"
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, self.gradient(theory)),
            details={"bound": "1/3 <= a/c <= 31/18", "a_over_c": ac,
                     "binding": binding, "g_R2": gR2, "g_C": gC, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        gR2, gC = self._coeffs(theory)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_R2", "g_C"):
            out.setdefault(k, 0.0)
        if gC <= 0.0:
            out["g_C"] = 1.0
            return out
        lower = 3.0 * gR2 - gC
        upper = 31.0 * gC - 18.0 * gR2
        if lower <= upper:               # lower bound is binding
            out["g_R2"] = 3.0
            out["g_C"] = -1.0
        else:                            # upper bound is binding
            out["g_R2"] = -18.0
            out["g_C"] = 31.0
        return out
