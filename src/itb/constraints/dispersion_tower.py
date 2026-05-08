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
