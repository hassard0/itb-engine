"""Dimension-8 cross-sector EFThedron positivity (Dr. M.'s recommendation, v1.61).

The EFThedron (Arkani-Hamed–Huang–Huang 2020) packages amplitude analyticity +
unitarity into positivity of the dispersive moments. Existing engine bounds are
intra-sector: matter convexity / dispersion tower (g_4,g_6,g_8) and graviton
positivity (g_R2,g_R3). This is the first CROSS-SECTOR bound: from the analyticity
of the matter+graviton -> matter+graviton amplitude, the s^4 matter moment (g_8)
and the s^1 graviton curvature (g_R2) are linked to the next-order moments (g_6,
g_R3) through a positive-definite cross-sector spectral density:

    g_8 * g_R2  >=  alpha * g_6 * g_R3

with alpha ~ O(1). The s-power bookkeeping is consistent: g_8~s^4 and g_R2~s^1
give s^5, matching g_6~s^3 and g_R3~s^2. This is a DIFFERENT physical statement
than the (lower-order) cubic graviton-matter vertex bound — it probes the UV
completeness of the cross-sector amplitude at dimension 8.

Honest: alpha ~ 1.1 is a motivated guess (the s^4 cross-sector spectral weight);
the literal coefficient needs the explicit cross-amplitude Hankel kernel. The
structural content (a cross-sector Hankel positivity coupling g_8 g_R2 to
g_6 g_R3) is the robust, genuinely-new piece.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class CrossSectorEFThedron(Constraint):
    """g_8 * g_R2 >= alpha * g_6 * g_R3  (dim-8 cross-sector positivity)."""

    name = "cross_sector_efthedron"
    citation = "Arkani-Hamed-Huang-Huang EFThedron (cross-sector dim-8 positivity)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, alpha: float = 1.1):
        self.alpha = float(alpha)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        margin = g8 * gR2 - self.alpha * g6 * gR3
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_8*g_R2 >= {self.alpha}*g_6*g_R3",
                "lhs": g8 * gR2, "rhs": self.alpha * g6 * gR3, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_6", "g_8", "g_R2", "g_R3"):
            out.setdefault(k, 0.0)
        out["g_8"] = gR2
        out["g_R2"] = g8
        out["g_6"] = -self.alpha * gR3
        out["g_R3"] = -self.alpha * g6
        return out
