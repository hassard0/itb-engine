"""Generalized 4D gravitational anomaly cancellation (class C universality).

In dimensions where parity-violating gauge couplings to gravity exist,
gravitational anomalies must cancel for the theory to be quantum-mechanically
consistent. Translated to our toy EFT, the constraint is:

    g_4 * g_6  -  c_anom * g_R2^2  =  0  (within tolerance)

where c_anom is a numerical coefficient. This is a *two-sided* equality
constraint encoded as a margin that's only positive in a thin slab around
the anomaly-cancellation surface.

Reference: Alvarez-Gaumé–Witten (1984), Bardeen–Zumino. The form here is a
representative simplification."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class AnomalyCancellation(Constraint):
    name = "anomaly_cancellation"
    citation = "Alvarez-Gaumé–Witten 1984 (toy 4D form)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, c_anom: float = 1.0, tolerance: float = 0.15):
        self.c_anom = float(c_anom)
        self.tolerance = float(tolerance)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        residual = g4 * g6 - self.c_anom * gR2 * gR2
        # Allow within ±tolerance of zero
        margin = self.tolerance - abs(residual)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "residual": residual,
                "tolerance": self.tolerance,
                "c_anom": self.c_anom,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        # Margin is a "slab" — gradient of |residual| flips sign at residual=0.
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        residual = g4 * g6 - self.c_anom * gR2 * gR2
        sgn = 1.0 if residual >= 0 else -1.0
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        # d(margin)/dx = -d|residual|/dx = -sgn * d(residual)/dx
        out["g_4"] = -sgn * g6
        out["g_6"] = -sgn * g4
        out["g_R2"] = -sgn * (-2.0 * self.c_anom * gR2)
        return out
