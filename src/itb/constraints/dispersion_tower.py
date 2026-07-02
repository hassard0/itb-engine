"""Dispersion-tower positivity bounds.

The Caron-Huot et al positivity bounds derive from twice-subtracted forward
dispersion relations applied to 2->2 amplitudes. The tower of bounds reads:

    g_{2n} >= 0                 (positivity at each order)
    g_{2n}^2 <= g_{2n-2} * g_{2n+2}    (Cauchy-Schwarz between adjacent orders)

For our extended toy basis with (g_4, g_6, g_8) — i.e., adding the next-order
forward-amplitude coefficient g_8 = (1/8!) * d^8 M(s,0)/ds^8 |_{s=0} — the
chained bound is:

    g_6^2 <= g_4 * g_8

This is the genuine structure of the Caron-Huot dispersion tower (with our
prefactors set to 1 for clarity; published forms have O(1) numerical
prefactors that differ slightly by basis choice). The tower keeps going to
arbitrarily high orders; we encode just the next two for now.

References:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin. "Sharp boundaries for the
  swampland." JHEP 07 (2021) 110.
  Caron-Huot, de Rham, Tolley, Zhou. "Positivity bounds on bouncing
  cosmologies and their gauge fields." (2024)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarPositivityG8(Constraint):
    name = "scalar_positivity_g8"
    citation = "Caron-Huot et al 2021 — fourth-order forward positivity"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g8 = theory.coefficients.get("g_8", 0.0)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g8 >= 0,
            margin=g8,
            signed_distance_margin=self._signed_distance(g8, grad),
            details={"bound": "g_8 >= 0", "value": g8},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_8", 0.0)
        out["g_8"] = 1.0
        return out


class DispersionTowerCauchySchwarz(Constraint):
    """Chained Cauchy-Schwarz bound: g_6^2 <= g_4 * g_8."""

    name = "dispersion_tower_g6_squared_bound"
    citation = "Caron-Huot, Mazac, Rastelli, Simmons-Duffin 2021"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        margin = g4 * g8 - g6 * g6
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": "g_6^2 <= g_4 * g_8",
                "g_4": g4, "g_6": g6, "g_8": g8, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_8"):
            out.setdefault(k, 0.0)
        out["g_4"] = g8
        out["g_8"] = g4
        out["g_6"] = -2.0 * g6
        return out


class ScalarPositivityG10(Constraint):
    """g_10 >= 0: positivity of the next matter-tower moment (v2.426, MT extension)."""

    name = "scalar_positivity_g10"
    citation = "Caron-Huot et al 2021 -- fifth-order forward positivity (matter moment mu_5)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g10 = theory.coefficients.get("g_10", 0.0)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=g10 >= 0,
            margin=g10,
            signed_distance_margin=self._signed_distance(g10, grad),
            details={"bound": "g_10 >= 0", "value": g10},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_10", 0.0)
        out["g_10"] = 1.0
        return out


class MatterTowerRungG10(Constraint):
    """The next matter moment-tower rung: g_8^2 <= g_6 * g_10 (v2.426, MT extension).

    The dispersion tower's chained Cauchy-Schwarz bound g_{2n}^2 <= g_{2n-2} g_{2n+2} continued one rung past
    what the engine had (g_6^2 <= g_4 g_8): treating the matter Wilson coefficients (g_4, g_6, g_8, g_10) as
    consecutive moments mu_k of the positive spectral density (Im of the forward amplitude), the Hankel matrix of
    moments is positive semi-definite, so every adjacent 2x2 minor gives a log-convexity bound. This is the
    SAME source-exact moment-problem structure the engine already uses for the leading matter rung and for the
    curvature tower (g_R3^2 <= g_R2 g_R4, v2.375) -- pure Cauchy-Schwarz on a positive measure, RIGOROUS. Opt-in;
    it makes the "infinite matter tower" (v2.375/v2.381) concrete by one more rung.

    Reference: Caron-Huot-Van Duong 2021 (dispersive moments / Hankel positivity); Arkani-Hamed-Huang-Huang
    (EFThedron moment structure)."""

    name = "matter_tower_g8_squared_bound"
    citation = "Caron-Huot-Van Duong 2021 (matter moment-tower Hankel positivity, next rung)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        g10 = theory.coefficients.get("g_10", 0.0)
        margin = g6 * g10 - g8 * g8
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": "g_8^2 <= g_6 * g_10", "g_6": g6, "g_8": g8, "g_10": g10, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        g10 = theory.coefficients.get("g_10", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_6", "g_8", "g_10"):
            out.setdefault(k, 0.0)
        out["g_6"] = g10
        out["g_10"] = g6
        out["g_8"] = -2.0 * g8
        return out
